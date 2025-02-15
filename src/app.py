from flask import Flask
from routes import routes


def create_app():
    app = Flask(__name__)
    app.register_blueprint(routes)
    return app


app = create_app()
if __name__ == "__main__":
    app.run(host="0.0.0.0",port=8000,debug=True)
