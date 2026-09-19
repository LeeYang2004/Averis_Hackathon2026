from argparse import ArgumentParser
from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.database import SessionLocal  # noqa: E402
from services.input_importer import InputDataImporter, reset_database  # noqa: E402


def main() -> None:
    parser = ArgumentParser(description="Import SDOC inbox data into SQLite.")
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Drop and recreate all application tables before importing.",
    )
    args = parser.parse_args()

    if args.reset:
        reset_database()

    db = SessionLocal()
    try:
        result = InputDataImporter().import_all(db)
    finally:
        db.close()

    print(f"Imported {result['emails']} emails and {result['documents']} documents.")


if __name__ == "__main__":
    main()
