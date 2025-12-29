async function login(email, password) {
    const res = await apiPost("/auth/login", { email, password });

    if (res.error || res.detail) {
        return null;
    }

    localStorage.setItem("user_id", res.localId);
    localStorage.setItem("id_token", res.idToken);

    return res;
}

async function register(email, password) {
    const res = await apiPost("/auth/register", { email, password });

    if (res.error || res.detail) {
        return null;
    }

    localStorage.setItem("user_id", res.localId);
    localStorage.setItem("id_token", res.idToken);

    return res;
}

function logout() {
    localStorage.clear();
    window.location.href = "login.html";
}
