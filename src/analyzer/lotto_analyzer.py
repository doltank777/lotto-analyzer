from collections import Counter

from src.db.database import get_connection


class LottoAnalyzer:
    def get_all_numbers(self, limit=None):
        conn = get_connection()
        cursor = conn.cursor()

        query = """
            SELECT number1, number2, number3, number4, number5, number6
            FROM lotto_winning_numbers
            ORDER BY draw_no DESC
        """

        if limit:
            query += " LIMIT ?"
            cursor.execute(query, (limit,))
        else:
            cursor.execute(query)

        rows = cursor.fetchall()
        conn.close()

        numbers = []
        for row in rows:
            numbers.extend(row)

        return numbers

    def analyze_frequency(self):
        numbers = self.get_all_numbers()
        counter = Counter(numbers)
        return counter.most_common()

    def analyze_recent_frequency(self, recent_count):
        numbers = self.get_all_numbers(limit=recent_count)
        counter = Counter(numbers)

        result = []

        for number in range(1, 46):
            result.append({
                "number": number,
                "count": counter.get(number, 0)
            })

        result.sort(key=lambda item: item["count"], reverse=True)
        return result

    def print_top_bottom_frequency(self, top_count=10):
        frequency = self.analyze_frequency()

        print("\n가장 많이 나온 번호 TOP 10")
        for number, count in frequency[:top_count]:
            print(f"{number}번 - {count}회")

        print("\n가장 적게 나온 번호 TOP 10")
        for number, count in frequency[-top_count:]:
            print(f"{number}번 - {count}회")

    def print_recent_frequency(self, recent_count, top_count=10):
        result = self.analyze_recent_frequency(recent_count)

        print(f"\n최근 {recent_count}회 출현 빈도 TOP {top_count}")
        for item in result[:top_count]:
            print(f"{item['number']}번 - {item['count']}회")

        print(f"\n최근 {recent_count}회 미출현/저출현 번호 TOP {top_count}")
        for item in sorted(result, key=lambda item: item["count"])[:top_count]:
            print(f"{item['number']}번 - {item['count']}회")