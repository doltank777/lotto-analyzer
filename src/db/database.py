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
    """
    Lotto Analyzer에서 사용하는 SQLite 연결을 반환한다.

    개발환경:
        프로젝트 루트/database/lotto.db

    PyInstaller EXE:
        EXE 위치/database/lotto.db
    """

    DB_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    return sqlite3.connect(DB_PATH)


def init_db():
    """
    Lotto Analyzer에서 사용하는 기본 DB 테이블을 생성한다.
    """

    conn = get_connection()

    try:
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

    finally:
        conn.close()


def get_latest_draw_no():
    """
    현재 DB에 저장된 가장 최신 회차 번호를 반환한다.

    데이터가 없는 경우 0을 반환한다.
    """

    conn = get_connection()

    try:
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT MAX(draw_no)
            FROM lotto_winning_numbers
            """
        )

        row = cursor.fetchone()

        if row is None or row[0] is None:
            return 0

        return int(row[0])

    finally:
        conn.close()


def draw_exists(draw_no):
    """
    특정 회차가 DB에 이미 존재하는지 확인한다.
    """

    conn = get_connection()

    try:
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT 1
            FROM lotto_winning_numbers
            WHERE draw_no = ?
            LIMIT 1
            """,
            (draw_no,),
        )

        return cursor.fetchone() is not None

    finally:
        conn.close()


def insert_lotto_draw(
    draw_no,
    numbers,
    bonus_number,
):
    """
    신규 당첨번호 1개 회차를 DB에 저장한다.

    기존 회차가 존재하면 데이터를 덮어쓰지 않고
    False를 반환한다.

    저장 성공 시 True를 반환한다.

    저장 도중 오류가 발생하면 Rollback한다.
    """

    conn = get_connection()

    try:
        cursor = conn.cursor()

        cursor.execute("BEGIN")

        cursor.execute(
            """
            INSERT INTO lotto_winning_numbers (
                draw_no,
                number1,
                number2,
                number3,
                number4,
                number5,
                number6,
                bonus_number
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(draw_no) DO NOTHING
            """,
            (
                draw_no,
                numbers[0],
                numbers[1],
                numbers[2],
                numbers[3],
                numbers[4],
                numbers[5],
                bonus_number,
            ),
        )

        inserted = cursor.rowcount > 0

        conn.commit()

        return inserted

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()


def reset_database():
    """
    lotto_winning_numbers 테이블을 삭제한 뒤 다시 생성한다.
    """

    DB_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    conn = sqlite3.connect(DB_PATH)

    try:
        cursor = conn.cursor()

        cursor.execute(
            """
            DROP TABLE IF EXISTS lotto_winning_numbers
            """
        )

        conn.commit()

    finally:
        conn.close()

    init_db()