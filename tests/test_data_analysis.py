import pytest
import pandas as pd
import json
import os
from scripts.data_analysis import (
    extract_fee_from_message,
    load_data,
    compare_fees,
    save_results,
    group_comparison_data
)


def test_extract_fee_from_message_valid():
    # message = '{"data": {"result": [{"fee": 0.05, "fee_currency": "BTC"}]}}'
    message = json.dumps(
        {
            "data": {
                "result": {
                    "fee": 0.05,
                    "fee_currency": "USD",
                    "gt_fee": 0.02,
                }
            }
        }
    )
    fee, fee_currency = extract_fee_from_message(message, "BTC")
    assert fee == 0.05, "Комиссия должна быть равна 0.05."
    assert fee_currency == "USD", "Валюта комиссии должна быть USD."

    # Тест для GT актива
    fee, fee_currency = extract_fee_from_message(message, "GT")
    assert fee == 0.02, "Комиссия для GT должна быть равна 0.02."
    assert fee_currency == "GT", "Валюта комиссии для GT должна быть GT."


def test_extract_fee_from_message_invalid():
    message = '{"data": {"result": {}}}'
    fee, fee_currency = extract_fee_from_message(message, "BTC")

    assert fee is None
    assert fee_currency is None

    # Тест для GT актива
    fee, fee_currency = extract_fee_from_message(message, "GT")
    assert fee is None
    assert fee_currency is None


def test_load_data(sample_data):
    """Тест успешной загрузки данных."""
    own_trade_path, dump_log_path, order_log_path = sample_data
    own_trade_log, dump_log, order_log = load_data(own_trade_path, dump_log_path, order_log_path)

    assert not own_trade_log.empty, "own_trade_log должен быть загружен."
    assert not dump_log.empty, "dump_log должен быть загружен."
    assert not order_log.empty, "order_log должен быть загружен."

    assert isinstance(own_trade_log, pd.DataFrame), "own_trade_log должен быть DataFrame."
    assert isinstance(dump_log, pd.DataFrame), "dump_log должен быть DataFrame."
    assert isinstance(order_log, pd.DataFrame), "order_log должен быть DataFrame."

    assert len(own_trade_log) == 2, "own_trade_log должен содержать 2 записи."


def test_load_data_file_not_found():
    """Тест обработки ошибки при отсутствии файла."""
    with pytest.raises(FileNotFoundError):
        load_data("nonexistent.csv", "nonexistent.csv", "nonexistent.csv")


def test_compare_fees(sample_data_extended):
    """Тест сравнения комиссий."""
    own_trade_log, dump_log, order_log = sample_data_extended

    comparison_df = compare_fees(own_trade_log, dump_log, order_log)

    assert not comparison_df.empty, "Результирующий DataFrame не должен быть пустым."
    assert "platform_fee_rate" in comparison_df.columns, "Должна быть колонка platform_fee_rate."
    assert "exchange_fee_rate" in comparison_df.columns, "Должна быть колонка exchange_fee_rate."
    assert len(comparison_df) == len(own_trade_log), "Количество строк должно совпадать с own_trade_log."


def test_save_results(tmp_path, sample_comparison_data_extended):
    """Тест сохранения результатов."""
    output_file = tmp_path / "test_fee_comparison.csv"
    save_results(sample_comparison_data_extended, output_file)

    assert os.path.exists(output_file), "Файл с результатами не создан."
    
    # Проверяем содержимое файла
    df = pd.read_csv(output_file)

    assert len(df) == len(sample_comparison_data_extended), "Количество строк в файле должно совпадать с входными данными."
    assert "platform_fee_rate" in df.columns, "Должна быть колонка platform_fee_rate."
    assert "exchange_fee_rate" in df.columns, "Должна быть колонка exchange_fee_rate."
    assert "platform_fee_asset" in df.columns, "Должна быть колонка platform_fee_asset."
    assert "exchange_fee_asset" in df.columns, "Должна быть колонка exchange_fee_asset."


def test_group_comparison_data(tmp_path, sample_comparison_data_extended):
    """Тест группировки данных."""
    output_file = tmp_path / "test_grouped_comparison.csv"

    group_comparison_data(sample_comparison_data_extended, ["side", "role"], output_file)

    assert os.path.exists(output_file), "Файл с группированными данными не создан."

    grouped_df = pd.read_csv(output_file)
    assert "total_count" in grouped_df.columns, "Должна быть колонка total_count."
    assert "avg_platform_fee" in grouped_df.columns, "Должна быть колонка avg_platform_fee."
