[![trump](https://github.com/cristobalqv/Opiniones_sobre_el_triunfo_de_Trump__ETL-postgres-/blob/main/reddit/varios/1.png "trump")](https://github.com/cristobalqv/Opiniones_sobre_el_triunfo_de_Trump__ETL-postgres-/blob/main/reddit/varios/1.png "trump")

El siguiente proyecto consistió en la creación de un procedimiento ETL de las opiniones y comentarios en el foro [reddit](https://www.reddit.com/ "reddit") sobre la victoria de Donald Trump en las elecciones 2024 de Estados Unidos. De esta forma, se extrajeron datos de los comentarios realizados sobre este evento mediante la API del sitio web, se transformaron para poder procesarlos y se almacenaron en una base de datos en Postgresql. Posterior a esto, se utilizaron bibliotecas especializadas para el análisis de texto y poder tener una visión generalizada sobre la apreciación de este acontecimiento para los usuarios de reddit.

[enlace al artículo](https://www.reddit.com/r/politics/comments/1gl0ty4/america_will_regret_its_decision_to_reelect/ "enlace al artículo")

## ️⚙️Características y herramientas

- ⛏️Extracción de datos desde la API de reddit
- 🔄Transformación de los datos para un análisis efectivo
- 🐘Carga a una base de datos Postgres
- 💬Análisis de sentimiento de los comentarios (negativo, neutral, positivo)🚦 mediante herramientas de Machine Learning

## 🗒️Estructura del proyecto y funcionamiento del código </>

```
reddit/
│
├── data/                           
│     ├── processed/             
│     │       └── analisis.ipynb      #Notebook Jupyter con el análisis de sentimiento
│     ├── raw/                       
│     │     └── all_comments.csv      #comentarios sin procesar
│     │
│     └── __init__.py                
│
├── src/                         
│     ├── data/   
│     │     ├── extractors.py         #script para extraer datos de reddit
│     │     ├── main.py               #script principal para ejecutar el ETL
│     │     └── __init__.py          
│     │
│     ├── utils/ 
│     │     ├── utils.py              #funciones de utilidad para el ETL
│     │     └── __init__.py 
│     │
│     └── __init__.py            
│
├── varios/
│
├── __init__.py                       #Directorio como un paquete de Python
├── .gitignore
└── requirements.txt                  #librerías requeridas
```

Los archivos y directorios del proyecto más relevantes para la lógica, funcionamiento e interacción con la API de reddit son:

[reddit/src/data/extractors.py](https://github.com/cristobalqv/Opiniones_sobre_el_triunfo_de_Trump__ETL-postgres-/blob/main/reddit/src/data/extractors.py "reddit/src/data/extractors.py") Script que contiene principalmente la lógica de extracción desde la API de reddit.

[reddit/src/data/extractors.py](https://github.com/cristobalqv/Opiniones_sobre_el_triunfo_de_Trump__ETL-postgres-/blob/main/reddit/src/data/main.py "reddit/src/data/extractors.py") Script en el que se ejecuta todo el procedimiento ETL

[reddit/src/utils/utils.py](https://github.com/cristobalqv/Opiniones_sobre_el_triunfo_de_Trump__ETL-postgres-/blob/main/reddit/src/utils/utils.py "reddit/src/utils/utils.py") Funciones de transformación y carga de datos

[reddit/data/processed/analisis.ipynb](https://github.com/cristobalqv/Opiniones_sobre_el_triunfo_de_Trump__ETL-postgres-/blob/main/reddit/data/processed/analisis.ipynb "reddit/data/processed/analisis.ipynb") Jupyter Notebook que contiene el análisis de sentimiento de los comentarios de los usuarios de reddit


## 🤝 Contribuciones

¡Las contribuciones son bienvenidas! Por favor, sigue los siguientes pasos:

** Haz un fork del proyecto y crea una nueva rama:**
git checkout -b feature/nueva-funcionalidad

** Realiza tus cambios y haz commit:**
git commit -am 'Agrega nueva funcionalidad'

** Sube los cambios:**
git push origin feature/nueva-funcionalidad

** Envía un Pull Request.**


## 📜 Licencia

Este proyecto está licenciado bajo la Licencia MIT, lo que permite su libre uso y modificación con fines personales o comerciales.