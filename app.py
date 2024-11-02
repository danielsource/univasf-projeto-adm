import os

from flask import (
        Flask,
        g,
        render_template,
        request,
        redirect,
        url_for,
        session,
        flash,
        send_from_directory
        )
from flask_babel import Babel, _
from flask_login import LoginManager, current_user, logout_user

from config import Config
from models.user import User, Role, LanguageConfig
from util import db, bcrypt, in_business_hours

app = Flask(__name__)
app.config.from_object(Config)
login_manager = LoginManager()
login_manager.init_app(app)
bcrypt.init_app(app)
db.init_app(app)
babel = Babel(app)

from routes import *
app.register_blueprint(index_bp)
app.register_blueprint(product_bp)
app.register_blueprint(client_bp)
app.register_blueprint(occurrence_bp)
app.register_blueprint(order_bp)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


@app.before_request
def before_request():
    g.current_user = current_user
    g.first_user = User.query.count() == 0
    g.current_route = request.endpoint
    if g.current_user.is_authenticated and \
            g.current_user.role == Role.OPERATOR and \
            not in_business_hours():
        logout_user()
        return redirect(url_for('index.inactive_page'))


@app.context_processor
def inject_on_templates():
    lang_config = LanguageConfig.query.first()
    return dict(get_locale=get_locale,
                current_lang=lang_config.lang,
                languages=Config.LANGUAGES,
                Role=Role,
                business_start_hour=Config.BUSINESS_START_HOUR.strftime('%H:%M'),
                business_end_hour=Config.BUSINESS_END_HOUR.strftime('%H:%M'))


@app.errorhandler(401)
def page_not_found(e):
    return render_template('error.html', page_title=_('Error: Unauthorized')), 401


@app.errorhandler(404)
def page_not_found(e):
    return render_template('error.html', page_title=_('Error: Page Not Found')), 404


@app.errorhandler(500)
def internal_error(e):
    db.session.rollback()
    return render_template('error.html', page_title=_('Error: Internal Server')), 500


def get_locale():
    lang_config = LanguageConfig.query.first()
    if lang_config:
        return lang_config.lang
    return Config.DEFAULT_LANGUAGE
babel.init_app(app, locale_selector=get_locale)


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')


with app.app_context():
    if not os.path.exists(os.path.join(app.instance_path, Config.DATABASE_PATH)):
        db.create_all()
        if Config.DEBUG:
            import db_init_example
    if not LanguageConfig.query.first():
        db.session.add(LanguageConfig(lang=Config.DEFAULT_LANGUAGE))
        db.session.commit()
