# banco/transformacao.py

import pandas as pd
import unicodedata

def _norm(s: str) -> str:
    s = unicodedata.normalize("NFKD", str(s)).encode("ASCII","ignore").decode()
    s = s.strip().lower().replace(" ", "_")
    s = "".join(ch if (ch.isalnum() or ch == "_") else "_" for ch in s)
    while "__" in s: s = s.replace("__","_")
    return s.strip("_")

# CSV -> coluna da TABELA (já no padrão que criamos)
RENAME_MAP = {
    "estabelecimento": "est",
    "especie":         "esp",
    "serie":           "ser",
    "titulo":          "titulo",
    "p":               "p",
    "cliente":         "cliente",
    "nome_cliente":    "nome_cliente",
    "portador":        "portador",
    "contato":         "contato",
    "agencia":         "agencia",          # “Agência”
    "intermediario":   "intermediario",    # “Intermediário”
    "diretor":         "diretor",
    "emissao":         "emissao",          # “Emissão”
    "vencto":          "vencto",
    "val_original":    "val_original",
    "saldo":           "saldo",
    "diferenca":       "diferenca",         # “Diferença”
    "status":          "status",
    "status_cobr":     "status_cobr",
    "obs":             "obs",
    "unid_negoc":      "unid_negoc",
    "nr_fiscal_pref":  "nr_fiscal_pref",
    "pi":              "pi",
    "titulo_programa": "titulo_programa",
}

def preparar_titulos_csv(caminho_csv: str) -> pd.DataFrame:
    # Lê CSV sem adivinhar muito: primeiro tenta vírgula, depois ponto-e-vírgula
    try:
        df = pd.read_csv(caminho_csv, sep=",", encoding="utf-8-sig")
        if df.shape[1] <= 1:
            raise ValueError("provável separador diferente de vírgula")
    except Exception:
        df = pd.read_csv(caminho_csv, sep=";", encoding="utf-8-sig")

    # normaliza cabeçalhos e aplica o mapeamento acima
    df.columns = [_norm(c) for c in df.columns]
    df = df.rename(columns={k:v for k,v in RENAME_MAP.items() if k in df.columns})

    # 🔹 mínimas conversões para não quebrar no MySQL:
    # datas estão em dd/mm/aaaa (seu exemplo), então dayfirst=True
    for col in ("emissao", "vencto"):
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce", dayfirst=True).dt.date

    # números: troca vírgula por ponto (ex.: "2.618,2" ou "4800")
    for col in ("val_original", "saldo", "diferenca"):
        if col in df.columns:
            s = (df[col].astype(str).str.strip()
                 .str.replace(".", "", regex=False)   # milhar
                 .str.replace(",", ".", regex=False)) # decimal
            df[col] = pd.to_numeric(s, errors="coerce")

    return df
