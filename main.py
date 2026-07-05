from src.db.database import init_db
from src.collector.excel_collector import collect_from_excel


def main():
    print("로또 분석기 프로젝트 시작")

    init_db()
    print("DB 초기화 완료")

    collect_from_excel("lotto_numbers.xlsx")

    print("작업 완료")


if __name__ == "__main__":
    main()