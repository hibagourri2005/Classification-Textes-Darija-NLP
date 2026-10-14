"""
scrapers/youtube_transcripts.py
Extraction des transcriptions automatiques YouTube via youtube-transcript-api.
Fonctionne SANS clé API (utilise le sous-titrage automatique public de YouTube).
"""

import re
import time
import logging
from youtube_transcript_api import (
    YouTubeTranscriptApi,
    TranscriptsDisabled,
    NoTranscriptFound,
    VideoUnavailable,
)

logger = logging.getLogger(__name__)

# Langues acceptées pour les transcriptions (ordre de priorité)
LANG_PRIORITY = ["ar", "fr", "en"]


class YouTubeTranscriptScraper:
    """
    Extrait les sous-titres automatiques des vidéos YouTube.
    Segmente chaque transcription en chunks exploitables.
    """

    def __init__(self, sleep: float = 1.0, max_chunk_chars: int = 500):
        self.sleep = sleep
        self.max_chunk_chars = max_chunk_chars

    # ------------------------------------------------------------------
    # 1. Extraire la transcription brute d'une vidéo
    # ------------------------------------------------------------------
    def get_transcript(self, video_id: str) -> str | None:
        """
        Tente d'obtenir la transcription dans les langues prioritaires.
        Retourne le texte complet ou None si indisponible.
        """
        try:
            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)

            # Cherche d'abord une transcription générée automatiquement
            for lang in LANG_PRIORITY:
                try:
                    transcript = transcript_list.find_generated_transcript([lang])
                    segments = transcript.fetch()
                    text = " ".join(s["text"] for s in segments)
                    return self._clean_transcript(text)
                except Exception:
                    pass

            # Fallback : n'importe quelle transcription disponible
            for t in transcript_list:
                try:
                    segments = t.fetch()
                    text = " ".join(s["text"] for s in segments)
                    return self._clean_transcript(text)
                except Exception:
                    pass

        except (TranscriptsDisabled, NoTranscriptFound, VideoUnavailable) as e:
            logger.debug(f"Transcription indisponible pour {video_id}: {type(e).__name__}")
        except Exception as e:
            logger.warning(f"Erreur inattendue transcription {video_id}: {e}")

        return None

    # ------------------------------------------------------------------
    # 2. Nettoyer la transcription brute
    # ------------------------------------------------------------------
    @staticmethod
    def _clean_transcript(text: str) -> str:
        """
        Nettoyage minimal : supprime les balises, normalise les espaces.
        On conserve volontairement la Darija telle quelle.
        """
        # Supprimer balises HTML résiduelle
        text = re.sub(r"<[^>]+>", " ", text)
        # Supprimer les timestamps éventuels [00:00]
        text = re.sub(r"\[\d{2}:\d{2}(?::\d{2})?\]", " ", text)
        # Normaliser les espaces multiples
        text = re.sub(r"\s+", " ", text).strip()
        return text

    # ------------------------------------------------------------------
    # 3. Découper en chunks
    # ------------------------------------------------------------------
    def _chunk_text(self, text: str) -> list[str]:
        """
        Divise un long texte en chunks de ~max_chunk_chars caractères,
        en coupant sur les espaces pour ne pas couper les mots.
        """
        chunks = []
        words = text.split()
        current = []
        current_len = 0

        for word in words:
            if current_len + len(word) + 1 > self.max_chunk_chars and current:
                chunks.append(" ".join(current))
                current = [word]
                current_len = len(word)
            else:
                current.append(word)
                current_len += len(word) + 1

        if current:
            chunks.append(" ".join(current))

        return chunks

    # ------------------------------------------------------------------
    # 4. Méthode principale : scrape les transcriptions d'une liste de vidéos
    # ------------------------------------------------------------------
    def scrape_transcripts(
        self,
        videos: list[dict],
        channel_name: str,
        channel_handle: str,
        domain: str,
        max_transcript_videos: int = 10,
    ) -> list[dict]:
        """
        Scrape les transcriptions des N premières vidéos.
        Retourne une liste de records (un par chunk).

        Args:
            videos: liste de dicts {video_id, title, published_at}
            channel_name: nom lisible de la chaîne
            channel_handle: handle YouTube
            domain: domaine thématique (religion, food, etc.)
            max_transcript_videos: nombre max de vidéos à transcrire
        """
        records = []
        videos_processed = 0

        for video in videos[:max_transcript_videos]:
            vid = video["video_id"]
            title = video["title"]

            transcript = self.get_transcript(vid)

            if not transcript:
                continue

            chunks = self._chunk_text(transcript)

            for i, chunk in enumerate(chunks):
                records.append({
                    "id": f"yt_transcript_{vid}_{i}",
                    "text": chunk,
                    "source_type": "youtube_transcript",
                    "domain": domain,
                    "channel_name": channel_name,
                    "channel_handle": channel_handle,
                    "video_id": vid,
                    "video_title": title,
                    "published_at": video.get("published_at", ""),
                    "label": domain
                })

            videos_processed += 1
            logger.info(
                f"    [{channel_name}] transcription {vid} : "
                f"{len(chunks)} chunks | vidéos={videos_processed}"
            )
            time.sleep(self.sleep)

        return records
