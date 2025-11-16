from flask import Blueprint, request, jsonify
from extensions import db
from models.product import Product
from models.category import Category
from utils import get_image_blob, extract_int, parse_date

bp = Blueprint('products', __name__)

# ----------------------------------------------------------------------
# GET /api/v1/products                → list all products
# ----------------------------------------------------------------------
@bp.route('', methods = ['GET'])
def list_product():
    search = request.args.get('search')
    category_id = request.args.get('category_id')
    include_image = request.args.get('include_image') == 'true'
    
    query = Product.query
    if search:
        query = query.filter(Product.name.ilike(f"%{search}%"))     
    if category_id:
        query = query.filter_by(category_id=category_id)    
        
    products = query.all()
    return jsonify([
        p.to_dict(include_image) for p in products
    ])
    
# ----------------------------------------------------------------------
# GET /api/v1/products/<id>           → retrieving a product based on ID 
# ----------------------------------------------------------------------    
@bp.route('/<int:id>', methods=['GET'])
def get_product(id):
    product = Product.query.get_or_404(id)
    include_image = request.args.get('include_image') == 'true'
    return jsonify(product.to_dict(include_image))

# ----------------------------------------------------------------------
# POST /api/v1/products               → create new product
# ----------------------------------------------------------------------
@bp.route('', methods=['POST'])
def create_product():
    is_form = request.content_type and 'multipart/form-data' in request.content_type
    data = request.form.to_dict() if is_form else (request.get_json() or {})

    if not data.get('name'):
        return jsonify({"errors": ["Product name is required"]}), 400

    price = extract_int(data.get('price'))
    if price is None:
        return jsonify({"errors": ["Price must be a number"]}), 400

    category_id = None
    if data.get('category_id'):
        category_id = extract_int(data['category_id'])
        if category_id and not Category.query.get(category_id):
            return jsonify({"errors": ["Invalid category ID"]}), 400

    image_blob = get_image_blob()

    product = Product(
        name=data['name'],
        brand=data.get('brand'),
        price=price,
        category_id=category_id,
        stock_level=extract_int(data.get('stock_level'), 0),
        min_stock_level=extract_int(data.get('min_stock_level'), 10),
        expiration_date=parse_date(data.get('expiration_date')),
        image_blob=image_blob
    )

    db.session.add(product)
    db.session.commit()
    return jsonify(product.to_dict()), 201


# ----------------------------------------------------------------------
# PUT /api/v1/products/<int:id>       → Replace a product
# ----------------------------------------------------------------------
@bp.route('/<int:product_id>', methods=['PUT'])
def replace_product(product_id):
    product = Product.query.get_or_404(product_id)

    is_form = request.content_type and 'multipart/form-data' in request.content_type
    data = request.form.to_dict() if is_form else (request.get_json() or {})

    if 'name' not in data:
        return jsonify({"errors": ["Product name is required for PUT"]}), 400

    price = extract_int(data.get('price'))
    if price is None:
        return jsonify({"errors": ["Price must be a number"]}), 400

    category_id = None
    if 'category_id' in data:
        category_id = extract_int(data['category_id'])
        if category_id and not Category.query.get(category_id):
            return jsonify({"errors": ["Invalid category ID"]}), 400

    product.name = data['name']
    product.brand = data.get('brand')
    product.price = price
    product.category_id = category_id
    product.stock_level = extract_int(data.get('stock_level'), product.stock_level)
    product.min_stock_level = extract_int(data.get('min_stock_level'), product.min_stock_level)
    product.expiration_date = parse_date(data.get('expiration_date')) or product.expiration_date

    # Image handling
    new_image = get_image_blob()
    if new_image is not None:
        product.image_blob = new_image

    db.session.commit()
    return jsonify(product.to_dict())

# ----------------------------------------------------------------------
# PATCH /api/v1/products/<int:id>     → edit product details
# ----------------------------------------------------------------------   
@bp.route('/<int:id>', methods=['PATCH'])
def patch_product(id):
    product = Product.query.get_or_404(id)
    is_form = request.content_type and 'multipart/form-data' in request.content_type
    data = request.form.to_dict() if is_form else (request.get_json() or {})

    if 'name' in data and not data['name']:
        return jsonify({"errors": ["Product name cannot be empty"]}), 400

    if 'price' in data:
        price = extract_int(data['price'])
        if price is None:
            return jsonify({"errors": ["Price must be a number"]}), 400
        product.price = price

    if 'category_id' in data:
        cat_id = extract_int(data['category_id'])
        if cat_id and not Category.query.get(cat_id):
            return jsonify({"errors": ["Invalid category ID"]}), 400
        product.category_id = cat_id

    # Simple field updates
    for field in ('name', 'brand', 'stock_level', 'min_stock_level'):
        if field in data:
            setattr(product, field, data[field])

    if 'expiration_date' in data:
        product.expiration_date = parse_date(data['expiration_date'])

    # Image update (replace only if sent)
    new_image = get_image_blob()
    if new_image is not None:
        product.image_blob = new_image
        
    db.session.commit()
    return jsonify(product.to_dict())
        

# ----------------------------------------------------------------------
# DELETE /api/v1/products/<int:id>    → delete product
# ----------------------------------------------------------------------
@bp.route('/<int:id>', methods=['DELETE'])
def delete_product(id):
    product = Product.query.get_or_404(id)
    db.session.delete(product)
    db.session.commit()
    return jsonify({"message": "Product deleted successfully"}), 200