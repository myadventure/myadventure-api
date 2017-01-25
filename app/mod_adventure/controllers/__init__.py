"""
Initialize adventure module controllers

"""

from flask import Blueprint

MOD_ADVENTURE = Blueprint('adventure', __name__, url_prefix='/api/v1/adventure')
