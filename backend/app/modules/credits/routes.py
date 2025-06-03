"""
credits API routes
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from typing import List
import uuid

from ...api.deps import SessionDep, CurrentUser, get_current_active_superuser
from .models import *
from .service import CreditsService

router = APIRouter(prefix="/credits", tags=["credits"])
service = CreditsService()

# Add routes here
# Example:
# @router.get("/")
# def list_items(session: SessionDep, current_user: CurrentUser):
#     """List items"""
#     return {"message": "credits routes"}
