import sys
from pathlib import Path

from src.collector.excel_collector import ExcelCollector
from src.db.database import (
    get_latest_draw_no,
    init_db,
)
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


def import_initial_lotto_data_if_needed(base_dir):
    """
    DB에 당첨 데이터가 하나도 없는 경우에만
    lotto_numbers.xlsx 파일을 이용하여 초기 데이터를 구축한다.

    기존 데이터가 존재하는 경우에는 Excel Import를 실행하지 않는다.

    이를 통해 프로그램 실행 시마다 Excel 데이터가
    DB에 반복적으로 덮어써지는 것을 방지한다.

    개발환경에서는 lotto_numbers.xlsx를
    초기 DB 구축용 원본 데이터로 사용할 수 있다.

    배포환경에서는 database/lotto.db를 사용하므로
    lotto_numbers.xlsx 파일이 없어도 정상 실행된다.
    """

    latest_draw_no = get_latest_draw_no()

    if latest_draw_no > 0:
        return 0

    excel_path = base_dir / "lotto_numbers.xlsx"

    if not excel_path.exists():
        return 0

    collector = ExcelCollector(excel_path)

    return collector.import_excel()


def main():
    base_dir = get_base_dir()

    init_db()

    import_initial_lotto_data_if_needed(base_dir)

    app = MainWindow()
    app.run()


if __name__ == "__main__":
    main()