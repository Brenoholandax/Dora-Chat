# banco/conexao.py

import mysql.connector
import os
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

def consultar_banco(query: str) -> str:
    try:
        conn = mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            port=int(os.getenv("DB_PORT", 3306)),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME")
        )
        cursor = conn.cursor()
        cursor.execute(query)
        resultados = cursor.fetchall()
        colunas = [desc[0] for desc in cursor.description]
        cursor.close()
        conn.close()

        if not resultados:
            return "Nenhum resultado encontrado."

        return "\n".join(
            ", ".join(str(v) for v in linha) for linha in resultados
        )
    except Exception as e:
        return f"Erro: {str(e)}"
