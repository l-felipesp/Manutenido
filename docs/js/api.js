const API_BASE_URL = "https://manutenido-api.onrender.com";

async function apiGet(path) {
    try {
        const res = await fetch(`${API_BASE_URL}${path}`);
        if (!res.ok) {
            throw new Error(`Erro ${res.status}`);
        }
        return await res.json();
    } catch (err) {
        console.error("API GET erro:", err);
        return { error: err.message };
    }
}

async function apiPost(path, data) {
    try {
        const res = await fetch(`${API_BASE_URL}${path}`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(data),
        });
        if (!res.ok) {
            throw new Error(`Erro ${res.status}`);
        }
        return await res.json();
    } catch (err) {
        console.error("API POST erro:", err);
        return { error: err.message };
    }
}
