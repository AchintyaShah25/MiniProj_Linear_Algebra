# Customers Like You: PCA / SVD recommender for GiftLane

DS5020 mini-project. Achintya Shah (Data Engineer) and Tanay Mihani (ML Engineer).

## Success targets (J1)

Taken from Sarah's email and Section 1.4 of the brief.

| # | What Sarah asked for | Target | How we measure it |
|---|---|---|---|
| 1 | Much smaller data | Stored factors at least 10x smaller than the dense matrix (160.6 MB), so under 16 MB | Size of customer + product factors at the chosen k |
| 2 | Nightly job is fast | Fit + similar-products table + top 10 for every customer in under 60 seconds on a laptop | Timed in ML4 |
| 3 | Better than best sellers | Hit rate at 10 on held-out test purchases is higher than the top-10 best-seller baseline | Hit rate at 10 over all 1,919 test customers |
| 4 | Customer groups marketing can name | 3 to 6 segments, each described by its top products and countries, no customer IDs | ML6 figure and segment table |

### Results against the targets

| # | Result |
|---|---|
| 1 | 7.31 MB of factors at k = 100, 22x smaller than the dense matrix. Met |
| 2 | About 1 s for the whole nightly job. Met |
| 3 | Hit rate at 10 of 40.9% vs 26.5% for best sellers, on 1,919 test customers. Met |
| 4 | 6 groups: heart and wicker home decor, traditional toys and crafts, funny metal signs, Regency tea and baking, kids' party tableware, jumbo bags and storage. Met |

Details are in `ML_Engineer.ipynb` (section 16 summarises), the memo is `docs/memo.pdf` and the slides are `docs/slides.pptx`. `DS5020_MiniProject_Shah_Mihani.pdf` combines a cover page (team, repository link, contents), the memo and the slides in one file.

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
2. Run `python build_matrix.py` (or `Data_Engineer.ipynb` top to bottom). Either one writes the matrix and index files to `data/processed/` and caches the raw file in `data/cache/`.
3. Run `ML_Engineer.ipynb` top to bottom. Section 5 re-runs the code in `Data_Engineer.ipynb` to get the dated training lines, so that notebook and the raw file (or its cache) need to be there. It writes figures to `figures/` and the numbers quoted in the memo to `results/results.json`.

All random steps use seed 42.

## Repository layout

| Path | What it is | Owner |
|---|---|---|
| `DS5020_MiniProject_Shah_Mihani.pdf` | Submission file: cover page, memo and slides | Both |
| `Data_Engineer.ipynb` | Profile, cleaning, time split, sparse matrix, matrix report (DE1 to DE5) | Achintya |
| `build_matrix.py` | The same pipeline as one script: rebuilds `data/processed/` from the raw file (DE6) | Achintya |
| `ML_Engineer.ipynb` | Method choice, validation, recommendations, evaluation, PCA comparison, customer map, purchase value check (ML1 to ML7) | Tanay |
| `figures/` | Figures from `ML_Engineer.ipynb` (no customer IDs) | Tanay |
| `results/` | `results.json` and `segments.csv` from `ML_Engineer.ipynb`; `cleaning_log.csv` and `matrix_report.json` from `build_matrix.py` (DE2, DE5). No customer IDs | Tanay, Achintya |
| `docs/decision_log.md` | Every decision and its reason (R1) | Both |
| `docs/memo.pdf`, `docs/slides.pptx` | One-page memo to Sarah (J2) and the 5-minute presentation (J3) | Both |
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

Customer IDs only exist in `data/processed/customers_internal.csv` and in memory while the notebooks run. Neither is committed. Everything else uses row numbers or segment names.
