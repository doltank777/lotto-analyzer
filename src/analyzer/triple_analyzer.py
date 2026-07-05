# Triple 분석
from collections import Counter
from itertools import combinations

from src.db.database import get_connection


class TripleAnalyzer:
    def get_all_draw_numbers(self):
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT draw_no, number1, number2, number3, number4, number5, number6
            FROM lotto_winning_numbers
            ORDER BY draw_no DESC
        """)

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

        for draw in draws:
            numbers = sorted(draw["numbers"])

            for triple in combinations(numbers, 3):
                triple_counter[triple] += 1

        return triple_counter.most_common()

    def get_top_triples(self, top_count=20):
        return self.analyze_triple_frequency()[:top_count]

    def print_top_triples(self, top_count=20):
        top_triples = self.get_top_triples(top_count)

        print(f"\n3개 번호 동시 출현 TOP {top_count}")
        for triple, count in top_triples:
            print(f"{triple[0]}번 + {triple[1]}번 + {triple[2]}번 - {count}회")