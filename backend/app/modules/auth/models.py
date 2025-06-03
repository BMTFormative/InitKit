import uuid
from datetime import datetime
from typing import List, Optional
from pydantic import EmailStr
from sqlmodel import Field, Relationship, SQLModel, Column, JSON
# Models will be extracted from main models.py during migration
