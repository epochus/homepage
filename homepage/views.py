"""
    homepage/views.py
    -----------------
    Defines url routes and logic

"""
from flask import request, session, redirect, url_for, \
        render_template, flash, abort, json, jsonify
from sqlalchemy import exc

from homepage import app, db
from homepage.models import Project, Tag
from demos.fifteen import FifteenSolver


def init_db():
    db.drop_all()
    db.create_all()


@app.route('/')
def index():
    return render_template('homepage/index.html')


@app.errorhandler(404)
def not_found(error):
    return render_template('homepage/notfound.html'), 404


@app.route('/projects')
def projects():
    error = False
    try:
        projects = Project.query.order_by(Project.id.desc()).all()
    except exc.SQLAlchemyError:
        error = True
        projects = []

    return render_template('homepage/projects.html', projects=projects, error=error)


# Project demos
@app.route('/projects/fifteen-puzzle')
def fifteen_puzzle():
    return render_template('demos/fifteen-puzzle.html')

@app.route('/projects/fifteen-puzzle/solve')
def solve():
    response_data = {'result': []}
    board_msg = request.args.get('board', None)

    if board_msg:
        board_arr = json.loads(board_msg)
        solver = FifteenSolver(4, 4, board_arr)
        move_str = solver.solve_puzzle();
        response_data['result'] = list(move_str)

    return jsonify(response_data)