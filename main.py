from src.db.database import init_db
from src.collector.excel_collector import ExcelCollector
from src.gui.main_window import MainWindow


def main():
    init_db()

    collector = ExcelCollector("lotto_numbers.xlsx")
    collector.import_excel()

    app = MainWindow()
    app.run()


if __name__ == "__main__":
    main()