from flask import Flask
from flask_cors import CORS
from config.settings import Config

from database import db

def create_app():
    """Factory para crear la aplicación Flask"""
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Habilitar CORS
    CORS(app)
    
    # Inicializar base de datos
    db.init_app(app)
    
    # Registrar blueprints
    from routes.chat import chat_bp
    app.register_blueprint(chat_bp)
    
    # Crear tablas si no existen
    with app.app_context():
        db.create_all()
    
    @app.route('/health', methods=['GET'])
    def health_check():
        return {'status': 'ok', 'message': 'AI Booking Assistant running'}, 200
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)
