class AppTheme:
    """Lotto Analyzer GUI에서 공통으로 사용하는 디자인 시스템."""

    # Window
    WINDOW_WIDTH = 1040
    WINDOW_HEIGHT = 820

    # Colors
    BACKGROUND = "#0F172A"
    SURFACE = "#111827"
    PANEL = "#1E293B"
    PANEL_ALT = "#243247"
    INPUT_BACKGROUND = "#0B1220"

    PRIMARY = "#3B82F6"
    PRIMARY_ACTIVE = "#2563EB"
    SUCCESS = "#22C55E"
    WARNING = "#F59E0B"
    ERROR = "#EF4444"

    TEXT_PRIMARY = "#F8FAFC"
    TEXT_SECONDARY = "#94A3B8"
    TEXT_MUTED = "#64748B"
    BORDER = "#334155"
    DIVIDER = "#273449"

    # Fonts
    FONT_FAMILY = "맑은 고딕"
    MONO_FONT_FAMILY = "Consolas"

    FONT_TITLE = (FONT_FAMILY, 23, "bold")
    FONT_SUBTITLE = (FONT_FAMILY, 10)
    FONT_SECTION_TITLE = (FONT_FAMILY, 16, "bold")
    FONT_SECTION_DESCRIPTION = (FONT_FAMILY, 10)
    FONT_BODY = (FONT_FAMILY, 10)
    FONT_BODY_BOLD = (FONT_FAMILY, 10, "bold")
    FONT_BUTTON = (FONT_FAMILY, 10, "bold")
    FONT_SMALL = (FONT_FAMILY, 9)
    FONT_MONO = (MONO_FONT_FAMILY, 10)

    # Spacing
    WINDOW_PADDING_X = 22
    HEADER_PADDING_Y = 18
    CONTENT_PADDING = 16
    SECTION_GAP = 10
    CONTROL_GAP = 8

    # Widget sizes
    TAB_PADDING = (26, 11)
    BUTTON_PADDING = (18, 9)
    TEXT_PADDING_X = 14
    TEXT_PADDING_Y = 12

    @classmethod
    def text_widget_options(cls):
        return {
            "font": cls.FONT_MONO,
            "bg": cls.INPUT_BACKGROUND,
            "fg": cls.TEXT_PRIMARY,
            "insertbackground": cls.TEXT_PRIMARY,
            "selectbackground": cls.PRIMARY,
            "selectforeground": cls.TEXT_PRIMARY,
            "relief": "flat",
            "borderwidth": 0,
            "highlightthickness": 1,
            "highlightbackground": cls.BORDER,
            "highlightcolor": cls.PRIMARY,
            "padx": cls.TEXT_PADDING_X,
            "pady": cls.TEXT_PADDING_Y,
        }