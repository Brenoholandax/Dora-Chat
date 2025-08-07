# banco/transformacao.py

import pandas as pd

def preparar_titulos_csv(caminho_csv: str) -> pd.DataFrame:
    try:
        df = pd.read_csv(caminho_csv)

        # Padroniza os nomes das colunas
        df.columns = [col.strip().lower().replace(" ", "_") for col in df.columns]

        # Renomeia colunas específicas
        df = df.rename(columns={
            "emissão": "emissao",
            "diferença": "diferenca",
            "val_original": "val_original",
            "status_cobr": "status_cobr",
            "titulo_programa": "titulo_programa",
            "nr_fiscal_pref": "nr_fiscal_pref"
        })

        # Converte datas do formato brasileiro para YYYY-MM-DD
        df["emissao"] = pd.to_datetime(df["emissao"], format="%d/%m/%Y", errors="coerce").dt.date
        df["vencto"] = pd.to_datetime(df["vencto"], format="%d/%m/%Y", errors="coerce").dt.date

        # Converte valores monetários
        for col in ["val_original", "saldo", "diferenca"]:
            df[col] = pd.to_numeric(df[col], errors="coerce")

        # Remove linhas sem título ou vencimento
        df = df.dropna(subset=["titulo", "vencto"])

        print(f"✅ CSV tratado com sucesso: {len(df)} registros prontos.")
        return df

    except Exception as e:
        print(f"❌ Erro ao preparar CSV: {str(e)}")
        return pd.DataFrame()
