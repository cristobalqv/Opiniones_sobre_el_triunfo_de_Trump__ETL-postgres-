import requests
import time
import pandas as pd 
import os
import json 
import logging
import praw 
from typing import List, Dict, Set
from datetime import datetime



class CommentDownloader:     #Clase que maneja la descarga de comentarios
    # de manera eficiente y por lotes
    def __init__(self, reddit_instance: praw.Reddit):
        self.reddit = reddit_instance
        self.logger = self._setup_logger()

        # Crea carpetas y archivos necesarios. Controla el progreso y la recuperacion
        self.checkpoint_file = "comment_checkpoint.json"
        self.output_folder = "comment_batches"
        os.makedirs(self.output_folder, exist_ok = True)

    #configura logging para monitoreo del proceso
    def _setup_logger(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler("comment_download.log"),
                logging.StreamHandler()
            ]
        )
        return logging.getLogger(__name__)
    
    #carga los comentarios ya procesados
    def _load_checkpoint(self) -> Set[str]:
        if os.path.exists(self.checkpoint_file):
            with open (self.checkpoint_file, 'r') as f:
                return set(json.load(f)['processed_comments'])
        return set()

    #guarda el progreso actual
    def _save_checkpoint(self, processed_comments: Set[str]):
        with open(self.checkpoint_file, 'w') as f:
            json.dump({'processed_comments': list(processed_comments)}, f)

    # guarda un lote de comentarios en un archivo separado
    def _save_batch(self, comments: List[Dict], batch_num: int):
        df = pd.DataFrame(comments)
        filename = f"{self.output_folder}/comments_batch_{batch_num}.csv"
        df.to_csv(filename, index=False)
        self.logger.info(f"Guardado lote {batch_num} con {len(comments)} comentarios")

    #descarga todos los comentarios de un post en lotes manejables
    def download_all_comments(self, post_id: str, comments_per_batch: int = 100, pause_seconds: int = 62):
        submission = self.reddit.submission(id=post_id)
        self.logger.info(f"Iniciando descarga de {submission.num_comments} comentarios")

        #cargamos progreso anterior si existe
        processed_comments = self._load_checkpoint()
        self.logger.info(f"Comentarios ya procesados: {len(processed_comments)}")

        # Expandimos todos los comentarios
        self.logger.info("Expandiendo árbol de comentarios...")
        submission.comments.replace_more(limit=None)

        #obtener lista plana de todos los comentarios
        all_comments = submission.comments.list()
        total_comments = len(all_comments)
        self.logger.info(f"Total de comentarios encontrados: {total_comments}")

        current_batch = []
        batch_number = len(processed_comments) // comments_per_batch + 1
        comments_processed = 0

        for comment in all_comments:
            if comment.id in processed_comments:
                continue

            comment_data = {
                'id': comment.id,
                'parent_id': comment.parent_id,
                'body': comment.body,
                'score': comment.score,
                'created_utc': datetime.fromtimestamp(comment.created_utc),
                'author': str(comment.author) if comment.author else '[deleted]',
                'depth': comment.depth,  # Nivel de anidación del comentario
                'is_root': comment.parent_id.startswith('t3_')  # True si es comentario principal
            }

            current_batch.append(comment_data)
            processed_comments.add(comment.id)
            comments_processed += 1

            if len(current_batch) >= comments_per_batch:
                self._save_batch(current_batch, batch_number)
                self._save_checkpoint(processed_comments)

                progress = (comments_processed / total_comments) * 100
                self.logger.info(f"Progreso: {progress:.2f}% ({comments_processed}/{total_comments})")

                current_batch = []     #vuelvo a iniciar una lista vacia
                batch_number += 1

                if comments_processed < total_comments:
                    self.logger.info(f"Pausa de {pause_seconds} segundos...")
                    time.sleep(pause_seconds)
        
        # Guardar último batch si quedan comentarios
        if current_batch:
            self._save_batch(current_batch, batch_number)
            self._save_checkpoint(processed_comments)

        self.logger.info(f"Descarga completada. Total de comentarios: {comments_processed}")
        return self._merge_all_batches()

    #Combina todos los lotes en un único DataFrame
    def _merge_all_batches(self) -> pd.DataFrame:
        all_files = sorted(os.listdir(self.output_folder))
        all_dfs = []

        for filename in all_files:
            if filename.endswith('.csv'):
                df = pd.read_csv(os.path.join(self.output_folder, filename))
                all_dfs.append(df)

        final_df = pd.concat(all_dfs, ignore_index = True)
        final_df.to_csv("all_comments.csv", index=False)
        self.logger.info(f"Archivo final creado con {len(final_df)} comentarios")
        return final_df