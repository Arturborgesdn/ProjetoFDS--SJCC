from flask import Flask
from flask_cors import CORS
import os
# Importa a classe de configuração
from config import Config
# Importa os Blueprints dos seus respectivos arquivos
from modules.core_bp import core_bp
from modules.api_bp import api_bp

# Padrão Factory: Função que cria e configura o aplicativo.
def create_app(config_class=Config):
    # Inicializa o Flask, definindo 'src' como a pasta estática principal
    app = Flask(__name__, static_folder='src') 
    
    # Carrega as configurações (incluindo SECRET_KEY, etc.)
    app.config.from_object(config_class)
    
    # Configura CORS para permitir requisições de outras origens
    CORS(app)

    # Registra os Blueprints (eles trazem todas as rotas)
    app.register_blueprint(api_bp) # Rotas de API (ex: /api/login)
    app.register_blueprint(core_bp) # Rotas Core (ex: /, /ranking.html)

    return app

# Bloco de Execução Principal
if __name__ == '__main__':
    # Cria as pastas do frontend (apenas para garantir a existência)
    os.makedirs('src', exist_ok=True)
    os.makedirs('src/styles', exist_ok=True)
    os.makedirs('src/scripts', exist_ok=True)
    os.makedirs('src/assets', exist_ok=True)
    
    # Cria a instância do aplicativo e executa
    app = create_app()
    app.run(host='localhost', port=5000, debug=True)

import os
import mysql.connector

def get_db_connection():
    # Tenta pegar a URL completa do banco (A Railway fornece isso)
    db_url = os.getenv("DATABASE_URL")
    
    if db_url:
        # Se existir URL (estamos na nuvem ou configurado via URL)
        # Nota: Bibliotecas como SQLAlchemy aceitam a URL direto.
        # Se usar mysql.connector puro, precisará "parsear" a URL ou usar as variáveis separadas:
        connection = mysql.connector.connect(
            host=os.getenv("MYSQLHOST"),
            user=os.getenv("MYSQLUSER"),
            password=os.getenv("MYSQLPASSWORD"),
            database=os.getenv("MYSQLDATABASE"),
            port=os.getenv("MYSQLPORT")
        )
    else:
        # Fallback: Estamos no Windows Local (localhost)
        connection = mysql.connector.connect(
            host="localhost",
            user="root",          # Seu usuário local
            password="senhabanco123@", # Sua senha local
            database="dbjc"
        )
    return connection