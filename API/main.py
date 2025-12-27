from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import firebase_admin
from firebase_admin import credentials, firestore
import requests
import os

# CONFIG
API_KEY = "AIzaSyB1Ak1llqb2_epOM6JuSMNL7mMzQKnOTyo"
SERVICE_ACCOUNT_PATH = "serviceAccountKey.json"
PROJECT_ID = "manutenido-c5c18"

if not os.path.exists(SERVICE_ACCOUNT_PATH):
    raise RuntimeError("Coloque serviceAccountKey.json na pasta api/ antes de rodar a API")

cred = credentials.Certificate(SERVICE_ACCOUNT_PATH)
firebase_admin.initialize_app(cred)
db = firestore.client()

app = FastAPI(title="Manutenido API")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

IDENTITY_SIGNIN = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={API_KEY}"
IDENTITY_SIGNUP = f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={API_KEY}"


@app.post("/auth/login")
def login(payload: dict):
    email = payload.get("email")
    password = payload.get("password")
    if not email or not password:
        raise HTTPException(status_code=400, detail="email/password required")

    r = requests.post(IDENTITY_SIGNIN, json={"email": email, "password": password, "returnSecureToken": True}, timeout=15)
    if r.status_code != 200:
        raise HTTPException(status_code=401, detail=r.json())
    return r.json()


@app.post("/auth/register")
def register(payload: dict):
    email = payload.get("email")
    password = payload.get("password")
    if not email or not password:
        raise HTTPException(status_code=400, detail="email/password required")

    r = requests.post(IDENTITY_SIGNUP, json={"email": email, "password": password, "returnSecureToken": True}, timeout=15)
    if r.status_code != 200:
        raise HTTPException(status_code=400, detail=r.json())
    return r.json()


@app.get("/vehicles/{user_id}")
def get_vehicles(user_id: str):
    try:
        docs = db.collection("vehicles").where("user_id", "==", user_id).stream()
        out = []
        for d in docs:
            doc = d.to_dict()
            doc["id"] = d.id
            out.append(doc)
        return out
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/vehicles")
def add_vehicle(payload: dict):
    try:
        db.collection("vehicles").add(payload)
        return {"ok": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/vehicles/plate/{plate}")
def get_vehicle_by_plate(plate: str):
    try:
        docs = db.collection("vehicles").where("placa", "==", plate).stream()
        for d in docs:
            doc = d.to_dict()
            doc["id"] = d.id
            return doc
        return {}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/events/{vehicle_id}")
def get_events(vehicle_id: str):
    try:
        docs = db.collection("events").where("vehicle_id", "==", vehicle_id).stream()
        out = []
        for d in docs:
            doc = d.to_dict()
            doc["id"] = d.id
            out.append(doc)
        return out
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/events")
def add_event(payload: dict):
    try:
        db.collection("events").add(payload)
        return {"ok": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
