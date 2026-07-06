from src.db.database import init_db
from src.collector.excel_collector import ExcelCollector
from src.analyzer.frequency_analyzer import FrequencyAnalyzer
from src.analyzer.trend_analyzer import TrendAnalyzer
from src.analyzer.pair_analyzer import PairAnalyzer
from src.analyzer.triple_analyzer import TripleAnalyzer
from src.analyzer.pattern_analyzer import PatternAnalyzer
from src.analyzer.missing_number_analyzer import MissingNumberAnalyzer
from src.analyzer.recommendation_engine import RecommendationEngine
from src.analyzer.backtest_engine import BacktestEngine

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
    missing_number_analyzer = MissingNumberAnalyzer()
    recommendation_engine = RecommendationEngine()
    backtest_engine = BacktestEngine()    

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
    for item in pair_analyzer.get_top_pairs(20):
        pair = item["pair"]
        print(f"{pair[0]}번 + {pair[1]}번 - {item['count']}회 ({item['rate']}%)")

    print("\n34번과 같이 많이 나온 번호 TOP 10")
    for item in pair_analyzer.get_pairs_with_number(34, 10):
        print(
            f"34번 + {item['pair_number']}번 - "
            f"{item['count']}회 ({item['rate']}%)"
        )

    print("\nTriple TOP 20")
    for item in triple_analyzer.get_top_triples(20):
        triple = item["triple"]
        print(
            f"{triple[0]}번 + "
            f"{triple[1]}번 + "
            f"{triple[2]}번 - "
            f"{item['count']}회 ({item['rate']}%)"
        )
        
    print("\n장기 미출현 번호 TOP 10")
    for item in missing_number_analyzer.get_top_missing_numbers(10):
        print(
            f"{item['number']}번 - "
            f"{item['missing_draws']}회 미출현 "
            f"(마지막 출현: {item['last_seen_draw_no']}회)"
        )
        
    print("\n추천 점수 TOP 15")
    for item in recommendation_engine.calculate_number_scores()[:15]:
        print(
            f"{item['number']}번 - "
            f"총점 {item['total_score']} | "
            f"전체빈도 {item['frequency_score']} | "
            f"최근30회 {item['recent_30_score']} | "
            f"최근100회 {item['recent_100_score']} | "
            f"상승 {item['rising_score']} | "
            f"장기미출현 {item['missing_score']}"
        )        

    print("\n추천번호 10세트")
    recommendations = recommendation_engine.generate_recommendations(10)

    for index, item in enumerate(recommendations, start=1):
        pattern = item["pattern"]

        print(
            f"{index}. {item['numbers']} | "
            f"총점 {item['total_score']} | "
            f"홀짝 {pattern['odd_even']['pattern']} | "
            f"고저 {pattern['low_high']['pattern']} | "
            f"합계 {pattern['sum']['sum']} | "
            f"끝수 고유 {pattern['last_digit']['unique_digit_count']}개 | "
            f"연속쌍 {pattern['consecutive']['pair_count']}개"
        )
        
    print("\n최근 10회차 반복 백테스트")
    backtest_results = backtest_engine.run_recent_backtests(test_count=10, recommend_count=10)
    summary = backtest_engine.summarize_backtest_results(backtest_results)

    print(
        f"검증 회차 수: {summary['test_count']}회 | "
        f"추천 조합 수: {summary['total_recommendation_count']}세트 | "
        f"최대 일치 개수: {summary['max_match_count']}개"
    )

    print("\n등수 요약")
    for rank, count in summary["rank_counts"].items():
        print(f"{rank}: {count}건")

    print("\n회차별 최고 결과")
    for item in backtest_results:
        best = item["best_result"]

        print(
            f"{item['target_draw_no']}회 | "
            f"학습: {item['train_max_draw_no']}회까지 | "
            f"당첨: {item['winning_numbers']} + 보너스 {item['bonus_number']} | "
            f"최고 추천: {best['recommended_numbers']} | "
            f"일치 {best['match_count']}개 | "
            f"보너스 {'일치' if best['bonus_match'] else '불일치'} | "
            f"결과 {best['rank'] if best['rank'] else '낙첨'}"
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