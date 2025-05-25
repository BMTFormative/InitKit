"""
auth service layer
Contains business logic for auth operations
"""
import uuid
from typing import List, Optional
from sqlmodel import Session, select
from fastapi import HTTPException

from .models import *
from ..shared.exceptions import *


class AuthService:
    """Service class for auth operations"""
    
    def __init__(self):
        pass
    
    # Add service methods here
    # Example:
    # def get_by_id(self, session: Session, id: uuid.UUID):
    #     """Get entity by ID"""
    #     pass
