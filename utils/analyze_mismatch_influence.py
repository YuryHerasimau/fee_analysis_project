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