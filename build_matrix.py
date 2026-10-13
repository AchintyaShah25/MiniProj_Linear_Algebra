import os
import pandas as pd
import numpy as np
import json
import scipy.sparse as sp

RAW = "data/raw/online_retail_II.xlsx"
CACHE = "data/cache/raw_combined.pkl"
OUT = "data/processed"
os.makedirs("data/cache", exist_ok=True)
os.makedirs(OUT, exist_ok=True)
if os.path.exists(CACHE):
    df = pd.read_pickle(CACHE)
else:
    sheets = pd.read_excel(RAW, sheet_name=None, dtype={"Invoice": str, "StockCode": str})
    df = pd.concat(sheets.values(), ignore_index=True)
    df.to_pickle(CACHE)  
df.columns = df.columns.str.strip()
features = df.columns.tolist()
initial_rows = len(df)
cleaning_log = []
def log_step(rule_name, before_df, after_df):
    dropped = len(before_df) - len(after_df)
    cleaning_log.append({
        "Cleaning Step": rule_name,
        "Rows Retained": len(after_df),
        "Rows Dropped": dropped,
        "% of Original Dropped": f"{(dropped / initial_rows) * 100:.2f}%"
    })
    return after_df
df = log_step("Drop missing Customer ID", df, df[df['Customer ID'].notna()])
df = log_step("Drop exact duplicates", df, df.drop_duplicates(keep='first'))
df = log_step("Drop non-product StockCodes", df, df[df['StockCode'].str.fullmatch(r'\d{5}[A-Z]*$')])
df = log_step("Drop 0 or negative price", df, df[df['Price'] > 0])
df['Customer ID'] = df['Customer ID'].astype(int).astype(str)
common_description = (
    df.groupby(['StockCode', 'Description'])
      .size()
      .reset_index(name='count')
      .sort_values('count', ascending=False)
      .drop_duplicates(subset='StockCode')
      .set_index('StockCode')['Description']
)
df['Description'] = df['StockCode'].map(common_description)
cleaning_log_df = pd.DataFrame(cleaning_log)
print(f"\n Retained {len(df):,} out of {initial_rows:,} rows ({(len(df)/initial_rows)*100:.2f}%).")
cutoff_date = df['InvoiceDate'].max() - pd.DateOffset(months=2)
print(cutoff_date)
def net(d, label):
    is_cancel = (d['Invoice'].str.startswith('C') | (d['Quantity'] <=0))
    pos = d.groupby(['Customer ID', 'StockCode'])['Quantity'].sum()
    returned = pos[pos <=0].index
    key = pd.MultiIndex.from_frame(d[['Customer ID', 'StockCode']])
    fully_returned = key.isin(returned) & ~is_cancel
    ac = log_step(f"{label} drop cancellations", d, d[~is_cancel])
    return log_step(f"{label} drop fully returned purchases", ac, d[~is_cancel & ~fully_returned])
train_df = net(df[df['InvoiceDate'] < cutoff_date].copy(), 'Train')
test_df = net(df[df['InvoiceDate'] >= cutoff_date].copy(), 'Test')
cleaning_log_df = pd.DataFrame(cleaning_log)
print(cleaning_log_df)
min_customers = 10
train_pairs = train_df[["Customer ID", "StockCode"]].drop_duplicates()
n_customers = train_pairs.groupby('StockCode').size()
keep_products = n_customers[n_customers >= min_customers].index
pairs = train_pairs[train_pairs['StockCode'].isin(keep_products)]
print(f"Products Kept: {len(keep_products)} of {len(n_customers)}")
customers = np.sort(pairs["Customer ID"].unique())
products = np.sort(pairs["StockCode"].unique())
cust_idx = pd.Series(np.arange(len(customers)), index=customers)
prod_idx = pd.Series(np.arange(len(products)), index=products)
A = sp.csr_matrix((np.ones(len(pairs)),
                   (pairs["Customer ID"].map(cust_idx).to_numpy(), pairs["StockCode"].map(prod_idx).to_numpy())),
                  shape=(len(customers), len(products)))
print(A.shape)
test_pairs = test_df[['Customer ID', 'StockCode']].drop_duplicates()
test_pairs = test_pairs[test_pairs['Customer ID'].isin(cust_idx.index)]
m = test_pairs.merge(train_pairs, on=["Customer ID", "StockCode"], how="left", indicator=True)
heldout = m[m["_merge"] == "left_only"].drop(columns="_merge").copy()
heldout["cust_row"] = heldout["Customer ID"].map(cust_idx)
heldout["in_matrix"] = heldout["StockCode"].isin(prod_idx.index)
heldout["prod_col"] = heldout["StockCode"].map(prod_idx).astype("Int64")
print(f"Test customers: {heldout['cust_row'].nunique()}")
print(f"Held-out pairs: {len(heldout):,}  |  not in matrix: {(~heldout['in_matrix']).mean():.1%}")
country = (train_df.groupby(["Customer ID", "Country"]).size().reset_index(name="n")
           .sort_values("n", ascending=False).drop_duplicates("Customer ID")
           .set_index("Customer ID")["Country"])
sp.save_npz(f"{OUT}/A_train.npz", A)
pd.DataFrame({"col": prod_idx.values, "StockCode": prod_idx.index,
              "Description": prod_idx.index.map(common_description),
              "n_customers": prod_idx.index.map(n_customers)}).to_csv(f"{OUT}/products.csv", index=False)
pd.DataFrame({"row": cust_idx.values, "Customer ID": cust_idx.index,
              "Country": cust_idx.index.map(country)}).to_csv(f"{OUT}/customers_internal.csv", index=False)
heldout[["cust_row", "prod_col", "StockCode", "in_matrix"]].to_csv(f"{OUT}/heldout.csv", index=False)
cleaning_log_df.to_csv(f"{OUT}/cleaning_log.csv", index=False)
rows, cols = A.shape
report = {
    "customers": rows, "products": cols, "non_zeros": int(A.nnz),
    "sparsity_%": round(100 * (1 - A.nnz / (rows * cols)), 3),
    "dense_MB": round(rows * cols * 8 / 1e6, 1),
    "sparse_MB": round((A.data.nbytes + A.indices.nbytes + A.indptr.nbytes) / 1e6, 2),
    "cutoff": str(cutoff_date), "min_customers_per_product": min_customers,
    "test_customers": int(heldout["cust_row"].nunique()), "heldout_pairs": len(heldout),
    "heldout_not_in_matrix_%": round(100 * (~heldout["in_matrix"]).mean(), 2),
}
with open(f"{OUT}/matrix_report.json", "w") as f:
    json.dump(report, f, indent=2)
print(pd.Series(report))