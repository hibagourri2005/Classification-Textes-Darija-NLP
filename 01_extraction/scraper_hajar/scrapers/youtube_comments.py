"""
scrapers/youtube_comments.py
Scraping GRATUIT des commentaires YouTube via yt-dlp.
Syntaxe correcte : --extractor-args "youtube:max_comments=N"
"""

import time
import logging
import subprocess
import json
import shutil
from pathlib import Path

logger = logging.getLogger(__name__)


class YouTubeCommentScraper:

    def __init__(self, sleep: float = 1.5):
        self.sleep = sleep
        self.tmp_dir = Path("_tmp_comments")
        self.tmp_dir.mkdir(exist_ok=True)
        self._check_ytdlp()

    def _check_ytdlp(self):
        try:
            result = subprocess.run(
                ["yt-dlp", "--version"],
                capture_output=True, text=True
            )
            logger.info(f"yt-dlp version : {result.stdout.strip()}")
        except FileNotFoundError:
            raise RuntimeError("yt-dlp non trouvé ! pip install yt-dlp")

    # ------------------------------------------------------------------
    # 1. Récupérer les vidéos d'une chaîne
    # ------------------------------------------------------------------
    def get_video_urls(self, channel_url: str, max_videos: int = 50) -> list[dict]:
        if not channel_url.endswith("/videos"):
            videos_url = channel_url.rstrip("/") + "/videos"
        else:
            videos_url = channel_url

        cmd = [
            "yt-dlp",
            "--flat-playlist",
            "--skip-download",
            "--print", "%(id)s|||%(title)s|||%(upload_date)s",
            "--playlist-end", str(max_videos),
            "--no-warnings",
            videos_url
        ]

        try:
            result = subprocess.run(
                cmd, capture_output=True, text=True,
                timeout=120, encoding="utf-8", errors="replace"
            )
            videos = []
            for line in result.stdout.strip().split("\n"):
                if "|||" not in line:
                    continue
                parts = line.split("|||")
                if len(parts) >= 2:
                    videos.append({
                        "video_id": parts[0].strip(),
                        "title": parts[1].strip(),
                        "published_at": parts[2].strip() if len(parts) > 2 else ""
                    })
            logger.info(f"  → {len(videos)} vidéos trouvées pour {channel_url}")
            return videos
        except subprocess.TimeoutExpired:
            logger.error(f"Timeout : {channel_url}")
            return []
        except Exception as e:
            logger.error(f"Erreur get_video_urls: {e}")
            return []

    # ------------------------------------------------------------------
    # 2. Récupérer les commentaires d'une vidéo
    # ------------------------------------------------------------------
    def get_comments(self, video_id: str, max_comments: int = 100) -> list[dict]:
        video_url = f"https://www.youtube.com/watch?v={video_id}"

        vid_dir = self.tmp_dir / video_id
        vid_dir.mkdir(exist_ok=True)
        output_template = str(vid_dir / "%(id)s.%(ext)s")

        cmd = [
            "yt-dlp",
            "--skip-download",
            "--write-info-json",
            "--write-comments",
            "--extractor-args", f"youtube:max_comments={max_comments}",  # ✅ syntaxe correcte
            "--output", output_template,
            "--no-warnings",
            "--quiet",
            video_url
        ]

        try:
            subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=180,
                encoding="utf-8",
                errors="replace"
            )

            json_files = list(vid_dir.glob("*.info.json"))
            if not json_files:
                logger.debug(f"Pas de .info.json pour {video_id}")
                return []

            with open(json_files[0], "r", encoding="utf-8", errors="replace") as f:
                data = json.load(f)

            raw_comments = data.get("comments", []) or []
            comments = []
            for c in raw_comments[:max_comments]:
                text = c.get("text", "").strip()
                if text:
                    comments.append({
                        "text": text,
                        "like_count": c.get("like_count", 0),
                        "published_at": str(c.get("timestamp", ""))
                    })

            return comments

        except subprocess.TimeoutExpired:
            logger.debug(f"Timeout commentaires : {video_id}")
            return []
        except json.JSONDecodeError as e:
            logger.debug(f"JSON invalide pour {video_id}: {e}")
            return []
        except Exception as e:
            logger.debug(f"Erreur commentaires {video_id}: {e}")
            return []
        finally:
            try:
                shutil.rmtree(vid_dir, ignore_errors=True)
            except Exception:
                pass

    # ------------------------------------------------------------------
    # 3. Scrape complet d'une chaîne
    # ------------------------------------------------------------------
    def scrape_channel(
        self,
        channel_url: str,
        channel_handle: str,
        channel_name: str,
        domain: str,
        max_videos: int = 50,
        max_comments_per_video: int = 100
    ) -> list[dict]:
        records = []
        videos = self.get_video_urls(channel_url, max_videos=max_videos)

        for video in videos:
            vid = video["video_id"]
            comments = self.get_comments(vid, max_comments=max_comments_per_video)

            for c in comments:
                records.append({
                    "id": f"yt_comment_{vid}_{len(records)}",
                    "text": c["text"],
                    "source_type": "youtube_comment",
                    "domain": domain,
                    "channel_name": channel_name,
                    "channel_handle": channel_handle,
                    "video_id": vid,
                    "video_title": video["title"],
                    "published_at": c["published_at"],
                    "label": domain
                })

            logger.info(
                f"    [{channel_name}] {vid} : "
                f"{len(comments)} commentaires | total={len(records)}"
            )
            time.sleep(self.sleep)

        return records
