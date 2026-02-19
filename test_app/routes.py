"""
Blueprint тестового приложения.

Все маршруты доступны по префиксу /test.
"""
from flask import Blueprint, render_template

test_bp = Blueprint('test_app', __name__, url_prefix='/test')


@test_bp.route('/')
def index():
    """Главная страница тестового приложения."""
    return render_template('test_app/index.html')
