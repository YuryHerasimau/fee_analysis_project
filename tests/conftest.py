import pytest
import pandas as pd
from scripts.data_analysis import load_data


@pytest.fixture
def sample_data(tmpdir):
    """Создает временные файлы с тестовыми данными."""
    own_trade_path = tmpdir.join("own_trade_log.csv")
    dump_log_path = tmpdir.join("dump_log.csv")
    order_log_path = tmpdir.join("order_log.csv")

    own_trade_data = """trace_id,fee_amount,price,base_amount,fee_asset_name,base_asset_name,quote_asset_name,side,role,is_fee_evaluated
1,0.001,100,1,USD,BTC,USD,bid,taker,True
2,0.002,200,2,USD,BTC,USD,ask,maker,True"""

    dump_log_data = """trace_id,direction,message_name,message_kind,message
1,In,WsPayload,Regular,{"data": {"result": [{"fee": 0.001, "fee_currency": "USD"}]}}
2,In,WsPayload,Regular,{"data": {"result": [{"fee": 0.002, "fee_currency": "USD"}]}}"""

    order_log_data = """trace_id,status,side
1,canceling,bid
2,filled,ask"""

    own_trade_path.write(own_trade_data)
    dump_log_path.write(dump_log_data)
    order_log_path.write(order_log_data)

    return str(own_trade_path), str(dump_log_path), str(order_log_path)


@pytest.fixture
def sample_data_extended():
    """Создаёт тестовые данные для сравнения."""
    own_trade_log = pd.DataFrame(
        {
            "trace_id": [1, 2, 3],
            "side": ["bid", "ask", "bid"],
            "role": ["taker", "maker", "taker"],
            "price": [100, 200, 300],
            "base_amount": [1, 2, 3],
            "base_asset_name": ["BTC", "BTC", "BTC"],
            "quote_amount": [100, 200, 300],
            "quote_asset_name": ["USD", "USD", "USD"],
            "fee_amount": [0.1, 0.25, 0.15],
            "fee_asset_name": ["USD", "USD", "BTC"],
            "is_fee_evaluated": [True, True, True],
        }
    )

    dump_log = pd.DataFrame(
        {
            "trace_id": [1, 2, 3],
            "direction": ["In", "In", "In"],
            "message_name": ["WsPayload", "WsPayload", "WsPayload"],
            "message_kind": ["Regular", "Regular", "Regular"],
            "message": [
                '{"data": {"result": [{"fee": 0.1, "fee_currency": "USD"}]}}',
                '{"data": {"result": [{"fee": 0.25, "fee_currency": "USD"}]}}',
                '{"data": {"result": [{"fee": 0.15, "fee_currency": "BTC"}]}}',
            ],
        }
    )

    order_log = pd.DataFrame(
        {
            "trace_id": [1, 2, 3],
            "status": ["canceling", "filled", "filled"],
            "side": ["bid", "ask", "bid"],
        }
    )

    return own_trade_log, dump_log, order_log


@pytest.fixture
def sample_comparison_data(tmpdir):
    """Создает временные файлы с данными для сравнения."""
    comparison_path = tmpdir.join("_fee_comparison.csv")

    comparison_data = """trace_id,platform_fee_rate,exchange_fee_rate,platform_fee_asset,exchange_fee_asset,side,role
1,0.1,0.1,USD,USD,buy,taker
2,0.2,0.15,USD,EUR,sell,maker"""

    comparison_path.write(comparison_data)
    return str(comparison_path)


@pytest.fixture
def sample_comparison_data_extended():
    """Создаёт тестовые данные для сохранения результатов."""
    return pd.DataFrame(
        {
            "trace_id": [1, 2, 3],
            "side": ["bid", "ask", "bid"],
            "role": ["taker", "maker", "taker"],
            "is_fee_evaluated": [True, True, True],
            "platform_fee_rate": [0.1, 0.2, 0.3],
            "platform_fee_asset": ["USD", "USD", "BTC"],
            "exchange_fee_rate": [0.1, 0.15, 0.3],
            "exchange_fee_asset": ["USD", "EUR", "BTC"],
        }
    )


@pytest.fixture
def sample_summary():
    """Пример сводного отчета для тестирования."""
    return {
        "Total mismatched rows": 5,
        "Mismatches by platform_fee_asset": {"BTC": 3, "ETH": 2},
        "Mismatches by exchange_fee_asset": {"BTC": 3, "ETH": 2},
        "Mismatches by sign_mismatch": {True: 1, False: 4},
        "Mismatches by fee_mismatch": {True: 2, False: 3},
        "Mismatches by asset_mismatch": {True: 3, False: 2},
    }