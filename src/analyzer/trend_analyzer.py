# 상승/하락 추세
from collections import Counter

from src.db.database import get_connection


class TrendAnalyzer:
    def get_numbers_by_limit(self, limit):
        conn = get_connection()
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

    def analyze_trend(self, short_range=30, long_range=100):
        short_numbers = self.get_numbers_by_limit(short_range)
        long_numbers = self.get_numbers_by_limit(long_range)

        short_counter = Counter(short_numbers)
        long_counter = Counter(long_numbers)

        result = []

        for number in range(1, 46):
            short_count = short_counter.get(number, 0)
            long_count = long_counter.get(number, 0)

            short_rate = short_count / short_range
            long_rate = long_count / long_range

            trend_score = short_rate - long_rate

            result.append({
                "number": number,
                "short_count": short_count,
                "long_count": long_count,
                "short_rate": short_rate,
                "long_rate": long_rate,
                "trend_score": trend_score
            })

        return result

    def get_rising_numbers(self, top_count=10):
        result = self.analyze_trend()
        result.sort(key=lambda item: item["trend_score"], reverse=True)
        return result[:top_count]

    def get_falling_numbers(self, top_count=10):
        result = self.analyze_trend()
        result.sort(key=lambda item: item["trend_score"])
        return result[:top_count]

    def print_trend_analysis(self, top_count=10):
        rising_numbers = self.get_rising_numbers(top_count)
        falling_numbers = self.get_falling_numbers(top_count)

        print("\n최근 상승 번호 TOP 10")
        for item in rising_numbers:
            print(
                f"{item['number']}번 - "
                f"최근30회 {item['short_count']}회 / "
                f"최근100회 {item['long_count']}회 / "
                f"상승점수 {item['trend_score']:.3f}"
            )

        print("\n최근 하락 번호 TOP 10")
        for item in falling_numbers:
            print(
                f"{item['number']}번 - "
                f"최근30회 {item['short_count']}회 / "
                f"최근100회 {item['long_count']}회 / "
                f"하락점수 {item['trend_score']:.3f}"
            )