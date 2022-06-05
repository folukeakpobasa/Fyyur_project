import os
SECRET_KEY = os.urandom(32)
# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))

# Enable debug mode.
DEBUG = True

# Connect to the database

SQLALCHEMY_TRACK_MODIFICATIONS = False

SQLALCHEMY_DATABASE_URI = 'postgresql://udacity:1234@localhost:5432/fyyurapp'

# POSTGRES = {
#     'user': 'udacity',
#     'pw': '1234',
#     'db': 'fyyur',
#     'host': 'localhost',
#     'port': '5432',
# }

# SQLALCHEMY_DATABASE_URI='postgresql://%(user)s:\%(pw)s@%(host)s:%(port)s/%(db)s' % POSTGRES