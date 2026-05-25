import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Configuración centralizada de la aplicación"""
    #Gemini
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    # Flask
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = os.getenv('FLASK_DEBUG', 'True') == 'True'
    
    # Database
    MYSQL_HOST = os.getenv('MYSQL_HOST', 'localhost')
    MYSQL_PORT = os.getenv('MYSQL_PORT', '3306')
    MYSQL_USER = os.getenv('MYSQL_USER', 'root')
    MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD', '1234')
    MYSQL_DATABASE = os.getenv('MYSQL_DATABASE', 'booking_db')
    
    SQLALCHEMY_DATABASE_URI = (
        f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@"
        f"{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # OpenAI
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'gpt-4o-mini')
    
    # n8n Webhook
    N8N_WEBHOOK_URL = os.getenv('N8N_WEBHOOK_URL', '')
    
    # Horarios del salón
    BUSINESS_HOURS = {
        'start': '09:00',
        'end': '19:00',
        'days': ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday']
    }
    
    # Servicios disponibles
    SERVICES = {
        'corte': {'duration': 30, 'price': 5000},
        'tintura': {'duration': 90, 'price': 15000},
        'manicura': {'duration': 45, 'price': 8000},
        'pedicura': {'duration': 60, 'price': 10000},
        'depilacion': {'duration': 30, 'price': 7000},
        'tratamiento_facial': {'duration': 60, 'price': 12000}
    }
