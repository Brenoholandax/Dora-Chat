from flask import Flask, request, Response
from flask_cors import CORS
from twilio.twiml.messaging_response import MessagingResponse
from pyngrok import conf, ngrok
from dotenv import load_dotenv
from openai import OpenAI
import os, mysql.connector

# 🔐 Carrega variáveis do .env
load_dotenv()
NGROK_TOKEN = os.getenv("NGROK_TOKEN")
OPENAI_KEY = os.getenv("OPENAI_API_KEY")
os.environ["OPENAI_API_KEY"] = OPENAI_KEY

# 🌐 Inicia ngrok
conf.get_default().auth_token = NGROK_TOKEN
public_url = ngrok.connect(5000)
print(f"🔗 Webhook para o Twilio: {public_url}/sms")

client = OpenAI(api_key=OPENAI_KEY)

# 📦 Função para executar query no banco
def consultar_banco(query: str) -> str:
    try:
        conn = mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME")
        )
        cursor = conn.cursor()
        cursor.execute(query)
        resultados = cursor.fetchall()
        colunas = [desc[0] for desc in cursor.description]
        conn.close()

        if not resultados:
            return "Nenhum resultado encontrado."

        return "\n".join(
            ", ".join(str(valor) for valor in linha) for linha in resultados
        )
    except Exception as e:
        return f"Erro: {str(e)}"

# 🧠 Gera resposta automática
def gerar_resposta(mensagem_usuario: str) -> str:
    msg = mensagem_usuario.strip().lower()

    if msg == "/menu":
        return (
            "📋 *Menu de Consultas Disponíveis:*\n"
            "- Dora, quantas visualizações tivemos hoje?\n"
            "- Dora, quais dias tiveram mais curtidas?\n"
            "- sql: SELECT * FROM redes_sociais LIMIT 3;"
        )

    if msg == "/ajuda":
        return (
            "🆘 *Ajuda:*\n"
            "Fale com a Dora em linguagem natural ou envie comandos SQL iniciando com `sql:`\n"
            "Exemplo: Dora, total de curtidas ontem\n"
            "Exemplo: sql: SELECT COUNT(*) FROM redes_sociais"
        )

    if msg.startswith("sql:"):
        query = mensagem_usuario[4:].strip()
        resultado = consultar_banco(query)
        return f"📊 Resultado da consulta:\n{resultado}"

    if "dora" in msg:
       
        prompt_sql = f"""
        
Você é uma assistente chamada Dora. Converta a pergunta abaixo para uma consulta SQL usando a tabela `redes_sociais`.

Tabela: redes_sociais  
Colunas: id, data (DATE), visualizacoes, curtidas, comentarios

Pergunta: \"{mensagem_usuario}\"

Responda apenas com a instrução SQL.
"""
        resposta_sql = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt_sql}]
        ).choices[0].message.content.strip()

        # ⚠️ Limpa código Markdown do SQL
        resposta_sql = resposta_sql.strip().strip("```sql").strip("```").strip()

        print(f"🔍 SQL gerado: {resposta_sql}")

        if not resposta_sql.lower().startswith("select"):
            return "❌ Só posso executar comandos SQL do tipo SELECT."

        resultado_query = consultar_banco(resposta_sql)

        # 🔁 Traduz resultado em linguagem natural
        prompt_resumo = f"""
Responda de forma curta e direta: qual o resultado da seguinte consulta SQL?

Pergunta: "{mensagem_usuario}"
Resultado: {resultado_query}

Use frases simples e objetivas, sem repetições.
"""
        resumo = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt_resumo}]
        ).choices[0].message.content.strip()

        return f"🤖 Dora responde:\n{resumo}"

    # 🤖 Resposta fallback
    fallback = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": mensagem_usuario}]
    ).choices[0].message.content.strip()

    return fallback

# 🚀 Inicializa servidor Flask
app = Flask(__name__)
CORS(app)

@app.route("/sms", methods=["POST"])
def sms_reply():
    mensagem = request.form.get("Body", "")
    resposta = gerar_resposta(mensagem)
    resposta_twilio = MessagingResponse()
    resposta_twilio.message(resposta)
    return Response(str(resposta_twilio), mimetype="application/xml")

app.run(host="0.0.0.0", port=5000)
