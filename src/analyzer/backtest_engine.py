from src.db.database import get_connection
from src.analyzer.recommendation_engine import RecommendationEngine


class BacktestEngine:
    def __init__(self):
        self.recommendation_engine = RecommendationEngine()

    def get_all_draws(self):
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT draw_no, number1, number2, number3, number4, number5, number6, bonus_number
            FROM lotto_winning_numbers
            ORDER BY draw_no ASC
        """)

        rows = cursor.fetchall()
        conn.close()

        return [
            {
                "draw_no": row[0],
                "numbers": sorted(list(row[1:7])),
                "bonus_number": row[7]
            }
            for row in rows
        ]

    def compare_numbers(self, recommended_numbers, winning_numbers, bonus_number):
        match_count = len(set(recommended_numbers) & set(winning_numbers))
        bonus_match = bonus_number in recommended_numbers

        rank = None

        if match_count == 6:
            rank = "1등"
        elif match_count == 5 and bonus_match:
            rank = "2등"
        elif match_count == 5:
            rank = "3등"
        elif match_count == 4:
            rank = "4등"
        elif match_count == 3:
            rank = "5등"

        return {
            "match_count": match_count,
            "bonus_match": bonus_match,
            "rank": rank
        }

    def run_latest_backtest(self, recommend_count=10):
        draws = self.get_all_draws()

        if not draws:
            return None

        latest_draw = draws[-1]

        recommendations = self.recommendation_engine.generate_recommendations(recommend_count)

        results = []

        for item in recommendations:
            compare_result = self.compare_numbers(
                item["numbers"],
                latest_draw["numbers"],
                latest_draw["bonus_number"]
            )

            results.append({
                "draw_no": latest_draw["draw_no"],
                "recommended_numbers": item["numbers"],
                "winning_numbers": latest_draw["numbers"],
                "bonus_number": latest_draw["bonus_number"],
                "match_count": compare_result["match_count"],
                "bonus_match": compare_result["bonus_match"],
                "rank": compare_result["rank"],
                "score": item["total_score"]
            })

        return results