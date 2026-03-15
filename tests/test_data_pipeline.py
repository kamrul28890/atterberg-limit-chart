import unittest

import pandas as pd

from atterberg_limit_chart.data import dataframe_to_rows, evaluate_rows, parse_clipboard_rows


class DataPipelineTests(unittest.TestCase):
    def test_dataframe_aliases_are_mapped_to_canonical_columns(self):
        dataframe = pd.DataFrame(
            {
                "Boring Name": ["BH-1", "BH-2"],
                "LL (Liquid Limit)": [48, 55],
                "PL (Plastic Limit)": [20, 27],
            }
        )

        rows = dataframe_to_rows(dataframe)

        self.assertEqual(
            rows,
            [
                {"Sample": "BH-1", "LL": "48", "PL": "20"},
                {"Sample": "BH-2", "LL": "55", "PL": "27"},
            ],
        )

    def test_clipboard_with_header_is_detected(self):
        clipboard = "Boring Name\tLL (Liquid Limit)\tPL (Plastic Limit)\nB-1\t48\t25\nB-2\t55\t31"

        rows = parse_clipboard_rows(clipboard)

        self.assertEqual(rows[0]["Sample"], "B-1")
        self.assertEqual(rows[1]["LL"], "55")
        self.assertEqual(rows[1]["PL"], "31")

    def test_clipboard_without_header_uses_first_three_columns(self):
        clipboard = "B-1\t48\t25\tignored\nB-2\t55\t31\tignored"

        rows = parse_clipboard_rows(clipboard)

        self.assertEqual(rows[0], {"Sample": "B-1", "LL": "48", "PL": "25"})
        self.assertEqual(rows[1], {"Sample": "B-2", "LL": "55", "PL": "31"})

    def test_evaluate_rows_builds_clean_dataframe_and_reports_invalid_rows(self):
        evaluation = evaluate_rows(
            [
                {"Sample": "", "LL": "48", "PL": "25"},
                {"Sample": "B-2", "LL": "20", "PL": "25"},
                {"Sample": "", "LL": "", "PL": ""},
            ]
        )

        self.assertEqual(evaluation.valid_row_count, 1)
        self.assertEqual(evaluation.total_non_blank_rows, 2)
        self.assertEqual(len(evaluation.issues), 1)
        self.assertEqual(evaluation.dataframe.iloc[0]["Sample"], "Sample 1")
        self.assertEqual(evaluation.dataframe.iloc[0]["PI"], 23.0)
        self.assertEqual(evaluation.dataframe.iloc[0]["Zone"], "CL")


if __name__ == "__main__":
    unittest.main()
