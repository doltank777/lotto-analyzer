from src.db.database import init_db
from src.collector.excel_collector import ExcelCollector
from src.analyzer.lotto_analyzer import LottoAnalyzer


def main():
    print("로또 분석기 프로젝트 시작")

    init_db()
    print("DB 초기화 완료")

    collector = ExcelCollector()
    saved_count = collector.import_excel()
    print(f"엑셀 당첨번호 저장 완료: {saved_count}건")

    analyzer = LottoAnalyzer()

    analyzer.print_top_bottom_frequency()

    recent_ranges = [10, 30, 50, 100]

    for recent_count in recent_ranges:
        analyzer.print_recent_frequency(recent_count)


if __name__ == "__main__":
    main()