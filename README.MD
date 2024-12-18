# BHFT Interview Task
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

Test task for the position of [QA Analyst in Algorithmic Trading](https://geekjob.ru/company/62e009541534b2e76202ba79)

## Description
This project is designed to analyze platform and exchange fees to identify discrepancies.
The project includes two main stages: comparing fee data and identifying discrepancies.

## Project structure

```
fee_analysis_project/
├── data/ # Input data
│ ├── own_trade_log.csv
│ ├── order_log.csv
│ ├── dump_log.csv # Hidden due to large size
├── output/ # Output data
│ ├── _fee_comparison.csv
│ ├── _mismatched_data.csv
├── scripts/ # Data Processing Scripts
│ ├── data_analysis.py
│ ├── inconsistency_detection.py
├── utils/
│ ├── analyze_mismatch_influence.py
│ ├── visualization.py
├── README.md # Project Description
└── requirements.txt # Project Dependencies
```

### Input data (`data/`)

1. **own_trade_log.csv**  
   Platform trade log containing information about fees, IDs and assets.

2. **order_log.csv**  
   Order log containing all orders placed on the exchange.

3. **dump_log.csv**  
   Exchange log containing detailed messages about trades.

### Output data (`output/`)

1. **_fee_comparison.csv**  
   Results of comparison of platform and exchange fees.

2. **_fee_comparison_grouped_by_fee_evaluated.csv**

3. **_fee_comparison_grouped_by_side_and_role.csv**

4. **_mismatched_data.csv**  
   Results of discrepancy analysis, including information about asset types and the size of the discrepancy.

5. **_mismatched_summary.csv**

6. **_grouped_summary.csv**  
   Grouping discrepancies by Side and Role

7. **histograms and heatmaps**  
  Visualizing fee discrepancies based on key features

## Getting Started

### Installing 
1. Clone the repository:
```
git clone https://github.com/YuryHerasimau/fee_analysis_project.git
```
2. Install the required dependencies:
```
pip install -r requirements.txt
``` 

### Usage
1. Commission comparison (creating `commission_comparison.csv`). To run, use the `data_analysis.py` script:
```
python scripts/data_analysis.py
```

2. Detecting discrepancies (creating `mismatched_data.csv`). To run, use the `inconsistency_detection.py` script:
```
python -m scripts.inconsistency_detection
```

## Results

### Summary of Mismatched Data
Below is a summary of discrepancies identified during the analysis:

* [Total mismatched rows](output/_mismatched_summary.csv): 35
* Breakdown by mismatch type:
   * `fee_mismatch`: 35 cases
   * `asset_mismatch`: 28 cases
   * `sign_mismatch`: 0 cases

**Top Contributing Features to Mismatches**

The features with the highest influence on mismatches are:
* [side & role](output/_fee_comparison_grouped_by_side_and_role.csv)
* [is_fee_evaluated](output/_fee_comparison_grouped_by_fee_evaluated.csv)

### Visualizations
Also created visualizations to understand the influence of these features.

Example 1: Histogram of `fee_mismatch` by `is_fee_evaluated`
<img src="output/asset_mismatch_by_is_fee_evaluated_histogram.png" width=600/ 
alt="asset_mismatch_by_is_fee_evaluated_histogram" />

Example 2: Heatmap of `asset_mismatch` by `role`
<img src="output/asset_mismatch_by_role_heatmap.png" width=600/ alt="asset_mismatch_by_role_heatmap" />

Example 3: Histogram of `fee_difference` by `side`
<img src="output/fee_difference_by_side_histogram.png" width=600/ alt="fee_difference_by_side_histogram" />


## What can be improved
- [X] Include `gt_fee` from `dump_log` in fee comparison
- [X] Filter `dump_log` by key parameters
<!-- - [X] Enable `order_log` analysis to check order statuses -->
- [X] Enable `is_fee_evaluated` analysis to understand trading context
<!-- - [X] Enable `source` analysis to understand trading context -->
- [X] Show fee discrepancies with histograms and heat maps
- [ ] Use `chunking` in pandas to work with large files
- [ ] Add error handling
- [ ] Use `logging` to inform about operation execution instead of `print`
- [ ] Add tests
