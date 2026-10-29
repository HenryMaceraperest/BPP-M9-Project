# BPP-M9-Project
BPP Module 9 Project

# Getting Started
## First Initialisation
1. Clone from the git repository
2. Open a integrated terminal in VSC [Termial -> New Terminal]
3. python -m venv .venv
4. .\venv\Scripts\activate
5. pip install -r requirements.txt
6. dvc repro
7. dvc metrics show
8. python -m pytest -v
9. uvicorn src.api:app --reload

# Local data setup
python -m src.download_data
<!-- Should create data/raw/california_housing.parquet -->
dvc add data/raw/california_housing.parquet


# Local DVC Setup
## Create a DVC folder
New-Item `
    -ItemType Directory `
    -Path ..\california-housing-dvc-storage `
    -Force


## Cofigure it to be local storage
dvc remote add `
    --default `
    local-storage `
    ..\california-housing-dvc-storage

dvc push

<!-- Then you can use "dvc pull" to pull the data -->