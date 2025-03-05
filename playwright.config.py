from playwright.sync_api import sync_playwright

def run(playwright):
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()
    
    # This is just a configuration file, actual tests are in test_frontend.py
    # The tests will start their own server
    
    browser.close()

if __name__ == "__main__":
    with sync_playwright() as playwright:
        run(playwright)
