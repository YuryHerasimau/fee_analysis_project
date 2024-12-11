import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


def load_comparison_data():
    """Загружает данные сравнения."""
    return pd.read_csv("output/_fee_comparison.csv")


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
    mismatched_data.to_csv("output/_mismatched_data.csv", index=False)
    print("Mismatches saved to output/_mismatched_data.csv")


def analyze_mismatch_influence(data, mismatch_column, feature_column):
    """
    Анализирует влияние переменной feature_column на расхождения в mismatch_column.
    """
    summary = data.groupby(feature_column)[mismatch_column].agg(
        count="size",  # Общее количество записей
        mismatched_count="sum",  # Количество расхождений
        proportion=lambda x: x.mean()  # Доля расхождений
    ).reset_index()
    summary = summary.sort_values(by="mismatched_count", ascending=False)
    return summary


def save_analysis_results(results, output_dir):
    """Сохраняет результаты анализа в CSV."""
    for mismatch_type, result in results.items():
        output_file = f"{output_dir}/{mismatch_type}_analysis.csv"
        result.to_csv(output_file, index=False)
        print(f"Analysis for {mismatch_type} saved to {output_file}")


def plot_histograms(data, mismatch_column, features):
    """Строит гистограммы только для значимых переменных, связанных с расхождением."""
    for feature in features:
        plt.figure(figsize=(10, 6))
        sns.countplot(data=data, x=feature, hue=mismatch_column, palette="viridis")
        plt.title(f"Histogram of {mismatch_column} by {feature}")
        plt.xlabel(feature)
        plt.ylabel("Count")
        plt.legend(title=mismatch_column, loc="upper right")
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(f"output/{mismatch_column}_by_{feature}_histogram.png")
        print(f"Histogram saved: output/{mismatch_column}_by_{feature}_histogram.png")
        plt.close()


def plot_heatmap(data, mismatch_column, features):
    """Строит тепловые карты только для значимых взаимосвязей переменных."""
    for feature in features:
        contingency_table = pd.crosstab(data[mismatch_column], data[feature])
        plt.figure(figsize=(10, 6))
        sns.heatmap(contingency_table, annot=True, fmt="d", cmap="YlGnBu")
        plt.title(f"Heatmap of {mismatch_column} by {feature}")
        plt.xlabel(feature)
        plt.ylabel(mismatch_column)
        plt.tight_layout()
        plt.savefig(f"output/{mismatch_column}_by_{feature}_heatmap.png")
        print(f"Heatmap saved: output/{mismatch_column}_by_{feature}_heatmap.png")
        plt.close()


def main():
    data = load_comparison_data()
    mismatched_data = detect_mismatches(data)
    save_mismatches(mismatched_data)
    
    # Сводный отчет о расхождениях
    summarize_mismatches(mismatched_data)

    # Анализ влияния переменных
    mismatch_types = ["fee_mismatch", "asset_mismatch", "gt_fee_mismatch", "gt_asset_mismatch"]
    features = ["side", "role", "source", "is_fee_evaluated", "order_status"]

    analysis_results = {}
    for mismatch_type in mismatch_types:
        for feature in features:
            print(f"Analyzing {mismatch_type} by {feature}...")
            result = analyze_mismatch_influence(mismatched_data, mismatch_type, feature)
            analysis_results[f"{mismatch_type}_{feature}"] = result
            print(result)
            print("\n")
    
    save_analysis_results(analysis_results, "output")

    # Визуализация
    for mismatch_type in mismatch_types:
        # Построение гистограмм
        plot_histograms(mismatched_data, mismatch_type, features)
        # Построение тепловых карт
        plot_heatmap(mismatched_data, mismatch_type, features)
        
    print("Analysis completed.")

       
if __name__ == "__main__":
    main()
