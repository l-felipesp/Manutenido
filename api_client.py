# api_client.py
import requests
import os

# API do servidor (mude para IP do seu PC quando testar no celular)
API_BASE_URL = os.environ.get("MANUTENIDO_API_URL", "http://192.168.1.115:8000")

def _post(path: str, json_payload: dict):
    url = f"{API_BASE_URL}{path}"
    try:
        r = requests.post(url, json=json_payload, timeout=15)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        print(f"[api_client] POST {url} erro:", e)
        return {"error": str(e)}

def _get(path: str):
    url = f"{API_BASE_URL}{path}"
    try:
        r = requests.get(url, timeout=15)
        r.raise_for_status()
        # Alguns endpoints retornam {} vazio quando não acham; mantemos isso
        return r.json()
    except Exception as e:
        print(f"[api_client] GET {url} erro:", e)
        return {"error": str(e)}


def auth_login(email: str, password: str):
    return _post("/auth/login", {"email": email, "password": password})

def auth_register(email: str, password: str):
    return _post("/auth/register", {"email": email, "password": password})

def list_vehicles(user_id: str):
    return _get(f"/vehicles/{user_id}")

def add_vehicle(data: dict):
    return _post("/vehicles", data)

def find_vehicle_by_plate(plate: str):
    return _get(f"/vehicles/plate/{plate}")

def list_events(vehicle_id: str):
    return _get(f"/events/{vehicle_id}")

def add_event(data: dict):
    return _post("/events", data)
