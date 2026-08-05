from tkinter import ttk


def create_indeterminate_progress(parent, style=None):
    """공통 무한 진행 표시줄을 생성합니다."""

    options = {
        "mode": "indeterminate",
    }

    if style:
        options["style"] = style

    return ttk.Progressbar(parent, **options)
