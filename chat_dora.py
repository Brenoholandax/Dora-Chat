# chat_dora.py
from flask import Flask, request, Response
from flask_cors import CORS
from twilio.twiml.messaging_response import MessagingResponse
from pyngrok import conf, ngrok
from dotenv import load_dotenv
from openai import OpenAI
import os
from agentes.financeiro import processar_pergunta_financeira
from banco.conexao import consultar_banco

# --- (configurações iniciais continuam iguais) ---
load_dotenv()
NGROK_TOKEN = os.getenv("NGROK_TOKEN")
OPENAI_KEY = os.getenv("OPENAI_API_KEY")
os.environ["OPENAI_API_KEY"] = OPENAI_KEY

conf.get_default().auth_token = NGROK_TOKEN
public_url = ngrok.connect(5000)
print(f"🔗 Webhook para o Twilio: {public_url}/sms")

client = OpenAI(api_key=OPENAI_KEY)


def gerar_mensagem_boas_vindas():
    """Gera a mensagem de boas-vindas focada no agente financeiro."""
    return (
        "Olá! Sou a Dora, sua assistente de dados financeiros. 👋\n\n"
        "Você pode me fazer perguntas sobre títulos em aberto ou em atraso.\n\n"
        "Exemplos:\n"
        "➡️ *'Qual o saldo total da Tv Recife?'*\n"
        "➡️ *'Liste os clientes com mais de 90 dias de atraso.'*\n\n"
        "Como posso te ajudar?"
    )

# --- AGENTE CONVERSACIONAL (COM NOVAS REGRAS) ---
def processar_pergunta_geral(pergunta: str) -> str:
    """Usa a IA para responder a perguntas não-financeiras e lidar com falhas."""
    print("➡️ Roteando para o AGENTE CONVERSACIONAL...")
    prompt_geral = f"""
Você é a Dora , uma assistente de dados especialista em finanças.

Siga estas regras estritamente:
1.  **Pergunta sobre seu criador:** Se o usuário perguntar "quem te criou?", "quem é seu criador?", ou algo similar, sua única resposta DEVE ser: "Fui criada por Breno Holanda Cientista de Dados do SJCC."
2.  **Pergunta sobre suas capacidades:** Se o usuário perguntar o que você pode fazer ou quais informações você tem, explique que você pode fornecer dados sobre títulos financeiros em aberto e em atraso.
3.  **Se você não entender a pergunta:** Se a pergunta do usuário for confusa, fora do escopo ou você não souber a resposta, responda com a seguinte mensagem, sem adicionar mais nada: "Desculpe, não consegui entender sua pergunta. Para te ajudar melhor, estou te direcionando para o time de dados. Por favor, envie um e-mail para bneves@jc.com.br e eles irão te ajudar."

Pergunta do usuário: "{pergunta}"
"""
    try:
        resposta = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt_geral}],
            timeout=20.0
        ).choices[0].message.content.strip()
        return resposta
    except Exception as e:
        print(f"❌ ERRO no agente conversacional: {e}")
        return "Desculpe, estou com um pequeno problema. Para te ajudar melhor, por favor, entre em contato com o time de dados em bneves@jc.com.br."

# --- FUNÇÃO PRINCIPAL ---
def gerar_resposta(mensagem_usuario: str) -> str:
    """Processa a mensagem do usuário e direciona para o agente correto."""
    msg = mensagem_usuario.strip().lower()

    saudacoes = ["oi", "ola", "olá", "bom dia", "boa tarde", "boa noite", "/start", "/menu", "voltar", "dora","ei"]
    if msg in saudacoes:
        return gerar_mensagem_boas_vindas()

    resposta_financeira = processar_pergunta_financeira(mensagem_usuario)
    
    if resposta_financeira == "NAO_FINANCEIRO":
        return processar_pergunta_geral(mensagem_usuario)
    
    return resposta_financeira

# --- (O resto do código do servidor Flask continua igual) ---
app = Flask(__name__)
CORS(app)

@app.route("/sms", methods=["POST"])
def sms_reply():
    mensagem = request.form.get("Body", "")
    print(f"\n--- MENSAGEM RECEBIDA: '{mensagem}' ---")
    
    resposta = gerar_resposta(mensagem)
    
    print(f"--- RESPOSTA GERADA: '{resposta}' ---")
    
    resposta_twilio = MessagingResponse()
    resposta_twilio.message(resposta)
    return Response(str(resposta_twilio), mimetype="application/xml")
 
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)