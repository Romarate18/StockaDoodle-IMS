from extensions import db
import base64

class Category(db.Model):
    __tablename__ = 'categories'
    
    # id of the category
    id = db.Column(db.Integer, primary_key=True)
    
    # name of the category, must be unique
    name = db.Column(db.String(100), unique=True, nullable=False)
    
    # optional description of the category
    description = db.Column(db.String(255), nullable=True)
    
    # optional image for the category
    category_image = db.Column(db.LargeBinary, nullable=True)
    
    # list of products inside this category
    products = db.relationship('Product', backref='category', lazy=True)
    
    def to_dict(self, include_image=False):
        data = {
            'id': self.id,
            'name': self.name,
            'description': self.description
        }
        
        if include_image and self.category_image:
            # convert image to base64 string for easy frontend use
            data['image_base64'] = base64.b64encode(self.category_image).decode('utf-8')
        
        return data
