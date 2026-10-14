"""
main.py — Point d'entrée du scraper Darija (100% gratuit, yt-dlp)

Usage :
    python main.py                                        # Scrape TOUS les domaines
    python main.py --domains religion food                # Domaines existants
    python main.py --domains medical business sports politics  # Nouveaux domaines
    python main.py --check-config                         # Vérifie sans scraper
"""

import argparse
import logging
import sys
import yaml
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("logs/scraping.log", encoding="utf-8")
    ]
)
logger = logging.getLogger(__name__)
ROOT_DIR = Path(__file__).parent

ALL_DOMAINS = [
    "religion", "food", "entertainment", "miscill",
    "medical", "business", "sports", "politics"
]


def load_config(config_path: Path) -> dict:
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def check_config(config: dict):
    print("\n" + "=" * 60)
    print("CONFIGURATION — Scraper Darija (yt-dlp, 100% gratuit)")
    print("=" * 60)

    import subprocess
    try:
        v = subprocess.run(["yt-dlp", "--version"], capture_output=True, text=True)
        print(f"✓ yt-dlp : {v.stdout.strip()}")
    except FileNotFoundError:
        print("✗ yt-dlp non trouvé → pip install yt-dlp")

    total_target = 0
    total_estimate = 0
    for domain, cfg in config.get("domains", {}).items():
        n_channels = len(cfg.get("channels", []))
        target = cfg.get("target_texts", 0)
        total_target += target
        domain_estimate = 0
        print(f"\n  Domaine '{domain}' : {n_channels} chaînes | cible {target} textes")
        for ch in cfg.get("channels", []):
            max_v = ch.get("max_videos", 0)
            max_c = ch.get("max_comments_per_video", 0)
            max_t = ch.get("max_transcript_videos", 0)
            estimate = max_v * max_c + max_t * 20
            domain_estimate += estimate
            print(f"    • {ch['name']:35s} ≈ {estimate:6d} textes")
        print(f"    → Estimation domaine : {domain_estimate} textes")
        total_estimate += domain_estimate

    print(f"\n{'='*60}")
    print(f"Domaines configurés  : {len(config.get('domains', {}))}")
    print(f"Total cible          : {total_target} textes")
    print(f"Total estimé         : {total_estimate} textes")
    print("=" * 60 + "\n")


def main():
    (ROOT_DIR / "logs").mkdir(exist_ok=True)

    parser = argparse.ArgumentParser(description="Scraper YouTube Darija (gratuit)")
    parser.add_argument(
        "--domains", nargs="+",
        choices=ALL_DOMAINS,
        default=None,
        help=f"Domaines à scraper. Disponibles : {', '.join(ALL_DOMAINS)}"
    )
    parser.add_argument("--check-config", action="store_true")
    parser.add_argument(
        "--config", type=Path,
        default=ROOT_DIR / "config" / "channels.yaml"
    )
    args = parser.parse_args()

    config = load_config(args.config)

    if args.check_config:
        check_config(config)
        return

    from pipeline.runner import ScrapingRunner
    runner = ScrapingRunner(config=config, output_dir=ROOT_DIR)
    runner.run(domains_filter=args.domains)
    logger.info("✅ Scraping terminé !")


if __name__ == "__main__":
    main()
