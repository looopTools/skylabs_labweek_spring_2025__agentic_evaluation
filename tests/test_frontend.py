import pytest
from playwright.sync_api import Page, expect

def test_homepage_title(page: Page):
    """Test that the homepage has the correct title."""
    page.goto("http://localhost:5000")
    expect(page).to_have_title("My Web Application")

def test_homepage_content(page: Page):
    """Test that the homepage contains expected content."""
    page.goto("http://localhost:5000")
    expect(page.locator("h1")).to_contain_text("Welcome")

def test_navigation(page: Page):
    """Test navigation between pages."""
    page.goto("http://localhost:5000")
    page.click("text=About")
    expect(page).to_have_url("http://localhost:5000/about")
    expect(page.locator("h1")).to_contain_text("About")

def test_form_submission(page: Page):
    """Test form submission."""
    page.goto("http://localhost:5000/contact")
    page.fill("input[name='name']", "Test User")
    page.fill("input[name='email']", "test@example.com")
    page.fill("textarea[name='message']", "This is a test message")
    page.click("button[type='submit']")
    
    # Check for success message
    success_message = page.locator(".success-message")
    expect(success_message).to_be_visible()
    expect(success_message).to_contain_text("Thank you for your message")
