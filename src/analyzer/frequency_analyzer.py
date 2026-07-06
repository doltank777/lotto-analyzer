import sqlite3
from collections import Counter


class FrequencyAnalyzer:
    def __init__(self, db_path="database/lotto.db", max_draw_no=None):
        self.db_path = db_path
        self.max_draw_no = max_draw_no

    def _get_connection(self):
        return sqlite3.connect(self.db_path)

    def get_all_numbers(self):
        conn = self._get_connection()
        cursor = conn.cursor()

        if self.max_draw_no is None:
            cursor.execute("""
                SELECT number1, number2, number3, number4, number5, number6
                FROM lotto_winning_numbers
                ORDER BY draw_no ASC
            """)
        else:
            cursor.execute("""
                SELECT number1, number2, number3, number4, number5, number6
                FROM lotto_winning_numbers
                WHERE draw_no <= ?
                ORDER BY draw_no ASC
            """, (self.max_draw_no,))

        rows = cursor.fetchall()
        conn.close()

        numbers = []
        for row in rows:
            numbers.extend(row)

        return numbers

    def get_total_draw_count(self):
        conn = self._get_connection()
        cursor = conn.cursor()

        if self.max_draw_no is None:
            cursor.execute("""
                SELECT COUNT(*)
                FROM lotto_winning_numbers
            """)
        else:
            cursor.execute("""
                SELECT COUNT(*)
                FROM lotto_winning_numbers
                WHERE draw_no <= ?
            """, (self.max_draw_no,))

        total_draw_count = cursor.fetchone()[0]
        conn.close()

        return total_draw_count

    def get_number_frequency(self):
        numbers = self.get_all_numbers()
        counter = Counter(numbers)
        total_draw_count = self.get_total_draw_count()

        result = []

        for number in range(1, 46):
            count = counter.get(number, 0)
            rate = round((count / total_draw_count) * 100, 2) if total_draw_count > 0 else 0

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