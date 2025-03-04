import pandas as pd
import re 
import psycopg2
from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv
from textblob import TextBlob
from nltk.sentiment.vader import SentimentIntensityAnalyzer 
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer as VaderSentimentAnalyzer
from psycopg2.extras import execute_values


load_dotenv()


class TransformarData:
    def __init__(self, dataframe):
        self.dataframe = dataframe


    def verificar_tipo_dato(self, dataframe):
        diccionario = {'nombre_campo': [], 'tipo_datos': [], 'no_nulos_%': [], 'nulos_%': [], 'nulos': []}
        for columna in dataframe.columns:
            porcentaje_no_nulos = (dataframe[columna].count()/len(dataframe[columna]))*100
            diccionario['nombre_campo'].append(columna)
            diccionario['tipo_datos'].append(dataframe[columna].apply(type).unique())
            diccionario['no_nulos_%'].append(round(porcentaje_no_nulos,2))
            diccionario['nulos_%'].append(round(100-porcentaje_no_nulos,2))
            diccionario['nulos'].append(dataframe[columna].isnull().sum())

        df = pd.DataFrame(diccionario)

        return df


    def limpiar_texto_regex(self, texto):
        # reemplaza una expresion regular por un nuevo string.
        texto = re.sub(r'https?://\S+|www\.\S+', '', texto)     #Elimina enlaces URLs
        texto = re.sub(r'@\w+', '', texto)     #elimina menciones de usuario
        texto = re.sub(r'#\w+', '', texto)     #elimina hashtags
        texto = re.sub(r'[^\w\s,]', '', texto)     #elimina emojis
        texto = re.sub(r'([?!.,])\1+', '', texto)     #elimina caracteres de puntuacion excesivos o repeticiones, como !!!!!!!
        texto = re.sub(r'\s+', ' ', texto).strip()  # elimina espacios extra

        return texto


    def limpieza_data(self):
        self.dataframe.drop(0, inplace=True)
        print(self.verificar_tipo_dato(self.dataframe))
        #ubicar y eliminar registro float
        self.dataframe[self.dataframe['body'].apply(lambda x: isinstance(x, float))]
        self.dataframe.drop(12040, inplace=True)
        print('limpiando textos. . .')
        self.dataframe['format_comment'] = self.dataframe['body'].apply(self.limpiar_texto_regex)
        print('limpieza exitosa, proceso de limpieza finalizado')
        print(self.dataframe)

        return self.dataframe

        

class AnalisisPolaridadYSentimiento:
    def __init__(self, dataframe):
        self.dataframe = dataframe


    def polaridad_textblob(self, texto):
        if texto is None:
            return 1
        analysis = TextBlob(texto)
        polarity = analysis.sentiment.polarity
        if polarity < -0.2:
            return 0
        elif polarity > 0.2:
            return 2
        else:
            return 1
        

    def polaridad_nltk(self, texto):
        if texto is None:
            return 1
        analysis = SentimentIntensityAnalyzer()
        polaridad = analysis.polarity_scores(texto)
        if polaridad['compound'] < -0.2:
            return 0
        elif polaridad['compound'] > 0.2:
            return 2
        else:
            return 1
        

    def polaridad_vader(self, texto):
        if texto is None:
            return 1
        analysis = VaderSentimentAnalyzer()
        polaridad = analysis.polarity_scores(texto)
        if polaridad['compound'] < -0.2:
            return 0
        elif polaridad['compound'] > 0.2:
            return 2
        else:
            return 1
        

    def agregar_polaridad_a_dataframe(self):
        self.dataframe['polaridad_textblob'] = self.dataframe['format_comment'].apply(self.polaridad_textblob)
        self.dataframe['polaridad_nltk'] = self.dataframe['format_comment'].apply(self.polaridad_nltk)
        self.dataframe['polaridad_vader'] = self.dataframe['format_comment'].apply(self.polaridad_vader)


    def comparador_analizadores_sentimiento(self):
        diccionario = {'negativo': 0, 'neutral': 0, 'positivo': 0} #llevamos un conteo del sentimiento poderado
        for index, row in self.dataframe.iterrows():
            sentiment = [str(row['polaridad_textblob']), str(row['polaridad_nltk']), str(row['polaridad_vader'])]
            if sentiment.count('2') >= 2:
                diccionario['positivo'] += 1
            elif sentiment.count('0') >= 2:
                diccionario['negativo'] += 1
            else:
                diccionario['neutral'] += 1

        print(diccionario)
        return diccionario



class ConexionYCargaPostgres:
    def __init__(self, credenciales: dict, schema: str):
        self.credenciales = credenciales
        self.schema = schema
        self.conexion = None


    def conexion_postgres_psycopg2(self):
        user = self.credenciales.get('postgres_user')
        password = self.credenciales.get('postgres_pass')
        host = self.credenciales.get('postgres_host')
        port = self.credenciales.get('postgres_port')
        database = self.credenciales.get('postgres_database')

        try:
            conn = psycopg2.connect(
            dbname=database,
            user=user,
            password=password,
            host=host,
            port=port
            )
            print('Motor creado exitosamente')
            return conn

        except Exception as e:
            print(f'Error al intentar crear el motor: {e}')  


    def crear_nueva_tabla(self, nombretabla: str):
        conn = self.conexion_postgres_psycopg2()
        if conn:
            try:
                cursor = conn.cursor()

                query_creacion_tabla = f"""CREATE TABLE IF NOT EXISTS {self.schema}.{nombretabla} (
                id VARCHAR(50) primary key,
                parent_id VARCHAR(256),
                body TEXT,
                score INT,
                created_utc VARCHAR(250),
                author VARCHAR(256),
                depth INT,
                is_root BOOL,
                format_comment TEXT
                );"""

                cursor.execute(query_creacion_tabla)
                conn.commit()
                print('Nueva tabla creada con éxito en Postgres con psycopg2')
                cursor.close()
                conn.close()
                
            except Exception as e:
                print(f'Hubo un error al crear la tabla: {e}')
        else:
            print('No se pudo conectar a Postgresql usando psycopg2')


    def cargar_datos_postgres(self, dataframe, nombre_tabla):
        # engine = create_engine(f'postgresql+psycopg2://{user}:{password}@{host}:{port}/{database}')

        conn = self.conexion_postgres_psycopg2()

        if conn:
            try:
                cursor = conn.cursor()

                #extraemos columnas del dataframe. psycopg2 no entiende dataframes directamente
                columnas = list(dataframe.columns)
                columnas_str = ', '.join(columnas)

                # Crear una lista de valores en formato de tupla
                valores = [tuple(x) for x in dataframe.itertuples(index=False, name=None)]

                 # Crear una consulta parametrizada para inserción eficiente
                query = f"INSERT INTO {self.schema}.{nombre_tabla} ({columnas_str}) VALUES %s"

                # Ejecutar la inserción en bloque
                execute_values(cursor, query, valores)

                # Confirmar los cambios
                conn.commit()
                cursor.close()
                conn.close()

                print(f'Dataframe cargado con éxito en Postgres con psycopg2') 

            except Exception as e:
                print(f'Error al cargar dataframe a Postgres: {e}')
        else:
            print("No hay conexión creada con Postgres. Intenta establecer una conexión")
