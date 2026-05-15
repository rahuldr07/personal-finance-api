# Release Checklist

- Confirm tests pass.
- Confirm auth-protected endpoints require a bearer token.
- Review `.env.example` for safe defaults.
- Update `CHANGELOG.md`.
- Build the Docker image.
- Run a local smoke test against `/health`.
- Confirm dashboard, savings goal, and recurring expense endpoints appear in `/docs`.
- Export a CSV after adding at least one expense with merchant and payment method metadata.
