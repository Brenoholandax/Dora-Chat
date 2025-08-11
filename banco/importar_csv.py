import pandas as pd
import numpy as np
import math
from dotenv import load_dotenv, find_dotenv
from banco.conexao import get_connection

load_dotenv(find_dotenv())

TABELA_COLS = [
    "est","esp","ser","titulo","p","cliente","nome_cliente","portador","contato",
    "agencia","intermediario","diretor","emissao","vencto","val_original","saldo",
    "diferenca","status","status_cobr","obs","unid_negoc","nr_fiscal_pref","pi",
    "titulo_programa"
]

def _to_mysql(v):
    # None ou string vazia -> NULL
    if v is None:
        return None
    if isinstance(v, str):
        v = v.strip()
        return v if v != "" else None
    # floats NaN/Inf -> NULL
    if isinstance(v, float):
        if math.isnan(v) or math.isinf(v):
            return None
    return v

def importar_csv_para_tabela(caminho_csv: str, nome_tabela: str):
    df = pd.read_csv(caminho_csv, sep=";", encoding="utf-8-sig")

    # cabeçalhos limpos e só colunas da tabela
    df = df.loc[:, df.columns.notna()]
    df.columns = [str(c).strip().lower() for c in df.columns]
    for c in TABELA_COLS:
        if c not in df.columns:
            df[c] = None
    df = df[TABELA_COLS]

    # normalizar NA/strings vazias
    df = df.replace({np.nan: None})

    # garantir tipos antes de inserir
    for col in ("emissao","vencto"):
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce").dt.date

    for col in ("val_original","saldo","diferenca"):
        if col in df.columns:
            s = pd.to_numeric(df[col], errors="coerce")
            df[col] = s.where(~s.isna(), None)

    # montar INSERT seguro
    cols_sql = ", ".join(f"`{c}`" for c in TABELA_COLS)
    placeholders = ", ".join(["%s"] * len(TABELA_COLS))
    sql = f"INSERT INTO `{nome_tabela}` ({cols_sql}) VALUES ({placeholders})"

    # converter linha a linha (sem NAs)
    data = [tuple(_to_mysql(v) for v in row)
            for row in df.itertuples(index=False, name=None)]

    cn = get_connection(); cur = cn.cursor()
    cur.executemany(sql, data)
    cn.commit(); cur.close(); cn.close()
    print(f"✅ {len(df)} registros importados para '{nome_tabela}'.")
