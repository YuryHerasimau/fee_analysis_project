import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from utils.visualization import plot_heatmap, plot_histograms, visualize_mismatches
from utils.analyze_mismatch_influence import analyze_mismatch_influence


def load_comparison_data():
    """Загружает данные сравнения."""
    return pd.read_csv("output/_fee_comparison.csv")


def detect_mismatches(data):
    """Выявляет расхождения между платформой и биржей."""
    # Сравнить платформенные и биржевые комиссии
    data["fee_mismatch"] = data["platform_fee_rate"] != data["exchange_fee_rate"]
    data["asset_mismatch"] = data["platform_fee_asset"] != data["exchange_fee_asset"]

    # Отфильтровать строки с расхождениями
    mismatched_data = data[(data["fee_mismatch"]) | (data["asset_mismatch"])]

    # Проанализировать характер ошибок
    mismatched_data["fee_difference"] = (
        data["platform_fee_rate"] - data["exchange_fee_rate"]
    )
    mismatched_data["sign_mismatch"] = (
        (data["platform_fee_rate"] > 0) & (data["exchange_fee_rate"] < 0)
    ) | ((data["platform_fee_rate"] < 0) & (data["exchange_fee_rate"] > 0))

    return mismatched_data


def save_summary_report(summary, output_file):
    """Сохраняет сводный отчет по расхождениям в CSV."""
    summary_rows = [
        {"Metric": key, "Category": sub_key, "Value": sub_value}
        for key, value in summary.items()
        for sub_key, sub_value in (value.items() if isinstance(value, dict) else [(None, value)])
    ]

    summary_df = pd.DataFrame(summary_rows)
    summary_df.to_csv(output_file, index=False)
    print(f"Summary report saved to {output_file}")


# def format_summary(summary):
#     """Форматирует сводный отчет для печати."""
#     formatted = []
#     for key, value in summary.items():
#         if isinstance(value, dict):
#             formatted.append(f"{key}:")
#             formatted.extend([f"  {sub_key}: {sub_value}" for sub_key, sub_value in value.items()])
#         else:
#             formatted.append(f"{key}: {value}")
#     return "\n".join(formatted)
    

def summarize_mismatches(mismatched_data, output_file="output/_mismatched_summary.csv"):
    """Выводит и сохраняет сводный отчет по расхождениям."""
    summary = {
        "Total mismatched rows": len(mismatched_data),
        "Mismatches by platform_fee_asset": mismatched_data["platform_fee_asset"].value_counts().to_dict(),
        "Mismatches by exchange_fee_asset": mismatched_data["exchange_fee_asset"].value_counts().to_dict(),
        "Mismatches by sign_mismatch": mismatched_data["sign_mismatch"].value_counts().to_dict(),
        "Mismatches by fee_mismatch": mismatched_data["fee_mismatch"].value_counts().to_dict(),
        "Mismatches by asset_mismatch": mismatched_data["asset_mismatch"].value_counts().to_dict(),
    }

    # print("\nSummary of mismatched data:")
    # print(format_summary(summary))
    save_summary_report(summary, output_file)


def summarize_grouped_mismatches(mismatched_data, output_file="output/_grouped_summary.csv"):
    """Создает группировку по Side и Role."""
    grouped = mismatched_data.groupby(['side', 'role']).size().reset_index(name='count')
    grouped.to_csv(output_file, index=False)
    print(f"Grouped summary saved to {output_file}")


def save_mismatches(mismatched_data, output_file="output/_mismatched_data.csv"):
    """Сохраняет расхождения в CSV."""
    mismatched_data.to_csv(output_file, index=False)
    print(f"Mismatches saved to {output_file}")


def main():
    data = load_comparison_data()
    mismatched_data = detect_mismatches(data)
    save_mismatches(mismatched_data)
    
    # Сводный отчет о расхождениях
    summarize_mismatches(mismatched_data)

    # Группировка расхождений по Side и Role
    summarize_grouped_mismatches(mismatched_data)

    # Анализ влияния переменных
    mismatch_types = ["fee_mismatch", "asset_mismatch", "fee_difference", "sign_mismatch"]
    features = ["side", "role","is_fee_evaluated"]

    analysis_results = {}

    for mismatch_type in mismatch_types:
        for feature in features:
            print(f"Analyzing {mismatch_type} by {feature}...")
            result = analyze_mismatch_influence(mismatched_data, mismatch_type, feature)
            analysis_results[f"{mismatch_type}_{feature}"] = result
            print(result)
            print("\n")

    # Визуализация
    visualize_mismatches(mismatched_data, mismatch_types, features)
       
if __name__ == "__main__":
    main()
