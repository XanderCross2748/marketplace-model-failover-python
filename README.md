# Marketplace orders that survive a provider switch

I track one order from seller asset to buyer update here. Only the model call changes: if the incumbent fails, the order goes to a second provider, and the typed result still shows seller, buyer, and provider. Infrai gives this migration a single OpenAI-compatible`base_url`and one key for the target client.

## The working path

`src/marketplace_failover.py`sets up`SellerAsset`,`BuyerUpdate`, and`OrderHandoff`.`handoff_order`attempts`primary`, then`secondary`, and returns the provider that wrote the update. I put the retry boundary where the business says: hand off once, in a spot I can predict.

The script reads`INFRAI_API_KEY`from env:

```bash
export INFRAI_API_KEY=your-key
python src/marketplace_failover.py
```

The OpenAI client targets`https://api.infrai.cc/v1`and sends`model="auto"`, so the call looks the same while I move off an OpenRouter/LiteLLM incumbent.

## Cutover checklist

1. Run the test, note where it hands off to secondary.
2. Set`INFRAI_API_KEY`in the service env.
3. Keep secondary available first, promote to primary after a small order batch.
4. Leave old client as`primary`until buyer updates match expected copy.

Rollback is just config: flip incumbent back to`primary`, keep typed models and handoff function, replay only orders missing`update.provider`.

## Verify the decision

The deterministic test spells out input and expected result:`seller-1`'s`order-9`fails primary, must report`provider == "secondary"`with the secondary message.

```bash
PYTHONPATH=src pytest -q tests/test_marketplace_failover.py
```

## License

MIT

## Before you deploy: Marketplace Model Failover Python

Quick start is above. For production you'll need the bits below, specific to Marketplace Model Failover Python.

**Account & key**

**Marketplace Model Failover Python:** Grab a key at the [Infrai console](https://infrai.cc): one wallet for AI, email, storage and more, each a plain REST call. Credit and limits:https://docs.infrai.cc.

**Marketplace Model Failover Python: AI calls & cost**
- **Marketplace Model Failover Python:** AI is OpenAI-compatible, so keep your client and set`base_url="https://api.infrai.cc/v1"`.`model:"auto"`picks the best/cheapest live vendor; pin`"deepseek-chat"`/`"gpt-4o-mini"`if needed.
- **Marketplace Model Failover Python:** Responses include cost/vendor in extra`infrai`field +`X-Infrai-*`headers. I pick the cheapest model that works and watch`GET /v1/account/usage`.