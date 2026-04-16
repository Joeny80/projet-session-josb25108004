function showMessage(text, type) {
    const msgDiv = document.getElementById("message");
    if (!msgDiv) {
        return;
    }

    msgDiv.textContent = text;
    msgDiv.className = `message ${type}`;
    msgDiv.style.display = "block";
}

function nettoyerMessage() {
    const msgDiv = document.getElementById("message");
    if (!msgDiv) {
        return;
    }

    msgDiv.textContent = "";
    msgDiv.className = "message";
    msgDiv.style.display = "none";
}

function validerAvantEnvoi(payload) {
    const champs = [
        payload.nom_etablissement,
        payload.adresse,
        payload.ville,
        payload.date_visite,
        payload.nom_prenom,
        payload.description
    ];

    if (champs.some((v) => !v || !String(v).trim())) {
        showMessage("Veuillez remplir tous les champs obligatoires.", "error");
        return false;
    }

    const dateRegex = /^\d{4}-\d{2}-\d{2}$/;
    if (!dateRegex.test(payload.date_visite)) {
        showMessage("Le format de la date est invalide. Utilisez AAAA-MM-JJ.", "error");
        return false;
    }

    const dateVisite = new Date(`${payload.date_visite}T00:00:00`);
    const aujourdHui = new Date();
    aujourdHui.setHours(0, 0, 0, 0);

    if (dateVisite > aujourdHui) {
        showMessage("La date de visite ne peut pas être dans le futur.", "error");
        return false;
    }

    if (payload.description.trim().length < 10) {
        showMessage("La description doit contenir au moins 10 caractères.", "error");
        return false;
    }

    return true;
}

function construirePayload() {
    return {
        nom_etablissement: document.getElementById("in-nom-etablissement").value.trim(),
        adresse: document.getElementById("in-adresse").value.trim(),
        ville: document.getElementById("in-ville").value.trim(),
        date_visite: document.getElementById("in-date-visite").value,
        nom_prenom: document.getElementById("in-nom-prenom").value.trim(),
        description: document.getElementById("in-description").value.trim()
    };
}

async function soumettrePlainte(event) {
    event.preventDefault();
    nettoyerMessage();

    const btn = document.getElementById("submit-btn");
    if (btn) {
        btn.disabled = true;
    }

    const payload = construirePayload();

    if (!validerAvantEnvoi(payload)) {
        if (btn) {
            btn.disabled = false;
        }
        return;
    }

    try {
        const resp = await fetch("/api/inspection", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(payload)
        });

        let data = {};
        try {
            data = await resp.json();
        } catch {
            data = {};
        }

        if (resp.status === 201) {
            showMessage("Plainte envoyée avec succès.", "success");
            const form = document.getElementById("plainte-form");
            if (form) {
                form.reset();
            }
        } else {
            const msg = data.erreur || "Erreur lors de la soumission.";
            showMessage(msg, "error");
        }
    } catch (err) {
        showMessage("Erreur réseau lors de la soumission.", "error");
    } finally {
        if (btn) {
            btn.disabled = false;
        }
    }
}

document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("plainte-form");
    if (form) {
        form.addEventListener("submit", soumettrePlainte);
    }
});