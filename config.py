import os
from hydrogram import Client

plugins = []

try:
    # API_ID é um número inteiro
    API_ID = int(os.environ.get("API_ID"))
    # API_HASH é uma string
    API_HASH = os.environ.get("API_HASH")

except (TypeError, ValueError) as e:
    # Esta exceção será levantada se API_ID não for um número ou se faltar alguma variável.
    print("\n\n############################################################")
    print("ERRO: Credenciais do Telegram não encontradas ou inválidas.")
    print("Certifique-se de que API_ID e API_HASH estão definidos corretamente no seu arquivo .env")
    print("############################################################\n")
    # Para garantir que o bot não tente iniciar com credenciais nulas:
    API_ID = 0
    API_HASH = "" 


bot = Client("bot", api_id=API_ID, api_hash=API_HASH, plugins=dict(root="plugins/bot"))
user = Client("user", api_id=API_ID, api_hash=API_HASH, plugins=dict(root="plugins/user"))
user.assistant = bot
