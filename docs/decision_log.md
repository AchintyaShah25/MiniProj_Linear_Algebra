# Decision log (R1)

Every decision with its reason. Add new ones at the bottom of the right section.

## Data decisions (owner: Achintya)

Choices are filled in from `Data_Engineer.ipynb`. Reasons still to be written.

| ID | Decision | Choice | Reason |
|---|---|---|---|
| D1 | Lines without a customer ID | Dropped (243,007 rows, 22.8%) | |
| D2 | Exact duplicate lines | Dropped (26,479 rows) | |
| D3 | Non-product codes | Kept only 5-digit codes with optional letters on the end; dropped 3,662 rows | |
| D4 | Zero or negative prices | Dropped (60 rows) | |
| D5 | Cancellations and returns | Dropped cancellation lines; dropped customer-product pairs fully returned within the same period | |
| D6 | Test period | Last 2 months, from 2011-10-09 12:50 | |
| D7 | Held-out purchases | Test purchases of products the customer never bought in training | |
| D8 | Purchase value | 1/0 "ever bought" | |
| D9 | Product filter | Bought by at least 10 distinct customers in training (3,680 of 4,519 kept) | |

## ML decisions (owner: Tanay)

| ID | Date | Decision | Choice | Reason |
|---|---|---|---|---|
| M1 | 2026-10-12 | Main method | Truncated SVD; PCA run as the comparison in ML5 | Matrix is 97.95% zeros; SVD works on it sparse without centring, captures co-buying directly, and gives customer and product factors in one fit. Written before fitting anything. |
| M2 | 2026-10-12 | k values to try | 10, 20, 50, 100, 200 | Set by the brief (ML2) |
| M3 | 2026-10-12 | How k is chosen | Reconstruction-error elbow, plus validation hit rate: smallest k within 1 percentage point of the best | Smaller k is cheaper to store and run; the test months are never used to pick k (R2) |
| M4 | 2026-10-12 | Validation split | Learn from before 2011-08-09, check against new products bought 2011-08-09 to 2011-10-09 | Same two-month setup as the real test, but entirely inside the training period |
| M5 | 2026-10-12 | Who counts in hit rate | All 1,919 test customers; held-out products outside the matrix count as misses for both model and baseline | Keeps the model vs baseline comparison fair |
| M6 | 2026-10-12 | Best-seller baseline | Top 10 products by distinct training customers, skipping ones the customer already bought | R3; distinct buyers rather than units so one bulk order can't make a "best seller" |
| M7 | 2026-10-12 | Random seed | 42 everywhere | Reproducibility (R6) |
| M8 | 2026-10-12 | Where the dated training lines come from | Run the code cells of `Data_Engineer.ipynb` inside my notebook, with its output folder redirected to a temp dir, and check it rebuilds `A_train.npz` exactly | `build_matrix.py` (DE6) isn't written yet; this avoids copying Achintya's cleaning into my notebook, and the check catches it if his code changes |
| M9 | 2026-10-12 | How a customer's products get scored | Picked on validation from three options: cosine on V (starter code), cosine on V·S, dot product on V (= rank-k rebuild) | The starter code is a starting point; tested the alternatives instead of assuming |
| M10 | 2026-10-12 | Product page box | Top 10 by cosine on V·S | On a product page there's no customer to score. Cosine on V·S approximates the cosine between two products' columns in A, i.e. how much their buyers overlap |
| M11 | 2026-10-12 | Customer map | Separate 10-component SVD, drop component 1, scale rows to length 1, k-means for 3 to 6 groups, keep the best silhouette | Component 1 is basket size, so dropping it groups customers by what they buy rather than how much; a separate fit keeps segments stable if the recommender's k changes |
| M12 | 2026-10-12 | ML7 purchase value check | Report count and log(1 + count) next to 1/0, on validation and test; main model stays 1/0 | Matrix was frozen on Day 4; ML7 is a finding and a next step, not a late switch |
