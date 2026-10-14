"""
=====================================================================
 DARIJA PROJECT — Scraping YouTube MAXIMUM
 Scrape TOUT ce qui est disponible — pas de limite par categorie
 Commentaires + Transcriptions sur TOUTES les videos
=====================================================================
COMMANDES :
  cd scraping
  python youtube_scraper.py

Pour repartir de zero :
  del data\\raw\\yt_checkpoint.json
  del data\\raw\\youtube_raw.json
  del data\\raw\\youtube_raw.csv
=====================================================================
"""

import csv, json, time, re, logging, urllib.request
from pathlib import Path
from collections import Counter

import yt_dlp
from youtube_comment_downloader import YoutubeCommentDownloader, SORT_BY_RECENT

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("scraping.log", encoding="utf-8"),
    ]
)
logger = logging.getLogger(__name__)

# =====================================================================
#  VOS CHAINES — exactement comme vous les avez donnees
#  + les chaines confirmees des sessions precedentes
# =====================================================================
YOUTUBE_CHANNELS = {

    "Medical": [
        "https://www.youtube.com/@Dr.abderrahimznt",      # CDC - 516 deja
        "https://www.youtube.com/@DrMouad",               # CDC confirme
        "https://www.youtube.com/@sehtima",               # votre chaine
        "https://www.youtube.com/@Medic-all",             # votre chaine     
        "https://www.youtube.com/@OUALIDALLALI",          # votre chaine
        "https://www.youtube.com/@drsihammansouri",       # CDC confirme
        "https://www.youtube.com/@Dr.RachidElFakir",      # nutrition darija
    ],

    "Business": [
        "https://www.youtube.com/@YoussefAkalal7",        # CDC - 570 deja
        "https://www.youtube.com/@SimoLifeCom",           # votre chaine
        "https://www.youtube.com/@Ounacerhassan",         # votre chaine
        "https://www.youtube.com/@abdonobil",             # votre chaine
          
    ],

    "Sports": [
        "https://www.youtube.com/@ingenieur.fitness",              # CDC - 3500 deja
        "https://www.youtube.com/@federationroyalemarocained3087", # CDC confirme
        "https://www.youtube.com/@RadioSportMaroc",                # votre chaine
        "https://www.youtube.com/@anas02",                         # votre chaine
           "https://www.youtube.com/@coachhajar",                     # votre chaine
        "https://www.youtube.com/@wydadac",                        # Wydad officiel
        "https://www.youtube.com/@RajaClubAthletic",               # Raja officiel
        "https://www.youtube.com/@equipedumaroc",  
        "https://www.youtube.com/@michafit5034"
        "https://www.youtube.com/@michafit5034/videos"
        "http://youtube.com/@ArryadiaTv"
      
                      
                     
    ],

    "Politics": [
        "https://www.youtube.com/@i3lamtvcom",                      # CDC confirme
        "https://www.youtube.com/@younesftaite2917",                # CDC confirme
        "https://www.youtube.com/@AjiTfham",                        # votre chaine
        "https://www.youtube.com/@amineaouni",                      # satire politique
        "https://www.youtube.com/@anasfetoui",                      # votre chaine
        "https://www.youtube.com/channel/UCMXjbEfbtBRudn1j1FS-rxA",# votre chaine (ID)
    ],

   
}

# =====================================================================
#  CONFIG — SCRAPER TOUT SANS LIMITE ARTIFICIELLE
# =====================================================================
MAX_VIDEOS_PER_CHANNEL = 40     # 200 videos par chaine = maximum utile
MAX_COMMENTS_PER_VIDEO = 500     # 500 commentaires par video
MIN_TEXT_LENGTH        = 5       # longueur minimale
DELAY_BETWEEN_VIDEOS   = 1.0     # secondes entre videos

OUTPUT_DIR = Path("../data/raw")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# =====================================================================
#  UTILITAIRES
# =====================================================================

def channel_label(url):
    handle = url.split("@")[-1] if "@" in url else url.split("/")[-1]
    return re.sub(r"[^a-zA-Z0-9]", "", handle)[:10].upper()

def gen_id(prefix, url, idx):
    return f"{prefix}_{channel_label(url)}_{idx:07d}"

def is_exploitable(text):
    if not text or len(text.strip()) < MIN_TEXT_LENGTH:
        return False
    return sum(1 for c in text if c.isalpha()) >= 3

def load_checkpoint():
    p = OUTPUT_DIR / "yt_checkpoint.json"
    if p.exists():
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
            done = set(data.get("done", []))
            logger.info(f"  Checkpoint : {len(done)} chaines deja traitees")
            return done
        except Exception:
            pass
    return set()

def save_checkpoint(done):
    (OUTPUT_DIR / "yt_checkpoint.json").write_text(
        json.dumps({"done": list(done)}, ensure_ascii=False), encoding="utf-8"
    )

def load_existing():
    p = OUTPUT_DIR / "youtube_raw.json"
    if p.exists():
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
            logger.info(f"  {len(data)} records existants charges")
            return data
        except Exception as e:
            logger.warning(f"  Impossible charger youtube_raw.json : {e}")
    return []

