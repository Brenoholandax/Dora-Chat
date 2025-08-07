import pandas as pd
import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()

def importar_csv_para_tabela(caminho_csv: str, nome_tabela: str):
    try:
        # Lê o CSV
        df = pd.read_csv(caminho_csv)

        if df.empty:
            print("⚠️ CSV vazio. Nenhum dado importado.")
            return

        # Conexão com o banco
        conn = mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            port=int(os.getenv("DB_PORT", 3306)),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME")
        )
        cursor = conn.cursor()

        # Monta comando INSERT
        colunas = ", ".join(df.columns)
        placeholders = ", ".join(["%s"] * len(df.columns))
        sql = f"INSERT INTO {nome_tabela} ({colunas}) VALUES ({placeholders})"

        # Insere linha por linha
        for _, row in df.iterrows():
            cursor.execute(sql, tuple(row))

        conn.commit()
        cursor.close()
        conn.close()

        print(f"✅ {len(df)} registros importados para a tabela '{nome_tabela}' com sucesso!")

    except FileNotFoundError:
        print(f"❌ Arquivo não encontrado: {caminho_csv}")
    except mysql.connector.Error as err:
        print(f"❌ Erro MySQL: {err}")
    except Exception as e:
        print(f"❌ Erro inesperado: {str(e)}")
