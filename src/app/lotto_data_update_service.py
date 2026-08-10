from src.db.database import (
    get_existing_draw_nos,
    get_latest_draw_no,
    save_new_lotto_draws,
)


class LottoDataValidationError(ValueError):
    """
    외부에서 수집한 로또 당첨번호 데이터의
    검증에 실패했을 때 발생하는 예외.
    """

    pass


class LottoDataUpdateService:
    """
    로또 당첨 데이터 업데이트를 담당하는 Service.

    역할

    1. 현재 DB 최신 회차 확인
    2. 외부 Collector 최신 회차 확인
    3. 신규 회차 데이터 수집
    4. 데이터 검증
    5. 중복 회차 제거
    6. Transaction 기반 DB 저장

    GUI에서는 Collector나 DB를 직접 호출하지 않고
    이 Service만 호출한다.
    """

    def __init__(self, collector=None):
        self.collector = collector

    def get_current_latest_draw_no(self):
        """
        현재 DB에 저장된 최신 회차를 반환한다.
        """

        return get_latest_draw_no()

    def validate_draw_data(self, draw):
        """
        단일 회차의 당첨번호 데이터를 검증하고
        정규화된 형태로 반환한다.

        검증 조건

        - 데이터는 dict
        - draw_no는 1 이상의 정수
        - 일반번호 정확히 6개
        - 일반번호는 모두 정수
        - 일반번호 범위 1~45
        - 일반번호 중복 없음
        - 보너스번호 정수
        - 보너스번호 범위 1~45
        - 보너스번호와 일반번호 중복 없음

        Returns
        -------
        dict
            검증 완료된 데이터
        """

        if not isinstance(draw, dict):
            raise LottoDataValidationError(
                "당첨번호 데이터 형식이 올바르지 않습니다."
            )

        required_keys = {
            "draw_no",
            "numbers",
            "bonus_number",
        }

        missing_keys = required_keys - set(draw.keys())

        if missing_keys:
            missing_text = ", ".join(
                sorted(missing_keys)
            )

            raise LottoDataValidationError(
                f"필수 데이터가 없습니다: {missing_text}"
            )

        draw_no = draw["draw_no"]
        numbers = draw["numbers"]
        bonus_number = draw["bonus_number"]

        self._validate_draw_no(draw_no)
        self._validate_numbers(numbers)
        self._validate_bonus_number(
            bonus_number,
            numbers,
        )

        return {
            "draw_no": int(draw_no),
            "numbers": [
                int(number)
                for number in numbers
            ],
            "bonus_number": int(bonus_number),
        }

    def _validate_draw_no(self, draw_no):
        """
        회차 번호를 검증한다.
        """

        if (
            isinstance(draw_no, bool)
            or not isinstance(draw_no, int)
        ):
            raise LottoDataValidationError(
                "회차 번호는 정수여야 합니다."
            )

        if draw_no <= 0:
            raise LottoDataValidationError(
                "회차 번호는 1 이상이어야 합니다."
            )

    def _validate_numbers(self, numbers):
        """
        일반 당첨번호 6개를 검증한다.
        """

        if not isinstance(
            numbers,
            (list, tuple),
        ):
            raise LottoDataValidationError(
                "일반 당첨번호는 목록 형식이어야 합니다."
            )

        if len(numbers) != 6:
            raise LottoDataValidationError(
                "일반 당첨번호는 정확히 6개여야 합니다."
            )

        for number in numbers:
            if (
                isinstance(number, bool)
                or not isinstance(number, int)
            ):
                raise LottoDataValidationError(
                    "일반 당첨번호는 모두 정수여야 합니다."
                )

            if number < 1 or number > 45:
                raise LottoDataValidationError(
                    "일반 당첨번호는 1~45 범위여야 합니다."
                )

        if len(set(numbers)) != 6:
            raise LottoDataValidationError(
                "일반 당첨번호에 중복된 번호가 있습니다."
            )

    def _validate_bonus_number(
        self,
        bonus_number,
        numbers,
    ):
        """
        보너스 번호를 검증한다.
        """

        if (
            isinstance(bonus_number, bool)
            or not isinstance(bonus_number, int)
        ):
            raise LottoDataValidationError(
                "보너스 번호는 정수여야 합니다."
            )

        if bonus_number < 1 or bonus_number > 45:
            raise LottoDataValidationError(
                "보너스 번호는 1~45 범위여야 합니다."
            )

        if bonus_number in numbers:
            raise LottoDataValidationError(
                "보너스 번호가 일반 당첨번호와 중복됩니다."
            )

    def validate_draws(self, draws):
        """
        여러 회차의 데이터를 한 번에 검증한다.

        하나라도 검증에 실패하면 예외가 발생하며
        DB에는 아무 데이터도 저장하지 않는다.
        """

        if draws is None:
            raise LottoDataValidationError(
                "당첨번호 데이터가 없습니다."
            )

        draws = list(draws)

        validated_draws = []

        for index, draw in enumerate(
            draws,
            start=1,
        ):
            try:
                validated_draw = self.validate_draw_data(
                    draw
                )

            except LottoDataValidationError as error:
                draw_no = None

                if isinstance(draw, dict):
                    draw_no = draw.get("draw_no")

                if draw_no is not None:
                    location = f"{draw_no}회"
                else:
                    location = f"{index}번째 데이터"

                raise LottoDataValidationError(
                    f"{location} 검증 실패: {error}"
                ) from error

            validated_draws.append(
                validated_draw
            )

        return validated_draws

    def _remove_duplicate_draws(
        self,
        draws,
    ):
        """
        같은 업데이트 데이터 안에 중복된 회차가 있는 경우
        최초 데이터만 유지한다.
        """

        unique_draws = []
        seen_draw_nos = set()

        for draw in draws:
            draw_no = draw["draw_no"]

            if draw_no in seen_draw_nos:
                continue

            seen_draw_nos.add(draw_no)
            unique_draws.append(draw)

        return unique_draws

    def update_draws(self, draws):
        """
        외부에서 전달받은 당첨번호 데이터를 검증한 뒤
        신규 회차만 DB에 저장한다.

        이 메서드는 Collector와 관계없이 사용할 수 있으므로
        향후 수동 회차 추가 기능에서도 재사용할 수 있다.

        Returns
        -------
        dict
            업데이트 처리 결과
        """

        latest_before = self.get_current_latest_draw_no()

        raw_draws = list(draws)

        validated_draws = self.validate_draws(
            raw_draws
        )

        unique_draws = self._remove_duplicate_draws(
            validated_draws
        )

        unique_draws.sort(
            key=lambda item: item["draw_no"]
        )

        incoming_draw_nos = [
            draw["draw_no"]
            for draw in unique_draws
        ]

        existing_draw_nos = get_existing_draw_nos(
            incoming_draw_nos
        )

        new_draws = [
            draw
            for draw in unique_draws
            if draw["draw_no"] not in existing_draw_nos
        ]

        inserted_draw_nos = save_new_lotto_draws(
            new_draws
        )

        latest_after = self.get_current_latest_draw_no()

        return {
            "latest_draw_no_before": latest_before,
            "latest_draw_no_after": latest_after,
            "received_count": len(raw_draws),
            "validated_count": len(validated_draws),
            "unique_count": len(unique_draws),
            "existing_count": len(existing_draw_nos),
            "inserted_count": len(inserted_draw_nos),
            "skipped_count": (
                len(raw_draws)
                - len(inserted_draw_nos)
            ),
            "inserted_draw_nos": inserted_draw_nos,
        }

    def get_update_plan(self):
        """
        현재 DB와 외부 Collector의 최신 회차를 비교하여
        업데이트가 필요한 범위를 계산한다.

        STEP17-2에서 실제 Collector를 연결하면
        GUI의 '업데이트 확인' 기능에서 사용할 수 있다.
        """

        collector = self._require_collector()

        current_latest_draw_no = (
            self.get_current_latest_draw_no()
        )

        source_latest_draw_no = (
            collector.fetch_latest_draw_no()
        )

        self._validate_source_latest_draw_no(
            source_latest_draw_no
        )

        if (
            source_latest_draw_no
            <= current_latest_draw_no
        ):
            return {
                "current_latest_draw_no": (
                    current_latest_draw_no
                ),
                "source_latest_draw_no": (
                    source_latest_draw_no
                ),
                "update_available": False,
                "start_draw_no": None,
                "end_draw_no": None,
                "update_count": 0,
            }

        start_draw_no = (
            current_latest_draw_no + 1
        )

        return {
            "current_latest_draw_no": (
                current_latest_draw_no
            ),
            "source_latest_draw_no": (
                source_latest_draw_no
            ),
            "update_available": True,
            "start_draw_no": start_draw_no,
            "end_draw_no": source_latest_draw_no,
            "update_count": (
                source_latest_draw_no
                - current_latest_draw_no
            ),
        }

    def update_from_collector(self):
        """
        Collector를 사용하여 최신 신규 회차를 조회하고
        DB에 저장한다.

        STEP17-2에서 실제 웹 Collector가 구현되면
        이 메서드가 자동 업데이트의 핵심 진입점이 된다.
        """

        collector = self._require_collector()

        plan = self.get_update_plan()

        if not plan["update_available"]:
            return {
                "current_latest_draw_no": (
                    plan["current_latest_draw_no"]
                ),
                "source_latest_draw_no": (
                    plan["source_latest_draw_no"]
                ),
                "latest_draw_no_before": (
                    plan["current_latest_draw_no"]
                ),
                "latest_draw_no_after": (
                    plan["current_latest_draw_no"]
                ),
                "received_count": 0,
                "validated_count": 0,
                "unique_count": 0,
                "existing_count": 0,
                "inserted_count": 0,
                "skipped_count": 0,
                "inserted_draw_nos": [],
            }

        start_draw_no = plan["start_draw_no"]
        end_draw_no = plan["end_draw_no"]

        draws = collector.fetch_draws(
            start_draw_no,
            end_draw_no,
        )

        draws = list(draws)

        self._validate_collected_range(
            draws,
            start_draw_no,
            end_draw_no,
        )

        result = self.update_draws(draws)

        result.update(
            {
                "current_latest_draw_no": (
                    plan["current_latest_draw_no"]
                ),
                "source_latest_draw_no": (
                    plan["source_latest_draw_no"]
                ),
            }
        )

        return result

    def _validate_collected_range(
        self,
        draws,
        start_draw_no,
        end_draw_no,
    ):
        """
        Collector가 요청한 모든 회차를 빠짐없이 반환했는지
        DB 저장 전에 확인한다.

        일부 회차만 수집된 상태에서 부분 저장되는 것을 방지한다.
        """

        validated_draws = self.validate_draws(
            draws
        )

        expected_draw_nos = set(
            range(
                start_draw_no,
                end_draw_no + 1,
            )
        )

        actual_draw_nos = [
            draw["draw_no"]
            for draw in validated_draws
        ]

        actual_draw_no_set = set(
            actual_draw_nos
        )

        if len(actual_draw_nos) != len(
            actual_draw_no_set
        ):
            raise LottoDataValidationError(
                "수집 데이터에 중복된 회차가 있습니다."
            )

        missing_draw_nos = (
            expected_draw_nos
            - actual_draw_no_set
        )

        unexpected_draw_nos = (
            actual_draw_no_set
            - expected_draw_nos
        )

        if missing_draw_nos:
            missing_text = ", ".join(
                str(draw_no)
                for draw_no in sorted(
                    missing_draw_nos
                )
            )

            raise LottoDataValidationError(
                "수집되지 않은 회차가 있습니다: "
                f"{missing_text}"
            )

        if unexpected_draw_nos:
            unexpected_text = ", ".join(
                str(draw_no)
                for draw_no in sorted(
                    unexpected_draw_nos
                )
            )

            raise LottoDataValidationError(
                "요청 범위에 포함되지 않은 회차가 "
                f"수집되었습니다: {unexpected_text}"
            )

    def _validate_source_latest_draw_no(
        self,
        draw_no,
    ):
        """
        Collector가 반환한 최신 회차 번호를 검증한다.
        """

        if (
            isinstance(draw_no, bool)
            or not isinstance(draw_no, int)
        ):
            raise LottoDataValidationError(
                "외부 데이터의 최신 회차 번호가 "
                "올바르지 않습니다."
            )

        if draw_no <= 0:
            raise LottoDataValidationError(
                "외부 데이터의 최신 회차 번호는 "
                "1 이상이어야 합니다."
            )

    def _require_collector(self):
        """
        Collector가 설정되어 있는지 확인한다.
        """

        if self.collector is None:
            raise RuntimeError(
                "당첨번호 데이터 Collector가 "
                "설정되어 있지 않습니다."
            )

        return self.collector