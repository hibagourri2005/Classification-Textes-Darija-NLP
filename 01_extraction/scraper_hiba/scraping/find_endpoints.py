"""
Script de detection des vrais endpoints de l'API RockSolid.
Lancer ce script AVANT instagram_scraper_final.py
Il teste tous les noms possibles et vous dit lequel fonctionne.
"""
import requests
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
HEADERS = {
    "x-rapidapi-key":  RAPIDAPI_KEY,
    "x-rapidapi-host": RAPIDAPI_HOST,
}

TEST_USERNAME  = "dr.abderrahimznt"
TEST_MEDIACODE = "DLUWkieNc0u"   # code vu dans votre capture

# ── Endpoints possibles pour GET POSTS D'UN COMPTE ──────────────
POSTS_ENDPOINTS = [
    ("GET", "/get_ig_user_posts.php",          {"username": TEST_USERNAME}),
    ("GET", "/get_ig_user_media.php",           {"username": TEST_USERNAME}),
    ("GET", "/get_user_posts.php",              {"username": TEST_USERNAME}),
    ("GET", "/get_user_media.php",              {"username": TEST_USERNAME}),
    ("GET", "/get_ig_user_reels.php",           {"username": TEST_USERNAME}),
    ("GET", "/get_user_reels.php",              {"username": TEST_USERNAME}),
    ("GET", "/get_ig_posts.php",                {"username": TEST_USERNAME}),
    ("GET", "/v1/posts",                        {"username": TEST_USERNAME}),
    ("GET", "/get_user_timeline.php",           {"username": TEST_USERNAME}),
    ("GET", "/user_posts.php",                  {"username": TEST_USERNAME}),
    ("GET", "/get_profile_posts.php",           {"username": TEST_USERNAME}),
    ("GET", "/get_ig_profile.php",              {"username": TEST_USERNAME}),
    ("POST","/get_ig_user_posts.php",           {"username": TEST_USERNAME}),
    ("POST","/get_ig_user_media_v2.php",        {"username": TEST_USERNAME}),
    ("POST","/get_user_posts.php",              {"username": TEST_USERNAME}),
]

# ── Endpoints possibles pour GET COMMENTS ──────────────────────
COMMENTS_ENDPOINTS = [
    ("GET", "/get_post_comments.php",           {"media_code": TEST_MEDIACODE, "sort_order": "popular"}),
    ("GET", "/get_ig_post_comments.php",        {"media_code": TEST_MEDIACODE}),
    ("GET", "/get_media_comments.php",          {"media_code": TEST_MEDIACODE}),
    ("POST","/get_ig_media_comments_v2.php",    {"media_code": TEST_MEDIACODE}),
    ("POST","/get_post_comments.php",           {"media_code": TEST_MEDIACODE}),
]

def test_endpoint(method, path, params):
    url = BASE_URL + path
    try:
        if method == "GET":
            r = requests.get(url, headers=HEADERS, params=params, timeout=10)
        else:
            r = requests.post(url, headers=HEADERS, data=params, timeout=10)
        return r.status_code, r.text[:200]
    except Exception as e:
        return 0, str(e)

print("=" * 60)
print("  TEST ENDPOINTS — GET USER POSTS")
print("=" * 60)
for method, path, params in POSTS_ENDPOINTS:
    status, body = test_endpoint(method, path, params)
    icon = "✅" if status == 200 else "❌"
    print(f"{icon} [{method}] {path:<45} -> {status}")
    if status == 200:
        print(f"   REPONSE : {body[:150]}")

print("\n" + "=" * 60)
print("  TEST ENDPOINTS — GET COMMENTS")
print("=" * 60)
for method, path, params in COMMENTS_ENDPOINTS:
    status, body = test_endpoint(method, path, params)
    icon = "✅" if status == 200 else "❌"
    print(f"{icon} [{method}] {path:<45} -> {status}")
    if status == 200:
        print(f"   REPONSE : {body[:150]}")

print("\nCopiez les endpoints en ✅ et envoyez-les !")