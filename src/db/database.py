import sqlite3
import sys
from pathlib import Path


if getattr(sys, "frozen", False):
    BASE_DIR = Path(sys.executable).resolve().parent
else:
    BASE_DIR = Path(__file__).resolve().parents[2]


DB_DIR = BASE_DIR / "database"
DB_PATH = DB_DIR / "lotto.db"


def get_connection():
    DB_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    return sqlite3.connect(DB_PATH)


def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS lotto_winning_numbers (
            draw_no INTEGER PRIMARY KEY,
            number1 INTEGER NOT NULL,
            number2 INTEGER NOT NULL,
            number3 INTEGER NOT NULL,
            number4 INTEGER NOT NULL,
            number5 INTEGER NOT NULL,
            number6 INTEGER NOT NULL,
            bonus_number INTEGER NOT NULL
        )
        """
    )

    conn.commit()
    conn.close()


def reset_database():
    DB_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        """
        DROP TABLE IF EXISTS lotto_winning_numbers
        """
    )

    conn.commit()
    conn.close()

    init_db()