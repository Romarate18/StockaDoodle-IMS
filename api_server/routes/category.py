from flask import Blueprint, request, jsonify
from extensions import db
from models.category import Category
from core.activity_logger import ActivityLogger
from utils import get_image_blob

bp = Blueprint('categories', __name__)


# ----------------------------------------------------------------------
# GET /api/v1/categories → list all categories
# ----------------------------------------------------------------------
@bp.route('', methods=['GET'])
def list_categories():
    """List all categories with optional image inclusion"""
    include_image = request.args.get('include_image') == 'true'
    categories = Category.query.order_by(Category.name).all()
    
    return jsonify({
        'total': len(categories),
        'categories': [c.to_dict(include_image) for c in categories]
    }), 200


# ----------------------------------------------------------------------
# GET /api/v1/categories/<id> → get single category
# ----------------------------------------------------------------------
@bp.route('/<int:cat_id>', methods=['GET'])
def get_category(cat_id):
    """Get single category by ID"""
    category = Category.query.get_or_404(cat_id)
    include_image = request.args.get('include_image') == 'true'
    
    return jsonify(category.to_dict(include_image)), 200


# ----------------------------------------------------------------------
# POST /api/v1/categories → create new category
# name: String (required)
# description: String (optional)
# category_image: File (optional, multipart/form-data)
# ----------------------------------------------------------------------
@bp.route('', methods=['POST'])
def create_category():
    """Create new category"""
    is_form = request.content_type and 'multipart/form-data' in request.content_type
    data = request.form.to_dict() if is_form else (request.get_json() or {})
    
    name = data.get('name')
    if not name:
        return jsonify({"errors": ["Category name is required"]}), 400
    
    # Check uniqueness
    if Category.query.filter_by(name=name).first():
        return jsonify({"errors": ["Category name already exists"]}), 400
    
    # Handle image
    image_blob = get_image_blob()
    
    category = Category(
        name=name,
        description=data.get('description'),
        category_image=image_blob
    )
    
    db.session.add(category)
    db.session.commit()
    
    # Log activity
    user_id = data.get('user_id')
    if user_id:
        ActivityLogger.log_api_activity(
            method='POST',
            target_entity='category',
            user_id=user_id,
            details=f"Created category: {name}"
        )
    
    return jsonify(category.to_dict(include_image=True)), 201


# ----------------------------------------------------------------------
# PUT /api/v1/categories/<id> → replace category
# name: String (required)
# description: String (optional)
# category_image: File (optional)
# ----------------------------------------------------------------------
@bp.route('/<int:cat_id>', methods=['PUT'])
def replace_category(cat_id):
    """Replace entire category"""
    category = Category.query.get_or_404(cat_id)
    
    is_form = request.content_type and 'multipart/form-data' in request.content_type
    data = request.form.to_dict() if is_form else (request.get_json() or {})
    
    name = data.get('name')
    if not name:
        return jsonify({"errors": ["Category name is required for PUT"]}), 400
    
    # Check uniqueness (excluding current)
    existing = Category.query.filter(
        Category.name == name,
        Category.id != cat_id
    ).first()
    if existing:
        return jsonify({"errors": ["Category name already exists"]}), 400
    
    old_name = category.name
    category.name = name
    category.description = data.get('description')
    
    # Handle image
    new_image = get_image_blob()
    if new_image is not None:
        category.category_image = new_image
    
    db.session.commit()
    
    # Log activity
    ActivityLogger.log_api_activity(
        method='PUT',
        target_entity='category',
        user_id=data.get('user_id'),
        details=f"Replaced category: {old_name} → {name}"
    )
    
    return jsonify(category.to_dict(include_image=True)), 200


# ----------------------------------------------------------------------
# PATCH /api/v1/categories/<id> → update category
# name: String (optional)
# description: String (optional)
# category_image: File (optional)
# ----------------------------------------------------------------------
@bp.route('/<int:cat_id>', methods=['PATCH'])
def update_category(cat_id):
    """Partially update category"""
    category = Category.query.get_or_404(cat_id)
    
    is_form = request.content_type and 'multipart/form-data' in request.content_type
    data = request.form.to_dict() if is_form else (request.get_json() or {})
    
    changes = []
    
    if 'name' in data:
        if not data['name']:
            return jsonify({"errors": ["Category name cannot be empty"]}), 400
        
        # Check uniqueness
        existing = Category.query.filter(
            Category.name == data['name'],
            Category.id != cat_id
        ).first()
        if existing:
            return jsonify({"errors": ["Category name already exists"]}), 400
        
        changes.append(f"name: {category.name} → {data['name']}")
        category.name = data['name']
    
    if 'description' in data:
        changes.append("description updated")
        category.description = data['description']
    
    # Handle image
    new_image = get_image_blob()
    if new_image is not None:
        changes.append("image updated")
        category.category_image = new_image
    
    db.session.commit()
    
    # Log activity
    ActivityLogger.log_api_activity(
        method='PATCH',
        target_entity='category',
        user_id=data.get('user_id'),
        details=f"Updated category {category.name}: {', '.join(changes)}"
    )
    
    return jsonify(category.to_dict(include_image=True)), 200


# ----------------------------------------------------------------------
# DELETE /api/v1/categories/<id> → delete category
# ----------------------------------------------------------------------
@bp.route('/<int:cat_id>', methods=['DELETE'])
def delete_category(cat_id):
    """Delete category (only if no products linked)"""
    data = request.get_json(silent=True) or {}

    category = Category.query.get_or_404(cat_id)
    user_id = data.get("user_id")

    # Check if category has products
    if category.products:
        return jsonify({
            "errors": [f"Cannot delete category while it has {len(category.products)} linked products"]
        }), 400
    
    category_name = category.name
    db.session.delete(category)
    db.session.commit()
    
    # Log activity
    ActivityLogger.log_api_activity(
        method='DELETE',
        target_entity='category',
        user_id=user_id,
        details=f"Deleted category '{category_name}'"
    )
    
    return jsonify({
        "message": f"Category '{category_name}' deleted successfully"
    }), 200