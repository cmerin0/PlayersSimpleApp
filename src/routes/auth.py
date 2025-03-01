from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, unset_jwt_cookies
from ..models import User
from ..db import session

auth = Blueprint("auth", __name__)

# Route for registration of user
@auth.route("/register", methods=["POST"])
def register():
    try:
        data = request.get_json()
        username = data.get("username")
        password = data.get("password")
        is_admin = False  # Default role is not admin

        # Validation (Important: Add more robust validation as needed)
        if not username or not password:
            return jsonify({"message": "Username and password are required"}), 400
        if session.query(User).filter_by(username=username).first():
            return jsonify({"message": "Username already exists"}), 400

        # Hash the password before storing it (Security Best Practice)
        hashed_password = generate_password_hash(password, method="pbkdf2:sha256")

        new_user = User(username=username, password=hashed_password, is_admin=is_admin)
        session.add(new_user)
        session.commit()

        return jsonify({"message": "User registered successfully"}), 201

    except Exception as e:
        session.rollback()
        return jsonify({"Error": "An Error occurred while creating the user", "message": str(e) }), 500

@auth.route("/login", methods=["POST"])
def login():
    try:
        data = request.get_json()
        username = data.get("username")
        password = data.get("password")

        # Getting the username 
        user = session.query(User).filter_by(username=username).first()

        if not user or not check_password_hash(user.password, password):
            return jsonify({"message": "Invalid credentials"}), 401

        # JWT creation (using flask_jwt_extended)
        access_token = create_access_token(identity=str(user.id))
        refresh_token = create_access_token(identity=str(user.id)) # Refresh token

        # Set JWTs as cookies (Modern approach and more secure than local storage)
        response = jsonify({
            "message": "Login successful",
            "access_token" : access_token,
            "refresh_token": refresh_token
        })
        response.set_cookie("access_token_cookie", access_token) 
        response.set_cookie("refresh_token_cookie", refresh_token)

        return response, 200

    except Exception as e:
        return jsonify({"Error": "An Error occurred while Loggin In", "message": str(e) }), 500
    
# New route for token refresh
@auth.route('/refresh', methods=['POST'])  
@jwt_required(refresh=True)  # Protect with refresh token
def refresh():
    try:
        current_user_id = get_jwt_identity()  # Get user ID from the refresh token

        new_access_token = create_access_token(identity=current_user_id)

        response = jsonify({'message': 'Access token refreshed'})
        response.set_cookie('access_token_cookie', new_access_token)
        return response, 200

    except Exception as e:
        return jsonify({'message': 'Something went wrong during token refresh', "refresh_error": str(e)}), 500

# Log Out route
@auth.route('/logout', methods=['POST'])
def logout():
    response = jsonify({'message': 'Logged out successfully'})
    unset_jwt_cookies(response)  # Clear both access and refresh token cookies
    return response, 200

# Route to get all users 
@auth.route("/users", methods=["GET"])
@jwt_required() # Protecting route with JWT Auth
def get_users():
    try:
        # Getting current user id
        current_user_id = get_jwt_identity()

        # Checking if my Current Logged In User is Admin
        current_user = session.query(User).filter_by(id=current_user_id).first()

        if not current_user.is_admin:
            return jsonify({"Error": "Forbidden Access, User is not an Admin" }), 403

        # Getting all users and list them
        users = session.query(User).all()
        users_list = [{"id": user.id, "username": user.username, "is_admin": user.is_admin} for user in users]
        
        return jsonify(users_list), 200
    except Exception as e:
        return jsonify({"Error": "An Error occurred while fetching users", "message": str(e)}), 500