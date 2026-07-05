import time
import requests

from src.db.database import get_connection

LOTTO_API_URL = "https://www.bokgwon.go.kr/nb1.jsp"


def fetch_lotto_number(draw_no: int):
    params = {
        "lottoId": "lotto",
        "method": "drawNo",
        "turn": draw_no
    }

    for retry in range(3):
        try:
            response = requests.get(
                LOTTO_API_URL,
                params=params,
                timeout=30
            )
            response.raise_for_status()

            data = response.json()

            if data.get("result") != "SUCCESS":
                return None

            draw_numbers = data["drawNo"]

            return {
                "draw_no": data["turn"],
                "draw_date": data["endDate"],
                "number1": draw_numbers["1st"],
                "number2": draw_numbers["2nd"],
                "number3": draw_numbers["3rd"],
                "number4": draw_numbers["4th"],
                "number5": draw_numbers["5th"],
                "number6": draw_numbers["6th"],
                "bonus_number": draw_numbers["bounsNo"],
            }

        except requests.RequestException as e:
            print(f"{draw_no}회 요청 실패 {retry + 1}/3: {e}")
            time.sleep(2)

    raise Exception(f"{draw_no}회 데이터를 가져오지 못했습니다.")


def save_lotto_number(lotto_data: dict):
    conn = get_connection()
    cursor = conn.cursor()

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
        lotto_data["draw_no"],
        lotto_data["draw_date"],
        lotto_data["number1"],
        lotto_data["number2"],
        lotto_data["number3"],
        lotto_data["number4"],
        lotto_data["number5"],
        lotto_data["number6"],
        lotto_data["bonus_number"],
    ))

    conn.commit()
    conn.close()


def collect_all_lotto_numbers():
    draw_no = 1
    saved_count = 0

    while True:
        try:
            lotto_data = fetch_lotto_number(draw_no)

            if lotto_data is None:
                print(f"최신 회차까지 수집 완료. 마지막 저장 회차: {draw_no - 1}")
                break

            save_lotto_number(lotto_data)
            saved_count += 1

            print(
                f"{lotto_data['draw_no']}회 저장 완료 "
                f"- {lotto_data['draw_date']} "
                f"[{lotto_data['number1']}, {lotto_data['number2']}, "
                f"{lotto_data['number3']}, {lotto_data['number4']}, "
                f"{lotto_data['number5']}, {lotto_data['number6']}] "
                f"+ 보너스 {lotto_data['bonus_number']}"
            )

            draw_no += 1
            time.sleep(0.05)

        except requests.RequestException as e:
            print(f"{draw_no}회 수집 중 네트워크 오류 발생: {e}")
            break
        except Exception as e:
            print(f"{draw_no}회 수집 중 오류 발생: {e}")
            break

    print(f"총 저장/갱신된 회차 수: {saved_count}")