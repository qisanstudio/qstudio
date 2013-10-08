from flask import Flask
import views

import blueprints as b

app = Flask(__name__)
app.register_blueprint(b.bp)


