from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from ..models import User
from ..db import sessionmaker

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    print(request.method)
    if request.method == 'POST':
        return jsonify({'message': 'Register POST'}), 200
    return jsonify({'message': 'Register GET'}), 200