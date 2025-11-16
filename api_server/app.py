import os

from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    
    # Config
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'stockadoodle-flask-key')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv ('DATABASE_URL', 'sqlite:///stockadoodle.db')
    
    # Import and register models here
    with app.app_context():
        from models import category, product
        db.create_all()
        
    # Register routes here
    from routes.products import bp as product_bp
    app.register_blueprint(products_bp, url_prefix='/api/v1/products')
    
    @app.route('/')
    def index():
        return jsonify({
            "message": "Stockadoodle API",
            "database": "stockadoodle.db",
            "status": "running"
        })
        
    @app.route('/health')
    def health():
        return jsonify ({
            "status": "healthy",
            "db": "stockadoodle.db"
        }), 200
        
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='127.0.0.1', port=5000, debug=True)