from src.db.database import get_connection


class DrawSearchService:
    def get_draw_by_no(self, draw_no):
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                draw_no,
                number1,
                number2,
                number3,
                number4,
                number5,
                number6,
                bonus_number
            FROM lotto_winning_numbers
            WHERE draw_no = ?
        """, (draw_no,))

        row = cursor.fetchone()
        conn.close()

        if row is None:
            return None

        return {
            "draw_no": row[0],
            "numbers": [row[1], row[2], row[3], row[4], row[5], row[6]],
            "bonus_number": row[7]
        }