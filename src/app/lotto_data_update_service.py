from src.db.database import (
    draw_exists,
    get_latest_draw_no,
    insert_lotto_draw,
)


class LottoDataValidationError(ValueError):
    """
    사용자가 입력한 로또 당첨번호 데이터의
    검증에 실패했을 때 발생하는 예외.
    """

    pass


class LottoDrawAlreadyExistsError(ValueError):
    """
    등록하려는 회차가 이미 DB에 존재할 때
    발생하는 예외.
    """

    pass


class LottoDataUpdateService:
    """
    로또 당첨 데이터 수동 등록 기능을 담당하는 Service.

    GUI에서는 DB를 직접 호출하지 않고
    이 Service만 사용한다.

    역할

    - 현재 DB 최신 회차 조회
    - 다음 등록 예정 회차 계산
    - 사용자 입력값 변환
    - 당첨번호 데이터 검증
    - 기존 회차 중복 확인
    - 신규 당첨 데이터 저장
    """

    def get_latest_draw_no(self):
        """
        현재 DB에 저장된 최신 회차를 반환한다.
        """

        return get_latest_draw_no()

    def get_next_draw_no(self):
        """
        다음 등록 예정 회차를 반환한다.

        예:
            DB 최신 회차가 1231회라면
            1232를 반환한다.

        DB가 비어 있는 경우 1을 반환한다.
        """

        latest_draw_no = self.get_latest_draw_no()

        return latest_draw_no + 1

    def is_draw_exists(self, draw_no):
        """
        특정 회차가 이미 DB에 존재하는지 확인한다.
        """

        normalized_draw_no = self._normalize_integer(
            draw_no,
            "회차",
        )

        return draw_exists(normalized_draw_no)

    def add_draw(
        self,
        draw_no,
        numbers,
        bonus_number,
    ):
        """
        사용자가 입력한 신규 당첨번호 1개 회차를
        검증 후 DB에 저장한다.

        Parameters
        ----------
        draw_no
            회차 번호

        numbers
            일반 당첨번호 6개

        bonus_number
            보너스 번호

        Returns
        -------
        dict
            {
                "draw_no": 1232,
                "numbers": [1, 2, 3, 4, 5, 6],
                "bonus_number": 7,
                "latest_draw_no": 1232
            }
        """

        draw = self.validate_draw(
            draw_no=draw_no,
            numbers=numbers,
            bonus_number=bonus_number,
        )

        if draw_exists(draw["draw_no"]):
            raise LottoDrawAlreadyExistsError(
                f"{draw['draw_no']}회 당첨 데이터는 "
                "이미 저장되어 있습니다."
            )

        inserted = insert_lotto_draw(
            draw_no=draw["draw_no"],
            numbers=draw["numbers"],
            bonus_number=draw["bonus_number"],
        )

        if not inserted:
            raise LottoDrawAlreadyExistsError(
                f"{draw['draw_no']}회 당첨 데이터는 "
                "이미 저장되어 있습니다."
            )

        return {
            "draw_no": draw["draw_no"],
            "numbers": draw["numbers"],
            "bonus_number": draw["bonus_number"],
            "latest_draw_no": self.get_latest_draw_no(),
        }

    def validate_draw(
        self,
        draw_no,
        numbers,
        bonus_number,
    ):
        """
        사용자가 입력한 당첨번호 데이터를 검증한다.

        검증 조건

        - 회차는 정수
        - 회차는 1 이상
        - 일반번호는 정확히 6개
        - 일반번호는 모두 정수
        - 일반번호는 1~45
        - 일반번호 중복 없음
        - 보너스번호는 정수
        - 보너스번호는 1~45
        - 보너스번호와 일반번호 중복 없음

        문자열 형태의 GUI 입력값도 정수로 변환한다.

        Returns
        -------
        dict
            검증 및 정규화가 완료된 데이터
        """

        normalized_draw_no = self._normalize_integer(
            draw_no,
            "회차",
        )

        if normalized_draw_no < 1:
            raise LottoDataValidationError(
                "회차는 1 이상이어야 합니다."
            )

        if not isinstance(
            numbers,
            (list, tuple),
        ):
            raise LottoDataValidationError(
                "당첨번호 입력 형식이 올바르지 않습니다."
            )

        if len(numbers) != 6:
            raise LottoDataValidationError(
                "당첨번호는 정확히 6개를 입력해야 합니다."
            )

        normalized_numbers = []

        for index, number in enumerate(
            numbers,
            start=1,
        ):
            normalized_number = self._normalize_integer(
                number,
                f"당첨번호 {index}",
            )

            if (
                normalized_number < 1
                or normalized_number > 45
            ):
                raise LottoDataValidationError(
                    f"당첨번호 {index}는 "
                    "1~45 범위로 입력해야 합니다."
                )

            normalized_numbers.append(
                normalized_number
            )

        if len(set(normalized_numbers)) != 6:
            raise LottoDataValidationError(
                "당첨번호에는 중복된 번호를 "
                "입력할 수 없습니다."
            )

        normalized_bonus_number = (
            self._normalize_integer(
                bonus_number,
                "보너스번호",
            )
        )

        if (
            normalized_bonus_number < 1
            or normalized_bonus_number > 45
        ):
            raise LottoDataValidationError(
                "보너스번호는 1~45 범위로 "
                "입력해야 합니다."
            )

        if normalized_bonus_number in normalized_numbers:
            raise LottoDataValidationError(
                "보너스번호는 일반 당첨번호와 "
                "중복될 수 없습니다."
            )

        return {
            "draw_no": normalized_draw_no,
            "numbers": normalized_numbers,
            "bonus_number": normalized_bonus_number,
        }

    def _normalize_integer(
        self,
        value,
        field_name,
    ):
        """
        GUI 입력값을 정수로 변환한다.

        Tkinter Entry에서 넘어오는 문자열도 처리한다.

        공백 문자열, 소수, 음수 문자열 등
        잘못된 입력은 ValidationError로 변환한다.
        """

        if isinstance(value, bool):
            raise LottoDataValidationError(
                f"{field_name}은 숫자로 입력해주세요."
            )

        if isinstance(value, int):
            return value

        if isinstance(value, str):
            value = value.strip()

            if not value:
                raise LottoDataValidationError(
                    f"{field_name}을 입력해주세요."
                )

            if not value.isdigit():
                raise LottoDataValidationError(
                    f"{field_name}은 숫자로 입력해주세요."
                )

            return int(value)

        raise LottoDataValidationError(
            f"{field_name}은 숫자로 입력해주세요."
        )