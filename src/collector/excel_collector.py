import pandas as pd
import sqlite3


class ExcelCollector:
    def __init__(self, excel_path="lotto_numbers.xlsx", db_path="database/lotto.db"):
        self.excel_path = excel_path
        self.db_path = db_path

    def import_excel(self):
        df = pd.read_excel(self.excel_path)

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        saved_count = 0

        for _, row in df.iterrows():
            draw_no = int(row["회차"])
            draw_date = str(row["추첨일"])
            number1 = int(row["번호1"])
            number2 = int(row["번호2"])
            number3 = int(row["번호3"])
            number4 = int(row["번호4"])
            number5 = int(row["번호5"])
            number6 = int(row["번호6"])
            bonus_number = int(row["보너스"])

            cursor.execute("""
                INSERT OR REPLACE INTO lotto_winning_numbers (
                    draw_no,
                    draw_date,
                    number1,
                    number2,
                    number3,
                    number4,
                    number5,
                    number6,
                    bonus_number
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                draw_no,
                draw_date,
                number1,
                number2,
                number3,
                number4,
                number5,
                number6,
                bonus_number
            ))

            saved_count += 1

        conn.commit()
        conn.close()

        return saved_count