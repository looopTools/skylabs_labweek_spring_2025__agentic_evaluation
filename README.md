# QA Database System

A comprehensive system for QA departments to track test suites, test cases, test run templates, and test results.

## Project Structure

The project is divided into two main directories:
- `backend/`: Contains the FastAPI application, database models, and API endpoints
- `frontend/`: Contains the Vue 3 application for the user interface

## Backend Setup

### Prerequisites
- Python 3.8+
- pip (Python package manager)

### Installation

1. Navigate to the backend directory:
```bash
cd backend
```

2. Create a virtual environment:
```bash
python -m venv venv
```

3. Activate the virtual environment:
- On Linux/Mac:
```bash
source venv/bin/activate
```
- On Windows:
```bash
venv\Scripts\activate
```

4. Install dependencies:
```bash
pip install -r requirements.txt
```

5. Run the development server:
```bash
uvicorn app.main:app --reload
```

The backend API will be available at http://localhost:8000

### API Documentation

Once the backend is running, you can access:
- Interactive API documentation: http://localhost:8000/docs
- Alternative API documentation: http://localhost:8000/redoc

### Common API Tasks (using curl)

#### Get all test suites
```bash
curl -X GET "http://localhost:8000/api/test-suites" -H "accept: application/json"
```

#### Create a new test suite
```bash
curl -X POST "http://localhost:8000/api/test-suites" -H "accept: application/json" -H "Content-Type: application/json" -d '{"id": "UI", "name": "UI Test Suite", "url": "https://example.com/ui-tests", "format": "json", "version": 1, "version_string": "1.0", "is_final": false}'
```

#### Get all test cases
```bash
curl -X GET "http://localhost:8000/api/test-cases" -H "accept: application/json"
```

#### Create a test run
```bash
curl -X POST "http://localhost:8000/api/test-runs" -H "accept: application/json" -H "Content-Type: application/json" -d '{"status": "In Progress", "operator_id": 1}'
```

#### Get all test run templates
```bash
curl -X GET "http://localhost:8000/api/test-run-templates" -H "accept: application/json"
```

#### Create a new test run template
```bash
curl -X POST "http://localhost:8000/api/test-run-templates" -H "accept: application/json" -H "Content-Type: application/json" -d '{"template_id": "REL-2023-Q1", "name": "Release Test Run Q1 2023", "description": "Standard test run for quarterly release", "field": "Release"}'
```

#### Get test cases for a template
```bash
curl -X GET "http://localhost:8000/api/test-run-templates/1/test-cases" -H "accept: application/json"
```

### Database Backup

To backup the database to a JSON file:
```bash
python -m app.tools.backup
```

This will create a backup file in the `backend/backups` directory.

### Database Migration

If the schema changes, you can migrate the database using Alembic:

1. Generate a migration script:
```bash
alembic revision --autogenerate -m "Description of changes"
```

2. Apply the migration:
```bash
alembic upgrade head
```

## Frontend Setup

### Prerequisites
- Node.js (v14+)
- npm or yarn

### Installation

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
# or
yarn install
```

3. Run the development server:
```bash
npm run serve
# or
yarn serve
```

The frontend will be available at http://localhost:8080

### Frontend Features

The frontend provides a user-friendly interface for:
- Managing test suites and test cases
- Creating and using test run templates for different types of testing (Release, Regression, etc.)
- Running tests directly through the interface with the Direct Test Run feature
- Uploading test results from JSON files
- Viewing detailed reports and statistics

## Testing

The project includes comprehensive test suites for both the backend API and frontend components.

### API Testing with pytest

The backend API is tested using pytest. Tests verify that endpoints return the expected responses and handle various input scenarios correctly.

To run the API tests:
```bash
pytest tests/test_api.py -v
```

Key API test features:
- Tests for all major endpoints (GET, POST, PUT, DELETE)
- Validation of response status codes and data structures
- Testing of error handling and edge cases
- Fixtures that provide isolated test environments

### Frontend Testing with Playwright

Frontend tests use Playwright to automate browser interactions and verify UI functionality.

To run the frontend tests:
```bash
pytest tests/test_frontend.py -v
```

Key frontend test features:
- Tests run in real browser environments (Chromium by default)
- Page navigation and URL verification
- Form submission and validation
- Dynamic content updates
- Visual element verification

### Test Configuration

Tests are configured in `pytest.ini` and use fixtures defined in `conftest.py` to set up test environments.

The frontend tests automatically start a local test server during test execution, so no manual server setup is required.

## Using Aider for Development

[Aider](https://github.com/paul-gauthier/aider) is an AI pair programming tool that can help you develop this project further. It uses large language models to understand and modify code based on natural language instructions.

### Setting Up Aider

1. Install Aider:
```bash
pip install aider-chat
```

2. Navigate to your project directory:
```bash
cd qa-database-system
```

3. Start Aider with your preferred LLM:
```bash
aider --openai-api-key YOUR_API_KEY
```

4. For more advanced usage with specific models:
```bash
# Use GPT-4 model
aider --model gpt-4

# Use Claude model
aider --model claude-3-opus-20240229
```

### Key Aider Features

- **Multi-file edits**: Aider can make changes across multiple files in a single operation
- **Git integration**: Automatically commits changes with descriptive commit messages
- **Context awareness**: Understands your entire codebase and maintains context between sessions
- **Code explanation**: Can explain complex parts of your codebase
- **Incremental development**: Build features step by step with natural conversation
- **Debugging assistance**: Help identify and fix bugs in your code

### Using Aider for Development Tasks

Aider is particularly useful for:

- Adding new features to existing components
- Creating new API endpoints
- Implementing new frontend views
- Fixing bugs across multiple files
- Refactoring code

### Common Aider Commands

```
# Get help with available commands
/help

# Add files to the chat context
/add backend/app/models/*.py

# Show which files are in the current chat context
/files

# Create a new file
Create a new file called backend/app/models/test_metric.py

# Commit changes
/commit "Add test metrics model and API endpoints"

# Undo the last edit
/undo

# Exit aider
/exit
```

### Example Development Prompts

```
# Add a new field to a model
Add a 'priority' field to the TestCase model with options 'High', 'Medium', and 'Low'

# Create a new component
Create a new Vue component for displaying test metrics with a bar chart visualization

# Implement a new API endpoint
Add an endpoint for exporting test results as CSV with filtering options

# Fix a bug
Fix the issue where test case results aren't being properly associated with test runs

# Refactor code
Refactor the test run creation process to use a factory pattern

# Add documentation
Add JSDoc comments to all the Vue component methods
```

Aider will understand the project structure and make appropriate changes across files, automatically committing the changes to git with descriptive commit messages.

## Transitioning to Production

### Backend

1. Update the database connection in `backend/app/core/config.py` to use PostgreSQL instead of SQLite.
2. Set up a PostgreSQL database and update the connection string.
3. Run migrations to set up the schema in PostgreSQL.
4. Deploy the backend to your production environment.

### Frontend

1. Build the production version of the frontend:
```bash
cd frontend
npm run build
# or
yarn build
```

2. Deploy the contents of the `frontend/dist` directory to your web server.
