# agentes/financeiro.py

from openai import OpenAI
import os
from banco.conexao import consultar_banco

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def processar_pergunta_financeira(pergunta: str) -> str:
    prompt_sql = f"""
Você é uma assistente chamada Dora. Converta a pergunta abaixo em uma consulta SQL relacionada à tabela `titulos_financeiros`.

Tabela: titulos_financeiros  
Colunas: id, nome_titulo, vencimento, valor_atual, rendimento, categoria

Pergunta: \"{pergunta}\"

Responda apenas com a instrução SQL.
"""

    resposta_sql = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt_sql}]
    ).choices[0].message.content.strip()

    resposta_sql = resposta_sql.strip().strip("```sql").strip("```").strip()

    if not resposta_sql.lower().startswith("select"):
        return "❌ Só posso executar comandos SQL do tipo SELECT."

    resultado = consultar_banco(resposta_sql)

    prompt_resumo = f"""
Resuma de forma clara e direta o resultado da seguinte consulta SQL:

Pergunta: \"{pergunta}\"
Resultado: {resultado}
"""

    resumo = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt_resumo}]
    ).choices[0].message.content.strip()

    return f"💰 Financeiro:\n{resumo}"
