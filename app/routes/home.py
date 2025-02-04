from flask import Blueprint, render_template
from flask_login import login_required, current_user
from app.models import Project

home_bp = Blueprint('home', __name__)


@home_bp.route('/')
@login_required
def index():
    projects = Project.query.filter_by(owner_id=current_user.id).all()  # Fetch projects for the logged-in user
    return render_template('home/home.html', projects=projects)
