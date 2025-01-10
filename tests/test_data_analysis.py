import pytest
import pandas as pd
from scripts.data_analysis import extract_fee_from_message, load_data


def test_extract_fee_from_message_valid():
    message = '{"data": {"result": [{"fee": 0.05, "fee_currency": "BTC"}]}}'
    fee, fee_currency = extract_fee_from_message(message, "BTC")
    assert fee == 0.05
    assert fee_currency == "BTC"


def test_extract_fee_from_message_invalid():
    message = '{"data": {"result": {}}}'
    fee, fee_currency = extract_fee_from_message(message, "BTC")
    assert fee is None
    assert fee_currency is None


def test_load_data():
    try:
        own_trade_log, dump_log, order_log = load_data()
        assert isinstance(own_trade_log, pd.DataFrame)
        assert isinstance(dump_log, pd.DataFrame)
        assert isinstance(order_log, pd.DataFrame)
    except Exception as e:
        pytest.fail(f"Data loading failed: {e}")