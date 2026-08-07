import sys
from pathlib import Path

from src.collector.excel_collector import ExcelCollector
from src.db.database import init_db
from src.gui.main_window import MainWindow


def get_base_dir():
    """
    프로그램 기준 디렉터리를 반환한다.

    개발환경:
        lotto-analyzer/

    PyInstaller EXE:
        Lotto Analyzer.exe가 위치한 디렉터리
    """

    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent

    return Path(__file__).resolve().parent


def import_lotto_excel_if_exists(base_dir):
    """
    lotto_numbers.xlsx 파일이 존재하는 경우에만
    당첨번호 데이터를 DB로 가져온다.

    배포 환경에서는 lotto.db만 배포해도
    프로그램이 정상 실행될 수 있도록 한다.
    """

    excel_path = base_dir / "lotto_numbers.xlsx"

    if not excel_path.exists():
        return

    collector = ExcelCollector(excel_path)
    collector.import_excel()


def main():
    base_dir = get_base_dir()

    init_db()

    import_lotto_excel_if_exists(base_dir)

    app = MainWindow()
    app.run()


if __name__ == "__main__":
    main()