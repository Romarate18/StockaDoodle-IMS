from .products import bp as products_bp
from .category import bp as categories_bp
from .logs import bp as logs_bp
from .sales import bp as sales_bp
from .users import bp as users_bp

__all__ = [
    'products_bp', 
    'categories_bp',
    'logs_bp',
    'sales_bp',
    'users_bp'
    ]