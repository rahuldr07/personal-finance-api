# Security Notes

## Authentication

The API uses bearer tokens signed with `SECRET_KEY`. Local development can use the example
value, but any shared or deployed environment must set a unique secret.

## Passwords

Passwords are hashed with bcrypt through Passlib. Plaintext passwords are accepted only at
registration and login boundaries.

## Data Scope

Expense queries are scoped to the authenticated user. Shared helper functions require the
current user object before reading or mutating expense data.

## Local Files

SQLite databases and `.env` files are ignored by Git and Docker builds to avoid leaking local
state or secrets.

