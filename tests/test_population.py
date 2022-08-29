from fastapi.testclient import TestClient
from productizer.main import app

client = TestClient(app)


def test_population():
    response = client.post(
        "/test/Figure/Population", json={"city": "Tampere", "year": 2021}
    )
    assert response.status_code == 200

    # Check all expected keys found in the response
    responseKeys = response.json().keys()
    expectedAttrs = ["population", "description", "sourceName", "updatedAt"]
    assert all(attr in responseKeys for attr in expectedAttrs)
