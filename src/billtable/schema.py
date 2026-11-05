"""The shape every extracted bill must fit. The same model drives the LLM's JSON schema."""
from pydantic import BaseModel, Field


class LineItem(BaseModel):
    description: str
    quantity: float = Field(default=1, ge=0)
    unit_price: float | None = Field(default=None, ge=0)
    amount: float = Field(ge=0)


class Bill(BaseModel):
    vendor: str | None = None
    date: str | None = Field(default=None, description="ISO date YYYY-MM-DD if readable")
    currency: str | None = Field(default=None, description="e.g. INR, USD")
    items: list[LineItem] = Field(default_factory=list)
    subtotal: float | None = None
    tax: float | None = None
    total: float | None = None
