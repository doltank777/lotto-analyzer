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
            draw_no = int(str(row.iloc[1]).replace(",", ""))

            number1 = int(row.iloc[2])
            number2 = int(row.iloc[3])
            number3 = int(row.iloc[4])
            number4 = int(row.iloc[5])
            number5 = int(row.iloc[6])
            number6 = int(row.iloc[7])
            bonus_number = int(row.iloc[8])

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
                None,
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