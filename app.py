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