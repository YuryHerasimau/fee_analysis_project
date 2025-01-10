import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import logging


logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


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
        logging.info(f"Histogram saved: output/{mismatch_column}_by_{feature}_histogram.png")
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
        logging.info(f"Heatmap saved: output/{mismatch_column}_by_{feature}_heatmap.png")
        plt.close()


def visualize_mismatches(mismatched_data, mismatch_types, features):
    """Визуализирует расхождения с помощью гистограмм и тепловых карт."""
    for mismatch_type in mismatch_types:
        # Построение гистограмм
        plot_histograms(mismatched_data, mismatch_type, features)
        # Построение тепловых карт
        plot_heatmap(mismatched_data, mismatch_type, features)
