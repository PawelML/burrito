from app import create_app
from flask_login import login_required

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)