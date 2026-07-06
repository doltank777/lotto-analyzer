from collections import Counter
from itertools import combinations

from src.db.database import get_connection


class PairAnalyzer:
    def __init__(self, max_draw_no=None):
        self.max_draw_no = max_draw_no

    def get_all_draw_numbers(self):
        conn = get_connection()
        cursor = conn.cursor()

        if self.max_draw_no is None:
            cursor.execute("""
                SELECT draw_no, number1, number2, number3, number4, number5, number6
                FROM lotto_winning_numbers
                ORDER BY draw_no DESC
            """)
        else:
            cursor.execute("""
                SELECT draw_no, number1, number2, number3, number4, number5, number6
                FROM lotto_winning_numbers
                WHERE draw_no <= ?
                ORDER BY draw_no DESC
            """, (self.max_draw_no,))

        rows = cursor.fetchall()
        conn.close()

        result = []

        for row in rows:
            result.append({
                "draw_no": row[0],
                "numbers": list(row[1:])
            })

        return result

    def analyze_pair_frequency(self):
        draws = self.get_all_draw_numbers()
        pair_counter = Counter()
        total_draws = len(draws)

        for draw in draws:
            numbers = sorted(draw["numbers"])

            for pair in combinations(numbers, 2):
                pair_counter[pair] += 1

        result = []

        for pair, count in pair_counter.most_common():
            result.append({
                "pair": pair,
                "count": count,
                "rate": round((count / total_draws) * 100, 2) if total_draws > 0 else 0
            })

        return result

    def get_top_pairs(self, top_count=20):
        return self.analyze_pair_frequency()[:top_count]

    def get_pairs_with_number(self, target_number, top_count=10):
        pair_frequency = self.analyze_pair_frequency()

        result = []

        for item in pair_frequency:
            pair = item["pair"]

            if target_number in pair:
                other_number = pair[0] if pair[1] == target_number else pair[1]

                result.append({
                    "target_number": target_number,
                    "pair_number": other_number,
                    "pair": pair,
                    "count": item["count"],
                    "rate": item["rate"]
                })

        return result[:top_count]

    def print_top_pairs(self, top_count=20):
        top_pairs = self.get_top_pairs(top_count)

        print(f"\n동시 출현 번호쌍 TOP {top_count}")
        for item in top_pairs:
            pair = item["pair"]
            print(f"{pair[0]}번 + {pair[1]}번 - {item['count']}회 ({item['rate']}%)")

    def print_pairs_with_number(self, target_number, top_count=10):
        pairs = self.get_pairs_with_number(target_number, top_count)

        print(f"\n{target_number}번과 같이 많이 나온 번호 TOP {top_count}")
        for item in pairs:
            print(
                f"{target_number}번 + {item['pair_number']}번 - "
                f"{item['count']}회 ({item['rate']}%)"
            )