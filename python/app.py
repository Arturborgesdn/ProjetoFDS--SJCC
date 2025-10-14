 # ============================================
     # CÓDIGO MÍNIMO COM CORS: Para Integração com JS
     # ============================================

from flask import Flask, jsonify, request  # Importações básicas.
from flask_cors import CORS  # Nova: Para permitir chamadas do browser.

app = Flask(__name__)  # Cria o app.
CORS(app)  # Nova: Ativa CORS para todas as rotas (permite localhost do JS chamar Python).

     # ============================================
     # ROTA SIMPLES: /api/conectar (POST)
     # ============================================
     
@app.route('/api/conectar', methods=['POST'])
def conectar():
         dados = request.get_json()  # Lê JSON do JS.
         acao = dados.get('acao', 'desconhecida') if dados else 'desconhecida'
         
         # Resposta simples.
         return jsonify({
             'sucesso': True,
             'mensagem': f'Conexão OK! Ação: {acao}'
         }), 200

     # ============================================
     # Rodar o Servidor
     # ============================================
if __name__ == '__main__':
        app.run(host='localhost', port=5000, debug=True)
     