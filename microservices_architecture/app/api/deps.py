"""
API bağımlılıkları (dependency injection).
"""
from typing import Generator
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.connection import get_db