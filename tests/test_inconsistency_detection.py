import pytest
import pandas as pd
from scripts.inconsistency_detection import (
    load_comparison_data,
    detect_mismatches,
    save_summary_report,
    summarize_mismatches,
    summarize_grouped_mismatches
)
from io import StringIO


# Пример данных для тестирования
mock_data = """
trace_id,side,role,is_fee_evaluated,platform_fee_rate,platform_fee_asset,exchange_fee_rate,exchange_fee_asset
1,buy,maker,True,0.1,base,0.1,base
2,sell,taker,True,0.05,quote,0.05,quote
3,buy,maker,False,0.08,base,0.08,quote
4,sell,taker,True,0.1,aux,0.12,aux
"""


# Функция для загрузки данных для теста
def mock_load_data():
    return pd.read_csv(StringIO(mock_data))


def test_load_comparison_data(monkeypatch):
    """Тестирование загрузки данных."""
    # Используем mock-данные для теста
    monkeypatch.setattr("scripts.inconsistency_detection.load_comparison_data", mock_load_data)
    
    data = load_comparison_data()
    
    # Проверяем, что данные загружены правильно
    assert isinstance(data, pd.DataFrame)
    assert data.shape == (4, 8)


def test_detect_mismatches():
    """Тестирование обнаружения расхождений"""
    data = mock_load_data()
    
    mismatched_data = detect_mismatches(data)
    
    # Проверяем, что найдено 1 расхождение (строка с trace_id=4)
    assert len(mismatched_data) == 1
    assert mismatched_data["fee_mismatch"].iloc[0] is True
    assert mismatched_data["asset_mismatch"].iloc[0] is False


def test_save_summary_report():
    """Тестирование сохранения сводного отчета"""
    summary = {
        "Total mismatched rows": 1,
        "Mismatches by platform_fee_asset": {"base": 1},
        "Mismatches by exchange_fee_asset": {"base": 1},
    }
    
    # Пример того, что может быть сохранено
    output = StringIO()
    save_summary_report(summary, output)
    
    # Проверим, что сводный отчет был записан в output
    output.seek(0)
    result = output.read()
    assert "Total mismatched rows" in result
    assert "Mismatches by platform_fee_asset" in result
