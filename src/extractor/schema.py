"""The structured output schema.

A concrete, realistic extraction target: turn a free-text customer support
message into a structured ticket. Pydantic gives us validation for free — wrong
types, out-of-range values, or invalid enum members are rejected, which is
exactly what we feed back to the model on a retry.
"""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field


class Urgency(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"


class Sentiment(str, Enum):
    positive = "positive"
    neutral = "neutral"
    negative = "negative"


class SupportTicket(BaseModel):
    """Structured representation of a support message."""

    category: str = Field(description="Short topic label, e.g. 'billing', 'bug'.")
    urgency: Urgency = Field(description="How urgent the issue is.")
    sentiment: Sentiment = Field(description="The customer's emotional tone.")
    summary: str = Field(description="One-sentence summary of the request.")
    entities: list[str] = Field(
        default_factory=list,
        description="Notable entities mentioned (products, order ids, names).",
    )
    requires_human: bool = Field(
        description="True if a human agent should handle this."
    )
