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

