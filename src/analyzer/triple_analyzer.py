from collections import Counter
from itertools import combinations

from src.db.database import get_connection


class TripleAnalyzer:
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

    def analyze_triple_frequency(self):
        draws = self.get_all_draw_numbers()
        triple_counter = Counter()
        total_draws = len(draws)

        for draw in draws:
            numbers = sorted(draw["numbers"])

            for triple in combinations(numbers, 3):
                triple_counter[triple] += 1

        result = []

        for triple, count in triple_counter.most_common():
            result.append({
                "triple": triple,
                "count": count,
                "rate": round((count / total_draws) * 100, 2) if total_draws > 0 else 0
            })

        return result

    def get_top_triples(self, top_count=20):
        return self.analyze_triple_frequency()[:top_count]

    def print_top_triples(self, top_count=20):
        top_triples = self.get_top_triples(top_count)

        print(f"\n3개 번호 동시 출현 TOP {top_count}")
        for item in top_triples:
            triple = item["triple"]
            print(
                f"{triple[0]}번 + "
                f"{triple[1]}번 + "
                f"{triple[2]}번 - "
                f"{item['count']}회 ({item['rate']}%)"
            )