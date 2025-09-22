# README — Dora Chatbot

## 📌 Visão geral
Dora é um chatbot com IA integrado a um banco MySQL.  
Ele interpreta perguntas em linguagem natural, gera consultas SQL, acessa o banco e responde de forma clara.  
A comunicação é feita via **Twilio/WhatsApp**, com servidor exposto pelo **ngrok**.

---

## 📂 Estrutura do projeto
```
DORA-CHAT/
├─ agentes/
│  ├─ __init__.py
│  └─ financeiro.py
├─ banco/
│  ├─ __init__.py
│  ├─ atualizacao_semanal.py
│  └─ conexao.py
├─ data/
│  ├─ dados_meta.csv
│  ├─ dia_atraso_v1.csv
│  ├─ Titulos em abertos.xlsx - Plan1.csv
│  ├─ titulos_limpo.csv
│  └─ Visão_por_dia_em_atrazo.xlsx
├─ chat_dora.py
├─ README.md
├─ requirements.txt
├─ .env.example
├─ setup.sh
└─ setup.ps1
```

---

## ⚙️ Pré-requisitos
- Python **3.10+**
- MySQL em execução e acessível
- Conta no **Twilio** com **WhatsApp Sandbox** ativo
- Conta no **ngrok**

---

## 🚀 Setup inicial

### 1) Criar `.env`
Copie o exemplo:
```bash
cp .env.example .env
```
Edite e preencha:
```ini
DB_HOST=127.0.0.1
DB_PORT=3306
DB_USER=seu_usuario
DB_PASSWORD=sua_senha
DB_NAME=dora_chatbot

OPENAI_API_KEY=sua_chave_openai
NGROK_TOKEN=seu_token_ngrok
```

### 2) Rodar o script de setup
Linux/Mac:
```bash
bash setup.sh
```

Windows (PowerShell):
```powershell
.\setup.ps1
```

Isso irá:
- Criar o ambiente virtual `.venv`
- Instalar dependências (`requirements.txt`)
- Copiar `.env.example → .env` (se não existir)

---

## ⚡ Como rodar depois do setup
Você **não precisa rodar o setup toda vez**.  
Basta ativar o ambiente virtual e iniciar o chatbot:

### Linux/Mac
```bash
source .venv/bin/activate
python chat_dora.py
```

### Windows (PowerShell)
```powershell
.venv\Scripts\Activate.ps1
python chat_dora.py
```

Ao iniciar, será exibido algo assim:
```
🔗 Webhook para o Twilio: https://seu-endereco-ngrok.ngrok-free.app/sms
```

---

## 📲 Configuração do Twilio (WhatsApp Sandbox)

1. Crie uma conta em [Twilio](https://www.twilio.com/).  
2. Ative o **WhatsApp Sandbox** no [console do Twilio](https://console.twilio.com/).  
3. Copie o número de telefone do sandbox (ex.: `+14155238886`).  
4. Configure o **Webhook**:
   - Vá em **Messaging → WhatsApp Sandbox Settings**  
   - No campo **WHEN A MESSAGE COMES IN**, cole a URL gerada pelo ngrok:
     ```
     https://seu-endereco-ngrok.ngrok-free.app/sms
     ```
5. Salve.  
6. No celular, envie a mensagem de código de convite para o número do Twilio (ex.: “join bright-sun”).  

Pronto ✅ — agora qualquer mensagem enviada ao número do Twilio será roteada para seu servidor Flask (`chat_dora.py`).

---

## 📊 Atualizar dados no banco
O script `banco/atualizacao_semanal.py` importa os CSVs de `data/` para o MySQL.

Rodar atualização:
```bash
python -m banco.atualizacao_semanal
```

- **Títulos em aberto** → tabela `titulos_abertos`  
- **Títulos em atraso** → tabela `titulos_em_atraso`  

---

## 🤖 Fluxo do chatbot
1. Usuário envia mensagem via WhatsApp (Twilio Sandbox).  
2. Twilio chama o endpoint `/sms` do `chat_dora.py` (via ngrok).  
3. Dora decide:
   - Pergunta financeira → agente `financeiro` gera SQL e consulta banco.  
   - Pergunta fora de escopo → agente conversacional responde ou encaminha.  

---

## 🛠️ Troubleshooting
- **Erro de conexão MySQL** → confira `.env` (DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME).  
- **Erro ngrok** → confirme que o token NGROK está correto.  
- **Webhook Twilio não funciona** → verifique se o link ngrok está ativo e colado no Sandbox Settings.  
- **Arquivo não encontrado** → valide os nomes em `data/`.  

---

## 📌 Próximos passos
- Documentar endpoints e integração Twilio  
- Criar testes unitários para os agentes  
