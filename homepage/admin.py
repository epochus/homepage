from flask import request, session, redirect, url_for, flash
from flask_admin.contrib.sqla import ModelView
from flask_admin import Admin, AdminIndexView, helpers, expose
from wtforms import Form, StringField, PasswordField
from wtforms.validators import InputRequired, ValidationError
from werkzeug.security import generate_password_hash, check_password_hash
from jinja2 import Markup

from homepage import app, db
from homepage.models import Project, Post, Tag

def validate_login(form, field):
    if form.username.data != app.config['USERNAME']:
        raise ValidationError('Invalid username or password.')

    pw = (form.password.data + app.config['SALT']).encode('utf-8')
    if not check_password_hash(app.config['PASSWORD'], pw):
        raise ValidationError('Invalid username or password.')

class LoginForm(Form):
    username = StringField('Username', [InputRequired("Username is required")])
    password = PasswordField('Password', [InputRequired("Password is required"),
                              validate_login])

def flash_errors(form):
    for field, errors in form.errors.items():
        for error in errors:
            flash(error, 'error')

class AuthIndexView(AdminIndexView):
    @expose('/')
    def index(self):
        if not session.get('is_authenticated', False):
            return redirect(url_for('.login'))
        return super(AuthIndexView, self).index()

    @expose('/login/', methods=('GET', 'POST'))
    def login(self):
        form = LoginForm(request.form)
        if request.method == 'POST' and form.validate():
            session['is_authenticated'] = True
            session['user'] = form.username.data
            flash('You are now logged in.', 'success')
            return redirect(url_for('.index'))

        flash_errors(form)
        self._template_args['form'] = form
        return super(AuthIndexView, self).index()

    @expose('/logout/')
    def logout(self):
        session.pop('is_authenticated', None)
        flash('You are now logged out.', 'success')
        return redirect(url_for('.index'))

class AuthModelView(ModelView):
    def is_accessible(self):
        return session.get('is_authenticated', False)

    def _handle_view(self, name , **kwargs):
        if not self.is_accessible():
            return redirect(url_for('admin.login', next=request.url))

class ProjectView(AuthModelView):
    """ Admin display for all projects """
    def _list_format_links(view, context, model, name):
        link = model.url
        return Markup(
                ('<a href="{url}" rel="external">{url}</a></p>\n'
                ).format(url=link))

    column_formatters = dict(url=_list_format_links)
    column_list = ('title', 'description', 'url')
    column_labels = dict(url='URL', text="Description")
    column_sortable_list = ('title',)
    column_searchable_list = ('title',)

class PostView(AuthModelView):
    column_list = ('title', 'pub_date', 'is_published', 'tags')
    column_labels = dict(pub_date='Published Date', tag='Tag(s)')

# Initialize admin
admin = Admin(app, name='Jackson Wu :: Admin',
        index_view=AuthIndexView(),
        base_template='admin/custom_master.html',
        template_mode='bootstrap3')


admin.add_view(ProjectView(Project, db.session))
admin.add_view(PostView(Post, db.session))
admin.add_view(AuthModelView(Tag, db.session))