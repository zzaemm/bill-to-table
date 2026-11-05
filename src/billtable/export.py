import csv
import io

from .schema import Bill


def to_rows(bill: Bill) -> list[dict]:
    return [
        {
            "description": i.description,
            "quantity": i.quantity,
            "unit_price": i.unit_price,
            "amount": i.amount,
        }
        for i in bill.items
    ]


def to_csv(bill: Bill) -> str:
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=["description", "quantity", "unit_price", "amount"])
    w.writeheader()
    w.writerows(to_rows(bill))
    return buf.getvalue()
