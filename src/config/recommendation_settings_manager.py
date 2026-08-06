import copy
import json
import sys
from pathlib import Path

from src.analyzer.recommendation_config import (
    COMBINATION_WEIGHTS,
    FINAL_RECOMMENDATION_SETTINGS,
    RECOMMENDATION_CONDITIONS,
    RECOMMENDATION_WEIGHTS,
)


class RecommendationSettingsManager:
    """추천 설정 JSON 파일의 생성, 조회, 저장, 기본값 복원을 담당한다."""

    SETTINGS_FILE_NAME = "recommendation_settings.json"

    def __init__(self, settings_path=None):
        self.settings_path = (
            Path(settings_path)
            if settings_path is not None
            else self._get_default_settings_path()
        )

        self.settings_path.parent.mkdir(parents=True, exist_ok=True)
        self._ensure_settings_file()

    def _get_default_settings_path(self):
        if getattr(sys, "frozen", False):
            base_dir = Path(sys.executable).resolve().parent
        else:
            base_dir = Path(__file__).resolve().parents[2]

        return base_dir / "config" / self.SETTINGS_FILE_NAME

    def get_default_settings(self):
        return {
            "weights": copy.deepcopy(RECOMMENDATION_WEIGHTS),
            "combination_weights": copy.deepcopy(COMBINATION_WEIGHTS),
            "final_settings": copy.deepcopy(FINAL_RECOMMENDATION_SETTINGS),
            "conditions": copy.deepcopy(RECOMMENDATION_CONDITIONS),
        }

    def get_settings(self):
        """JSON 설정을 읽고 누락 항목은 기본값으로 보완한다."""
        self._ensure_settings_file()

        try:
            with self.settings_path.open("r", encoding="utf-8") as file:
                saved_settings = json.load(file)
        except (OSError, json.JSONDecodeError):
            default_settings = self.get_default_settings()
            self.save_settings(default_settings)
            return default_settings

        merged_settings = self._merge_with_defaults(saved_settings)
        self.validate_settings(merged_settings)

        if merged_settings != saved_settings:
            self.save_settings(merged_settings)

        return merged_settings

    def save_settings(self, settings):
        validated_settings = self._merge_with_defaults(settings)
        self.validate_settings(validated_settings)

        temp_path = self.settings_path.with_suffix(".tmp")

        try:
            with temp_path.open("w", encoding="utf-8") as file:
                json.dump(
                    validated_settings,
                    file,
                    ensure_ascii=False,
                    indent=4,
                )

            temp_path.replace(self.settings_path)
        except OSError:
            if temp_path.exists():
                temp_path.unlink(missing_ok=True)
            raise

        return copy.deepcopy(validated_settings)

    def restore_defaults(self):
        default_settings = self.get_default_settings()
        return self.save_settings(default_settings)

    def _ensure_settings_file(self):
        if not self.settings_path.exists():
            self.save_settings(self.get_default_settings())

    def _merge_with_defaults(self, settings):
        defaults = self.get_default_settings()

        if not isinstance(settings, dict):
            return defaults

        merged = copy.deepcopy(defaults)

        for section_name, default_section in defaults.items():
            saved_section = settings.get(section_name)

            if not isinstance(saved_section, dict):
                continue

            for key in default_section:
                if key in saved_section:
                    merged[section_name][key] = copy.deepcopy(
                        saved_section[key]
                    )

        return merged

    def validate_settings(self, settings):
        weights = settings["weights"]
        combination_weights = settings["combination_weights"]
        final_settings = settings["final_settings"]
        conditions = settings["conditions"]

        for name, value in weights.items():
            self._validate_non_negative_number(
                value,
                f"weights.{name}",
            )

        if sum(weights.values()) <= 0:
            raise ValueError("추천 가중치 합계는 0보다 커야 합니다.")

        for name, value in combination_weights.items():
            self._validate_non_negative_number(
                value,
                f"combination_weights.{name}",
            )

        self._validate_integer_range(
            final_settings["set_count"],
            "final_settings.set_count",
            minimum=1,
            maximum=100,
        )
        self._validate_integer_range(
            final_settings["candidate_pool_size"],
            "final_settings.candidate_pool_size",
            minimum=6,
            maximum=45,
        )
        self._validate_integer_range(
            final_settings["max_attempts"],
            "final_settings.max_attempts",
            minimum=100,
            maximum=1_000_000,
        )
        self._validate_integer_range(
            final_settings["max_overlap_count"],
            "final_settings.max_overlap_count",
            minimum=0,
            maximum=6,
        )

        min_sum = conditions["min_sum"]
        max_sum = conditions["max_sum"]

        self._validate_integer_range(
            min_sum,
            "conditions.min_sum",
            minimum=21,
            maximum=255,
        )
        self._validate_integer_range(
            max_sum,
            "conditions.max_sum",
            minimum=21,
            maximum=255,
        )

        if min_sum > max_sum:
            raise ValueError("번호합 최소값은 최대값보다 클 수 없습니다.")

        self._validate_integer_range(
            conditions["min_unique_digit_count"],
            "conditions.min_unique_digit_count",
            minimum=1,
            maximum=6,
        )
        self._validate_integer_range(
            conditions["max_consecutive_pair_count"],
            "conditions.max_consecutive_pair_count",
            minimum=0,
            maximum=5,
        )

        self._validate_pattern_list(
            conditions["allowed_odd_even_patterns"],
            "conditions.allowed_odd_even_patterns",
        )
        self._validate_pattern_list(
            conditions["allowed_low_high_patterns"],
            "conditions.allowed_low_high_patterns",
        )

        return True

    def _validate_non_negative_number(self, value, field_name):
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ValueError(f"{field_name} 값은 숫자여야 합니다.")

        if value < 0:
            raise ValueError(f"{field_name} 값은 0 이상이어야 합니다.")

    def _validate_integer_range(
        self,
        value,
        field_name,
        minimum,
        maximum,
    ):
        if isinstance(value, bool) or not isinstance(value, int):
            raise ValueError(f"{field_name} 값은 정수여야 합니다.")

        if not minimum <= value <= maximum:
            raise ValueError(
                f"{field_name} 값은 {minimum}~{maximum} 범위여야 합니다."
            )

    def _validate_pattern_list(self, patterns, field_name):
        if not isinstance(patterns, list) or not patterns:
            raise ValueError(
                f"{field_name} 값은 하나 이상의 패턴 목록이어야 합니다."
            )

        for pattern in patterns:
            if not isinstance(pattern, str):
                raise ValueError(
                    f"{field_name} 패턴은 문자열이어야 합니다."
                )

            parts = pattern.split(":")

            if len(parts) != 2 or not all(part.isdigit() for part in parts):
                raise ValueError(
                    f"{field_name} 패턴 형식이 올바르지 않습니다: {pattern}"
                )

            if sum(int(part) for part in parts) != 6:
                raise ValueError(
                    f"{field_name} 패턴의 합은 6이어야 합니다: {pattern}"
                )
