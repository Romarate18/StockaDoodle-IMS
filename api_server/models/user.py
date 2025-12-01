from werkzeug.security import generate_password_hash, check_password_hash
from mongoengine import StringField, EmailField, BooleanField, DateTimeField
from .base import BaseDocument
from datetime import datetime, timezone
import base64

class User(BaseDocument):
    meta = {
        'collection': 'users',
        'ordering': ['username'],
        'indexes': ['username', 'email', 'role']
        }
    
    # full name for display
    full_name = StringField(max_length=120, required=True)

    # used for login
    username = StringField(max_length=120, unique=True, required=True)

    # admin/manager/retailer
    role = StringField(max_length=50, default="retailer")
    
    # email address
    email = EmailField(max_length=255, unique=True, required=True)

    # hashed password only
    password_hash = StringField(max_length=255, required=True)

    # optional profile picture
    user_image = StringField()
    
    # status of user (for system access)
    is_active = BooleanField(default=True)
    
    # creation timestamp
    created_at = DateTimeField(default=lambda: datetime.now(timezone.utc))

    def set_password(self, password):
        # turn plain password into hashed password
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        # check if password is correct
        return check_password_hash(self.password_hash, password)

    def to_dict(self, include_image=False):
        data = {
            "id": self.id,
            "full_name": self.full_name,
            "username": self.username,
            "role": self.role,
            "email": self.email,
            "has_image": bool(self.user_image)
        }

        if include_image and self.user_image:
            # return user image as base64 string
            data["image_base64"] = self.user_image

        return data
