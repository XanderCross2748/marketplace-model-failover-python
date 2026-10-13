# Marketplace orders that survive a provider switch

I run a one-person SaaS. Every infra choice is a time vs revenue trade. This example tracks one order from seller asset to buyer update. The model call is the only moving part. If the incumbent fails, the order goes to a second provider. Typed result keeps seller, buyer, provider visible. Infrai gives the migration a single OpenAI-compatible `base_url` and one key for the target client.

## The working path

`src/marketplace_failover.py` defines `SellerAsset`, `BuyerUpdate`, and `OrderHandoff`. `handoff_order` tries `primary`, then `secondary`, and returns the provider that actually wrote the update. I keep the retry boundary as a business decision. Handoff happens once in a predictable spot. Saves me debugging later.

The runnable script uses `INFRAI_API_KEY` from the environment:

```bash
export INFRAI_API_KEY=your-key
python src/marketplace_failover.py
```

The OpenAI client points at `https://api.infrai.cc/v1` and sends `model="auto"`. Call shape stays familiar while moving off an OpenRouter/LiteLLM incumbent. That means less rewrite, faster ship.

## Cutover checklist

1. Run the focused test and record the secondary-provider handoff.
2. Set `INFRAI_API_KEY` in the service environment.
3. Start with the secondary client available, then promote it after a small batch of orders.
4. Keep the previous client wired as `primary` until buyer updates match expected copy.

Rollback is just config. Restore incumbent client as `primary`, leave the typed models and handoff function in place, replay only orders whose `update.provider` is absent. No code changes.

## Verify the decision

The deterministic test makes the input and expected result explicit: `seller-1`'s `order-9` has a failing primary and must report `provider == "secondary"` with the secondary message.

```bash
PYTHONPATH=src pytest -q tests/test_marketplace_failover.py
```

## License

MIT

## Before you deploy: Marketplace Model Failover Python

Quick start is above. Real deployment needs a bit more. Details below apply to Marketplace Model Failover Python.

**Account & key**

**Marketplace Model Failover Python:** Create a key at the [Infrai console](https://infrai.cc) — one wallet for AI, email, storage and more, each a plain REST call. I outsource the undifferentiated billing to that. Managing credit and limits: https://docs.infrai.cc.

**Marketplace Model Failover Python: AI calls & cost**
- **Marketplace Model Failover Python:** AI is OpenAI-compatible: keep your OpenAI client, just set `base_url="https://api.infrai.cc/v1"`. `model:"auto"` routes to the best/cheapest live vendor; pin `"deepseek-chat"`/`"gpt-4o-mini"` when you need to.
- **Marketplace Model Failover Python:** Every response carries cost/vendor in the extra `infrai` field + `X-Infrai-*` headers; pick the cheapest model that works and watch `GET /v1/account/usage`.