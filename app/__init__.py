from flask import Flask
from flask_login import LoginManager
from .models import User

def create_app():
    app = Flask(__name__, static_folder='../static', template_folder='../templates')
    
    app.config['SECRET_KEY'] = 'your_secret_key'
    
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.get_by_id(int(user_id))
    
    from .index import index_bp
    from .auth import auth_bp
    
    app.register_blueprint(index_bp, url_prefix='/')
    app.register_blueprint(auth_bp, url_prefix='/auth')
    
    return app