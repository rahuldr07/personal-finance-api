# API Reference

## System

- `GET /health` checks whether the API is running.

## Auth

- `POST /auth/register` creates a user.
- `POST /auth/login` returns a bearer token.

## Expenses

- `POST /expenses` creates an expense.
- `GET /expenses` lists expenses for the logged-in user.
- `GET /expenses/{expense_id}` returns one expense.
- `PATCH /expenses/{expense_id}` updates an expense.
- `DELETE /expenses/{expense_id}` deletes an expense.

## Budgets

- `POST /budgets` creates a monthly category budget.
- `GET /budgets` lists budgets.
- `PATCH /budgets/{budget_id}` updates a budget.
- `DELETE /budgets/{budget_id}` deletes a budget.
- `GET /budgets/status/monthly?year=2026&month=5` compares budgets against spending.

## Recurring Expenses

- `POST /recurring-expenses` creates a recurring expense template.
- `GET /recurring-expenses` lists recurring expense templates by due date.
- `GET /recurring-expenses/{recurring_id}` returns one recurring expense template.
- `PATCH /recurring-expenses/{recurring_id}` updates a recurring expense template.
- `DELETE /recurring-expenses/{recurring_id}` removes a recurring expense template.

## Reports

- `GET /reports/monthly?year=2026&month=5` returns monthly totals grouped by category.
- `GET /reports/yearly?year=2026` returns totals grouped by month.
- `GET /reports/top-expenses?limit=5` returns the largest expenses.
- `GET /reports/category-shares?year=2026&month=5` returns category percentages.
- `GET /reports/insights?year=2026&month=5` returns spending count, total, average, largest expense, and highest category.
- `GET /reports/export.csv` exports expenses as CSV.

## CLI

- `finance-cli register EMAIL PASSWORD` creates an account.
- `finance-cli login EMAIL PASSWORD` stores an access token.
- `finance-cli add TITLE AMOUNT CATEGORY SPENT_ON` creates an expense.
- `finance-cli list` prints recent expenses.
- `finance-cli summary YEAR MONTH` prints monthly totals.
- `finance-cli budget-add CATEGORY LIMIT` creates a category budget.
- `finance-cli budget-status YEAR MONTH` prints monthly budget status.
- `finance-cli recurring-add TITLE AMOUNT CATEGORY FREQUENCY NEXT_DUE_ON` creates a recurring template.
- `finance-cli recurring-list` prints recurring templates.
- `finance-cli insights YEAR MONTH` prints monthly spending insights.
- `finance-cli export --output expenses.csv` exports expense data.
