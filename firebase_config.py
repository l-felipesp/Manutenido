# firebase_config.py
# Adapter Firestore REST + Firebase Auth (email/password)
# Uso: primeiro chame sign_in_with_email_and_password(email, password)
# depois get_firestore_client() ou get_firestore_client(id_token=...)

import requests
import time
import datetime
from typing import Optional

# --- CONFIGURAÇÃO: preencha sua API KEY aqui ---
API_KEY = "AIzaSyB1Ak1llqb2_epOM6JuSMNL7mMzQKnOTyo"
PROJECT_ID = "manutenido-c5c18"
BASE_URL = f"https://firestore.googleapis.com/v1/projects/{PROJECT_ID}/databases/(default)/documents"

# Endpoints de Auth REST
AUTH_SIGNIN_URL = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={API_KEY}"
AUTH_REFRESH_URL = f"https://securetoken.googleapis.com/v1/token?key={API_KEY}"

# Estado global de autenticação (em memória)
_auth_state = {
    "id_token": None,
    "refresh_token": None,
    "uid": None,
    "expires_at": None  # epoch seconds
}


# ----------------- AUTENTICAÇÃO -----------------
def sign_in_with_email_and_password(email: str, password: str) -> dict:
    """
    Realiza login com email/senha via Firebase Auth REST.
    Retorna dict com idToken, refreshToken, expiresIn, localId.
    Em caso de erro, lança requests.HTTPError.
    """
    payload = {
        "email": email,
        "password": password,
        "returnSecureToken": True
    }
    r = requests.post(AUTH_SIGNIN_URL, json=payload, timeout=15)
    r.raise_for_status()
    data = r.json()

    # Salva no estado global
    id_token = data.get("idToken")
    refresh_token = data.get("refreshToken")
    expires_in = int(data.get("expiresIn", 3600))
    uid = data.get("localId")

    _auth_state["id_token"] = id_token
    _auth_state["refresh_token"] = refresh_token
    _auth_state["uid"] = uid
    _auth_state["expires_at"] = int(time.time()) + expires_in - 30  # refresh 30s antes

    return data


def register_with_email_and_password(email: str, password: str) -> dict:
    """
    Cria um novo usuário no Firebase Auth (email/senha).
    """
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={API_KEY}"
    payload = {
        "email": email,
        "password": password,
        "returnSecureToken": True
    }
    r = requests.post(url, json=payload, timeout=15)
    r.raise_for_status()
    data = r.json()

    # salva estado de auth
    _auth_state["id_token"] = data.get("idToken")
    _auth_state["refresh_token"] = data.get("refreshToken")
    _auth_state["uid"] = data.get("localId")
    _auth_state["expires_at"] = int(time.time()) + int(data.get("expiresIn", 3600)) - 30

    return data


def refresh_id_token() -> Optional[str]:
    """
    Usa refresh_token para trocar por um novo idToken.
    Retorna novo idToken ou None se falhar.
    """
    refresh_token = _auth_state.get("refresh_token")
    if not refresh_token:
        return None

    payload = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token
    }
    r = requests.post(AUTH_REFRESH_URL, data=payload, timeout=15)
    if r.status_code != 200:
        # falha, limpa auth
        _auth_state["id_token"] = None
        _auth_state["refresh_token"] = None
        _auth_state["expires_at"] = None
        return None

    j = r.json()
    id_token = j["id_token"]
    new_refresh_token = j["refresh_token"]
    expires_in = int(j.get("expires_in", 3600))

    _auth_state["id_token"] = id_token
    _auth_state["refresh_token"] = new_refresh_token
    _auth_state["expires_at"] = int(time.time()) + expires_in - 30

    return id_token


def get_id_token() -> Optional[str]:
    """
    Retorna id_token válido, fazendo refresh se necessário.
    """
    id_token = _auth_state.get("id_token")
    expires_at = _auth_state.get("expires_at") or 0
    now = int(time.time())

    if id_token and now < expires_at:
        return id_token

    # tenta refresh
    return refresh_id_token()


# ----------------- FIRESTORE REST ADAPTER -----------------
class FirestoreRestAdapter:
    def __init__(self, id_token: Optional[str] = None):
        # se id_token for None, o adapter tentará pegar do auth state
        self._id_token = id_token

    def collection(self, name: str):
        return CollectionRef(name, self._id_token)


