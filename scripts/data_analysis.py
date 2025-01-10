import pandas as pd
import json
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


def load_data():
    """Загружает входные данные."""
    try:
        own_trade_log = pd.read_csv("data/own_trade_log.csv")
        dump_log = pd.read_csv("data/dump_log.csv")
        order_log = pd.read_csv("data/order_log.csv")
        return own_trade_log, dump_log, order_log
    except FileNotFoundError as e:
        logging.error(f"Error loading data: {e}")
        raise


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


def extract_fee_from_message(message, fee_asset_name):
    """
    Извлекает комиссию из сообщения биржевого трафика.
    Если asset равен GT, возвращает gt_fee вместо fee.
    """
    try:
        data = json.loads(message)

        # Проверяем, является ли 'result' списком или словарем
        if isinstance(data["data"]["result"], list):
            first_result = data["data"]["result"][0]
        else:
            first_result = data["data"]["result"]

        # Используем gt_fee для GT-актива
        if fee_asset_name.upper() == "GT":
            fee = first_result.get("gt_fee", None)
            # Для GT используем 'GT' как ассет
            fee_currency = "GT" if fee else None
        else:
            fee = first_result.get("fee", None)
            fee_currency = first_result.get("fee_currency", None)

        return fee, fee_currency
    except (KeyError, json.JSONDecodeError, IndexError) as e:
        logging.error(f"Error extracting fee from message: {e}")
        return None, None


def compare_fees(own_trade_log, dump_log, order_log):
    """Сравнивает комиссии платформы и биржи, вычисляя ставку как отношение комиссии к объему сделки."""
    # Фильтруем dump_log по ключевым параметрам
    filtered_dump_log = dump_log[
        (dump_log["direction"] == "In")
        & (dump_log["message_name"] == "WsPayload")
        & (dump_log["message_kind"] == "Regular")
    ]

    comparison_data = []

    # Пройдем по всем записям в own_trade_log
    for _, row in own_trade_log.iterrows():
        trace_id = row["trace_id"]

        # Преобразуем значения к числовому типу
        fee_amount = pd.to_numeric(row["fee_amount"], errors="coerce")
        price = pd.to_numeric(row["price"], errors="coerce")
        base_amount = pd.to_numeric(row["base_amount"], errors="coerce")

        fee_asset_name = row["fee_asset_name"]
        base_asset = row["base_asset_name"]
        quote_asset = row["quote_asset_name"]
        side = row["side"]
        role = row["role"]
        is_fee_evaluated = row["is_fee_evaluated"]

        # Проверка на корректность значений перед расчетом
        if pd.notna(price) and pd.notna(base_amount) and price > 0 and base_amount > 0:
            trade_volume = price * base_amount
        else:
            trade_volume = 0

        # Вычисляем ставку комиссии платформы
        if trade_volume != 0 and pd.notna(fee_amount):
            # platform_fee_rate = round(fee_amount / trade_volume, 3)
            platform_fee_rate = round((fee_amount / trade_volume) * 100, 5)
        else:
            platform_fee_rate = 0

        # Найдем соответствующие сообщения в dump_log по trace_id
        related_dump_entries = filtered_dump_log[
            filtered_dump_log["trace_id"] == trace_id
        ]

        for _, dump_row in related_dump_entries.iterrows():
            message = dump_row["message"]

            # Извлекаем комиссию из сообщения
            exchange_fee_amount, exchange_fee_asset = extract_fee_from_message(
                message, fee_asset_name
            )

            # Проверка на корректность значений перед расчетом ставки комиссии биржи
            if trade_volume != 0 and pd.notna(exchange_fee_amount):
                # Преобразуем exchange_fee_amount к числовому типу
                exchange_fee_amount = pd.to_numeric(exchange_fee_amount, errors="coerce")
                
                if pd.notna(exchange_fee_amount):
                    # exchange_fee_rate = round(exchange_fee_amount / trade_volume, 3)
                    exchange_fee_rate = round((exchange_fee_amount / trade_volume) * 100, 5)
                else:
                    exchange_fee_rate = 0
            else:
                exchange_fee_rate = 0

            # Классифицируем asset для платформы и биржи
            platform_asset_type = classify_asset(
                fee_asset_name, base_asset, quote_asset
            )
            exchange_asset_type = (
                classify_asset(exchange_fee_asset, base_asset, quote_asset)
                if exchange_fee_asset
                else None
            )

            # Составляем запись для сравнения
            comparison_data.append(
                {
                    "trace_id": trace_id,
                    "side": side,
                    "role": role,
                    "is_fee_evaluated": is_fee_evaluated,
                    "platform_fee_rate": platform_fee_rate,
                    "platform_fee_asset": platform_asset_type,
                    "exchange_fee_rate": exchange_fee_rate,
                    "exchange_fee_asset": exchange_asset_type,
                }
            )

    # Преобразуем результат в DataFrame
    return pd.DataFrame(comparison_data)


def save_results(comparison_df, output_file="output/_fee_comparison.csv"):
    """Сохраняет результаты в CSV."""
    try:
        comparison_df.to_csv(output_file, index=False)
        logging.info(f"Results saved to {output_file}")
    except Exception as e:
        logging.error(f"Error saving results: {e}")
        raise


def group_comparison_data(comparison_df, group_by_columns, output_file):
    """Создаёт сгруппированную таблицу по заданным столбцам, вычисляя средние значения.."""
    # Группируем по указанным столбцам
    grouped = (
        comparison_df.groupby(group_by_columns)
        .agg(
            total_count=("trace_id", "count"),
            avg_platform_fee=("platform_fee_rate", "mean"),
            sum_platform_fee=("platform_fee_rate", "sum"),
            avg_exchange_fee=("exchange_fee_rate", "mean"),
            sum_exchange_fee=("exchange_fee_rate", "sum"),
        )
        .reset_index()
    )

    # Округляем числовые столбцы до 3 знаков после запятой
    grouped[["avg_platform_fee", "sum_platform_fee", "avg_exchange_fee", "sum_exchange_fee"]] = grouped[
        ["avg_platform_fee", "sum_platform_fee", "avg_exchange_fee", "sum_exchange_fee"]
    ].round(5)

    # Сохраняем результаты в CSV файл
    grouped.to_csv(output_file, index=False)
    logging.info(f"Grouped results saved to {output_file}")


def main():
    own_trade_log, dump_log, order_log = load_data()
    comparison_df = compare_fees(own_trade_log, dump_log, order_log)
    save_results(comparison_df)

    # Группировка итоговой таблицы по Side и Role
    group_comparison_data(
        comparison_df,
        ["side", "role"],
        "output/_fee_comparison_grouped_by_side_and_role.csv",
    )

    # Группировка итоговой таблицы по is_fee_evaluated
    group_comparison_data(
        comparison_df,
        ["is_fee_evaluated"],
        "output/_fee_comparison_grouped_by_fee_evaluated.csv",
    )


if __name__ == "__main__":
    main()
