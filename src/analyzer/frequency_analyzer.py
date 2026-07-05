# 빈도 분석
import sqlite3
from collections import Counter


class FrequencyAnalyzer:
    def __init__(self, db_path="database/lotto.db"):
        self.db_path = db_path

    def _get_connection(self):
        return sqlite3.connect(self.db_path)

    def get_all_numbers(self):
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT number1, number2, number3, number4, number5, number6
            FROM lotto_winning_numbers
            ORDER BY draw_no ASC
        """)

        rows = cursor.fetchall()
        conn.close()

        numbers = []
        for row in rows:
            numbers.extend(row)

        return numbers

    def get_number_frequency(self):
        numbers = self.get_all_numbers()
        counter = Counter(numbers)
        total_draws = len(numbers) // 6

        result = []

        for number in range(1, 46):
            count = counter.get(number, 0)
            rate = round((count / total_draws) * 100, 2) if total_draws > 0 else 0

            result.append({
                "number": number,
                "count": count,
                "rate": rate
            })

        return result

    def get_most_common_numbers(self, limit=10):
        frequencies = self.get_number_frequency()

        return sorted(
            frequencies,
            key=lambda x: x["count"],
            reverse=True
        )[:limit]

    def get_least_common_numbers(self, limit=10):
        frequencies = self.get_number_frequency()

        return sorted(
            frequencies,
            key=lambda x: x["count"]
        )[:limit]