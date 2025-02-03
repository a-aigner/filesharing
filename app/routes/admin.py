from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash

from app import db
from app.models import User

admin_bp = Blueprint('admin_panel', __name__)


# Restrict access to admins only
def admin_required(func):
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash("Access denied: Admins only!", "danger")
            return redirect(url_for('home.index'))
        return func(*args, **kwargs)

    wrapper.__name__ = func.__name__
    return login_required(wrapper)


@admin_bp.route('/admin/users')
@admin_required
def user_list():
    search_query = request.args.get('search', '')

    # Pagination setup
    page = request.args.get('page', 1, type=int)
    per_page = 5  # Users per page

    if search_query:
        users = User.query.filter(User.username.ilike(f"%{search_query}%")).paginate(page=page, per_page=per_page)
    else:
        users = User.query.paginate(page=page, per_page=per_page)

    return render_template('admin/user_list.html', users=users, search_query=search_query)


@admin_bp.route('/admin/user/<int:user_id>')
@admin_required
def view_user(user_id):
    user = User.query.get_or_404(user_id)
    return render_template('admin/user_profile.html', user=user)


@admin_bp.route('/admin/user/<int:user_id>/toggle_admin', methods=['POST'])
@admin_required
def toggle_admin(user_id):
    user = User.query.get_or_404(user_id)

    if user.id == current_user.id:
        flash("You cannot change your own admin status!", "warning")
        return redirect(url_for('admin_panel.user_list'))

    user.is_admin = not user.is_admin
    db.session.commit()
    flash(f"Updated admin status for {user.username}.", "success")
    return redirect(url_for('admin_panel.user_list'))


@admin_bp.route('/admin/add_user', methods=['GET', 'POST'])
@admin_required
def add_user():
    if request.method == 'POST':
        username = request.form['username']
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email = request.form['email']
        password = request.form['password']
        is_admin = 'is_admin' in request.form  # Checkbox for admin status

        existing_user = User.query.filter((User.username == username) | (User.email == email)).first()
        if existing_user:
            flash("Username or email already exists!", "danger")
        else:
            new_user = User(
                username=username,
                first_name=first_name,
                last_name=last_name,
                email=email,
                password=generate_password_hash(password),
                is_admin=is_admin
            )
            db.session.add(new_user)
            db.session.commit()
            flash("User created successfully!", "success")
            return redirect(url_for('admin_panel.user_list'))

    return render_template('admin/add_user.html')
