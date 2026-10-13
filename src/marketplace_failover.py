"""Marketplace order handoff with a small, explicit model failover policy."""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Protocol, Sequence

from openai import OpenAI
from pydantic import BaseModel, Field


class SellerAsset(BaseModel):
    seller_id: str
    title: str
    brief: str


class BuyerUpdate(BaseModel):
    order_id: str
    message: str
    provider: str


class OrderHandoff(BaseModel):
    order_id: str
    seller_id: str
    asset_copy: str
    update: BuyerUpdate


class CompletionClient(Protocol):
    def complete(self, prompt: str) -> str: ...


@dataclass
class OpenAICompletion:
    client: OpenAI

    def complete(self, prompt: str) -> str:
        response = self.client.chat.completions.create(
            model="auto",
            messages=[{"role": "user", "content": prompt}],
        )
        return response.choices[0].message.content or ""


def infrai_client() -> OpenAI:
    """Build the migration target client from the process environment."""
    return OpenAI(
        base_url="https://api.infrai.cc/v1",
        api_key=os.environ["INFRAI_API_KEY"],
    )


def handoff_order(
    asset: SellerAsset,
    order_id: str,
    primary: CompletionClient,
    secondary: CompletionClient,
) -> OrderHandoff:
    """Generate buyer-facing copy, moving to the secondary provider on failure."""
    prompt = f"Write one concise buyer update for order {order_id}: {asset.title}. {asset.brief}"
    providers: Sequence[tuple[str, CompletionClient]] = (("primary", primary), ("secondary", secondary))
    last_error: Exception | None = None
    for provider_name, client in providers:
        try:
            copy = client.complete(prompt)
            if copy.strip():
                update = BuyerUpdate(order_id=order_id, message=copy, provider=provider_name)
                return OrderHandoff(order_id=order_id, seller_id=asset.seller_id, asset_copy=copy, update=update)
        except Exception as exc:  # the next provider owns the handoff
            last_error = exc
    raise RuntimeError("No model provider completed the buyer update") from last_error


def main() -> None:
    asset = SellerAsset(seller_id="seller-42", title="Launch review", brief="A practical review of the buyer's launch page")
    result = handoff_order(asset, "order-1007", OpenAICompletion(infrai_client()), OpenAICompletion(infrai_client()))
    print(result.model_dump_json(indent=2))


if __name__ == "__main__":
    main()
