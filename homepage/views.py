"""
    homepage/views.py
    -----------------
    Defines url routes and logic

"""
from flask import request, session, redirect, url_for, \
        render_template, flash, abort
from sqlalchemy import exc

from homepage import app, db
from homepage.models import Project, Tag


@app.route('/')
def index():
    return render_template('homepage/index.html')


@app.route('/projects')
def projects():
    error = False
    try:
        projects = Project.query.all()
    except exc.SQLAlchemyError:
        error = True
        projects = []

    return render_template('homepage/projects.html', projects=projects, error=error)


@app.errorhandler(404)
def not_found(error):
    return render_template('homepage/notfound.html'), 404


def init_db():
    db.drop_all()
    db.create_all()