from app import appfrom app test_home():
    client = app.test_client()
    response = client.get('/')
    assert response.status_code == 200
