# banco/atualizacao_semanal.py
import pandas as pd
import os
import sys

# Adiciona o diretório raiz ao path para que o script encontre a pasta 'banco' e 'data'
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from banco.conexao import get_sqlalchemy_engine

# --- MAPEAMENTO CENTRALIZADO DE UNIDADES ---
MAPEAMENTO_UNIDADES = {
    '101': 'Editora', '201': 'Tv Recife', '202': 'Rádio Caruaru',
    '203': 'Rádio Garanhuns', '204': 'Rádio Recife', '401': 'Rádio JC FM',
    '501': 'Elo'
}

# --- FUNÇÕES DE PROCESSAMENTO DE DADOS ---

def processar_titulos_abertos(engine):
    """Lê, limpa e importa os dados de títulos em aberto para o banco de dados."""
    arquivo_csv = os.path.join("data", "Titulos em abertos.xlsx - Plan1.csv")
    nome_tabela = "titulos_abertos"
    print(f"\n--- Processando Títulos em Aberto: {arquivo_csv} ---")
    
    if not os.path.exists(arquivo_csv):
        print(f"⚠️ Arquivo não encontrado. A pular importação para '{nome_tabela}'.")
        return

    try:
        # CORREÇÃO: Alterado o separador de ';' para ',' para ler o CSV corretamente.
# Linha 25 corrigida
df = pd.read_csv(arquivo_csv, sep=';', encoding='utf-8-sig', low_memory=False)        
        # Limpa os nomes das colunas (remove espaços, acentos e converte para minúsculas)
        df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_')
        df.rename(columns={'estabelecimento': 'est'}, inplace=True)
        
        # Usa o SQLAlchemy engine para importar os dados, substituindo a tabela existente
        df.to_sql(nome_tabela, con=engine, if_exists='replace', index=False)
        print(f"✅ {len(df)} registos importados com sucesso para '{nome_tabela}'.")
    except Exception as e:
        print(f"❌ Erro ao processar '{nome_tabela}': {e}")


def processar_titulos_em_atraso(engine):
    """Lê, transforma e importa os dados de títulos em atraso."""
    arquivo_csv = os.path.join("data", "dia_atraso_v1.csv")
    nome_tabela = "titulos_em_atraso"
    print(f"\n--- Processando Títulos em Atraso: {arquivo_csv} ---")

    if not os.path.exists(arquivo_csv):
        print(f"⚠️ Arquivo não encontrado. A pular importação para '{nome_tabela}'.")
        return
    
    try:
        df = pd.read_csv(arquivo_csv)
        df.columns = df.columns.str.strip()
        df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
        df.dropna(subset=['nome', 'empresa'], how='all', inplace=True)
        
        # Transforma as colunas de faixa de atraso em linhas (unpivot)
        df_unpivoted = df.melt(id_vars=['nome', 'empresa'], var_name='faixa_atraso', value_name='saldo_atraso')
        df_unpivoted.dropna(subset=['saldo_atraso'], inplace=True)
        
        # Renomeia as colunas para o padrão do banco de dados
        df_unpivoted.rename(columns={'nome': 'nome_cliente', 'empresa': 'unidade_codigo'}, inplace=True)
        
        # Aplica o mapeamento de unidades
        df_unpivoted['unidade_codigo'] = df_unpivoted['unidade_codigo'].astype(int).astype(str)
        df_unpivoted['unidade_nome'] = df_unpivoted['unidade_codigo'].map(MAPEAMENTO_UNIDADES)
        
        df_unpivoted.to_sql(nome_tabela, con=engine, if_exists='replace', index=False)
        print(f"✅ {len(df_unpivoted)} registos de atraso importados para '{nome_tabela}'.")
    except Exception as e:
        print(f"❌ Erro ao processar '{nome_tabela}': {e}")


# --- SCRIPT PRINCIPAL QUE ORQUESTRA A ATUALIZAÇÃO ---
if __name__ == "__main__":
    print("🚀 A iniciar processo de atualização de dados...")
    try:
        db_engine = get_sqlalchemy_engine()
        
        # Executa a importação para cada tipo de dado
        processar_titulos_abertos(db_engine)
        processar_titulos_em_atraso(db_engine)
        
        print("\n🎉 Processo de atualização concluído com sucesso!")
        
    except Exception as e:
        print(f"❌ ERRO GERAL NO PROCESSO DE ATUALIZAÇÃO: {e}")