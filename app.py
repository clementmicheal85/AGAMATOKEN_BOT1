# app.py
from flask import Flask

# This simple Flask app is required by Render to create a web service.
# It serves a basic health-check endpoint.
app = Flask(__name__)

@app.route('/')
def home():
    """A simple homepage to confirm the service is running."""
    return "Agama Coin Bot Web Service is Live!"

if __name__ == '__main__':
    # This block is for local development only and will not be used in production on Render.
    app.run(host='0.0.0.0', port=5000)
