import pytest
from flask import Flask
import sys
import os

# Add the project root to the path so we can import modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Create a simple Flask app for testing
@pytest.fixture
def app():
    app = Flask(__name__)
    
    @app.route('/')
    def home():
        return "Welcome to the test app"
    
    @app.route('/api/data')
    def api_data():
        return {"data": "test data"}
    
    @app.route('/api/submit', methods=['POST'])
    def submit():
        return {"success": True}
    
    @app.route('/about')
    def about():
        return "<h1>About</h1>"
    
    @app.route('/contact')
    def contact():
        return """
        <form>
            <input name="name" type="text">
            <input name="email" type="email">
            <textarea name="message"></textarea>
            <button type="submit">Submit</button>
            <div class="success-message" style="display:none">Thank you for your message</div>
        </form>
        <script>
            document.querySelector('form').addEventListener('submit', function(e) {
                e.preventDefault();
                document.querySelector('.success-message').style.display = 'block';
            });
        </script>
        """
    
    return app

# This fixture provides a Flask test client
@pytest.fixture
def client(app):
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client
