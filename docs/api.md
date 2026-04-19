# API Reference

## System

- `GET /health` checks whether the API is running.

## Auth

- `POST /auth/register` creates a user.
- `POST /auth/login` returns a bearer token.

## Expenses

- `POST /expenses` creates an expense.
- `GET /expenses` lists expenses for the logged-in user.
- `PATCH /expenses/{expense_id}` updates an expense.
- `DELETE /expenses/{expense_id}` deletes an expense.

## Reports

- `GET /reports/monthly?year=2026&month=5` returns monthly totals grouped by category.
- `GET /reports/yearly?year=2026` returns totals grouped by month.
- `GET /reports/export.csv` exports expenses as CSV.

## CLI

- `finance-cli register EMAIL PASSWORD` creates an account.
- `finance-cli login EMAIL PASSWORD` stores an access token.
- `finance-cli add TITLE AMOUNT CATEGORY SPENT_ON` creates an expense.
- `finance-cli list` prints recent expenses.
- `finance-cli summary YEAR MONTH` prints monthly totals.
- `finance-cli export --output expenses.csv` exports expense data.
