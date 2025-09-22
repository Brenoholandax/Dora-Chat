# agentes/financeiro.py
from openai import OpenAI
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from banco.conexao import consultar_banco

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def processar_pergunta_financeira(pergunta: str) -> str:
    prompt_sql = f"""
Você é a Dora, uma especialista em análise de dados financeiros. A sua tarefa é converter a pergunta do utilizador numa consulta SQL precisa, seguindo as regras abaixo SEM EXCEÇÃO.

Você tem acesso a duas tabelas com estruturas DIFERENTES:

Tabela 1: `titulos_abertos`
- DESCRIÇÃO: Usada para perguntas sobre títulos em geral, que NÃO envolvem atraso.
- COLUNAS DESTA TABELA: `nome_cliente`, `saldo`, `vencto`, `est`.
- REGRA 1: Para filtrar por empresa, use a coluna `est` (ex: `WHERE est = 101`). Esta tabela NÃO POSSUI a coluna `unidade_nome`.

Tabela 2: `titulos_em_atraso`
- DESCRIÇÃO: Usada EXCLUSIVAMENTE para perguntas sobre títulos vencidos, cobrança ou atraso.
- COLUNAS DESTA TABELA: `nome_cliente`, `unidade_nome`, `faixa_atraso`, `saldo_atraso`.
- REGRA 2: Para filtrar por empresa, use a coluna `unidade_nome` (ex: `WHERE unidade_nome = 'Tv Recife'`).
- REGRA 3: Para filtrar por tempo de atraso, use a coluna `faixa_atraso`. Para "mais de 90 dias", o comando DEVE SER `WHERE faixa_atraso IN ('91 A 180', 'MAIS DE 180')`.

COMO DECIDIR QUAL TABELA USAR:
- Se a pergunta tiver "atraso", "atrasado", "vencido", "cobrança" ou "devendo", USE A TABELA `titulos_em_atraso`.
- Para todas as outras perguntas financeiras, USE A TABELA `titulos_abertos`.

Pergunta do utilizador: \"{pergunta}\"

Responda apenas com a instrução SQL.
"""
    try:
        resposta_sql = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt_sql}],
            timeout=20.0
        ).choices[0].message.content.strip().strip("```sql").strip("```").strip()

        print(f"🔍 SQL Financeiro Gerado: {resposta_sql}")
        resultado_banco = consultar_banco(resposta_sql)

        if "Erro MySQL:" in resultado_banco:
            print(f"❌ Erro retornado pelo banco: {resultado_banco}")
            return f"💰 Dora Financeiro:\nDesculpe, ocorreu um erro ao consultar a base de dados. Acredito que a informação não está disponível. Por favor, tente outra pergunta."
        if resultado_banco == "Nenhum resultado.":
            return "💰 Dora Financeiro:\nNão encontrei nenhum registo que corresponda à sua pesquisa."

        prompt_resumo = f"""
Resuma o resultado da consulta SQL de forma clara e direta, como um analista financeiro.
Pergunta Original: \"{pergunta}\"
Resultado da Consulta:
{resultado_banco}
"""
        resumo = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt_resumo}],
            timeout=20.0
        ).choices[0].message.content.strip()

        return f"💰 Dora Financeiro:\n{resumo}"

    except Exception as e:
        print(f"❌ ERRO no agente financeiro: {e}")
        return "Desculpe, estou com um problema para processar a sua pergunta. A equipa de dados já foi notificada."