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
    현재 DB에 저장된 가장 최신 회차를 반환한다.

    저장된 데이터가 없는 경우 0을 반환한다.
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
    특정 회차가 DB에 이미 저장되어 있는지 확인한다.
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


def get_existing_draw_nos(draw_nos):
    """
    전달받은 회차 번호 중 DB에 이미 존재하는 회차 번호를 반환한다.
    """

    draw_nos = list(draw_nos)

    if not draw_nos:
        return set()

    placeholders = ",".join("?" for _ in draw_nos)

    conn = get_connection()

    try:
        cursor = conn.cursor()

        cursor.execute(
            f"""
            SELECT draw_no
            FROM lotto_winning_numbers
            WHERE draw_no IN ({placeholders})
            """,
            tuple(draw_nos),
        )

        return {
            int(row[0])
            for row in cursor.fetchall()
        }

    finally:
        conn.close()


def save_new_lotto_draws(draws):
    """
    검증이 완료된 신규 당첨번호 데이터를 저장한다.

    기존에 저장된 회차는 수정하지 않고 건너뛴다.

    전체 저장 작업은 하나의 Transaction으로 처리한다.
    저장 도중 오류가 발생하면 전체 작업을 Rollback한다.

    Parameters
    ----------
    draws : iterable
        {
            "draw_no": 1232,
            "numbers": [1, 2, 3, 4, 5, 6],
            "bonus_number": 7
        }

    Returns
    -------
    list[int]
        실제 신규 저장된 회차 번호 목록
    """

    draws = list(draws)

    if not draws:
        return []

    conn = get_connection()

    inserted_draw_nos = []

    try:
        cursor = conn.cursor()

        cursor.execute("BEGIN")

        for draw in draws:
            draw_no = draw["draw_no"]
            numbers = draw["numbers"]
            bonus_number = draw["bonus_number"]

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

            if cursor.rowcount > 0:
                inserted_draw_nos.append(draw_no)

        conn.commit()

        return inserted_draw_nos

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()


def reset_database():
    """
    lotto_winning_numbers 테이블을 삭제한 후 다시 생성한다.
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