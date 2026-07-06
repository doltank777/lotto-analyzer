import sys
from pathlib import Path

import pandas as pd

from src.db.database import get_connection


class ExcelCollector:
    def __init__(self, excel_path="lotto_numbers.xlsx"):
        if getattr(sys, "frozen", False):
            base_dir = Path(sys.executable).parent
        else:
            base_dir = Path(__file__).resolve().parents[2]

        self.excel_path = base_dir / excel_path

    def import_excel(self):
        if not self.excel_path.exists():
            raise FileNotFoundError(
                f"엑셀 파일을 찾을 수 없습니다.\n{self.excel_path}"
            )

        df = pd.read_excel(self.excel_path)

        conn = get_connection()
        cursor = conn.cursor()

        saved_count = 0

        for _, row in df.iterrows():
            draw_no = int(str(row.iloc[1]).replace(",", ""))

            numbers = [
                int(row.iloc[2]),
                int(row.iloc[3]),
                int(row.iloc[4]),
                int(row.iloc[5]),
                int(row.iloc[6]),
                int(row.iloc[7]),
            ]

            bonus_number = int(row.iloc[8])

            cursor.execute("""
                INSERT OR REPLACE INTO lotto_winning_numbers (
                    draw_no,
                    number1,
                    number2,
                    number3,
                    number4,
                    number5,
                    number6,
                    bonus_number
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                draw_no,
                numbers[0],
                numbers[1],
                numbers[2],
                numbers[3],
                numbers[4],
                numbers[5],
                bonus_number
            ))

            saved_count += 1

        conn.commit()
        conn.close()

        return saved_count