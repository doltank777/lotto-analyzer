from collections import Counter

from src.db.database import get_connection


def get_all_winning_numbers():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT number1, number2, number3, number4, number5, number6
        FROM lotto_winning_numbers
        ORDER BY draw_no ASC
    """)

    rows = cursor.fetchall()
    conn.close()

    return rows


def analyze_number_frequency():
    rows = get_all_winning_numbers()

    counter = Counter()

    for row in rows:
        counter.update(row)

    total_draws = len(rows)

    result = []

    for number in range(1, 46):
        count = counter[number]
        rate = round((count / total_draws) * 100, 2) if total_draws > 0 else 0

        result.append({
            "number": number,
            "count": count,
            "rate": rate
        })

    return result


def print_frequency_summary():
    frequency = analyze_number_frequency()

    top_10 = sorted(frequency, key=lambda x: x["count"], reverse=True)[:10]
    bottom_10 = sorted(frequency, key=lambda x: x["count"])[:10]

    print("\n가장 많이 나온 번호 TOP 10")
    for item in top_10:
        print(f"{item['number']}번 - {item['count']}회 ({item['rate']}%)")

    print("\n가장 적게 나온 번호 TOP 10")
    for item in bottom_10:
        print(f"{item['number']}번 - {item['count']}회 ({item['rate']}%)")