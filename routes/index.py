from flask import (
        g,
        Blueprint,
        render_template,
        request,
        redirect,
        url_for,
        flash,
        session,
        )
from flask_babel import _
from flask_login import (
        login_user,
        logout_user,
        login_required,
        )

from config import Config
from models.user import User, Role, LanguageConfig
from util import db, bcrypt, requires_role

index_bp = Blueprint('index', __name__)


@index_bp.route('/')
def start_page():
    if g.first_user:
        return redirect(url_for('.register_page'))
    elif not g.current_user.is_authenticated:
        flash(_('User is not autenticated, please login.'), 'info')
        return redirect(url_for('.login_page'))
    elif g.current_user.role == Role.ADMIN:
        users = User.query.all()
        return render_template('index-admin.html', page_title=_('Admin page'), users=users)
    return render_template('index.html', page_title=_('Start page'))


@index_bp.route('/register', methods=['GET', 'POST'])
def register_page():
    if not g.first_user and (not hasattr(g.current_user, 'role') or g.current_user.role != Role.ADMIN):
        flash(_('You do not have permission to access this page.'), 'error')
        return redirect(url_for('.error_page'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']

        if User.query.filter_by(username=username).first():
            flash(_('Username already exists.'), 'error')
            return redirect(url_for('.register_page'))

        role = Role(role)
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        new_user = User(username=username, password=hashed_password,
                        role=role)
        db.session.add(new_user)
        db.session.commit()
        if g.first_user:
            g.first_user = False
            login_user(new_user)
        flash(_('User ') + username + _(' has been successfully registered!'), 'info')
        return redirect(url_for('.start_page'))
    elif g.first_user:
        flash(_('No users found, create a user admin.'), 'warn')

    return render_template('register.html', page_title=_('User registration'))


@index_bp.route('/login', methods=['GET', 'POST'])
def login_page():
    if g.first_user:
        return redirect(url_for('.register_page'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()

        if user and bcrypt.check_password_hash(user.password, password):
            login_user(user)
            flash(_('Login successful!'), 'info')
            return redirect(url_for('.start_page'))
        else:
            flash(_('Invalid username or password.'), 'error')
            return redirect(url_for('.login_page'))
    return render_template('login.html', page_title=_('User login'))


@index_bp.route('/logout')
@login_required
def logout_page():
    flash(_('User ') + g.current_user.username + _(' has been logged out.'), 'info')
    logout_user()
    return redirect(url_for('.login_page'))


@index_bp.route('/inactive')
def inactive_page():
    return render_template('inactive.html', page_title=_('In inactive mode...'))


@index_bp.route('/error')
def error_page():
    error_message = session.pop('error_message', '')
    return render_template('error.html', page_title=_('Error'),
                           error_message=error_message)


@index_bp.route('/delete-user/<int:id>')
@requires_role(Role.ADMIN)
def delete_user(id):
    user = User.query.get_or_404(id)
    db.session.delete(user)
    db.session.commit()
    flash(_('User deleted successfully.'), 'info')
    return redirect(url_for('.start_page'))


@index_bp.route('/login-as/<int:id>')
@requires_role(Role.ADMIN)
def login_as(id):
    user = User.query.get_or_404(id)
    logout_user()
    login_user(user)
    return redirect(url_for('.start_page'))


@index_bp.route('/change-lang/<lang>')
@requires_role(Role.ADMIN)
def change_lang(lang):
    if lang in Config.LANGUAGES:
        lang_config = LanguageConfig.query.first()
        lang_config.lang = lang
        db.session.commit()
    return redirect(request.referrer or url_for('.start_page'))
