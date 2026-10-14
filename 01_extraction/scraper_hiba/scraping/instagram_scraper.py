"""
=====================================================================
 DARIJA PROJECT — Scraping Instagram (Version Anti-Ban)
 Identifiants lus depuis les variables d'environnement (.env)
=====================================================================
"""

import csv
import json
import time
import random
import logging
from pathlib import Path
from datetime import datetime

import instaloader

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

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────
#  CREDENTIALS
# ─────────────────────────────────────────────
INSTAGRAM_USERNAME = _env("INSTAGRAM_USERNAME")
INSTAGRAM_PASSWORD = _env("INSTAGRAM_PASSWORD")

# ─────────────────────────────────────────────
#  SOURCES PAR CATEGORIE
# ─────────────────────────────────────────────
INSTAGRAM_ACCOUNTS = {
    "Medical":       ["dr.abderrahimznt", "dr_siham_mansouri"],
    "Business":      ["youssefakalal", "hamzaboulfeth"],
    "Sports":        ["ingenieur.fitness", "equipedumaroc"],
    "Politics":      ["achraf_belmoudden", "younes.ftaite"],
    "Entertainment": ["ezzoubairhilal", "bahae.sanari"],
    "Food":          ["cuisine_halima__filali", "mehdi_tastediscovery"],
    "Miscill":       ["hesspress"],
}

# ─────────────────────────────────────────────
#  CONFIG ANTI-BAN
# ─────────────────────────────────────────────
MAX_POSTS_PER_ACCOUNT    = 10
MAX_COMMENTS_PER_POST    = 40
MIN_COMMENT_LENGTH       = 5
DELAY_BETWEEN_COMMENTS   = (1.5, 3.0)
DELAY_BETWEEN_POSTS      = (8, 15)
DELAY_BETWEEN_ACCOUNTS   = (30, 60)
DELAY_BETWEEN_CATEGORIES = (60, 120)

OUTPUT_DIR = Path("../data/raw")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# ─────────────────────────────────────────────
#  UTILITAIRES
# ─────────────────────────────────────────────

def random_sleep(min_sec, max_sec, label=""):
    duration = random.uniform(min_sec, max_sec)
    if label:
        logger.info(f"  Pause {label}: {duration:.1f}s...")
    time.sleep(duration)


def is_exploitable(text):
    if not text or len(text.strip()) < MIN_COMMENT_LENGTH:
        return False
    return sum(1 for c in text if c.isalpha()) >= 3


def generate_id(account, idx):
    return f"IGC_{account[:6].upper()}_{idx:06d}"


def load_checkpoint():
    path = OUTPUT_DIR / "checkpoint.json"
    if path.exists():
        with open(path) as f:
            data = json.load(f)
        logger.info(f"  Checkpoint: {len(data['done'])} comptes deja faits -> on reprend")
        return set(data["done"])
    return set()


def save_checkpoint(done_accounts):
    path = OUTPUT_DIR / "checkpoint.json"
    with open(path, "w") as f:
        json.dump({"done": list(done_accounts), "updated": str(datetime.now())}, f)


def load_existing_records():
    path = OUTPUT_DIR / "instagram_raw.json"
    if path.exists():
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        logger.info(f"  {len(data)} records existants charges")
        return data
    return []


