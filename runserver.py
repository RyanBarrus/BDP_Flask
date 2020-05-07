"""
This script runs the FlaskWebProject application using custom development server.
"""

from os import environ
from FlaskWebProject import app

if __name__ == '__main__':
    from waitress import serve
    serve(app, host="0.0.0.0", port=5555)
