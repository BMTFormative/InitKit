"""
items API routes
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from typing import List
import uuid

from ...api.deps import SessionDep, CurrentUser, get_current_active_superuser
from .models import *
from .service import ItemsService

router = APIRouter(prefix="/items", tags=["items"])
service = ItemsService()

# Add routes here
# Example:
# @router.get("/")
# def list_items(session: SessionDep, current_user: CurrentUser):
#     """List items"""
#     return {"message": "items routes"}