def save_records(records, filename="instagram_raw"):
    if not records:
        return
    fieldnames = ["id", "text", "source_type", "channel",
                  "category", "url", "date", "label", "language"]

    with open(OUTPUT_DIR / f"{filename}.csv", "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(records)

    with open(OUTPUT_DIR / f"{filename}.json", "w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=2)

    logger.info(f"  Sauvegarde OK: {len(records)} records dans data/raw/")


# ─────────────────────────────────────────────
#  INITIALISATION
# ─────────────────────────────────────────────

def init_loader():
    L = instaloader.Instaloader(
        quiet=True,
        download_pictures=False,
        download_videos=False,
        download_video_thumbnails=False,
        download_geotags=False,
        download_comments=False,
        save_metadata=False,
        compress_json=False,
        max_connection_attempts=3,
    )

    # Charger session sauvegardee si elle existe (evite re-login)
    session_file = Path(f"session_{INSTAGRAM_USERNAME}")
    if session_file.exists():
        try:
            L.load_session_from_file(INSTAGRAM_USERNAME, str(session_file))
            logger.info(f"Session restauree pour @{INSTAGRAM_USERNAME}")
            return L
        except Exception:
            logger.info("Session expiree, reconnexion en cours...")

    try:
        L.login(INSTAGRAM_USERNAME, INSTAGRAM_PASSWORD)
        L.save_session_to_file(str(session_file))
        logger.info(f"Connecte avec succes: @{INSTAGRAM_USERNAME}")
    except Exception as e:
        logger.error(f"ERREUR connexion: {e}")

    return L


# ─────────────────────────────────────────────
#  SCRAPING D'UN COMPTE
# ─────────────────────────────────────────────

def scrape_account_safe(loader, account, category, start_idx=0):
    records    = []
    global_idx = start_idx

    try:
        profile = instaloader.Profile.from_username(loader.context, account)
        logger.info(f"  @{account} — {profile.mediacount} posts disponibles")

        posts_done = 0
        for post in profile.get_posts():
            if posts_done >= MAX_POSTS_PER_ACCOUNT:
                break

            post_url      = f"https://www.instagram.com/p/{post.shortcode}/"
            comments_done = 0
            retry_count   = 0

            while retry_count < 3:
                try:
                    for comment in post.get_comments():
                        if comments_done >= MAX_COMMENTS_PER_POST:
                            break
                        text = comment.text.strip()
                        if not is_exploitable(text):
                            continue
                        records.append({
                            "id":          generate_id(account, global_idx),
                            "text":        text,
                            "source_type": "Instagram_comment",
                            "channel":     account,
                            "category":    category,
                            "url":         post_url,
                            "date":        str(post.date_utc.date()),
                            "label":       None,
                            "language":    "darija",
                        })
                        comments_done += 1
                        global_idx    += 1
                        random_sleep(*DELAY_BETWEEN_COMMENTS)
                    break  # succes -> sortir du while

                except instaloader.exceptions.TooManyRequestsException:
                    retry_count += 1
                    wait = 30 * retry_count   # 30s, 60s, 90s
                    logger.warning(
                        f"    [429] Instagram bloque — attente {wait}s "
                        f"(tentative {retry_count}/3)"
                    )
                    time.sleep(wait)

                except Exception as e:
                    logger.warning(f"    Erreur commentaires post {post.shortcode}: {e}")
                    break

            logger.info(f"    Post {posts_done+1}: {comments_done} commentaires collectes")
            posts_done += 1
            random_sleep(*DELAY_BETWEEN_POSTS, label="entre posts")

    except instaloader.exceptions.ProfileNotExistsException:
        logger.error(f"  Profil @{account} introuvable sur Instagram")

    except instaloader.exceptions.LoginRequiredException:
        logger.error(f"  @{account}: connexion requise (profil prive?)")

    except instaloader.exceptions.TooManyRequestsException:
        wait = random.randint(300, 600)   # 5 a 10 minutes
        logger.warning(f"  [429] Rate limit global — attente {wait//60} min...")
        time.sleep(wait)

    except Exception as e:
        logger.error(f"  Erreur inattendue @{account}: {e}")

    return records


# ─────────────────────────────────────────────
#  PIPELINE PRINCIPALE
# ─────────────────────────────────────────────

def scrape_all_instagram():
    loader        = init_loader()
    all_records   = load_existing_records()   # reprend si deja des donnees
    done_accounts = load_checkpoint()         # reprend si deja des comptes faits
    start_idx     = len(all_records)

    total_accounts = sum(len(v) for v in INSTAGRAM_ACCOUNTS.values())
    logger.info(f"  {total_accounts} comptes a scraper au total")

    for category, account_list in INSTAGRAM_ACCOUNTS.items():
        if not account_list:
            continue

        logger.info(f"\n{'='*52}")
        logger.info(f"  Categorie : {category}")
        logger.info(f"{'='*52}")

        for i, account in enumerate(account_list):
            if account in done_accounts:
                logger.info(f"  @{account} deja scrape — skip")
                continue

            logger.info(f"\n  Scraping @{account}...")
            records = scrape_account_safe(loader, account, category, start_idx)
            all_records.extend(records)
            start_idx += len(records)

            # Sauvegarder apres chaque compte (securite)
            done_accounts.add(account)
            save_checkpoint(done_accounts)
            save_records(all_records)

            logger.info(
                f"  @{account}: +{len(records)} textes | "
                f"Total cumule: {len(all_records)}"
            )

            # Pause longue entre comptes (sauf le dernier de la categorie)
            if i < len(account_list) - 1:
                random_sleep(*DELAY_BETWEEN_ACCOUNTS, label="entre comptes")

        # Pause tres longue entre categories
        random_sleep(*DELAY_BETWEEN_CATEGORIES, label="entre categories")

    # Stats finales
    logger.info(f"\n{'='*52}")
    logger.info(f"  TERMINE — {len(all_records)} textes collectes au total")
    logger.info(f"{'='*52}")
    _print_stats(all_records)
    return all_records


def _print_stats(records):
    from collections import Counter
    print("\n  Repartition par categorie :")
    for cat, count in sorted(Counter(r["category"] for r in records).items()):
        print(f"    {cat:<20} {count:>5} textes")
    print("\n  Repartition par type de source :")
    for src, count in sorted(Counter(r["source_type"] for r in records).items()):
        print(f"    {src:<30} {count:>5} textes")


# ─────────────────────────────────────────────
#  POINT D'ENTREE
# ─────────────────────────────────────────────

if __name__ == "__main__":
    logger.info("Demarrage scraping Instagram...")
    logger.info(f"  Compte         : @{INSTAGRAM_USERNAME}")
    logger.info(f"  Posts/compte   : {MAX_POSTS_PER_ACCOUNT}")
    logger.info(f"  Comments/post  : {MAX_COMMENTS_PER_POST}")
    logger.info(f"  Delai comptes  : {DELAY_BETWEEN_ACCOUNTS[0]}s – {DELAY_BETWEEN_ACCOUNTS[1]}s")
    print()
    scrape_all_instagram()