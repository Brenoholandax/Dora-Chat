# banco/importar_titulos.py

import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from banco.transformacao import preparar_titulos_csv
from banco.importar_csv import importar_csv_para_tabela


# Caminhos dos arquivos
arquivo_original = "C:/Users/bneves/Desktop/Dora-Chat/data/Titulos em abertos.xlsx - Plan1.csv"
arquivo_limpo = "data/titulos_limpo.csv"
tabela_destino = "titulos_abertos"

# Etapa 1: limpar CSV original
df = preparar_titulos_csv(arquivo_original)

# Etapa 2: salvar CSV limpo
df.to_csv(arquivo_limpo, index=False)

# Etapa 3: importar no MySQL
importar_csv_para_tabela(arquivo_limpo, tabela_destino)
