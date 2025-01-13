import pytest
import pandas as pd
import os
from scripts.inconsistency_detection import (
    load_comparison_data,
    detect_mismatches,
    save_summary_report,
    summarize_mismatches,
    summarize_grouped_mismatches
)


def test_load_comparison_data(sample_comparison_data):
    """Тест успешной загрузки данных сравнения."""
    comparison_df = load_comparison_data(sample_comparison_data)

    assert not comparison_df.empty, "comparison_df должен быть загружен."
    assert isinstance(comparison_df, pd.DataFrame), "comparison_df должен быть DataFrame."
    assert len(comparison_df) == 2, "comparison_df должен содержать 2 записи."
    assert comparison_df.shape == (2, 7), "comparison_df должен иметь размер (2, 7)."


def test_load_comparison_data_file_not_found():
    """Тест обработки ошибки при отсутствии файла."""
    with pytest.raises(FileNotFoundError):
        load_comparison_data("nonexistent.csv")


def test_detect_mismatches():
    """Тест обнаружения расхождений."""
    data = pd.DataFrame(
        {
            "trace_id": [1, 2, 3],
            "side": ["bid", "ask", "bid"],
            "role": ["taker", "maker", "taker"],
            "platform_fee_rate": [0.1, 0.2, 0.3],
            "exchange_fee_rate": [0.1, 0.15, 0.3],
            "platform_fee_asset": ["USD", "USD", "BTC"],
            "exchange_fee_asset": ["USD", "EUR", "BTC"],
        }
    )

    mismatched_data = detect_mismatches(data)

    # Проверяем общее количество расхождений
    assert len(mismatched_data) == 1, "Должно быть обнаружено одно расхождение."

    # Проверяем конкретное расхождение по trace_id = 2
    # assert mismatched_data.iloc[0]["trace_id"] == 2, "Расхождение должно быть в строке с trace_id = 2."
    row = mismatched_data[mismatched_data["trace_id"] == 2].iloc[0]

    assert row["fee_mismatch"], "fee_mismatch должен быть True."
    assert row["asset_mismatch"], "asset_mismatch должен быть True."
    assert row["fee_difference"] == pytest.approx(0.05), "fee_difference должен быть 0.05."
    assert not row["sign_mismatch"], "sign_mismatch должен быть False."


def test_save_summary_report(tmp_path, sample_summary):
    """Тестирует функцию save_summary_report на корректное сохранение файла."""
    output_file = tmp_path / "test_summary_report.csv"

    # Сохранение сводного отчета
    save_summary_report(sample_summary, output_file)

    # Проверка, что файл создан
    assert os.path.exists(output_file), "Файл сводного отчета не создан."

    # Проверка содержимого файла
    df = pd.read_csv(output_file)

    # Проверяем наличие ключевых метрик
    assert "Metric" in df.columns, "Отсутствует колонка 'Metric' в отчете."
    assert "Category" in df.columns, "Отсутствует колонка 'Category' в отчете."
    assert "Value" in df.columns, "Отсутствует колонка 'Value' в отчете."

    # Проверяем корректность количества строк
    expected_row_count = sum(
        len(value) if isinstance(value, dict) else 1 for value in sample_summary.values()
    )
    assert len(df) == expected_row_count, "Некорректное количество строк в отчете."

    # Проверяем наличие ключевой метрики "Total mismatched rows"
    assert df[df["Metric"] == "Total mismatched rows"]["Value"].iloc[0] == 5, (
        "Некорректное значение для 'Total mismatched rows'."
    )