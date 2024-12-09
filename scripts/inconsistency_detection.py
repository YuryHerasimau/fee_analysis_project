import pandas as pd


def load_comparison_data():
    """Загружает данные сравнения."""
    return pd.read_csv("output/commission_comparison.csv")


def detect_mismatches(data):
    """Выявляет расхождения между платформой и биржей."""
    # Сравнить платформенные и биржевые комиссии
    data["fee_mismatch"] = data["platform_fee_rate"] != data["exchange_fee_rate"]
    data["asset_mismatch"] = data["platform_fee_asset"] != data["exchange_fee_asset"]

    # Отфильтровать строки с расхождениями
    mismatched_data = data[(data["fee_mismatch"]) | (data["asset_mismatch"])]

    # Проанализировать характер ошибок
    mismatched_data["difference"] = (
        data["platform_fee_rate"] - data["exchange_fee_rate"]
    )
    mismatched_data["sign_mismatch"] = (
        (data["platform_fee_rate"] > 0) & (data["exchange_fee_rate"] < 0)
    ) | ((data["platform_fee_rate"] < 0) & (data["exchange_fee_rate"] > 0))

    return mismatched_data


def save_mismatches(mismatched_data):
    """Сохраняет расхождения в CSV."""
    mismatched_data.to_csv("output/mismatched_data.csv", index=False)
    print("Mismatches saved to output/mismatched_data.csv")


def main():
    data = load_comparison_data()
    mismatched_data = detect_mismatches(data)
    save_mismatches(mismatched_data)
    print(mismatched_data["platform_fee_asset"].value_counts())


if __name__ == "__main__":
    main()
