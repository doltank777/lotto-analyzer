from src.db.database import get_connection
from src.analyzer.recommendation_engine import RecommendationEngine


class BacktestEngine:
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

    def get_draw_by_no(self, draw_no):
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT draw_no, number1, number2, number3, number4, number5, number6, bonus_number
            FROM lotto_winning_numbers
            WHERE draw_no = ?
        """, (draw_no,))

        row = cursor.fetchone()
        conn.close()

        if row is None:
            return None

        return {
            "draw_no": row[0],
            "numbers": sorted(list(row[1:7])),
            "bonus_number": row[7]
        }

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

    def run_backtest_for_draw(self, target_draw_no, recommend_count=10):
        target_draw = self.get_draw_by_no(target_draw_no)

        if target_draw is None:
            return None

        train_max_draw_no = target_draw_no - 1
        recommendation_engine = RecommendationEngine(max_draw_no=train_max_draw_no)

        recommendations = recommendation_engine.generate_recommendations(recommend_count)

        results = []

        for item in recommendations:
            compare_result = self.compare_numbers(
                item["numbers"],
                target_draw["numbers"],
                target_draw["bonus_number"]
            )

            results.append({
                "target_draw_no": target_draw_no,
                "train_max_draw_no": train_max_draw_no,
                "recommended_numbers": item["numbers"],
                "winning_numbers": target_draw["numbers"],
                "bonus_number": target_draw["bonus_number"],
                "match_count": compare_result["match_count"],
                "bonus_match": compare_result["bonus_match"],
                "rank": compare_result["rank"],
                "score": item["total_score"]
            })

        return results

    def run_recent_backtests(self, test_count=10, recommend_count=10):
        draws = self.get_all_draws()

        if len(draws) < 2:
            return []

        recent_draws = draws[-test_count:]

        all_results = []

        for draw in recent_draws:
            target_draw_no = draw["draw_no"]
            results = self.run_backtest_for_draw(target_draw_no, recommend_count)

            if results:
                best_result = self.get_best_result(results)

                all_results.append({
                    "target_draw_no": target_draw_no,
                    "train_max_draw_no": target_draw_no - 1,
                    "winning_numbers": draw["numbers"],
                    "bonus_number": draw["bonus_number"],
                    "best_result": best_result,
                    "results": results
                })

        return all_results
    
    def run_recent_final_recommendation_backtests(self, test_count=10):
        draws = self.get_all_draws()

        if len(draws) < 2:
            return []

        recent_draws = draws[-test_count:]
        all_results = []

        for draw in recent_draws:
            target_draw_no = draw["draw_no"]
            target_draw = self.get_draw_by_no(target_draw_no)

            if target_draw is None:
                continue

            train_max_draw_no = target_draw_no - 1
            recommendation_engine = RecommendationEngine(max_draw_no=train_max_draw_no)
            recommendations = recommendation_engine.generate_final_recommendations()

            results = []

            for item in recommendations:
                compare_result = self.compare_numbers(
                    item["numbers"],
                    target_draw["numbers"],
                    target_draw["bonus_number"]
                )

                results.append({
                    "target_draw_no": target_draw_no,
                    "train_max_draw_no": train_max_draw_no,
                    "recommended_numbers": item["numbers"],
                    "winning_numbers": target_draw["numbers"],
                    "bonus_number": target_draw["bonus_number"],
                    "match_count": compare_result["match_count"],
                    "bonus_match": compare_result["bonus_match"],
                    "rank": compare_result["rank"],
                    "score": item["total_score"]
                })

            if results:
                best_result = self.get_best_result(results)

                all_results.append({
                    "target_draw_no": target_draw_no,
                    "train_max_draw_no": train_max_draw_no,
                    "winning_numbers": draw["numbers"],
                    "bonus_number": draw["bonus_number"],
                    "best_result": best_result,
                    "results": results
                })

        return all_results
    
    def get_best_result(self, results):
        return sorted(
            results,
            key=lambda x: (
                x["match_count"],
                1 if x["bonus_match"] else 0,
                x["score"]
            ),
            reverse=True
        )[0]

    def summarize_backtest_results(self, backtest_results):
        summary = {
            "test_count": len(backtest_results),
            "total_recommendation_count": 0,
            "rank_counts": {
                "1등": 0,
                "2등": 0,
                "3등": 0,
                "4등": 0,
                "5등": 0,
                "낙첨": 0
            },
            "match_count_distribution": {
                0: 0,
                1: 0,
                2: 0,
                3: 0,
                4: 0,
                5: 0,
                6: 0
            },
            "max_match_count": 0,
            "total_match_count": 0,
            "average_match_count": 0,
            "number_hit_rate": 0,
            "best_total_match_count": 0,
            "best_average_match_count": 0,
            "best_max_match_count": 0
        }

        for backtest in backtest_results:
            best_result = backtest["best_result"]

            summary["best_total_match_count"] += best_result["match_count"]

            if best_result["match_count"] > summary["best_max_match_count"]:
                summary["best_max_match_count"] = best_result["match_count"]

            for result in backtest["results"]:
                summary["total_recommendation_count"] += 1
                summary["total_match_count"] += result["match_count"]

                rank = result["rank"] if result["rank"] else "낙첨"
                summary["rank_counts"][rank] += 1

                summary["match_count_distribution"][result["match_count"]] += 1

                if result["match_count"] > summary["max_match_count"]:
                    summary["max_match_count"] = result["match_count"]

        total_recommendation_count = summary["total_recommendation_count"]

        if total_recommendation_count > 0:
            summary["average_match_count"] = round(
                summary["total_match_count"] / total_recommendation_count,
                2
            )

            summary["number_hit_rate"] = round(
                (summary["total_match_count"] / (total_recommendation_count * 6)) * 100,
                2
            )

        if summary["test_count"] > 0:
            summary["best_average_match_count"] = round(
                summary["best_total_match_count"] / summary["test_count"],
                2
            )

        return summary