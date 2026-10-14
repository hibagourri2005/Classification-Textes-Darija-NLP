"""
pipeline/runner.py
Orchestrateur RAPIDE — parallélisation par chaîne (ThreadPoolExecutor).
Objectif : 50 000 textes en 2-3 jours.
"""

import time
import logging
import pandas as pd
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

from scrapers.youtube_comments import YouTubeCommentScraper
from scrapers.youtube_transcripts import YouTubeTranscriptScraper
from pipeline.exporter import DatasetExporter

logger = logging.getLogger(__name__)


class ScrapingRunner:

    def __init__(self, config: dict, output_dir: Path):
        self.config = config
        self.output_dir = output_dir
        self.settings = config.get("settings", {})

        sleep = self.settings.get("sleep_between_requests", 1.0)
        self.comment_scraper = YouTubeCommentScraper(sleep=sleep)
        self.transcript_scraper = YouTubeTranscriptScraper(
            sleep=sleep,
            max_chunk_chars=self.settings.get("max_text_length", 500)
        )
        self.exporter = DatasetExporter(output_dir)
        self.min_len = self.settings.get("min_text_length", 10)
        self.max_workers = self.settings.get("max_workers", 3)  # threads parallèles
        self.all_records: list[dict] = []

    # ------------------------------------------------------------------
    def run(self, domains_filter: list[str] | None = None):
        domains = self.config.get("domains", {})

        for domain_name, domain_cfg in domains.items():
            if domains_filter and domain_name not in domains_filter:
                continue

            logger.info(f"\n{'='*60}")
            logger.info(f"DOMAINE : {domain_name.upper()}")
            logger.info(f"Objectif : {domain_cfg.get('target_texts', '?')} textes")
            logger.info(f"Parallélisme : {self.max_workers} threads")
            logger.info(f"{'='*60}")

            raw_dir = self.output_dir / "data" / "raw" / domain_name
            raw_dir.mkdir(parents=True, exist_ok=True)

            channels = domain_cfg.get("channels", [])
            domain_records = []

            # Lancer les chaînes en parallèle
            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                futures = {
                    executor.submit(
                        self._scrape_channel, ch, domain_name
                    ): ch for ch in channels
                }

                for future in as_completed(futures):
                    ch = futures[future]
                    try:
                        records = future.result()
                        domain_records.extend(records)

                        # Checkpoint immédiat par chaîne
                        if records:
                            checkpoint_path = raw_dir / f"{ch['handle']}.csv"
                            pd.DataFrame(records).to_csv(
                                checkpoint_path, index=False, encoding="utf-8"
                            )
                            logger.info(
                                f"  ✓ [{ch['name']}] checkpoint : "
                                f"{len(records)} textes → {checkpoint_path.name}"
                            )
                    except Exception as e:
                        logger.error(f"  ✗ Erreur chaîne {ch['name']}: {e}")

            self.all_records.extend(domain_records)
            logger.info(
                f"  → Domaine '{domain_name}' terminé : "
                f"{len(domain_records)} textes"
            )

        logger.info(f"\n{'='*60}\nEXPORT FINAL\n{'='*60}")
        self._export_final()

    # ------------------------------------------------------------------
    def _scrape_channel(self, channel_cfg: dict, domain: str) -> list[dict]:
        handle = channel_cfg["handle"]
        name = channel_cfg["name"]
        url = channel_cfg["url"]
        max_videos = channel_cfg.get("max_videos", 50)
        max_comments = channel_cfg.get("max_comments_per_video", 100)
        max_transcripts = channel_cfg.get("max_transcript_videos", 10)

        logger.info(f"\n  ▶ Démarrage : {name} (@{handle})")
        records = []

        # --- Commentaires ---
        try:
            comment_records = self.comment_scraper.scrape_channel(
                channel_url=url,
                channel_handle=handle,
                channel_name=name,
                domain=domain,
                max_videos=max_videos,
                max_comments_per_video=max_comments
            )
            logger.info(f"    [{name}] commentaires : {len(comment_records)}")
            records.extend(comment_records)
        except Exception as e:
            logger.error(f"    [{name}] Erreur commentaires : {e}")

        # --- Transcriptions ---
        try:
            videos = self.comment_scraper.get_video_urls(url, max_videos=max_transcripts)
            transcript_records = self.transcript_scraper.scrape_transcripts(
                videos=videos,
                channel_name=name,
                channel_handle=handle,
                domain=domain,
                max_transcript_videos=max_transcripts
            )
            logger.info(f"    [{name}] transcriptions : {len(transcript_records)} chunks")
            records.extend(transcript_records)
        except Exception as e:
            logger.error(f"    [{name}] Erreur transcriptions : {e}")

        # Filtrage minimal
        filtered = [
            r for r in records
            if r.get("text") and len(r["text"].strip()) >= self.min_len
        ]
        logger.info(f"    [{name}] ✓ total retenu : {len(filtered)} textes")
        return filtered

    # ------------------------------------------------------------------
    def _export_final(self):
        df = pd.DataFrame(self.all_records)
        before = len(df)
        df = df.drop_duplicates(subset=["text"])
        logger.info(f"Doublons supprimés : {before - len(df)}")
        df["id"] = [f"darija_{i:06d}" for i in range(len(df))]
        df["language"] = "darija"

        final_dir = self.output_dir / "data" / "final"
        final_dir.mkdir(parents=True, exist_ok=True)
        self.exporter.export(df, final_dir / "dataset_final.csv")

        logger.info(f"\n{'='*60}")
        logger.info(f"TOTAL : {len(df)} textes")
        for domain, count in df["domain"].value_counts().items():
            logger.info(f"  {domain:20s} : {count:6d}")
        for src, count in df["source_type"].value_counts().items():
            logger.info(f"  {src:30s} : {count:6d}")
