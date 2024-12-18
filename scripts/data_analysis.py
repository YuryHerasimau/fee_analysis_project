import pandas as pd
import json


def load_data():
    """Загружает входные данные."""
    own_trade_log = pd.read_csv("data/own_trade_log.csv")
    dump_log = pd.read_csv("data/dump_log.csv")
    order_log = pd.read_csv("data/order_log.csv")
    return own_trade_log, dump_log, order_log


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
    except (KeyError, json.JSONDecodeError, IndexError):
        return None, None


def compare_fees(own_trade_log, dump_log, order_log):
    """Сравнивает комиссии платформы и биржи."""
    # Фильтруем dump_log по ключевым параметрам
    filtered_dump_log = dump_log[
        (dump_log['direction'] == 'In') &
        (dump_log['message_name'] == 'WsPayload') &
        (dump_log['message_kind'] == 'Regular')
    ]

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
        is_fee_evaluated = row['is_fee_evaluated']

        # Найдем соответствующие сообщения в dump_log по trace_id
        related_dump_entries = filtered_dump_log[filtered_dump_log["trace_id"] == trace_id]
    
        for _, dump_row in related_dump_entries.iterrows():
            message = dump_row["message"]

            # Извлекаем комиссию из сообщения
            exchange_fee_rate, exchange_fee_asset = extract_fee_from_message(
                message, platform_fee_asset
            )

            # Классифицируем asset для платформы и биржи
            platform_asset_type = classify_asset(
                platform_fee_asset, base_asset, quote_asset
            )
            exchange_asset_type = (
                classify_asset(exchange_fee_asset, base_asset, quote_asset)
                if exchange_fee_asset
                else None
            )

            # Составляем запись для сравнения
            comparison_data.append(
                {
                    'trace_id': trace_id,
                    "side": side,
                    "role": role,
                    'is_fee_evaluated': is_fee_evaluated,
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
    comparison_df.to_csv(output_file, index=False)
    print(f"Results saved to {output_file}")


def group_comparison_data(comparison_df, group_by_columns, output_file):
    """Создаёт сгруппированную таблицу по заданным столбцам, вычисляя средние значения.."""
    # Преобразуем числовые столбцы к числовому типу
    numeric_columns = ['platform_fee_rate', 'exchange_fee_rate']
    for col in numeric_columns:
        comparison_df[col] = pd.to_numeric(comparison_df[col], errors='coerce')
    
    # Заполняем NaN значениями 0 или другим подходящим значением
    comparison_df.fillna(0, inplace=True)

    # Группируем по указанным столбцам
    grouped = (
        comparison_df.groupby(group_by_columns)
        .agg(
            total_count=('trace_id', 'count'),
            avg_platform_fee=('platform_fee_rate', 'mean'),
            sum_platform_fee=('platform_fee_rate', 'sum'),
            avg_exchange_fee=('exchange_fee_rate', 'mean'),
            sum_exchange_fee=('exchange_fee_rate', 'sum'),
        )
        .reset_index()
    )
    # Сохраняем результаты в CSV файл
    grouped.to_csv(output_file, index=False)
    print(f"Grouped results saved to {output_file}")


def main():
    own_trade_log, dump_log, order_log = load_data()
    comparison_df = compare_fees(own_trade_log, dump_log, order_log)
    save_results(comparison_df)

    # Группировка итоговой таблицы по Side и Role
    group_comparison_data(comparison_df, ['side', 'role'], "output/_fee_comparison_grouped_by_side_and_role.csv")

    # Группировка итоговой таблицы по is_fee_evaluated
    group_comparison_data(comparison_df, ['is_fee_evaluated'], "output/_fee_comparison_grouped_by_fee_evaluated.csv")

if __name__ == "__main__":
    main()
    