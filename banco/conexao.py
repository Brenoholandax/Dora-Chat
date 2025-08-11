import mysql.connector
import os
from dotenv import load_dotenv, find_dotenv

# garante que o .env seja encontrado a partir de qualquer subpasta
load_dotenv(find_dotenv())

def get_connection():
    """Abre conexão MySQL usando variáveis do .env"""
    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "127.0.0.1"),
        port=int(os.getenv("DB_PORT", 3306)),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME"),
    )

def consultar_banco(query: str) -> str:
    try:
        cn = get_connection()
        cur = cn.cursor()
        cur.execute(query)
        rows = cur.fetchall()
        cols = [d[0] for d in cur.description]
        cur.close(); cn.close()
        if not rows:
            return "Nenhum resultado."
        linhas = [", ".join(cols)]
        for r in rows:
            linhas.append(", ".join(str(v) for v in r))
        return "\n".join(linhas)
    except mysql.connector.Error as err:
        return f"Erro MySQL: {err}"
    except Exception as e:
        return f"Erro: {e}"
