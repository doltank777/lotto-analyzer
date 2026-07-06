import sqlite3
from collections import Counter


class PatternAnalyzer:
    def __init__(self, db_path="database/lotto.db", max_draw_no=None):
        self.db_path = db_path
        self.max_draw_no = max_draw_no

    def _get_connection(self):
        return sqlite3.connect(self.db_path)

    def get_all_draws(self):
        conn = self._get_connection()
        cursor = conn.cursor()

        if self.max_draw_no is None:
            cursor.execute("""
                SELECT draw_no, number1, number2, number3, number4, number5, number6
                FROM lotto_winning_numbers
                ORDER BY draw_no ASC
            """)
        else:
            cursor.execute("""
                SELECT draw_no, number1, number2, number3, number4, number5, number6
                FROM lotto_winning_numbers
                WHERE draw_no <= ?
                ORDER BY draw_no ASC
            """, (self.max_draw_no,))

        rows = cursor.fetchall()
        conn.close()

        return [
            {
                "draw_no": row[0],
                "numbers": sorted(list(row[1:7]))
            }
            for row in rows
        ]

    def analyze_single_draw_pattern(self, numbers):
        numbers = sorted(numbers)

        return {
            "odd_even": self.get_odd_even_pattern(numbers),
            "low_high": self.get_low_high_pattern(numbers),
            "sum": self.get_sum_pattern(numbers),
            "last_digit": self.get_last_digit_pattern(numbers),
            "consecutive": self.get_consecutive_pattern(numbers),
        }

    def get_odd_even_pattern(self, numbers):
        odd_count = sum(1 for number in numbers if number % 2 == 1)
        even_count = len(numbers) - odd_count

        return {
            "odd_count": odd_count,
            "even_count": even_count,
            "pattern": f"{odd_count}:{even_count}"
        }

    def get_low_high_pattern(self, numbers):
        low_count = sum(1 for number in numbers if number <= 22)
        high_count = len(numbers) - low_count

        return {
            "low_count": low_count,
            "high_count": high_count,
            "pattern": f"{low_count}:{high_count}"
        }

    def get_sum_pattern(self, numbers):
        total_sum = sum(numbers)

        return {
            "sum": total_sum,
            "range": self.get_sum_range(total_sum)
        }

    def get_sum_range(self, total_sum):
        if total_sum < 80:
            return "80미만"
        elif total_sum < 100:
            return "80~99"
        elif total_sum < 120:
            return "100~119"
        elif total_sum < 140:
            return "120~139"
        elif total_sum < 160:
            return "140~159"
        elif total_sum < 180:
            return "160~179"
        else:
            return "180이상"

    def get_last_digit_pattern(self, numbers):
        last_digits = [number % 10 for number in numbers]
        digit_counter = Counter(last_digits)

        duplicated_digits = {
            digit: count
            for digit, count in digit_counter.items()
            if count >= 2
        }

        return {
            "last_digits": last_digits,
            "unique_digit_count": len(digit_counter),
            "duplicated_digits": duplicated_digits,
            "max_duplicate_count": max(digit_counter.values()) if digit_counter else 0
        }

    def get_consecutive_pattern(self, numbers):
        numbers = sorted(numbers)
        consecutive_pairs = []

        for i in range(len(numbers) - 1):
            if numbers[i + 1] - numbers[i] == 1:
                consecutive_pairs.append((numbers[i], numbers[i + 1]))

        return {
            "has_consecutive": len(consecutive_pairs) > 0,
            "pair_count": len(consecutive_pairs),
            "pairs": consecutive_pairs
        }

    def analyze_odd_even_distribution(self):
        draws = self.get_all_draws()
        counter = Counter()

        for draw in draws:
            pattern = self.get_odd_even_pattern(draw["numbers"])
            counter[pattern["pattern"]] += 1

        return self._to_sorted_distribution(counter)

    def analyze_low_high_distribution(self):
        draws = self.get_all_draws()
        counter = Counter()

        for draw in draws:
            pattern = self.get_low_high_pattern(draw["numbers"])
            counter[pattern["pattern"]] += 1

        return self._to_sorted_distribution(counter)

    def analyze_sum_distribution(self):
        draws = self.get_all_draws()
        counter = Counter()

        for draw in draws:
            pattern = self.get_sum_pattern(draw["numbers"])
            counter[pattern["range"]] += 1

        return self._to_sorted_distribution(counter)

    def analyze_last_digit_distribution(self):
        draws = self.get_all_draws()

        unique_digit_counter = Counter()
        max_duplicate_counter = Counter()
        duplicated_digit_counter = Counter()

        for draw in draws:
            pattern = self.get_last_digit_pattern(draw["numbers"])

            unique_digit_counter[pattern["unique_digit_count"]] += 1
            max_duplicate_counter[pattern["max_duplicate_count"]] += 1

            for digit, count in pattern["duplicated_digits"].items():
                duplicated_digit_counter[digit] += count

        return {
            "unique_digit_count_distribution": self._to_sorted_distribution(unique_digit_counter),
            "max_duplicate_count_distribution": self._to_sorted_distribution(max_duplicate_counter),
            "duplicated_digit_distribution": self._to_sorted_distribution(duplicated_digit_counter)
        }

    def analyze_consecutive_distribution(self):
        draws = self.get_all_draws()
        counter = Counter()

        for draw in draws:
            pattern = self.get_consecutive_pattern(draw["numbers"])
            counter[pattern["pair_count"]] += 1

        return self._to_sorted_distribution(counter)

    def analyze_all_patterns(self):
        return {
            "odd_even": self.analyze_odd_even_distribution(),
            "low_high": self.analyze_low_high_distribution(),
            "sum": self.analyze_sum_distribution(),
            "last_digit": self.analyze_last_digit_distribution(),
            "consecutive": self.analyze_consecutive_distribution()
        }

    def get_recent_pattern_summary(self, limit=30):
        draws = self.get_all_draws()
        recent_draws = draws[-limit:]

        result = []

        for draw in recent_draws:
            result.append({
                "draw_no": draw["draw_no"],
                "numbers": draw["numbers"],
                "pattern": self.analyze_single_draw_pattern(draw["numbers"])
            })

        return result

    def _to_sorted_distribution(self, counter):
        total = sum(counter.values())

        return [
            {
                "pattern": key,
                "count": count,
                "rate": round((count / total) * 100, 2) if total > 0 else 0
            }
            for key, count in sorted(counter.items(), key=lambda x: x[0])
        ]