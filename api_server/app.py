import os
from flask import Flask, jsonify
from extensions import db, migrate
from dotenv import load_dotenv

load_dotenv()

def create_app():
    app = Flask(__name__)
    
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'stockadoodle-dev-2025')
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///stockadoodle.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # ← CRITICAL: These two lines MUST be here!
    db.init_app(app)
    migrate.init_app(app, db)

    # Import models AFTER init_app
    with app.app_context():
        from models import category, product
        db.create_all()

        # Seed default category
        from models.category import Category
        if Category.query.count() == 0:
            db.session.add(Category(name="General"))
            db.session.commit()

    # Register blueprint
    from routes.products import bp as products_bp
    app.register_blueprint(products_bp, url_prefix='/api/v1/products')

    @app.route('/api/v1')
    def home():
        return jsonify({
            "message": "StockaDoodle API LIVE!",
            "status": "Production Ready",
            "database": "stockadoodle.db"
        })

    @app.route('/api/v1/health')
    def health():
        return jsonify({"status": "healthy"}), 200

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='127.0.0.1', port=5000, debug=True)