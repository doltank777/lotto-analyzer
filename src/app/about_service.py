import platform
import sqlite3
import sys
from pathlib import Path


class AboutService:
    """프로그램 정보 화면에 필요한 실행환경 및 DB 정보를 제공한다."""

    DATABASE_FILE_NAME = "lotto.db"

    def get_program_information(self):
        database_path = self._get_database_path()
        database_summary = self._get_database_summary(database_path)

        return {
            "python_version": platform.python_version(),
            "sqlite_version": sqlite3.sqlite_version,
            "os_name": self._get_os_name(),
            "architecture": platform.machine() or "확인 불가",
            "stored_draw_count": database_summary["stored_draw_count"],
            "latest_draw_no": database_summary["latest_draw_no"],
            "database_path": str(database_path),
            "database_exists": database_path.exists(),
            "repository": "GitHub Private Repository",
            "license": "별도 라이선스 미지정",
        }

    def _get_database_path(self):
        if getattr(sys, "frozen", False):
            base_dir = Path(sys.executable).resolve().parent
        else:
            base_dir = Path(__file__).resolve().parents[2]

        return base_dir / "database" / self.DATABASE_FILE_NAME

    def _get_database_summary(self, database_path):
        if not database_path.exists():
            return {
                "stored_draw_count": 0,
                "latest_draw_no": None,
            }

        connection = None

        try:
            connection = sqlite3.connect(database_path)
            cursor = connection.cursor()
            cursor.execute(
                """
                SELECT COUNT(*), MAX(draw_no)
                FROM lotto_winning_numbers
                """
            )
            row = cursor.fetchone()

            return {
                "stored_draw_count": int(row[0] or 0),
                "latest_draw_no": (
                    int(row[1])
                    if row[1] is not None
                    else None
                ),
            }
        except sqlite3.Error:
            return {
                "stored_draw_count": 0,
                "latest_draw_no": None,
            }
        finally:
            if connection is not None:
                connection.close()

    def _get_os_name(self):
        system = platform.system()
        release = platform.release()

        if system and release:
            return f"{system} {release}"

        return system or "확인 불가"