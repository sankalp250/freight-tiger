import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

def test_health():
    res = client.get("/")
    assert res.status_code == 200
    assert res.json()["status"] == "online"

def test_summary():
    res = client.get("/api/summary")
    assert res.status_code == 200
    data = res.json()
    assert data["total_shipments"] == 2940
    assert data["total_corridors"] == 7
    assert data["total_weeks"] == 104
    assert data["total_justified_anomalies"] > 0
    assert data["total_unjustified_anomalies"] > 0

def test_corridors():
    res = client.get("/api/corridors")
    assert res.status_code == 200
    corridors = res.json()
    assert len(corridors) == 7
    routes = [c["route"] for c in corridors]
    assert "Mumbai-Pune" in routes
    assert "Delhi-Jaipur" in routes
    assert "Ahmedabad-Mumbai" in routes

def test_trends():
    res = client.get("/api/trends?route=Mumbai-Pune")
    assert res.status_code == 200
    trends = res.json()
    assert trends["route"] == "Mumbai-Pune"
    assert len(trends["weeks"]) == 104

def test_chat():
    res = client.post("/api/chat", json={"query": "Why did Ahmedabad-Mumbai spike in January 2025?"})
    assert res.status_code == 200
    answer = res.json()
    assert "N002" in answer["citations"]
    assert "festival" in answer["answer"].lower()
