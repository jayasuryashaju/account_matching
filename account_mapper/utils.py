from difflib import SequenceMatcher
from .models import RawData
from .config import USE_COLUMNS
import pandas as pd


def combine_row(row, columns):
    """
    Combine the specified columns of a row into a single string for comparison.
    """
    return " ".join([str(row[col]).strip().lower() if col in row and pd.notnull(row[col]) else "" for col in columns])


def get_best_match(input_combined_str, ram_combined_rows, high_threshold, low_threshold):
    """
    Get the best match for the input string from the combined RAM rows.
    """
    best_score = 0
    best_result = "No Match"

    for ram_combined_str in ram_combined_rows:
        score = SequenceMatcher(None, input_combined_str, ram_combined_str).ratio()
        if score == 1.0:  # Exact match
            return score, "No Review Needed"

        if score > best_score:
            best_score = score

    # Determine result based on thresholds
    if best_score >= high_threshold:
        best_result = "No Review Needed"
    elif best_score >= low_threshold:
        best_result = "Review Needed"

    return round(best_score, 2), best_result
