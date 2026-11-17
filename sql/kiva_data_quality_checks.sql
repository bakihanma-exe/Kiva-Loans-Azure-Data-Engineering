-- Run against the curated Silver kiva_loans table in Databricks SQL.
-- 1. Duplicate loan IDs (expected: no rows).
SELECT id, COUNT(*) AS duplicate_count FROM kiva_loans GROUP BY id HAVING COUNT(*) > 1;

-- 2. Null/invalid loan identifiers.
SELECT COUNT(*) AS invalid_id_count FROM kiva_loans WHERE id IS NULL OR id <= 0;

-- 3. Null or negative financial values; review exceptions rather than deleting rows.
SELECT COUNT(*) AS invalid_amount_count FROM kiva_loans WHERE loan_amount IS NULL OR loan_amount < 0 OR funded_amount < 0;

-- 4. Funded amount above requested amount; review, do not auto-delete.
SELECT COUNT(*) AS funded_over_loan_count FROM kiva_loans WHERE funded_amount > loan_amount;

-- 5. Invalid term/lender counts.
SELECT COUNT(*) AS invalid_term_or_lender_count FROM kiva_loans WHERE term_in_months < 0 OR lender_count < 0;

-- 6. Date ordering exceptions for review.
SELECT COUNT(*) AS date_order_exception_count FROM kiva_loans WHERE posted_time IS NOT NULL AND disbursed_time IS NOT NULL AND disbursed_time < posted_time;

-- 7. Row-count and distinct-key reconciliation.
SELECT COUNT(*) AS silver_loan_rows, COUNT(DISTINCT id) AS distinct_loan_ids FROM kiva_loans;
