"""
controllers.py

Spot module controllers.
"""
from flask import Blueprint

mod_spot = Blueprint('spot', __name__, url_prefix='/api/v1/spot')
