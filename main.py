from src.db.database import init_db


def main():
    print("로또 분석기 프로젝트 시작")
    init_db()
    print("DB 초기화 완료")


if __name__ == "__main__":
    main()