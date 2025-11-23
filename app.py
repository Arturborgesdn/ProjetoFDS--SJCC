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
    app.register_blueprint(api_bp) 
    app.register_blueprint(core_bp) 

    return app

# ==========================================================
# 🔴 A CORREÇÃO ESTÁ AQUI EMBAIXO 🔴
# ==========================================================

# Criamos a variável 'app' no escopo GLOBAL. 
# Agora o Gunicorn consegue vê-la!
app = create_app()

# Bloco de Execução Principal (Apenas para rodar localmente)
if __name__ == '__main__':
    # Cria as pastas do frontend
    os.makedirs('src', exist_ok=True)
    os.makedirs('src/styles', exist_ok=True)
    os.makedirs('src/scripts', exist_ok=True)
    os.makedirs('src/assets', exist_ok=True)
    
    # Não precisamos criar 'app' aqui de novo, pois já criamos acima.
    # Apenas rodamos.
    app.run(host='0.0.0.0', port=5000, debug=True)

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
            password="senhabanco123@",
            database="dbjc"
        )
    return connection