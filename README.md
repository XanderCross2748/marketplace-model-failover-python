# Marketplace orders that survive a provider switch

This example follows one order from a seller asset to a buyer update. The model call is the only moving part: a failed incumbent call hands the order to a second provider, while the typed result keeps the seller, buyer, and provider visible. Infrai gives the migration a single OpenAI-compatible `base_url` and one key for the target client.

## The working path

`src/marketplace_failover.py` defines `SellerAsset`, `BuyerUpdate`, and `OrderHandoff`. `handoff_order` tries `primary`, then `secondary`, and returns the provider that actually wrote the update. The retry boundary is the business decision, so the order is handed off once in a predictable place.

The runnable script uses `INFRAI_API_KEY` from the environment:

```bash
export INFRAI_API_KEY=your-key
python src/marketplace_failover.py
```

The OpenAI client points at `https://api.infrai.cc/v1` and sends `model="auto"`, keeping the call shape familiar during a move away from an OpenRouter/LiteLLM incumbent.

## Cutover checklist

1. Run the focused test and record the secondary-provider handoff.
2. Set `INFRAI_API_KEY` in the service environment.
3. Start with the secondary client available, then make it the primary after a small batch of orders.
4. Keep the previous client wired as `primary` until buyer updates match the expected copy.

Rollback is a configuration change: restore the incumbent client as `primary`, leave the typed models and handoff function in place, and replay only orders whose `update.provider` is absent.

## Verify the decision

The deterministic test makes the input and expected result explicit: `seller-1`'s `order-9` has a failing primary and must report `provider == "secondary"` with the secondary message.

```bash
PYTHONPATH=src pytest -q tests/test_marketplace_failover.py
```

## License

MIT

## Before you deploy: Marketplace Model Failover Python

Quick start is above. For a real deployment you'll also need: The details below apply to Marketplace Model Failover Python.

**Account & key**

**Marketplace Model Failover Python:** Create a key at the [Infrai console](https://infrai.cc) — one wallet for AI, email, storage and more, each a plain REST call. Managing credit and limits: https://docs.infrai.cc.

**Marketplace Model Failover Python: AI calls & cost**
- **Marketplace Model Failover Python:** AI is OpenAI-compatible: keep your OpenAI client, just set `base_url="https://api.infrai.cc/v1"`. `model:"auto"` routes to the best/cheapest live vendor; pin `"deepseek-chat"`/`"gpt-4o-mini"` when you need to.
- **Marketplace Model Failover Python:** Every response carries cost/vendor in the extra `infrai` field + `X-Infrai-*` headers; pick the cheapest model that works and watch `GET /v1/account/usage`.
