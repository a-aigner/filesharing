from flask import Blueprint, render_template

projects_bp = Blueprint('projects', __name__)


@projects_bp.route('/dashboard')
def dashboard():
    return render_template('projects/dashboard.html')
