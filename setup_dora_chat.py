import os

# Estrutura de arquivos e conteúdo inicial
estrutura = {
    ".env": """OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxx
NGROK_TOKEN=2wPAeTNLxxxxxxxxxxxxxxxx

DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=sua_senha
DB_NAME=dora_teste
""",
    ".gitignore": ".env\n__pycache__/\n*.pyc\n",
    "requirements.txt": "flask\npyngrok\ntwilio\npydantic-ai\nmysql-connector-python\npython-dotenv\npandas",
    "README.md": "# Dora Chatbot\n\nChatbot com IA e integração com banco de dados MySQL.\n\nVeja o README completo com instruções no projeto.",
    "data/dados_meta.csv": "data,visualizacoes,curtidas,comentarios\n2025-06-24,1000,250,30",
    "scripts/importar_csv_com_env.py": "# importar_csv_com_env.py\n# → insere dados do CSV no banco de dados MySQL usando variáveis do .env",
    "scripts/consulta_com_env.py": "# consulta_com_env.py\n# → consulta e exibe os dados da tabela redes_sociais do banco",
    "chatbot/chat_dora.py": "# chat_dora.py\n# → script principal do chatbot com Flask, OpenAI e banco de dados"
}

# Caminho base do projeto
base_dir = "Dora-Chat"

# Criação dos diretórios e arquivos
for path, content in estrutura.items():
    full_path = os.path.join(base_dir, path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content)

print("✅ Estrutura 'Dora-Chat' criada com sucesso!")
print("➡ Agora você pode abrir a pasta no VS Code e começar a trabalhar.")
