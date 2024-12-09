import pandas as pd
import json


def load_data():
    """Загружает входные данные."""
    own_trade_log = pd.read_csv("data/own_trade_log.csv")
    dump_log = pd.read_csv("data/dump_log.csv")
    return own_trade_log, dump_log


def classify_asset(asset, base_asset, quote_asset):
    """
    Классифицирует валюту как base, quote или aux.
    """
    if asset == base_asset:
        return "base"
    elif asset == quote_asset:
        return "quote"
    else:
        return "aux"


def extract_fee_from_message(message):
    """Извлекает комиссию из сообщения биржевого трафика"""
    try:
        data = json.loads(message)

        # Проверяем, является ли 'result' списком или словарем
        if isinstance(data["data"]["result"], list):
            # Если это список, обработатываем 1й элемент или выполнить итерацию по всем элементам
            first_result = data["data"]["result"][0]  # Adjust as necessary
            fee = first_result.get("fee", None)
            fee_currency = first_result.get("fee_currency", None)
        else:
            # Если 'result' является словарем
            fee = data["data"]["result"].get("fee", None)
            fee_currency = data["data"]["result"].get("fee_currency", None)

        return fee, fee_currency
    except (KeyError, json.JSONDecodeError, IndexError):
        return None, None


def compare_fees(own_trade_log, dump_log):
    """Сравнивает комиссии платформы и биржи."""
    comparison_data = []

    # Пройдем по всем записям в own_trade_log
    for _, row in own_trade_log.iterrows():
        trace_id = row["trace_id"]
        platform_fee_rate = row["fee_amount"]
        platform_fee_asset = row["fee_asset_name"]
        base_asset = row["base_asset_name"]
        quote_asset = row["quote_asset_name"]
        side = row["side"]
        role = row["role"]

        # Найдем соответствующие сообщения в dump_log по trace_id
        dump_entries = dump_log[dump_log["trace_id"] == trace_id]

        for _, dump_row in dump_entries.iterrows():
            message = dump_row["message"]

            # Извлекаем комиссию из сообщения
            exchange_fee_rate, exchange_fee_asset = extract_fee_from_message(message)

            # Классифицируем asset для платформы и биржи
            platform_asset_type = classify_asset(
                platform_fee_asset, base_asset, quote_asset
            )
            exchange_asset_type = (
                classify_asset(exchange_fee_asset, base_asset, quote_asset)
                if exchange_fee_asset
                else None
            )

            if exchange_fee_rate is not None:
                # Составляем запись для сравнения
                comparison_data.append(
                    {
                        "side": side,
                        "role": role,
                        "platform_fee_rate": platform_fee_rate,
                        "platform_fee_asset": platform_asset_type,
                        "exchange_fee_rate": exchange_fee_rate,
                        "exchange_fee_asset": exchange_asset_type,
                    }
                )

    # Преобразуем результат в DataFrame
    return pd.DataFrame(comparison_data)


def save_results(comparison_df):
    """Сохраняет результаты в CSV."""
    comparison_df.to_csv("output/commission_comparison.csv", index=False)
    print("Results saved to output/commission_comparison.csv")


def main():
    own_trade_log, dump_log = load_data()
    comparison_df = compare_fees(own_trade_log, dump_log)
    save_results(comparison_df)


if __name__ == "__main__":
    main()
