# 상승/하락 추세import sqlite3
from collections import Counter


class TrendAnalyzer:
    def __init__(self, db_path="database/lotto.db"):
        self.db_path = db_path

    def _get_connection(self):
        return sqlite3.connect(self.db_path)

    def get_recent_draws(self, limit):
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT number1, number2, number3, number4, number5, number6
            FROM lotto_winning_numbers
            ORDER BY draw_no DESC
            LIMIT ?
        """, (limit,))

        rows = cursor.fetchall()
        conn.close()

        numbers = []
        for row in rows:
            numbers.extend(row)

        return numbers

    def get_hot_numbers(self, recent_count=30, limit=10):
        numbers = self.get_recent_draws(recent_count)
        counter = Counter(numbers)

        result = []

        for number in range(1, 46):
            result.append({
                "number": number,
                "count": counter.get(number, 0)
            })

        return sorted(
            result,
            key=lambda x: x["count"],
            reverse=True
        )[:limit]

    def get_cold_numbers(self, recent_count=30, limit=10):
        numbers = self.get_recent_draws(recent_count)
        counter = Counter(numbers)

        result = []

        for number in range(1, 46):
            result.append({
                "number": number,
                "count": counter.get(number, 0)
            })

        return sorted(
            result,
            key=lambda x: x["count"]
        )[:limit]

    def get_rising_numbers(self, limit=10, recent_count=30, previous_count=30):
        recent_numbers = self.get_recent_draws(recent_count)

        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT number1, number2, number3, number4, number5, number6
            FROM lotto_winning_numbers
            ORDER BY draw_no DESC
            LIMIT ? OFFSET ?
        """, (previous_count, recent_count))

        rows = cursor.fetchall()
        conn.close()

        previous_numbers = []
        for row in rows:
            previous_numbers.extend(row)

        recent_counter = Counter(recent_numbers)
        previous_counter = Counter(previous_numbers)

        result = []

        for number in range(1, 46):
            recent_value = recent_counter.get(number, 0)
            previous_value = previous_counter.get(number, 0)
            diff = recent_value - previous_value

            result.append({
                "number": number,
                "recent_count": recent_value,
                "previous_count": previous_value,
                "diff": diff
            })

        return sorted(
            result,
            key=lambda x: x["diff"],
            reverse=True
        )[:limit]

    def get_falling_numbers(self, limit=10, recent_count=30, previous_count=30):
        recent_numbers = self.get_recent_draws(recent_count)

        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT number1, number2, number3, number4, number5, number6
            FROM lotto_winning_numbers
            ORDER BY draw_no DESC
            LIMIT ? OFFSET ?
        """, (previous_count, recent_count))

        rows = cursor.fetchall()
        conn.close()

        previous_numbers = []
        for row in rows:
            previous_numbers.extend(row)

        recent_counter = Counter(recent_numbers)
        previous_counter = Counter(previous_numbers)

        result = []

        for number in range(1, 46):
            recent_value = recent_counter.get(number, 0)
            previous_value = previous_counter.get(number, 0)
            diff = recent_value - previous_value

            result.append({
                "number": number,
                "recent_count": recent_value,
                "previous_count": previous_value,
                "diff": diff
            })

        return sorted(
            result,
            key=lambda x: x["diff"]
        )[:limit]