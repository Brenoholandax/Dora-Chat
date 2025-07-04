import mysql.connector
import pandas as pd
from dotenv import load_dotenv
import os

# Carrega variáveis do .env
load_dotenv()

# Conecta ao banco de dados usando as variáveis do .env
conn = mysql.connector.connect(
    host=os.getenv("DB_HOST"),
    port=int(os.getenv("DB_PORT", 3306)),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    database=os.getenv("DB_NAME")
)

# Executa a consulta
cursor = conn.cursor()
cursor.execute("SELECT * FROM redes_sociais")

# Pega os resultados e converte para DataFrame
resultados = cursor.fetchall()
colunas = [desc[0] for desc in cursor.description]

df = pd.DataFrame(resultados, columns=colunas)
print(df)

# Fecha a conexão
cursor.close()
conn.close()
