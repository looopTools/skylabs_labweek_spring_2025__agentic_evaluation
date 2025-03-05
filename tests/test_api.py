import pytest
import json

def test_home_endpoint(client):
    """Test the home endpoint returns a 200 status code."""
    response = client.get('/')
    assert response.status_code == 200

def test_api_endpoint(client):
    """Test the API endpoint returns expected data."""
    response = client.get('/api/data')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'data' in data

def test_post_endpoint(client):
    """Test a POST endpoint with JSON data."""
    test_data = {'key': 'value'}
    response = client.post(
        '/api/submit',
        data=json.dumps(test_data),
        content_type='application/json'
    )
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'success' in data
