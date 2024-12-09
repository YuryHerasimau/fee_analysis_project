# BHFT Interview Task
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

Test task for the position of [QA Analyst in Algorithmic Trading](https://geekjob.ru/company/62e009541534b2e76202ba79)

## Description
This project is designed to analyze platform and exchange fees to identify discrepancies.
The project includes two main stages: comparing fee data and identifying discrepancies.

## Project structure

```
fee_analysis_project/
├── data/ # Входные данные
│ ├── own_trade_log.csv
│ ├── order_log.csv
│ ├── dump_log.csv
├── output/ # Выходные данные
│ ├── commission_comparison.csv
│ ├── mismatched_data.csv
├── scripts/ # Скрипты для обработки данных
│ ├── data_analysis.py
│ ├── inconsistency_detection.py
├── README.md # Описание проекта
└── requirements.txt # Зависимости проекта
```

### Input data (`data/`)

1. **own_trade_log.csv**  
   Platform trade log containing information about fees, IDs and assets.

2. **order_log.csv** *(not used in the current version of the code, but reserved for future expansion)*  
   Order log.

3. **dump_log.csv**  
   Exchange log containing detailed messages about trades.

### Output data (`output/`)

1. **commission_comparison.csv**  
   Results of comparison of platform and exchange fees.

2. **mismatched_data.csv**  
   Results of discrepancy analysis, including information about asset types and the size of the discrepancy.


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
python scripts/inconsistency_detection.py
```