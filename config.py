# config.py
import os
from datetime import datetime, date

class Config:
    # ESSENCIAL: Chave Secreta para segurança do Flask (MUDE EM PRODUÇÃO!)
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'sua_chave_secreta_padrao_aqui' 
    
    # Configuração do MySQL
    MYSQL_CONFIG = {
        'user': 'root', 
        'password': 'senhabanco123@', 
        'host': 'localhost',
        'database': 'dbjc',
        'charset': 'utf8mb4',
    }