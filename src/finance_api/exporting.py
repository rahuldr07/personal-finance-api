import csv
from io import StringIO

from finance_api import models


def expenses_to_csv(expenses: list[models.Expense]) -> str:
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(["id", "spent_on", "category", "amount", "title", "note"])
    for expense in expenses:
        writer.writerow(
            [
                expense.id,
                expense.spent_on.isoformat(),
                expense.category.value,
                f"{expense.amount:.2f}",
                expense.title,
                expense.note or "",
            ]
        )
    return output.getvalue()

