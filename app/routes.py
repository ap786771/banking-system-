from flask import Blueprint, jsonify
import datetime

routes = Blueprint('routes', __name__)

@routes.route('/')
def home():
    return jsonify({
        "message": "Welcome to Banking System!",
        "current_time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })
