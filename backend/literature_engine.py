"""
T2D-EviGuide Literature Engine
Central entry point for the existing literature workflow.
"""

from pathlib import Path
import subprocess
import sys

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
REPORTS_DIR = PROJECT_ROOT / "reports"

LITERATURE_SCRIPTS = {
    "search": "literature_search_targeted.py",
    "concept_filter": "literature_filter_concept.py",
    "population_filter": "literature_filter_population.py",
    "targeted_filter": "literature_filter_targeted.py",
    "manager": "literature_manager.py",
    "processor": "literature_processor.py",
    "chunker": "text_chunker.py",
}


def check_literature_files():
    """Report which existing workflow scripts and data files are available."""
    return {
        "scripts": {
            name: (PROJECT_ROOT / filename).exists()
            for name, filename in LITERATURE_SCRIPTS.items()
        },
        "chunks": (DATA_DIR / "chunks.json").exists(),
        "article_registry": (DATA_DIR / "article_registry.csv").exists(),
    }


def run_literature_step(step):
    """Run one existing literature script without merging or rewriting it."""
    if step not in LITERATURE_SCRIPTS:
        raise ValueError(
            f"Unknown step: {step}. Choose from: "
            + ", ".join(LITERATURE_SCRIPTS)
        )

    script = PROJECT_ROOT / LITERATURE_SCRIPTS[step]

    if not script.is_file():
        raise FileNotFoundError(f"Literature script not found: {script}")

    return subprocess.run(
        [sys.executable, str(script)],
        cwd=str(PROJECT_ROOT),
        check=True,
    )


if __name__ == "__main__":
    print("T2D-EviGuide Literature Engine")
    print("-" * 40)

    status = check_literature_files()

    for name, exists in status["scripts"].items():
        print(f"{name}: {'AVAILABLE' if exists else 'MISSING'}")

    print(f"chunks.json: {'AVAILABLE' if status['chunks'] else 'MISSING'}")
    print(
        "article_registry.csv: "
        f"{'AVAILABLE' if status['article_registry'] else 'MISSING'}"
    )

    print("\nStatus check complete. No literature scripts were executed.")
