import pytest
from playwright.sync_api import Page, expect
import flask
import multiprocessing
import time
import os

# Setup a Flask server for testing
@pytest.fixture(scope="module")
def http_server():
    # Create a simple Flask app for testing
    app = flask.Flask(__name__)
    
    @app.route('/')
    def home():
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <title>My Web Application</title>
        </head>
        <body>
            <h1>Welcome</h1>
            <a href="/about">About</a>
        </body>
        </html>
        """
    
    @app.route('/about')
    def about():
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <title>About</title>
        </head>
        <body>
            <h1>About</h1>
        </body>
        </html>
        """
    
    @app.route('/contact')
    def contact():
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Contact</title>
        </head>
        <body>
            <h1>Contact</h1>
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
        </body>
        </html>
        """
    
    # Start the server in a separate process
    host = '127.0.0.1'
    port = 5000
    
    def run_app():
        app.run(host=host, port=port, debug=False)
    
    server = multiprocessing.Process(target=run_app)
    server.start()
    
    # Give the server time to start
    time.sleep(1)
    
    yield f"http://{host}:{port}"
    
    # Teardown - stop the server
    server.terminate()
    server.join()

# Update tests to use the http_server fixture
def test_homepage_title(page: Page, http_server):
    """Test that the homepage has the correct title."""
    page.goto(f"{http_server}")
    expect(page).to_have_title("My Web Application")

def test_homepage_content(page: Page, http_server):
    """Test that the homepage contains expected content."""
    page.goto(f"{http_server}")
    expect(page.locator("h1")).to_contain_text("Welcome")

def test_navigation(page: Page, http_server):
    """Test navigation between pages."""
    page.goto(f"{http_server}")
    page.click("text=About")
    expect(page).to_have_url(f"{http_server}/about")
    expect(page.locator("h1")).to_contain_text("About")

def test_form_submission(page: Page, http_server):
    """Test form submission."""
    page.goto(f"{http_server}/contact")
    page.fill("input[name='name']", "Test User")
    page.fill("input[name='email']", "test@example.com")
    page.fill("textarea[name='message']", "This is a test message")
    page.click("button[type='submit']")
    
    # Check for success message
    success_message = page.locator(".success-message")
    expect(success_message).to_be_visible()
    expect(success_message).to_contain_text("Thank you for your message")
