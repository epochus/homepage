"""
    homepage/views.py
    -----------------
    Defines url routes and logic

"""
from flask import request, session, redirect, url_for, \
        render_template, flash, abort
from sqlalchemy import exc
from homepage import app, db
from homepage.models import Project, Post, Tag


@app.route('/')
def index():
    return render_template('homepage/index.html')

@app.route('/resume')
def resume():
    return render_template('homepage/resume.html')

@app.route('/projects')
def projects():
    error = False
    try:
        projects = Project.query.all()
    except exc.SQLAlchemyError:
        error = True
        projects = []

    return render_template('homepage/projects.html', projects=projects, error=error)

@app.route('/notes')
def notes():
    error = False
    try:
        posts = Post.query.order_by(Post.pub_date.desc()).all()
    except exc.SQLAlchemyError:
        error = True
        posts = []

    return render_template('homepage/notes.html', posts=posts, error=error)

@app.route('/notes/<int:post_id>/<title>')
def page(post_id, title):
    try:
        post = Post.query.get_or_404(post_id)
    except exc.SQLAlchemyError:
        post = []
        abort(404)

    return render_template('homepage/page.html', post=post)

@app.errorhandler(404)
def not_found(error):
    return render_template('homepage/notfound.html'), 404

def init_db():
    db.drop_all()
    db.create_all()