class CollectionRef:
    def __init__(self, name: str, id_token: Optional[str] = None):
        self.name = name
        self.filters = []  # lista de tuplas (field, operator, value)
        self._id_token = id_token

    def _headers(self):
        token = self._id_token or get_id_token()
        headers = {"Content-Type": "application/json"}
        if token:
            headers["Authorization"] = f"Bearer {token}"
        return headers

    def add(self, data: dict):
        """
        Adiciona um documento na coleção.
        Retorna DocumentRef (com id) ou None em caso de falha.
        """
        firestore_data = {"fields": to_firestore_json(data)}
        url = f"{BASE_URL}/{self.name}"
        r = requests.post(url, json=firestore_data, headers=self._headers(), timeout=15)
        try:
            r.raise_for_status()
        except requests.HTTPError:
            print(f"[Firestore add] erro {r.status_code}: {r.text}")
            return None
        return DocumentRef(r.json())

    def where(self, field: str, operator: str, value):
        """
        Armazena filtro para aplicar no client (simples).
        Operadores suportados aqui: '=='
        """
        self.filters.append((field, operator, value))
        return self

    def stream(self):
        """
        Busca documentos da coleção (lista simples).
        Observação: para poucos documentos funciona; para muitos, paginar é necessário.
        """
        url = f"{BASE_URL}/{self.name}"
        params = {"pageSize": 1000}
        r = requests.get(url, params=params, headers=self._headers(), timeout=15)
        docs = []
        if r.status_code != 200:
            # imprime e retorna vazio
            print(f"[Firestore stream] erro {r.status_code}: {r.text}")
            return docs

        data = r.json()
        if "documents" not in data:
            return docs

        for d in data["documents"]:
            doc_id = d["name"].split("/")[-1]
            fields = from_firestore_json(d.get("fields", {}))

            # aplica filtros client-side
            passou = True
            for f_field, f_op, f_val in self.filters:
                val_no_banco = fields.get(f_field)
                if f_op == "==" and val_no_banco != f_val:
                    passou = False
                    break
            if passou:
                docs.append(DocumentSnapshot(doc_id, fields))
        return docs


class DocumentRef:
    def __init__(self, data):
        # tenta pegar o ID da resposta
        self.id = data.get("name", "").split("/")[-1] if data else "unknown"


class DocumentSnapshot:
    def __init__(self, doc_id, data):
        self.id = doc_id
        self._data = data

    def to_dict(self):
        return self._data


# ----------------- HELPERS DE CONVERSÃO -----------------
def to_firestore_json(data: dict) -> dict:
    """Converte dict Python -> Firestore JSON 'fields'"""
    fields = {}
    for k, v in data.items():
        if v is None:
            # ignora ou salva vazio como nullValue
            fields[k] = {"nullValue": None}
        elif isinstance(v, bool):
            fields[k] = {"booleanValue": v}
        elif isinstance(v, int):
            fields[k] = {"integerValue": str(v)}
        elif isinstance(v, float):
            fields[k] = {"doubleValue": v}
        elif isinstance(v, datetime.datetime):
            # firestore espera um RFC3339
            fields[k] = {"timestampValue": v.isoformat() + "Z"}
        elif isinstance(v, list):
            # simplificação: assume lista de strings/ints
            values = []
            for x in v:
                if isinstance(x, bool):
                    values.append({"booleanValue": x})
                elif isinstance(x, int):
                    values.append({"integerValue": str(x)})
                elif isinstance(x, float):
                    values.append({"doubleValue": x})
                elif isinstance(x, datetime.datetime):
                    values.append({"timestampValue": x.isoformat() + "Z"})
                else:
                    values.append({"stringValue": str(x)})
            fields[k] = {"arrayValue": {"values": values}}
        else:
            fields[k] = {"stringValue": str(v)}
    return fields


def from_firestore_json(fields: dict) -> dict:
    """Converte Firestore JSON fields -> dict Python"""
    data = {}
    for k, v in fields.items():
        if "stringValue" in v:
            data[k] = v["stringValue"]
        elif "integerValue" in v:
            try:
                data[k] = int(v["integerValue"])
            except:
                data[k] = v["integerValue"]
        elif "doubleValue" in v:
            data[k] = float(v["doubleValue"])
        elif "booleanValue" in v:
            data[k] = v["booleanValue"]
        elif "timestampValue" in v:
            data[k] = v["timestampValue"]
        elif "arrayValue" in v:
            vals = v["arrayValue"].get("values", [])
            # pega primeiro tipo de cada entry
            out = []
            for entry in vals:
                if "stringValue" in entry:
                    out.append(entry["stringValue"])
                elif "integerValue" in entry:
                    out.append(int(entry["integerValue"]))
                elif "doubleValue" in entry:
                    out.append(float(entry["doubleValue"]))
                elif "booleanValue" in entry:
                    out.append(entry["booleanValue"])
                else:
                    out.append(list(entry.values())[0])
            data[k] = out
        elif "nullValue" in v:
            data[k] = None
        else:
            # fallback: pega primeiro valor que existir
            data[k] = list(v.values())[0] if isinstance(v, dict) and v else v
    return data


# ----------------- FUNÇÕES PÚBLICAS -----------------
def get_firestore_client(id_token: Optional[str] = None) -> FirestoreRestAdapter:
    return FirestoreRestAdapter(id_token=id_token)

