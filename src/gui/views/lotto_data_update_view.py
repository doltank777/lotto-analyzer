import tkinter as tk
from tkinter import messagebox, ttk

from src.app.lotto_data_update_service import (
    LottoDataValidationError,
    LottoDrawAlreadyExistsError,
)
from src.gui.components import AppCard
from src.gui.theme import AppTheme


class LottoDataUpdateView(tk.Frame):
    """
    사용자가 당첨번호를 직접 입력하여 lotto.db에 신규 회차를 등록하는 화면.

    GUI는 DB에 직접 접근하지 않고 LottoDataUpdateService만 호출한다.
    """

    def __init__(
        self,
        parent,
        lotto_data_update_service,
        on_log=None,
        on_status=None,
    ):
        super().__init__(parent, bg=AppTheme.CONTENT_BACKGROUND)

        self.lotto_data_update_service = lotto_data_update_service
        self.on_log = on_log
        self.on_status = on_status

        self.number_entries = []

        self.create_widgets()
        self.refresh_data_info()

    def create_widgets(self):
        body = tk.Frame(self, bg=AppTheme.CONTENT_BACKGROUND)
        body.pack(fill="both", expand=True, padx=24, pady=20)

        self._create_page_intro(body)
        self._create_summary_area(body)
        self._create_input_card(body)
        self._create_notice_card(body)

    def _create_page_intro(self, parent):
        area = tk.Frame(parent, bg=AppTheme.CONTENT_BACKGROUND)
        area.pack(fill="x", pady=(0, 14))

        tk.Label(
            area,
            text="당첨 데이터 관리",
            font=AppTheme.FONT_PAGE_TITLE,
            fg=AppTheme.TEXT_PRIMARY,
            bg=AppTheme.CONTENT_BACKGROUND,
            anchor="w",
        ).pack(fill="x")

        tk.Label(
            area,
            text=(
                "새로운 회차의 당첨번호를 직접 입력하여 "
                "로또 데이터베이스에 추가합니다."
            ),
            font=AppTheme.FONT_BODY,
            fg=AppTheme.TEXT_SECONDARY,
            bg=AppTheme.CONTENT_BACKGROUND,
            anchor="w",
        ).pack(fill="x", pady=(5, 0))

    def _create_summary_area(self, parent):
        summary_row = tk.Frame(parent, bg=AppTheme.CONTENT_BACKGROUND)
        summary_row.pack(fill="x", pady=(0, 14))

        summary_row.grid_columnconfigure(0, weight=1, uniform="data_summary")
        summary_row.grid_columnconfigure(1, weight=1, uniform="data_summary")

        latest_card = self._create_summary_card(
            summary_row,
            title="현재 저장 최신 회차",
            description="database/lotto.db 기준",
            accent_color=AppTheme.PRIMARY,
        )
        latest_card.grid(row=0, column=0, sticky="nsew", padx=(0, 6))
        self.latest_draw_value_label = latest_card.value_label

        next_card = self._create_summary_card(
            summary_row,
            title="다음 등록 회차",
            description="최신 회차 + 1 자동 계산",
            accent_color=AppTheme.SUCCESS,
        )
        next_card.grid(row=0, column=1, sticky="nsew", padx=(6, 0))
        self.next_draw_value_label = next_card.value_label

    def _create_summary_card(self, parent, title, description, accent_color):
        card = tk.Frame(
            parent,
            bg=AppTheme.CARD_BACKGROUND,
            highlightthickness=1,
            highlightbackground=AppTheme.BORDER,
        )

        accent = tk.Frame(card, bg=accent_color, height=4)
        accent.pack(fill="x")

        content = tk.Frame(card, bg=AppTheme.CARD_BACKGROUND)
        content.pack(fill="both", expand=True, padx=18, pady=14)

        tk.Label(
            content,
            text=title,
            font=AppTheme.FONT_SMALL,
            fg=AppTheme.TEXT_SECONDARY,
            bg=AppTheme.CARD_BACKGROUND,
            anchor="w",
        ).pack(fill="x")

        value_label = tk.Label(
            content,
            text="-",
            font=(AppTheme.FONT_FAMILY, 22, "bold"),
            fg=AppTheme.TEXT_PRIMARY,
            bg=AppTheme.CARD_BACKGROUND,
            anchor="w",
        )
        value_label.pack(fill="x", pady=(5, 3))

        tk.Label(
            content,
            text=description,
            font=AppTheme.FONT_SMALL,
            fg=AppTheme.TEXT_MUTED,
            bg=AppTheme.CARD_BACKGROUND,
            anchor="w",
        ).pack(fill="x")

        card.value_label = value_label
        return card

    def _create_input_card(self, parent):
        card = AppCard(parent, title="신규 당첨 데이터 등록")
        card.pack(fill="x", pady=(0, 14))

        content = tk.Frame(card, bg=AppTheme.CARD_BACKGROUND)
        content.pack(fill="x", padx=20, pady=(0, 20))

        draw_row = tk.Frame(content, bg=AppTheme.CARD_BACKGROUND)
        draw_row.pack(fill="x", pady=(2, 18))

        draw_label_area = tk.Frame(draw_row, bg=AppTheme.CARD_BACKGROUND)
        draw_label_area.pack(side="left", fill="x", expand=True)

        tk.Label(
            draw_label_area,
            text="회차",
            font=AppTheme.FONT_BODY_BOLD,
            fg=AppTheme.TEXT_PRIMARY,
            bg=AppTheme.CARD_BACKGROUND,
            anchor="w",
        ).pack(anchor="w")

        tk.Label(
            draw_label_area,
            text="현재 최신 회차의 다음 번호가 자동 입력됩니다.",
            font=AppTheme.FONT_SMALL,
            fg=AppTheme.TEXT_SECONDARY,
            bg=AppTheme.CARD_BACKGROUND,
            anchor="w",
        ).pack(anchor="w", pady=(4, 0))

        self.draw_no_entry = self._create_entry(
            draw_row,
            width=12,
        )
        self.draw_no_entry.pack(side="right", ipady=8)

        number_section = tk.Frame(content, bg=AppTheme.CARD_BACKGROUND)
        number_section.pack(fill="x", pady=(0, 18))

        tk.Label(
            number_section,
            text="당첨번호 6개",
            font=AppTheme.FONT_BODY_BOLD,
            fg=AppTheme.TEXT_PRIMARY,
            bg=AppTheme.CARD_BACKGROUND,
            anchor="w",
        ).pack(anchor="w")

        tk.Label(
            number_section,
            text="각 번호는 1~45 범위로 입력하고 중복되지 않아야 합니다.",
            font=AppTheme.FONT_SMALL,
            fg=AppTheme.TEXT_SECONDARY,
            bg=AppTheme.CARD_BACKGROUND,
            anchor="w",
        ).pack(anchor="w", pady=(4, 10))

        number_row = tk.Frame(number_section, bg=AppTheme.CARD_BACKGROUND)
        number_row.pack(fill="x")

        for index in range(6):
            entry_area = tk.Frame(
                number_row,
                bg=AppTheme.CARD_BACKGROUND,
            )
            entry_area.pack(side="left", padx=(0, 10))

            tk.Label(
                entry_area,
                text=f"번호 {index + 1}",
                font=AppTheme.FONT_SMALL,
                fg=AppTheme.TEXT_SECONDARY,
                bg=AppTheme.CARD_BACKGROUND,
            ).pack(pady=(0, 5))

            entry = self._create_entry(
                entry_area,
                width=7,
            )
            entry.pack(ipady=8)
            self.number_entries.append(entry)

        bonus_area = tk.Frame(
            number_row,
            bg=AppTheme.CARD_BACKGROUND,
        )
        bonus_area.pack(side="left", padx=(12, 0))

        tk.Label(
            bonus_area,
            text="보너스",
            font=AppTheme.FONT_SMALL,
            fg=AppTheme.PRIMARY,
            bg=AppTheme.CARD_BACKGROUND,
        ).pack(pady=(0, 5))

        self.bonus_entry = self._create_entry(
            bonus_area,
            width=7,
        )
        self.bonus_entry.pack(ipady=8)

        self._bind_entry_navigation()

        preview_frame = tk.Frame(
            content,
            bg=AppTheme.INPUT_BACKGROUND,
            highlightthickness=1,
            highlightbackground=AppTheme.BORDER,
        )
        preview_frame.pack(fill="x", pady=(0, 18))

        preview_content = tk.Frame(
            preview_frame,
            bg=AppTheme.INPUT_BACKGROUND,
        )
        preview_content.pack(fill="x", padx=16, pady=14)

        tk.Label(
            preview_content,
            text="입력 안내",
            font=AppTheme.FONT_BODY_BOLD,
            fg=AppTheme.TEXT_PRIMARY,
            bg=AppTheme.INPUT_BACKGROUND,
        ).pack(side="left")

        tk.Label(
            preview_content,
            text="회차와 당첨번호를 확인한 뒤 등록 버튼을 눌러주세요.",
            font=AppTheme.FONT_SMALL,
            fg=AppTheme.TEXT_SECONDARY,
            bg=AppTheme.INPUT_BACKGROUND,
        ).pack(side="left", padx=(12, 0))

        action_row = tk.Frame(content, bg=AppTheme.CARD_BACKGROUND)
        action_row.pack(fill="x")

        self.status_label = tk.Label(
            action_row,
            text="신규 회차 데이터를 입력해주세요.",
            font=AppTheme.FONT_SMALL,
            fg=AppTheme.TEXT_SECONDARY,
            bg=AppTheme.CARD_BACKGROUND,
            anchor="w",
        )
        self.status_label.pack(side="left", fill="x", expand=True)

        self.reset_button = ttk.Button(
            action_row,
            text="입력 초기화",
            style="Secondary.TButton",
            command=self.reset_form,
        )
        self.reset_button.pack(side="right", padx=(8, 0))

        self.save_button = ttk.Button(
            action_row,
            text="당첨 데이터 등록",
            style="Primary.TButton",
            command=self.register_draw,
        )
        self.save_button.pack(side="right")

    def _create_notice_card(self, parent):
        card = AppCard(parent, title="등록 시 유의사항")
        card.pack(fill="x")

        content = tk.Frame(card, bg=AppTheme.CARD_BACKGROUND)
        content.pack(fill="x", padx=20, pady=(0, 18))

        notices = [
            "기존에 저장된 회차는 다시 등록하거나 덮어쓸 수 없습니다.",
            "당첨번호는 1~45 사이의 서로 다른 숫자 6개를 입력해야 합니다.",
            "보너스번호는 일반 당첨번호와 중복될 수 없습니다.",
            "등록 전 실제 동행복권 당첨 결과와 입력값을 다시 확인해주세요.",
        ]

        for notice in notices:
            tk.Label(
                content,
                text=f"• {notice}",
                font=AppTheme.FONT_SMALL,
                fg=AppTheme.TEXT_SECONDARY,
                bg=AppTheme.CARD_BACKGROUND,
                anchor="w",
            ).pack(fill="x", pady=2)

    def _create_entry(self, parent, width):
        return tk.Entry(
            parent,
            width=width,
            font=AppTheme.FONT_BODY,
            bg=AppTheme.INPUT_BACKGROUND,
            fg=AppTheme.TEXT_PRIMARY,
            insertbackground=AppTheme.TEXT_PRIMARY,
            relief="flat",
            justify="center",
            highlightthickness=1,
            highlightbackground=AppTheme.BORDER,
            highlightcolor=AppTheme.PRIMARY,
        )

    def _bind_entry_navigation(self):
        entries = [
            self.draw_no_entry,
            *self.number_entries,
            self.bonus_entry,
        ]

        for index, entry in enumerate(entries):
            if index < len(entries) - 1:
                next_entry = entries[index + 1]
                entry.bind(
                    "<Return>",
                    lambda event, target=next_entry: target.focus_set(),
                )
            else:
                entry.bind(
                    "<Return>",
                    lambda event: self.register_draw(),
                )

    def refresh_data_info(self):
        """현재 DB 최신 회차와 다음 등록 회차를 화면에 반영한다."""

        try:
            latest_draw_no = (
                self.lotto_data_update_service.get_latest_draw_no()
            )
            next_draw_no = (
                self.lotto_data_update_service.get_next_draw_no()
            )

            self.latest_draw_value_label.config(
                text=f"{latest_draw_no}회" if latest_draw_no else "없음"
            )
            self.next_draw_value_label.config(
                text=f"{next_draw_no}회"
            )

            self.draw_no_entry.delete(0, tk.END)
            self.draw_no_entry.insert(0, str(next_draw_no))

        except Exception as error:
            self._set_status(
                "DB 정보를 불러오지 못했습니다.",
                AppTheme.ERROR,
            )
            self._log(
                f"당첨 데이터 최신 회차 조회 오류 "
                f"[{type(error).__name__}]: {error}",
                "ERROR",
            )

    def reset_form(self):
        """입력값을 초기화하고 다음 등록 회차를 다시 설정한다."""

        try:
            next_draw_no = (
                self.lotto_data_update_service.get_next_draw_no()
            )
        except Exception:
            next_draw_no = ""

        self.draw_no_entry.delete(0, tk.END)
        self.draw_no_entry.insert(0, str(next_draw_no))

        for entry in self.number_entries:
            entry.delete(0, tk.END)

        self.bonus_entry.delete(0, tk.END)

        self._set_status(
            "입력값을 초기화했습니다.",
            AppTheme.TEXT_SECONDARY,
        )

        if self.number_entries:
            self.number_entries[0].focus_set()

    def register_draw(self):
        """입력값을 Service에 전달하여 신규 회차를 등록한다."""

        draw_no = self.draw_no_entry.get().strip()
        numbers = [
            entry.get().strip()
            for entry in self.number_entries
        ]
        bonus_number = self.bonus_entry.get().strip()

        try:
            validated = self.lotto_data_update_service.validate_draw(
                draw_no=draw_no,
                numbers=numbers,
                bonus_number=bonus_number,
            )
        except LottoDataValidationError as error:
            self._set_status(
                "입력값을 확인해주세요.",
                AppTheme.ERROR,
            )
            self._log(
                f"당첨 데이터 입력 검증 실패: {error}",
                "WARNING",
            )
            messagebox.showwarning(
                "입력 오류",
                str(error),
            )
            return

        numbers_text = ", ".join(
            str(number)
            for number in validated["numbers"]
        )

        confirmed = messagebox.askyesno(
            "당첨 데이터 등록 확인",
            (
                f"{validated['draw_no']}회 당첨 데이터를 등록하시겠습니까?\n\n"
                f"당첨번호 : {numbers_text}\n"
                f"보너스번호 : {validated['bonus_number']}\n\n"
                "등록 후에는 이 화면에서 기존 회차를 수정하지 않습니다."
            ),
        )

        if not confirmed:
            return

        self.save_button.config(state="disabled")
        self.reset_button.config(state="disabled")
        self._set_status(
            "당첨 데이터를 등록하고 있습니다.",
            AppTheme.PRIMARY,
        )
        self._status("당첨 데이터 등록 중...")

        try:
            result = self.lotto_data_update_service.add_draw(
                draw_no=draw_no,
                numbers=numbers,
                bonus_number=bonus_number,
            )

            self._log(
                (
                    f"{result['draw_no']}회 당첨 데이터 등록 완료 - "
                    f"당첨번호 {result['numbers']} / "
                    f"보너스 {result['bonus_number']}"
                ),
                "SUCCESS",
            )
            self._status(
                f"{result['draw_no']}회 당첨 데이터 등록 완료"
            )
            self._set_status(
                f"완료 · {result['draw_no']}회 당첨 데이터가 등록되었습니다.",
                AppTheme.SUCCESS,
            )

            messagebox.showinfo(
                "등록 완료",
                (
                    f"{result['draw_no']}회 당첨 데이터를 등록했습니다.\n\n"
                    f"현재 DB 최신 회차: {result['latest_draw_no']}회"
                ),
            )

            self.refresh_data_info()
            self._clear_number_inputs()

            if self.number_entries:
                self.number_entries[0].focus_set()

        except LottoDrawAlreadyExistsError as error:
            self._set_status(
                "등록 실패 · 이미 저장된 회차입니다.",
                AppTheme.WARNING,
            )
            self._status("당첨 데이터 중복 회차 등록 차단")
            self._log(str(error), "WARNING")
            messagebox.showwarning(
                "중복 회차",
                str(error),
            )

        except LottoDataValidationError as error:
            self._set_status(
                "입력값을 확인해주세요.",
                AppTheme.ERROR,
            )
            self._status("당첨 데이터 입력 오류")
            self._log(
                f"당첨 데이터 입력 검증 실패: {error}",
                "WARNING",
            )
            messagebox.showwarning(
                "입력 오류",
                str(error),
            )

        except Exception as error:
            self._set_status(
                "오류 · 당첨 데이터 등록에 실패했습니다.",
                AppTheme.ERROR,
            )
            self._status("당첨 데이터 등록 오류")
            self._log(
                f"당첨 데이터 등록 오류 "
                f"[{type(error).__name__}]: {error}",
                "ERROR",
            )
            messagebox.showerror(
                "등록 오류",
                f"당첨 데이터 등록 중 오류가 발생했습니다.\n\n{error}",
            )

        finally:
            self.save_button.config(state="normal")
            self.reset_button.config(state="normal")

    def _clear_number_inputs(self):
        for entry in self.number_entries:
            entry.delete(0, tk.END)

        self.bonus_entry.delete(0, tk.END)

    def _set_status(self, message, color):
        self.status_label.config(
            text=message,
            fg=color,
        )

    def _log(self, message, level="INFO"):
        if callable(self.on_log):
            self.on_log(message, level)

    def _status(self, message):
        if callable(self.on_status):
            self.on_status(message)
