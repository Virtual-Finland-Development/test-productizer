from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)


def test_population():
    response = client.post("/test/Figure/Population", json={"city": "Tampere", "year": 2021})
    assert response.status_code == 200
    assert response.json() == {
        "population": 244223,
        "description": "Väkiluku, Tampere, 2021",
        "sourceName": "Tilastokeskus",
        "updatedAt": "2022-06-17T11:52:00Z",
    }
