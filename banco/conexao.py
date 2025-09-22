# banco/conexao.py
import mysql.connector
import os
from dotenv import load_dotenv, find_dotenv
from sqlalchemy import create_engine

load_dotenv(find_dotenv())

def get_connection():
    """Abre uma conexão MySQL padrão."""
    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "127.0.0.1"),
        port=int(os.getenv("DB_PORT", 3306)),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME"),
    )

def get_sqlalchemy_engine():
    """Cria um 'engine' de conexão para o SQLAlchemy que o Pandas entende."""
    user = os.getenv("DB_USER")
    password = os.getenv("DB_PASSWORD")
    host = os.getenv("DB_HOST", "127.0.0.1")
    port = os.getenv("DB_PORT", 3306)
    db_name = os.getenv("DB_NAME")
    
    # Formato da URL de conexão: mysql+mysqlconnector://user:password@host:port/database
    db_url = f"mysql+mysqlconnector://{user}:{password}@{host}:{port}/{db_name}"
    return create_engine(db_url)

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