"""
This script runs the FlaskWebProject application using custom development server.
"""

from os import environ
from FlaskWebProject import app

if __name__ == '__main__':
    # from waitress import serve
    # serve(app, host="0.0.0.0", port=5555)
    HOST = environ.get('SERVER_HOST', '0.0.0.0')
    try:
        PORT = int(environ.get('SERVER_PORT', '5555'))
    except ValueError:
        PORT = 5555
    app.run(HOST, PORT)
