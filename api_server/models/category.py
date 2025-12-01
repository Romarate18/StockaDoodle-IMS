from mongoengine import StringField
from .base import BaseDocument
import base64

class Category(BaseDocument):
    meta = {
        'collection': 'categories',
        'ordering': ['name'],
        'indexes': ['name']
        }
    
    # name of the category, must be unique
    name = StringField(max_length=100, unique=True, required=True)
    
    # optional description of the category
    description = StringField(max_length=255)
    
    # optional image for the category
    category_image = StringField()
     
    def to_dict(self, include_image=False):
        data = {
            'id': self.id,
            'name': self.name,
            'description': self.description
        }
        
        if include_image and self.category_image:
            # convert image to base64 string for easy frontend use
            data['image_base64'] = self.category_image
        
        return data
