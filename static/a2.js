let nomOriginalModif = "";
let derniereRechercheDu = "";
let derniereRechercheAu = "";

function afficherMessageDans(elementId, texte, type = "error") {
    const container = document.getElementById(elementId);
    if (!container) {
        return;
    }

    container.innerHTML = `<div class="message ${type}">${texte}</div>`;
}

function echapperHtml(valeur) {
    return String(valeur ?? "")
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

function obtenirValeur(id) {
    const element = document.getElementById(id);
    return element ? element.value.trim() : "";
}

function rechercherParDates() {
    const du = obtenirValeur("date-du");
    const au = obtenirValeur("date-au");
    const resultats = document.getElementById("resultats-a5");

    if (!du || !au) {
        afficherMessageDans("resultats-a5", "Veuillez sélectionner les deux dates.");
        return;
    }

    if (du > au) {
        afficherMessageDans("resultats-a5", "La date « Du » doit être antérieure ou égale à la date « Au ».");
        return;
    }

    derniereRechercheDu = du;
    derniereRechercheAu = au;

    fetch(`/contrevenants?du=${encodeURIComponent(du)}&au=${encodeURIComponent(au)}`)
        .then((response) => response.json())
        .then((data) => {
            afficherResultatsA5(data, du, au);
        })
        .catch(() => {
            if (resultats) {
                resultats.innerHTML = '<div class="message error">Erreur lors de la recherche.</div>';
            }
        });
}

function afficherResultatsA5(data, du, au) {
    const container = document.getElementById("resultats-a5");

    if (!container) {
        return;
    }

    if (!Array.isArray(data) || data.length === 0) {
        container.innerHTML = `
            <div class="no-results">
                <h2>Aucun résultat</h2>
                <p>Aucune contravention trouvée pour cette période.</p>
            </div>
        `;
        return;
    }

    const compteur = {};

    data.forEach((contravention) => {
        const nom = contravention.con_etablissement || "Inconnu";
        compteur[nom] = (compteur[nom] || 0) + 1;
    });

    const titre = `
        <h3>Résultats du ${echapperHtml(du)} au ${echapperHtml(au)}</h3>
        <div class="result-count">${Object.keys(compteur).length} établissement(s) trouvé(s)</div>
    `;

    let html = `
        ${titre}
        <div class="table-wrap">
            <table>
                <thead>
                    <tr>
                        <th>Établissement</th>
                        <th>Nombre de contraventions</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>
    `;

    Object.entries(compteur).forEach(([nom, count]) => {
        const nomSecurise = echapperHtml(nom);

        html += `
            <tr>
                <td>${nomSecurise}</td>
                <td>${count}</td>
                <td>
                    <button type="button" class="btn-modifier" data-nom="${nomSecurise}">Modifier</button>
                    <button type="button" class="btn-supprimer" data-nom="${nomSecurise}">Supprimer</button>
                </td>
            </tr>
        `;
    });

    html += `
                </tbody>
            </table>
        </div>
    `;

    container.innerHTML = html;

    container.querySelectorAll(".btn-modifier").forEach((btn) => {
        btn.addEventListener("click", () => ouvrirModal(btn.dataset.nom));
    });

    container.querySelectorAll(".btn-supprimer").forEach((btn) => {
        btn.addEventListener("click", () => supprimerContrevenant(btn.dataset.nom));
    });
}

function chargerRestaurants() {
    fetch("/api/restaurants")
        .then((response) => response.json())
        .then((data) => {
            const select = document.getElementById("select-restaurant")
                || document.getElementById("restaurant-select");

            if (!select || !Array.isArray(data)) {
                return;
            }

            select.innerHTML = '<option value="">-- Choisir un restaurant --</option>';

            data.forEach((item) => {
                if (!item.con_etablissement) {
                    return;
                }

                const option = document.createElement("option");
                option.value = item.con_etablissement;
                option.textContent = item.con_etablissement;
                select.appendChild(option);
            });
        })
        .catch(() => {
            afficherMessageDans("resultats-a6", "Erreur lors du chargement des restaurants.");
        });
}

function rechercherRestaurant() {
    const select = document.getElementById("select-restaurant")
        || document.getElementById("restaurant-select");
    const restaurant = select ? select.value.trim() : "";

    if (!restaurant) {
        afficherMessageDans("resultats-a6", "Veuillez sélectionner un restaurant.");
        return;
    }

    fetch(`/api/contraventions?restaurant=${encodeURIComponent(restaurant)}`)
        .then((response) => response.json())
        .then((data) => {
            afficherResultatsA6(data, restaurant);
        })
        .catch(() => {
            afficherMessageDans("resultats-a6", "Erreur lors de la recherche.");
        });
}

function afficherResultatsA6(data, restaurant) {
    const container = document.getElementById("resultats-a6");

    if (!container) {
        return;
    }

    if (!Array.isArray(data) || data.length === 0) {
        container.innerHTML = `
            <div class="no-results">
                <h2>Aucune infraction</h2>
                <p>Aucune infraction trouvée pour ce restaurant.</p>
            </div>
        `;
        return;
    }

    let html = `
        <h3>Infractions — ${echapperHtml(restaurant)}</h3>
        <div class="result-count">${data.length} infraction(s) trouvée(s)</div>
        <div class="table-wrap">
            <table>
                <thead>
                    <tr>
                        <th>Date</th>
                        <th>Description</th>
                        <th>Montant</th>
                        <th>Adresse</th>
                    </tr>
                </thead>
                <tbody>
    `;

    data.forEach((c) => {
        html += `
            <tr>
                <td>${echapperHtml(c.con_date || "N/A")}</td>
                <td>${echapperHtml(c.con_description || "N/A")}</td>
                <td>${echapperHtml(c.con_montant ?? "N/A")}</td>
                <td>${echapperHtml(c.con_adresse || "N/A")}</td>
            </tr>
        `;
    });

    html += `
                </tbody>
            </table>
        </div>
    `;

    container.innerHTML = html;
}

function ouvrirModal(nom) {
    nomOriginalModif = nom;

    const modal = document.getElementById("modal-modifier");
    const champNom = document.getElementById("nouveau-nom");
    const champProprietaire = document.getElementById("nouveau-proprietaire");
    const champUser = document.getElementById("auth-user");
    const champPass = document.getElementById("auth-pass");

    if (champNom) {
        champNom.value = nom;
    }

    if (champProprietaire) {
        champProprietaire.value = "";
    }

    if (champUser) {
        champUser.value = "admin";
    }

    if (champPass) {
        champPass.value = "";
    }

    if (modal) {
        modal.style.display = "block";
    }
}

function fermerModal() {
    const modal = document.getElementById("modal-modifier");
    if (modal) {
        modal.style.display = "none";
    }
    nomOriginalModif = "";
}

function confirmerModification() {
    const nouveauNom = obtenirValeur("nouveau-nom");
    const nouveauProprietaire = obtenirValeur("nouveau-proprietaire");
    const user = obtenirValeur("auth-user") || "admin";
    const pass = document.getElementById("auth-pass")
        ? document.getElementById("auth-pass").value
        : "";

    if (!nomOriginalModif) {
        alert("Aucun contrevenant sélectionné.");
        return;
    }

    if (!nouveauNom || !nouveauProprietaire) {
        alert("Veuillez remplir tous les champs.");
        return;
    }

    fetch(`/api/contrevenant/${encodeURIComponent(nomOriginalModif)}`, {
        method: "PUT",
        headers: {
            "Content-Type": "application/json",
            "Authorization": `Basic ${btoa(`${user}:${pass}`)}`
        },
        body: JSON.stringify({
            nouveau_nom: nouveauNom,
            nouveau_proprietaire: nouveauProprietaire
        })
    })
        .then((response) => {
            if (response.status === 401) {
                alert("Identifiants incorrects.");
                throw new Error("Unauthorized");
            }
            return response.json();
        })
        .then(() => {
            alert("Contrevenant modifié avec succès.");
            fermerModal();

            if (derniereRechercheDu && derniereRechercheAu) {
                rechercherParDates();
            }
        })
        .catch((error) => {
            if (error.message !== "Unauthorized") {
                alert("Erreur lors de la modification.");
            }
        });
}

function supprimerContrevenant(nom) {
    if (!confirm(`Voulez-vous vraiment supprimer « ${nom} » ?`)) {
        return;
    }

    const user = prompt("Identifiant admin :", "admin") || "";
    const pass = prompt("Mot de passe :") || "";

    fetch(`/api/contrevenant/${encodeURIComponent(nom)}`, {
        method: "DELETE",
        headers: {
            "Authorization": `Basic ${btoa(`${user}:${pass}`)}`
        }
    })
        .then((response) => {
            if (response.status === 401) {
                alert("Identifiants incorrects.");
                throw new Error("Unauthorized");
            }
            return response.json();
        })
        .then(() => {
            alert("Contrevenant supprimé avec succès.");

            if (derniereRechercheDu && derniereRechercheAu) {
                rechercherParDates();
            }
        })
        .catch((error) => {
            if (error.message !== "Unauthorized") {
                alert("Erreur lors de la suppression.");
            }
        });
}

document.addEventListener("DOMContentLoaded", () => {
    const btnA5 = document.getElementById("btn-a5");
    const btnA6 = document.getElementById("btn-a6");
    const btnConfirm = document.getElementById("btn-confirm-modif");
    const btnCancel = document.getElementById("btn-cancel-modif");

    if (btnA5) {
        btnA5.addEventListener("click", rechercherParDates);
    }

    if (btnA6) {
        btnA6.addEventListener("click", rechercherRestaurant);
    }

    if (btnConfirm) {
        btnConfirm.addEventListener("click", confirmerModification);
    }

    if (btnCancel) {
        btnCancel.addEventListener("click", fermerModal);
    }

    chargerRestaurants();
});