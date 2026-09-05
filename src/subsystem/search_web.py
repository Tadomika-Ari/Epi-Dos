import os
import requests

def search_web(query: str) -> str:
    api_key = os.getenv("NEWSAPI_KEY")
    if not api_key:
        return "Erreur : clé NEWSAPI_KEY manquante dans les variables d'environnement."

    mots_generaux = ["actualité", "actualités", "info", "infos", "news", "dernières", "nouvelles"]
    is_general = any(mot in query.lower() for mot in mots_generaux)
    q = "France" if is_general else query

    try:
        resp = requests.get(
            "https://newsapi.org/v2/everything",
            params={
                "q": q,
                "language": "fr",
                "sortBy": "publishedAt",
                "pageSize": 5,
                "apiKey": api_key,
            },
            timeout=8,
        )
        data = resp.json()

        if data.get("status") != "ok":
            return f"Erreur API actualités : {data.get('message', 'inconnue')}"

        articles = data.get("articles", [])
        if not articles:
            return "Aucun résultat trouvé pour cette recherche."

        lignes = []
        for a in articles:
            titre = a.get("title", "").strip()
            source = a.get("source", {}).get("name", "")
            description = (a.get("description") or "").strip()
            if titre:
                ligne = f"- {titre} ({source})"
                if description:
                    ligne += f" : {description}"
                lignes.append(ligne)

        return "\n".join(lignes) if lignes else "Aucun résultat exploitable trouvé."

    except requests.exceptions.RequestException as e:
        return f"Erreur réseau lors de la recherche : {e}"