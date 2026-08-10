from abc import ABC, abstractmethod


class LottoDataCollector(ABC):
    """
    외부 로또 당첨번호 데이터 수집기의 공통 인터페이스.

    실제 동행복권 데이터 수집 구현은
    STEP17-2에서 이 클래스를 상속하여 추가한다.

    Collector의 역할은 외부 데이터 수집까지만 담당한다.

    데이터 검증과 DB 저장은
    LottoDataUpdateService에서 담당한다.
    """

    @abstractmethod
    def fetch_latest_draw_no(self):
        """
        외부 데이터 소스에서 확인 가능한
        가장 최신 회차 번호를 반환한다.

        Returns
        -------
        int
            최신 회차 번호
        """

        raise NotImplementedError

    @abstractmethod
    def fetch_draw(self, draw_no):
        """
        특정 회차의 당첨번호 데이터를 가져온다.

        Parameters
        ----------
        draw_no : int
            조회할 회차 번호

        Returns
        -------
        dict
            {
                "draw_no": 1232,
                "numbers": [1, 2, 3, 4, 5, 6],
                "bonus_number": 7
            }
        """

        raise NotImplementedError

    def fetch_draws(self, start_draw_no, end_draw_no):
        """
        지정된 회차 범위의 당첨번호 데이터를 가져온다.

        기본 구현에서는 fetch_draw()를 회차별로 호출한다.

        실제 Collector에서 더 효율적인 일괄 조회가 가능하다면
        이 메서드를 Override할 수 있다.
        """

        if start_draw_no > end_draw_no:
            return []

        draws = []

        for draw_no in range(
            start_draw_no,
            end_draw_no + 1,
        ):
            draw = self.fetch_draw(draw_no)
            draws.append(draw)

        return draws