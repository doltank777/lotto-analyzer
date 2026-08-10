import shutil
import subprocess
import sys
from pathlib import Path


APP_NAME = "Lotto Analyzer"
VERSION = "1.3.0"
SPEC_FILE_NAME = "lotto_analyzer.spec"


PROJECT_ROOT = Path(__file__).resolve().parent
DIST_DIR = PROJECT_ROOT / "dist"
BUILD_DIR = PROJECT_ROOT / "build"
RELEASE_ROOT = PROJECT_ROOT / "release"
RELEASE_DIR = RELEASE_ROOT / f"{APP_NAME} {VERSION}"

EXE_SOURCE = DIST_DIR / f"{APP_NAME}.exe"
DATABASE_SOURCE = PROJECT_ROOT / "database" / "lotto.db"
SETTINGS_SOURCE = PROJECT_ROOT / "config" / "recommendation_settings.json"
README_SOURCE = PROJECT_ROOT / "README.txt"
LICENSE_SOURCE = PROJECT_ROOT / "LICENSE.txt"
ICON_SOURCE = PROJECT_ROOT / "assets" / "LottoAnalyzer.ico"
VERSION_INFO_SOURCE = PROJECT_ROOT / "version_info.txt"
SPEC_SOURCE = PROJECT_ROOT / SPEC_FILE_NAME


def validate_required_files():
    required_files = [
        PROJECT_ROOT / "main.py",
        SPEC_SOURCE,
        ICON_SOURCE,
        VERSION_INFO_SOURCE,
        DATABASE_SOURCE,
        SETTINGS_SOURCE,
        README_SOURCE,
        LICENSE_SOURCE,
    ]

    missing_files = [
        path
        for path in required_files
        if not path.exists()
    ]

    if missing_files:
        missing_text = "\n".join(
            f"- {path.relative_to(PROJECT_ROOT)}"
            for path in missing_files
        )
        raise FileNotFoundError(
            "배포 빌드에 필요한 파일이 없습니다.\n"
            f"{missing_text}"
        )


def clean_build_directories():
    for directory in (BUILD_DIR, DIST_DIR):
        if directory.exists():
            shutil.rmtree(directory)


def run_pyinstaller():
    command = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--clean",
        "--noconfirm",
        str(SPEC_SOURCE),
    ]

    print("[BUILD] PyInstaller 빌드를 시작합니다.")
    subprocess.run(
        command,
        cwd=PROJECT_ROOT,
        check=True,
    )

    if not EXE_SOURCE.exists():
        raise FileNotFoundError(
            f"빌드 결과 EXE를 찾을 수 없습니다: {EXE_SOURCE}"
        )


def prepare_release_directory():
    if RELEASE_DIR.exists():
        shutil.rmtree(RELEASE_DIR)

    (RELEASE_DIR / "database").mkdir(
        parents=True,
        exist_ok=True,
    )
    (RELEASE_DIR / "config").mkdir(
        parents=True,
        exist_ok=True,
    )


def copy_release_files():
    shutil.copy2(
        EXE_SOURCE,
        RELEASE_DIR / f"{APP_NAME}.exe",
    )
    shutil.copy2(
        DATABASE_SOURCE,
        RELEASE_DIR / "database" / "lotto.db",
    )
    shutil.copy2(
        SETTINGS_SOURCE,
        RELEASE_DIR
        / "config"
        / "recommendation_settings.json",
    )
    shutil.copy2(
        README_SOURCE,
        RELEASE_DIR / "README.txt",
    )
    shutil.copy2(
        LICENSE_SOURCE,
        RELEASE_DIR / "LICENSE.txt",
    )


def print_release_summary():
    print()
    print("[SUCCESS] Lotto Analyzer 배포 패키지 생성 완료")
    print(f"[VERSION] {VERSION}")
    print(f"[PATH] {RELEASE_DIR}")
    print()
    print("배포 폴더 구성")
    print(f"{APP_NAME} {VERSION}/")
    print(f"├── {APP_NAME}.exe")
    print("├── database/")
    print("│   └── lotto.db")
    print("├── config/")
    print("│   └── recommendation_settings.json")
    print("├── README.txt")
    print("└── LICENSE.txt")


def main():
    validate_required_files()
    clean_build_directories()
    run_pyinstaller()
    prepare_release_directory()
    copy_release_files()
    print_release_summary()


if __name__ == "__main__":
    try:
        main()
    except (
        FileNotFoundError,
        subprocess.CalledProcessError,
        OSError,
    ) as error:
        print()
        print(f"[ERROR] 배포 빌드 실패: {error}")
        sys.exit(1)
