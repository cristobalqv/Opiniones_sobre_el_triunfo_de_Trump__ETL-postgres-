from reddit.src.data.extractors import CommentDownloader
import praw
import os
from dotenv import load_dotenv
from reddit.src.utils.utils import ConexionYCargaPostgres, TransformarData
import pandas as pd

load_dotenv()

credenciales_reddit = {
    'client_id': os.getenv('client_id'),
    'client_secret': os.getenv('client_secret'),
    'user_agent': os.getenv('user_agent')
    }

credenciales_postgres = {
    'postgres_user': os.getenv('postgres_user'),
    'postgres_pass': os.getenv('postgres_pass'),
    'postgres_host':  os.getenv('postgres_host'),
    'postgres_port': os.getenv('postgres_port'),
    'postgres_database': os.getenv('postgres_database')
    }


if __name__ == '__main__':

    reddit = praw.Reddit(
        client_id = credenciales_reddit['client_id'],
        client_secret = credenciales_reddit['client_secret'],
        user_agent = credenciales_reddit['user_agent']
    )

    loader = CommentDownloader(reddit)
    post_id = '1gl0ty4'
    df = loader.download_all_comments(
        post_id=post_id,
        comments_per_batch=1000,
        pause_seconds=62
    )


    df=pd.read_csv('reddit/data/raw/all_comments.csv')
    transformar = TransformarData(df)
    dataframe_final = transformar.limpieza_data()


    schema = 'reddit'
    nombre_tabla = 'comentarios_procesados'
    conectar_y_cargar = ConexionYCargaPostgres(credenciales_postgres, schema)
    conectar_y_cargar.conexion_postgres_psycopg2()
    conectar_y_cargar.crear_nueva_tabla(nombre_tabla)
    conectar_y_cargar.cargar_datos_postgres(dataframe=dataframe_final, nombre_tabla=nombre_tabla)
    
