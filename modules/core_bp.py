# modules/core_bp.py

from flask import Blueprint, send_from_directory
import os

# Cria o Blueprint para as rotas base do seu site
core_bp = Blueprint('core', __name__)

# Rota principal (serve login.html)
@core_bp.route('/')
def serve_login_page():
    return send_from_directory('src', 'login.html')

# Rota genérica para servir páginas HTML da raiz 'src'
@core_bp.route('/<path:filename>')
def serve_html_pages(filename):
    if filename.endswith('.html'):
        return send_from_directory('src', filename)
    else:
        return "Not Found", 404

# Rotas para servir arquivos estáticos específicos
@core_bp.route('/styles/<path:filename>')
def serve_styles(filename):
    return send_from_directory(os.path.join('src', 'styles'), filename)

@core_bp.route('/scripts/<path:filename>')
def serve_scripts(filename):
    return send_from_directory(os.path.join('src', 'scripts'), filename)

@core_bp.route('/assets/<path:filename>')
def serve_assets(filename):
    return send_from_directory(os.path.join('src', 'assets'), filename)