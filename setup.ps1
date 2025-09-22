Write-Host "🚀 Iniciando setup do projeto Dora..."

# Cria ambiente virtual
python -m venv .venv
.venv\Scripts\Activate.ps1

# Atualiza pip
python -m pip install --upgrade pip

# Instala dependências
pip install -r requirements.txt

# Cria .env se não existir
if (-Not (Test-Path ".env")) {
  Copy-Item ".env.example" ".env"
  Write-Host "⚠️ Arquivo .env criado a partir do exemplo. Preencha com suas credenciais reais."
}

Write-Host "✅ Setup concluído. Para rodar:"
Write-Host ".venv\Scripts\Activate.ps1"
Write-Host "python chat_dora.py"
