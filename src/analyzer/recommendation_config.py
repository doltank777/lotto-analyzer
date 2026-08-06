RECOMMENDATION_WEIGHTS = {
    "frequency": 0.25,
    "recent_30": 0.20,
    "recent_100": 0.20,
    "rising": 0.15,
    "missing": 0.20
}

COMBINATION_WEIGHTS = {
    "pair": 0.01,
    "triple": 0.005,
    "pattern": 1.0
}

FINAL_RECOMMENDATION_SETTINGS = {
    "set_count": 5,
    "candidate_pool_size": 35,
    "max_attempts": 10000,
    "max_overlap_count": 3
}

RECOMMENDATION_CONDITIONS = {
    "allowed_odd_even_patterns": ["3:3", "4:2", "2:4"],
    "allowed_low_high_patterns": ["3:3", "4:2", "2:4"],
    "min_sum": 100,
    "max_sum": 170,
    "min_unique_digit_count": 5,
    "max_consecutive_pair_count": 1
}
