"""
SQLAlchemy ORM Database Models (Member 3)

Defines relational database tables for products, user profiles, and scan logs.
"""
from typing import Optional
import json


class ProductModel:
    """Mock DB model for Product persistence."""

    def __init__(self, product_id: str, name: str, data_json: str):
        self.product_id = product_id
        self.name = name
        self.data_json = data_json

    def to_dict(self):
        return json.loads(self.data_json)


class UserProfileModel:
    """Mock DB model for User Profile persistence."""

    def __init__(self, user_id: str, name: str, allergies_json: str):
        self.user_id = user_id
        self.name = name
        self.allergies_json = allergies_json
