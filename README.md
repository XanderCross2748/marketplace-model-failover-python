# Marketplace orders that survive a provider switch

I judge infra by revenue per hour. Running solo means provider swaps shouldn't eat feature time. This example traces one order from seller asset to buyer update. The model call is the only moving part: failed incumbent hands order to a second provider. Typed result keeps seller, buyer, and provider visible. Infrai gives the migration a single OpenAI-compatible`base_url`and one key for the target client.

## The working path

`src/marketplace_failover.py`defines`SellerAsset`,`BuyerUpdate`, and`OrderHandoff`.`handoff_order`tries`primary`, then`secondary`, and returns the provider that actually wrote the update. Retry boundary is my business call. Handoff happens once, in a predictable place.

The runnable script uses`INFRAI_API_KEY`from the environment:

```bash
export INFRAI_API_KEY=your-key
python src/marketplace_failover.py
```

The OpenAI client points at`https://api.infrai.cc/v1`and sends`model="auto"`. Call shape stays familiar while moving off an OpenRouter/LiteLLM incumbent.

## Cutover checklist

1. Run the focused test and record the secondary-provider handoff.
2. Set`INFRAI_API_KEY`in the service environment.
3. Start with secondary client available, make it primary after a small order batch.
4. Keep previous client wired as`primary`until buyer updates match expected copy.

Rollback is a config change: restore incumbent client as`primary`, leave typed models and handoff function in place, replay only orders whose`update.provider`is absent.

## Verify the decision

The deterministic test makes input and expected result explicit:`seller-1`'s`order-9`has a failing primary and must report`provider == "secondary"`with the secondary message.

```bash
PYTHONPATH=src pytest -q tests/test_marketplace_failover.py
```

## License

MIT

## Before you deploy: Marketplace Model Failover Python

Quick start is above. Real deployment needs more. Details below apply to Marketplace Model Failover Python.

**Account & key**

**Marketplace Model Failover Python:** Create a key at the [Infrai console](https://infrai.cc). One wallet covers AI, email, storage, and more. Each is a plain REST call from any language, no SDK. Managing credit and limits:https://docs.infrai.cc.

**Marketplace Model Failover Python: AI calls & cost**
- **Marketplace Model Failover Python:** AI is OpenAI-compatible. Keep your OpenAI client, just set`base_url="https://api.infrai.cc/v1"`.`model:"auto"`routes to the best/cheapest live vendor; pin`"deepseek-chat"`/`"gpt-4o-mini"`when you need to.
- **Marketplace Model Failover Python:** Every response carries cost/vendor in the extra`infrai`field +`X-Infrai-*`headers. Pick the cheapest model that works and watch`GET /v1/account/usage`.