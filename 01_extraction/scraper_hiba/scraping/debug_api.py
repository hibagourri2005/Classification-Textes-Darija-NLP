"""
Debug : trouve le bon nom de parametre pour get_ig_user_posts.php
"""
import requests, json
import os, sys
try:  # charge automatiquement le fichier .env s'il existe (pip install python-dotenv)
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


def _env(name):
    value = os.environ.get(name)
    if not value:
        sys.exit(f"Variable d'environnement {name} manquante (voir .env.example à la racine du dépôt)")
    return value


RAPIDAPI_KEY  = _env("RAPIDAPI_KEY")
RAPIDAPI_HOST = "instagram-scraper-stable-api.p.rapidapi.com"
BASE_URL      = f"https://{RAPIDAPI_HOST}"

HEADERS_POST = {
    "x-rapidapi-key":  RAPIDAPI_KEY,
    "x-rapidapi-host": RAPIDAPI_HOST,
    "Content-Type":    "application/x-www-form-urlencoded",
}

TEST_USER = "dr.abderrahimznt"

# Tester tous les noms de parametres possibles
params_to_try = [
    {"user_name":    TEST_USER},
    {"ig_username":  TEST_USER},
    {"user":         TEST_USER},
    {"account":      TEST_USER},
    {"handle":       TEST_USER},
    {"name":         TEST_USER},
    {"ig_user":      TEST_USER},
    {"screen_name":  TEST_USER},
    {"username_or_id_or_url": TEST_USER},
    {"target":       TEST_USER},
    {"userid":       TEST_USER},
]

print("Recherche du bon nom de parametre pour /get_ig_user_posts.php\n")
for payload in params_to_try:
    r = requests.post(
        f"{BASE_URL}/get_ig_user_posts.php",
        headers=HEADERS_POST,
        data=payload,
        timeout=15
    )
    body = r.json()
    has_error = "error" in body or "message" in body
    icon = "ERREUR" if has_error else "OK !!!"
    param_name = list(payload.keys())[0]
    print(f"  [{icon}] param='{param_name:<30}' -> {body.get('error') or body.get('message') or str(list(body.keys()))[:80]}")
    if not has_error:
        print(f"\n  SUCCES avec param='{param_name}' !")
        print(json.dumps(body, indent=2, ensure_ascii=False)[:1000])
        break