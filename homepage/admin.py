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
    password = PasswordField('Password', [InputRequired("Password is required"),                              validate_login])

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
    def _list_format_thumbnail(view, context, model, name):
        if not model.image:
            return ''
        return Markup('<img src="{}" width="100" height="100">'.format(model.image))

    def _list_format_links(view, context, model, name):
        project, code, text = '', '', ''
        if model.url:
            project = model.url
        if model.code:
            code = model.code
        if model.text:
            text = model.text
        return Markup(
                ('<p><strong>Project: </strong>\n'
                 '<a href="{project}" rel="external" target="_blank">{project}</a></p>\n'
                 '<p><strong>Code: </strong>\n'
                 '<a href="{code}" rel="external" target="_blank">{code}</a></p>\n'
                 '<p><strong>Text: </strong>\n'
                 '<a href="{text}" rel="external" target="_blank">{text}</a></p>\n'
                ).format(project=project, text=text, code=code))

    column_formatters = dict(image=_list_format_thumbnail,
                             url=_list_format_links)
    column_list = ('title', 'url', 'image')
    column_labels = dict(url='URL(s)')
    column_sortable_list = ('title',)
    column_searchable_list = ('title',)

    form_args = dict(url=dict(label='Project/Demo URL'),
                     code=dict(label='Code Repo URL'),
                     text=dict(label='Text URL'),
                     image=dict(label='Image URL'))

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
