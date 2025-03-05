from playwright.sync_api import sync_playwright

def run(playwright):
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()
    page.goto("http://localhost:5000")
    # other actions...
    browser.close()

with sync_playwright() as playwright:
    run(playwright)
