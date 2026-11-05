"""Sanity checks on extracted numbers. LLMs misread digits, so we verify the arithmetic."""
from .schema import Bill

TOLERANCE = 0.02


def check(bill: Bill) -> list[str]:
    warnings = []
    if not bill.items:
        warnings.append("No line items were found.")
        return warnings

    items_sum = round(sum(i.amount for i in bill.items), 2)

    for i in bill.items:
        if i.unit_price is not None and abs(i.quantity * i.unit_price - i.amount) > TOLERANCE * max(1, i.amount):
            warnings.append(
                f"'{i.description}': {i.quantity} x {i.unit_price} does not equal {i.amount}."
            )

    if bill.subtotal is not None and abs(items_sum - bill.subtotal) > TOLERANCE:
        warnings.append(f"Line items add up to {items_sum}, but subtotal says {bill.subtotal}.")

    if bill.total is not None:
        expected = (bill.subtotal if bill.subtotal is not None else items_sum) + (bill.tax or 0)
        if abs(expected - bill.total) > TOLERANCE:
            warnings.append(f"Subtotal + tax is {round(expected, 2)}, but total says {bill.total}.")
    else:
        warnings.append("No total was found on the bill.")
    return warnings
