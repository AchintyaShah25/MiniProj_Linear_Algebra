# Customers Like You: PCA / SVD recommender for GiftLane

DS5020 mini-project. Achintya Shah (Data Engineer) and Tanay Mihani (ML Engineer).

## Success targets (J1)

Taken from Sarah's email and Section 1.4 of the brief. Draft by Tanay, needs Achintya's OK.

| # | What Sarah asked for | Target | How we measure it |
|---|---|---|---|
| 1 | Much smaller data | Stored factors at least 10x smaller than the dense matrix (160.6 MB), so under 16 MB | Size of customer + product factors at the chosen k |
| 2 | Nightly job is fast | Fit + similar-products table + top 10 for every customer in under 60 seconds on a laptop | Timed in ML4 |
| 3 | Better than best sellers | Hit rate at 10 on held-out test purchases is higher than the top-10 best-seller baseline | Hit rate at 10 over all 1,919 test customers |
| 4 | Customer groups marketing can name | 3 to 6 segments, each described by its top products and countries, no customer IDs | ML6 figure and segment table |

## Data

UCI Online Retail II: https://archive.ics.uci.edu/dataset/502/online+retail+ii (CC BY 4.0).

Download the zip, unzip it, and put `online_retail_II.xlsx` in `data/raw/`. The `data/` folder is not committed.

Row count check: **1,067,371 rows** across both sheets (2009-2010 and 2010-2011), confirmed in `Data_Engineer.ipynb`.

## How to run

From the repo root:

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

1. Put the raw file in `data/raw/` (see Data above).
2. Run `Data_Engineer.ipynb` top to bottom. It writes the matrix and index files to `data/processed/`. (To be replaced by `python build_matrix.py`, DE6.)
3. Run `ML_Engineer.ipynb` top to bottom.

All random steps use seed 42.

## Repository layout

| Path | What it is | Owner |
|---|---|---|
| `Data_Engineer.ipynb` | Profile, cleaning, time split, sparse matrix, matrix report (DE1 to DE5) | Achintya |
| `ML_Engineer.ipynb` | Method choice, fitting, recommendations, evaluation, customer map (ML1 to ML7) | Tanay |
| `docs/decision_log.md` | Every decision and its reason (R1) | Both |
| `docs/contribution_log.md` | Who did what, with evidence (C2) | Both |
| `requirements.txt` | Package versions (R6) | Both |
| `data/` | Raw and processed data, not committed | |

## Team roles

| Role | Person | Owns |
|---|---|---|
| Data Engineer | Achintya Shah | DE1 to DE6: raw data, cleaning, split, matrix |
| ML Engineer | Tanay Mihani | ML1 to ML7: method, recommendations, evaluation, customer map |
| Joint | Both | J1 targets, J2 memo, J3 slides |

## Privacy (R4)

Customer IDs only exist in `data/processed/customers_internal.csv`, which is never committed. Everything else uses row numbers or segment names.
