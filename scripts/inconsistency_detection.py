import pandas as pd


def load_comparison_data():
    """Загружает данные сравнения."""
    return pd.read_csv("output/commission_comparison.csv")


def detect_mismatches(data):
    """Выявляет расхождения между платформой и биржей."""
    # Сравнить платформенные и биржевые комиссии
    data["fee_mismatch"] = data["platform_fee_rate"] != data["exchange_fee_rate"]
    data["asset_mismatch"] = data["platform_fee_asset"] != data["exchange_fee_asset"]
    data['gt_fee_mismatch'] = data['platform_fee_rate'] != data['exchange_gt_fee_rate']
    data['gt_asset_mismatch'] = data['platform_fee_asset'] != data['exchange_gt_fee_asset']

    # Отфильтровать строки с расхождениями
    mismatched_data = data[
        (data['fee_mismatch']) | 
        (data['asset_mismatch']) | 
        (data['gt_fee_mismatch']) | 
        (data['gt_asset_mismatch'])
    ]

    # Проанализировать характер ошибок
    mismatched_data["fee_difference"] = (
        data["platform_fee_rate"] - data["exchange_fee_rate"]
    )
    mismatched_data['gt_fee_difference'] = (
        data['platform_fee_rate'] - data['exchange_gt_fee_rate']
    )
    mismatched_data["sign_mismatch"] = (
        ((data["platform_fee_rate"] > 0) & (data["exchange_fee_rate"] < 0)) |
        ((data["platform_fee_rate"] < 0) & (data["exchange_fee_rate"] > 0)) |
        ((data["platform_fee_rate"] > 0) & (data["exchange_gt_fee_rate"] < 0)) |
        ((data["platform_fee_rate"] < 0) & (data["exchange_gt_fee_rate"] > 0))
    )

    return mismatched_data


def summarize_mismatches(mismatched_data):
    """Выводит сводный отчет по расхождениям."""
    summary = {
        "Total mismatched rows": len(mismatched_data),
        "Mismatches by platform_fee_asset": mismatched_data["platform_fee_asset"].value_counts().to_dict(),
        "Mismatches by exchange_fee_asset": mismatched_data["exchange_fee_asset"].value_counts().to_dict(),
        "Mismatches by sign_mismatch": mismatched_data["sign_mismatch"].value_counts().to_dict(),
        "Mismatches by fee_mismatch": mismatched_data["fee_mismatch"].value_counts().to_dict(),
        "Mismatches by asset_mismatch": mismatched_data["asset_mismatch"].value_counts().to_dict(),
        "Mismatches by gt_fee_mismatch": mismatched_data["gt_fee_mismatch"].value_counts().to_dict(),
        "Mismatches by gt_asset_mismatch": mismatched_data["gt_asset_mismatch"].value_counts().to_dict(),
    }

    print("\nSummary of mismatched data:")
    for key, value in summary.items():
        print(f"{key}:")
        if isinstance(value, dict):
            for sub_key, sub_value in value.items():
                print(f"  {sub_key}: {sub_value}")
        else:
            print(f"  {value}")


def save_mismatches(mismatched_data):
    """Сохраняет расхождения в CSV."""
    mismatched_data.to_csv("output/mismatched_data.csv", index=False)
    print("Mismatches saved to output/mismatched_data.csv")


def main():
    data = load_comparison_data()
    mismatched_data = detect_mismatches(data)
    save_mismatches(mismatched_data)
    summarize_mismatches(mismatched_data)


if __name__ == "__main__":
    main()
