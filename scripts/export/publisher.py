from pathlib import Path
import shutil


PROJECT_ROOT = Path(__file__).resolve().parents[2]

PUBLISHED_DIR = PROJECT_ROOT / "data" / "published"
WEBSITE_DATA_DIR = PROJECT_ROOT / "website" / "src" / "data"


def publish_directory(directory: str) -> None:
    """
    Copia una carpeta de data/published a website/src/data.
    """

    source = PUBLISHED_DIR / directory
    destination = WEBSITE_DATA_DIR / directory

    destination.mkdir(parents=True, exist_ok=True)

    for file in source.glob("*"):

        if file.is_file():

            shutil.copy2(file, destination / file.name)