def save_all(records):
    if not records:
        return
    fields = ["id","text","source_type","channel","category","url","date","label","language"]
    with open(OUTPUT_DIR / "youtube_raw.csv", "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        w.writerows(records)
    (OUTPUT_DIR / "youtube_raw.json").write_text(
        json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    logger.info(f"  Sauvegarde : {len(records)} records total")


# =====================================================================
#  RECUPERER TOUTES LES VIDEOS D'UNE CHAINE
# =====================================================================

def get_all_videos(channel_url, max_videos=MAX_VIDEOS_PER_CHANNEL):
    """Recupere jusqu'a max_videos videos depuis la chaine."""
    # Essayer /videos d'abord, puis la chaine directement
    urls_to_try = [
        channel_url.rstrip("/") + "/videos",
        channel_url,
    ]
    ydl_opts = {
        "quiet":        True,
        "extract_flat": True,
        "playlistend":  max_videos,
        "ignoreerrors": True,
    }
    for url in urls_to_try:
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                if info and "entries" in info and info["entries"]:
                    result = []
                    for e in info["entries"]:
                        if e and e.get("id"):
                            result.append(f"https://www.youtube.com/watch?v={e['id']}")
                    if result:
                        logger.info(f"  {len(result)} videos trouvees : {channel_url}")
                        return result[:max_videos]
        except Exception as ex:
            logger.warning(f"  Echec ({url}) : {ex}")
    logger.warning(f"  Aucune video trouvee : {channel_url}")
    return []


# =====================================================================
#  TOUS LES COMMENTAIRES D'UNE VIDEO
# =====================================================================

def get_all_comments(video_url, channel_url, category, start_idx):
    """Recupere jusqu'a MAX_COMMENTS_PER_VIDEO commentaires."""
    downloader = YoutubeCommentDownloader()
    records, count = [], 0
    try:
        for comment in downloader.get_comments_from_url(video_url, sort_by=SORT_BY_RECENT):
            if count >= MAX_COMMENTS_PER_VIDEO:
                break
            text = comment.get("text", "").strip()
            if not is_exploitable(text):
                continue
            records.append({
                "id":          gen_id("YTC", channel_url, start_idx + count),
                "text":        text,
                "source_type": "YouTube_comment",
                "channel":     channel_label(channel_url),
                "category":    category,
                "url":         video_url,
                "date":        comment.get("time", ""),
                "label":       None,
                "language":    "darija",
            })
            count += 1
        logger.info(f"    Commentaires : {count}")
    except Exception as e:
        logger.warning(f"    Erreur commentaires : {e}")
    return records


# =====================================================================
#  TRANSCRIPTION D'UNE VIDEO
# =====================================================================

def _parse_json3(content):
    try:
        data, words = json.loads(content), []
        for event in data.get("events", []):
            for seg in event.get("segs", []):
                w = seg.get("utf8", "").strip()
                if w and w != "\n":
                    words.append(w)
        return " ".join(words)
    except Exception:
        return ""

def _parse_vtt(content):
    lines, seen = [], set()
    for line in content.split("\n"):
        line = line.strip()
        if (not line or line.startswith("WEBVTT") or "-->" in line
                or line.startswith("NOTE") or line.startswith("Kind:")
                or line.startswith("Language:") or line.isdigit()):
            continue
        line = re.sub(r"<[^>]+>", "", line).strip()
        line = re.sub(r"\w+:\w+[\w%]*", "", line).strip()
        if line and line not in seen:
            seen.add(line)
            lines.append(line)
    return " ".join(lines)

def get_transcription(video_url, channel_url, category, start_idx):
    """Recupere la transcription et la decoupe en segments de 100 mots."""
    records = []
    try:
        with yt_dlp.YoutubeDL({
            "writeautomaticsub": True,
            "subtitleslangs":    ["ar", "ar-MA", "fr"],
            "skip_download":     True,
            "quiet":             True,
            "subtitlesformat":   "json3",
        }) as ydl:
            info    = ydl.extract_info(video_url, download=False)
            auto    = info.get("automatic_captions", {})
            manu    = info.get("subtitles", {})
            lang    = next((l for l in ["ar-MA","ar","fr"] if l in auto or l in manu), None)
            if not lang:
                return records
            subs    = auto.get(lang) or manu.get(lang)
            sub_url = subs[0].get("url", "") if subs else ""
            if not sub_url:
                return records
            with urllib.request.urlopen(sub_url, timeout=15) as r:
                content = r.read().decode("utf-8")
            full_text = _parse_json3(content) if "json3" in sub_url else _parse_vtt(content)
            if not full_text.strip():
                return records
            words  = full_text.split()
            chunks = [" ".join(words[j:j+100]) for j in range(0, len(words), 100)]
            for i, seg in enumerate(chunks):
                if is_exploitable(seg):
                    records.append({
                        "id":          gen_id("YTT", channel_url, start_idx + i),
                        "text":        seg,
                        "source_type": "YouTube_transcription",
                        "channel":     channel_label(channel_url),
                        "category":    category,
                        "url":         video_url,
                        "date":        info.get("upload_date", ""),
                        "label":       None,
                        "language":    "darija",
                    })
        if records:
            logger.info(f"    Transcription : {len(records)} segments")
    except Exception as e:
        logger.warning(f"    Erreur transcription : {e}")
    return records


# =====================================================================
#  PIPELINE PRINCIPAL — SCRAPE TOUT SANS LIMITE
# =====================================================================

def scrape_all():
    logger.info("=" * 65)
    logger.info("  DARIJA PROJECT — SCRAPING MAXIMUM TOUTES CHAINES")
    logger.info(f"  {sum(len(v) for v in YOUTUBE_CHANNELS.values())} chaines | "
                f"{MAX_VIDEOS_PER_CHANNEL} videos/chaine | "
                f"{MAX_COMMENTS_PER_VIDEO} comments/video")
    logger.info("=" * 65)

    all_records   = load_existing()
    done_channels = load_checkpoint()
    cat_counts    = dict(Counter(r["category"] for r in all_records))
    global_idx    = len(all_records)

    # Etat de depart
    logger.info(f"\n  ETAT ACTUEL :")
    for cat, chs in YOUTUBE_CHANNELS.items():
        n    = cat_counts.get(cat, 0)
        done = sum(1 for c in chs if c in done_channels)
        logger.info(f"    {cat:<22} {n:>6} textes | {done}/{len(chs)} chaines traitees")
    logger.info(f"    {'TOTAL':<22} {len(all_records):>6} textes\n")

    for category, channels in YOUTUBE_CHANNELS.items():
        logger.info(f"\n{'='*65}")
        logger.info(f"  CATEGORIE : {category.upper()}")
        logger.info(f"  {len(channels)} chaines a traiter")
        logger.info(f"{'='*65}")

        for channel_url in channels:

            if channel_url in done_channels:
                logger.info(f"  SKIP (deja fait) : {channel_url}")
                continue

            logger.info(f"\n  ▶ {channel_url}")

            videos = get_all_videos(channel_url)
            if not videos:
                done_channels.add(channel_url)
                save_checkpoint(done_channels)
                continue

            ch_new = 0
            for j, vid_url in enumerate(videos):
                logger.info(f"  Video {j+1:>3}/{len(videos)} : {vid_url}")

                # Commentaires
                cmts = get_all_comments(vid_url, channel_url, category, global_idx)
                all_records.extend(cmts)
                global_idx += len(cmts)
                ch_new     += len(cmts)

                # Transcription
                trans = get_transcription(vid_url, channel_url, category, global_idx)
                all_records.extend(trans)
                global_idx += len(trans)
                ch_new     += len(trans)

                time.sleep(DELAY_BETWEEN_VIDEOS)

            # Sauvegarde apres chaque chaine
            cat_counts[category] = cat_counts.get(category, 0) + ch_new
            done_channels.add(channel_url)
            save_checkpoint(done_channels)
            save_all(all_records)

            logger.info(
                f"  ✓ {channel_url.split('@')[-1]:<28} "
                f"+{ch_new:>5} textes | "
                f"{category}: {cat_counts[category]} | "
                f"TOTAL: {len(all_records)}"
            )

    # Rapport final
    logger.info(f"\n{'='*65}")
    logger.info(f"  TERMINE — {len(all_records)} textes collectes au total")
    logger.info(f"{'='*65}")
    _print_stats(all_records)


# =====================================================================
#  RAPPORT FINAL
# =====================================================================

def _print_stats(records):
    total   = len(records)
    cat_cnt = Counter(r["category"]    for r in records)
    src_cnt = Counter(r["source_type"] for r in records)

    print("\n")
    print("  ╔══════════════════════════════════════════════════════╗")
    print(f"  ║  TOTAL COLLECTE : {total} textes" + " " * max(0, 33-len(str(total))) + "║")
    print("  ╠══════════════════════╦═════════╦════════════════════╣")
    print("  ║ Categorie            ║  Textes ║  % du total        ║")
    print("  ╠══════════════════════╬═════════╬════════════════════╣")
    for cat in sorted(YOUTUBE_CHANNELS.keys()):
        n   = cat_cnt.get(cat, 0)
        pct = n / total * 100 if total else 0
        bar = "█" * int(pct / 2)
        print(f"  ║ {cat:<20} ║ {n:>7} ║ {pct:>5.1f}% {bar:<12} ║")
    print("  ╠══════════════════════╩═════════╩════════════════════╣")
    for src, n in sorted(src_cnt.items()):
        pct = n / total * 100 if total else 0
        print(f"  ║  {src:<20} {n:>7} textes ({pct:.1f}%)       ║")
    print("  ╠══════════════════════════════════════════════════════╣")
    nb_ch_total = sum(len(v) for v in YOUTUBE_CHANNELS.values())
    print(f"  ║  Chaines configurees : {nb_ch_total:<30} ║")
    print("  ╚══════════════════════════════════════════════════════╝\n")


# =====================================================================
if __name__ == "__main__":
    scrape_all()