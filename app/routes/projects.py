from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from flask import send_file
import io
from app import db
from app.models import Project, File
import os

projects_bp = Blueprint('projects', __name__)


@projects_bp.route('/projects')
@login_required
def list_projects():
    search_query = request.args.get('search', '').strip()
    page = request.args.get('page', 1, type=int)
    per_page = 1  # One project per page

    # Filter projects by name or ID
    if search_query:
        projects = Project.query.filter(
            (Project.name.ilike(f"%{search_query}%")) | (Project.id.cast(db.String).ilike(f"%{search_query}%"))
        ).filter_by(owner_id=current_user.id).paginate(page=page, per_page=per_page)
    else:
        projects = Project.query.filter_by(owner_id=current_user.id).paginate(page=page, per_page=per_page)

    return render_template('projects/project_list.html', projects=projects, search_query=search_query)


@projects_bp.route('/projects/create', methods=['GET', 'POST'])
@login_required
def create_project():
    if request.method == 'POST':
        name = request.form['name']
        new_project = Project(name=name, owner_id=current_user.id)
        db.session.add(new_project)
        db.session.commit()
        flash("Project created successfully!", "success")
        return redirect(url_for('projects.list_projects'))

    return render_template('projects/create_project.html')


@projects_bp.route('/projects/<int:project_id>')
@login_required
def project_detail(project_id):
    """Display project details with paginated file list."""
    project = Project.query.filter_by(id=project_id, owner_id=current_user.id).first_or_404()

    # Pagination setup
    page = request.args.get('page', 1, type=int)
    per_page = 15
    files = File.query.filter_by(project_id=project.id).paginate(page=page, per_page=per_page)

    return render_template('projects/project_detail.html', project=project, files=files)


@projects_bp.route('/share/<access_key>')
def shared_project(access_key):
    """Allow non-users to view and download files from a shared project."""
    project = Project.query.filter_by(access_key=access_key).first_or_404()

    # Pagination setup
    page = request.args.get('page', 1, type=int)
    per_page = 15  # Show 15 files per page
    files = File.query.filter_by(project_id=project.id).paginate(page=page, per_page=per_page)

    return render_template('projects/shared_project.html', project=project, files=files)


@projects_bp.route('/projects/<int:project_id>/upload', methods=['POST'])
@login_required
def upload_file(project_id):
    """Upload a file to a project (stored in MySQL)."""
    project = Project.query.filter_by(id=project_id, owner_id=current_user.id).first_or_404()

    if 'file' not in request.files:
        flash('No file selected!', 'danger')
        return redirect(url_for('projects.project_detail', project_id=project.id))

    file = request.files['file']
    if file.filename == '':
        flash('No file selected!', 'danger')
        return redirect(url_for('projects.project_detail', project_id=project.id))

    filename = secure_filename(file.filename)
    file_data = file.read()  # Read file as binary data

    new_file = File(filename=filename, data=file_data, project_id=project.id)
    db.session.add(new_file)
    db.session.commit()

    flash('File uploaded successfully!', 'success')
    return redirect(url_for('projects.project_detail', project_id=project.id))


@projects_bp.route('/download/<int:file_id>')
def download_file(file_id):
    """Download a file from the database using its ID."""
    file = File.query.get_or_404(file_id)

    return send_file(
        io.BytesIO(file.data),
        as_attachment=True,
        download_name=file.filename
    )


@projects_bp.route('/projects/<int:project_id>/delete_file/<int:file_id>', methods=['POST'])
@login_required
def delete_file(project_id, file_id):
    project = Project.query.filter_by(id=project_id, owner_id=current_user.id).first_or_404()
    file = File.query.filter_by(id=file_id, project_id=project.id).first_or_404()

    db.session.delete(file)
    db.session.commit()
    flash(f'File "{file.filename}" deleted successfully.', 'success')

    return redirect(url_for('projects.project_detail', project_id=project.id))
