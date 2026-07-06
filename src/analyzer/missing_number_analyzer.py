from src.db.database import get_connection


class MissingNumberAnalyzer:
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

    def get_latest_draw_no(self):
        draws = self.get_all_draw_numbers()

        if not draws:
            return None

        return draws[0]["draw_no"]

    def analyze_missing_numbers(self):
        draws = self.get_all_draw_numbers()

        if not draws:
            return []

        latest_draw_no = draws[0]["draw_no"]
        result = []

        for number in range(1, 46):
            last_seen_draw_no = None

            for draw in draws:
                if number in draw["numbers"]:
                    last_seen_draw_no = draw["draw_no"]
                    break

            if last_seen_draw_no is None:
                missing_draws = latest_draw_no
            else:
                missing_draws = latest_draw_no - last_seen_draw_no

            result.append({
                "number": number,
                "missing_draws": missing_draws,
                "last_seen_draw_no": last_seen_draw_no
            })

        return sorted(
            result,
            key=lambda x: x["missing_draws"],
            reverse=True
        )

    def get_top_missing_numbers(self, top_count=10):
        return self.analyze_missing_numbers()[:top_count]