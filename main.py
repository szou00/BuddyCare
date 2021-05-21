from flask import Flask, redirect, url_for, render_template, request, session, flash
from datetime import timedelta

from flask.signals import Namespace
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

if __name__ == "__main__":
    app.run(debug=True)