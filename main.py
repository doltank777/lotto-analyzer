from src.db.database import init_db
from src.collector.excel_collector import ExcelCollector
from src.analyzer.frequency_analyzer import FrequencyAnalyzer
from src.analyzer.trend_analyzer import TrendAnalyzer
from src.analyzer.pair_analyzer import PairAnalyzer
from src.analyzer.triple_analyzer import TripleAnalyzer
from src.analyzer.pattern_analyzer import PatternAnalyzer


def print_distribution(title, distribution):
    print(f"\n{title}")
    for item in distribution:
        print(f"{item['pattern']} - {item['count']}회 ({item['rate']}%)")


def main():
    print("로또 분석기 프로젝트 시작")

    init_db()

    collector = ExcelCollector("lotto_numbers.xlsx")
    saved_count = collector.import_excel()
    print(f"엑셀 당첨번호 저장 완료: {saved_count}건")

    frequency_analyzer = FrequencyAnalyzer()
    trend_analyzer = TrendAnalyzer()
    pair_analyzer = PairAnalyzer()
    triple_analyzer = TripleAnalyzer()
    pattern_analyzer = PatternAnalyzer()

    print("\n가장 많이 나온 번호 TOP 10")
    for item in frequency_analyzer.get_most_common_numbers(10):
        print(f"{item['number']}번 - {item['count']}회 ({item['rate']}%)")

    print("\n가장 적게 나온 번호 TOP 10")
    for item in frequency_analyzer.get_least_common_numbers(10):
        print(f"{item['number']}번 - {item['count']}회 ({item['rate']}%)")

    print("\n최근 30회 Hot Number TOP 10")
    for item in trend_analyzer.get_hot_numbers(30, 10):
        print(f"{item['number']}번 - {item['count']}회")

    print("\n최근 30회 Cold Number TOP 10")
    for item in trend_analyzer.get_cold_numbers(30, 10):
        print(f"{item['number']}번 - {item['count']}회")

    print("\n최근 상승 번호 TOP 10")
    for item in trend_analyzer.get_rising_numbers(10):
        print(
            f"{item['number']}번 - "
            f"이전 {item['previous_count']}회 / 최근 {item['recent_count']}회 / "
            f"상승 {item['diff']}"
        )

    print("\n최근 하락 번호 TOP 10")
    for item in trend_analyzer.get_falling_numbers(10):
        print(
            f"{item['number']}번 - "
            f"이전 {item['previous_count']}회 / 최근 {item['recent_count']}회 / "
            f"하락 {item['diff']}"
        )

    print("\nPair TOP 20")
    for pair, count in pair_analyzer.get_top_pairs(20):
        print(f"{pair[0]}번 + {pair[1]}번 - {count}회")

    print("\n34번과 같이 많이 나온 번호 TOP 10")
    for item in pair_analyzer.get_pairs_with_number(34, 10):
        print(f"34번 + {item['pair_number']}번 - {item['count']}회")

    print("\nTriple TOP 20")
    for triple, count in triple_analyzer.get_top_triples(20):
        print(
            f"{triple[0]}번 + "
            f"{triple[1]}번 + "
            f"{triple[2]}번 - {count}회"
        )

    print("\n최근 30회 패턴 요약")
    recent_patterns = pattern_analyzer.get_recent_pattern_summary(30)

    for item in recent_patterns:
        pattern = item["pattern"]

        print(
            f"{item['draw_no']}회 {item['numbers']} | "
            f"홀짝 {pattern['odd_even']['pattern']} | "
            f"고저 {pattern['low_high']['pattern']} | "
            f"합계 {pattern['sum']['sum']} ({pattern['sum']['range']}) | "
            f"끝수 고유 {pattern['last_digit']['unique_digit_count']}개 | "
            f"연속쌍 {pattern['consecutive']['pair_count']}개"
        )

    all_patterns = pattern_analyzer.analyze_all_patterns()

    print_distribution("전체 홀짝 패턴 분포", all_patterns["odd_even"])
    print_distribution("전체 고저 패턴 분포", all_patterns["low_high"])
    print_distribution("전체 번호합 구간 분포", all_patterns["sum"])
    print_distribution("전체 연속번호 분포", all_patterns["consecutive"])

    print("\n전체 끝수 고유 개수 분포")
    for item in all_patterns["last_digit"]["unique_digit_count_distribution"]:
        print(f"{item['pattern']}개 - {item['count']}회 ({item['rate']}%)")

    print("\n전체 끝수 최대 중복 개수 분포")
    for item in all_patterns["last_digit"]["max_duplicate_count_distribution"]:
        print(f"{item['pattern']}개 - {item['count']}회 ({item['rate']}%)")


if __name__ == "__main__":
    main()