import sys
from pathlib import Path


def get_resource_base_dir():
    """GUI 리소스의 기준 디렉터리를 반환합니다."""
    if hasattr(sys, "_MEIPASS"):
        return Path(sys._MEIPASS)

    return Path(__file__).resolve().parents[2]


def get_resource_path(*parts):
    """개발 환경과 PyInstaller 번들에서 공통으로 사용할 리소스 경로를 반환합니다."""
    return get_resource_base_dir().joinpath(*parts)
