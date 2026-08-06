import tkinter as tk
from tkinter import ttk

from src.gui.components import AppCard, SummaryCard
from src.gui.theme import AppTheme


class AboutView(tk.Frame):
    """Lotto Analyzer 프로그램 및 실행환경 정보를 표시하는 화면."""

    def __init__(
        self,
        parent,
        about_service,
        app_name,
        version,
        developer,
        on_log=None,
        on_status=None,
    ):
        super().__init__(
            parent,
            bg=AppTheme.CONTENT_BACKGROUND,
        )

        self.about_service = about_service
        self.app_name = app_name
        self.version = version
        self.developer = developer
        self.on_log = on_log
        self.on_status = on_status

        self.information = (
            self.about_service.get_program_information()
        )

        self.create_widgets()

    def create_widgets(self):
        body = tk.Frame(
            self,
            bg=AppTheme.CONTENT_BACKGROUND,
        )
        body.pack(
            fill="both",
            expand=True,
            padx=24,
            pady=20,
        )

        self._create_page_intro(body)
        self._create_program_card(body)
        self._create_environment_cards(body)
        self._create_detail_card(body)

    def _create_page_intro(self, parent):
        intro = tk.Frame(
            parent,
            bg=AppTheme.CONTENT_BACKGROUND,
        )
        intro.pack(
            fill="x",
            pady=(0, 14),
        )

        tk.Label(
            intro,
            text="프로그램 정보",
            font=AppTheme.FONT_PAGE_TITLE,
            fg=AppTheme.TEXT_PRIMARY,
            bg=AppTheme.CONTENT_BACKGROUND,
            anchor="w",
        ).pack(fill="x")

        tk.Label(
            intro,
            text=(
                "Lotto Analyzer의 버전, 실행환경 및 "
                "데이터베이스 정보를 확인합니다."
            ),
            font=AppTheme.FONT_BODY,
            fg=AppTheme.TEXT_SECONDARY,
            bg=AppTheme.CONTENT_BACKGROUND,
            anchor="w",
        ).pack(
            fill="x",
            pady=(5, 0),
        )

    def _create_program_card(self, parent):
        card = AppCard(parent)
        card.pack(
            fill="x",
            pady=(0, 14),
        )

        content = tk.Frame(
            card,
            bg=AppTheme.CARD_BACKGROUND,
        )
        content.pack(
            fill="x",
            padx=22,
            pady=20,
        )

        logo = tk.Label(
            content,
            text="LA",
            font=(
                AppTheme.FONT_FAMILY,
                20,
                "bold",
            ),
            fg=AppTheme.TEXT_INVERSE,
            bg=AppTheme.PRIMARY,
            width=4,
            height=2,
        )
        logo.pack(side="left")

        description_area = tk.Frame(
            content,
            bg=AppTheme.CARD_BACKGROUND,
        )
        description_area.pack(
            side="left",
            fill="both",
            expand=True,
            padx=(18, 0),
        )

        tk.Label(
            description_area,
            text=self.app_name,
            font=(
                AppTheme.FONT_FAMILY,
                22,
                "bold",
            ),
            fg=AppTheme.TEXT_PRIMARY,
            bg=AppTheme.CARD_BACKGROUND,
            anchor="w",
        ).pack(anchor="w")

        tk.Label(
            description_area,
            text=(
                "과거 당첨 데이터 기반 통계 분석 후 "
                "추천번호 생성 프로그램"
            ),
            font=AppTheme.FONT_BODY,
            fg=AppTheme.TEXT_SECONDARY,
            bg=AppTheme.CARD_BACKGROUND,
            anchor="w",
        ).pack(
            anchor="w",
            pady=(6, 0),
        )

        version_area = tk.Frame(
            content,
            bg=AppTheme.SCORE_BACKGROUND,
        )
        version_area.pack(
            side="right",
            padx=(16, 0),
        )

        tk.Label(
            version_area,
            text="VERSION",
            font=(
                AppTheme.FONT_FAMILY,
                8,
                "bold",
            ),
            fg=AppTheme.PRIMARY,
            bg=AppTheme.SCORE_BACKGROUND,
        ).pack(
            padx=18,
            pady=(9, 2),
        )

        tk.Label(
            version_area,
            text=self.version,
            font=(
                AppTheme.FONT_FAMILY,
                15,
                "bold",
            ),
            fg=AppTheme.PRIMARY,
            bg=AppTheme.SCORE_BACKGROUND,
        ).pack(
            padx=18,
            pady=(0, 9),
        )

    def _create_environment_cards(self, parent):
        row = tk.Frame(
            parent,
            bg=AppTheme.CONTENT_BACKGROUND,
        )
        row.pack(
            fill="x",
            pady=(0, 14),
        )

        for column in range(4):
            row.grid_columnconfigure(
                column,
                weight=1,
                uniform="about_summary",
            )

        latest_draw_no = self.information[
            "latest_draw_no"
        ]
        stored_draw_count = self.information[
            "stored_draw_count"
        ]

        cards = [
            (
                "Python",
                self.information["python_version"],
                "현재 실행 중인 Python 버전",
                AppTheme.PRIMARY,
            ),
            (
                "SQLite",
                self.information["sqlite_version"],
                "내장 SQLite 라이브러리 버전",
                AppTheme.SUCCESS,
            ),
            (
                "저장 데이터",
                f"{stored_draw_count}건",
                (
                    f"최신 {latest_draw_no}회까지 저장"
                    if latest_draw_no is not None
                    else "저장된 회차 없음"
                ),
                AppTheme.WARNING,
            ),
            (
                "운영체제",
                self.information["os_name"],
                self.information["architecture"],
                AppTheme.ERROR,
            ),
        ]

        for column, (
            title,
            value,
            description,
            color,
        ) in enumerate(cards):
            card = SummaryCard(
                row,
                title=title,
                value=value,
                description=description,
                accent_color=color,
            )
            card.grid(
                row=0,
                column=column,
                sticky="nsew",
                padx=(
                    0 if column == 0 else 5,
                    0 if column == 3 else 5,
                ),
            )

    def _create_detail_card(self, parent):
        card = AppCard(
            parent,
            title="상세 정보",
        )
        card.pack(
            fill="both",
            expand=True,
        )

        content = tk.Frame(
            card,
            bg=AppTheme.CARD_BACKGROUND,
        )
        content.pack(
            fill="both",
            expand=True,
            padx=18,
            pady=(0, 18),
        )
        content.grid_columnconfigure(
            1,
            weight=1,
        )

        database_status = (
            "정상"
            if self.information["database_exists"]
            else "파일 없음"
        )

        details = [
            (
                "프로그램명",
                self.app_name,
            ),
            (
                "버전",
                self.version,
            ),
            (
                "개발자",
                self.developer,
            ),
            (
                "프로젝트 설명",
                (
                    "과거 당첨 데이터를 다양한 관점으로 "
                    "분석하고 추천번호를 생성합니다."
                ),
            ),
            (
                "데이터베이스 상태",
                database_status,
            ),
            (
                "데이터베이스 위치",
                self.information["database_path"],
            ),
            (
                "Repository",
                self.information["repository"],
            ),
            (
                "License",
                self.information["license"],
            ),
        ]

        for row_index, (
            label,
            value,
        ) in enumerate(details):
            background = (
                AppTheme.INPUT_BACKGROUND
                if row_index % 2 == 0
                else AppTheme.CARD_BACKGROUND
            )

            label_widget = tk.Label(
                content,
                text=label,
                font=AppTheme.FONT_BODY_BOLD,
                fg=AppTheme.TEXT_SECONDARY,
                bg=background,
                anchor="w",
                padx=14,
                pady=11,
                width=18,
            )
            label_widget.grid(
                row=row_index,
                column=0,
                sticky="nsew",
            )

            value_widget = tk.Label(
                content,
                text=value,
                font=AppTheme.FONT_BODY,
                fg=AppTheme.TEXT_PRIMARY,
                bg=background,
                anchor="w",
                justify="left",
                padx=14,
                pady=11,
                wraplength=680,
            )
            value_widget.grid(
                row=row_index,
                column=1,
                sticky="nsew",
            )

        footer = tk.Frame(
            content,
            bg=AppTheme.CARD_BACKGROUND,
        )
        footer.grid(
            row=len(details),
            column=0,
            columnspan=2,
            sticky="ew",
            pady=(16, 0),
        )

        tk.Label(
            footer,
            text=(
                "※ 본 프로그램은 당첨을 보장하지 않으며, "
                "과거 데이터 기반 통계 분석 결과를 제공합니다."
            ),
            font=AppTheme.FONT_SMALL,
            fg=AppTheme.TEXT_SECONDARY,
            bg=AppTheme.CARD_BACKGROUND,
            anchor="w",
        ).pack(
            side="left",
            fill="x",
            expand=True,
        )

        ttk.Button(
            footer,
            text="정보 새로고침",
            style="Secondary.TButton",
            command=self.refresh_information,
        ).pack(side="right")

    def refresh_information(self):
        self.information = (
            self.about_service.get_program_information()
        )

        for widget in self.winfo_children():
            widget.destroy()

        self.create_widgets()

        if self.on_status is not None:
            self.on_status(
                "프로그램 정보 새로고침 완료"
            )

        if self.on_log is not None:
            self.on_log(
                "프로그램 정보 새로고침 완료",
                "SUCCESS",
            )