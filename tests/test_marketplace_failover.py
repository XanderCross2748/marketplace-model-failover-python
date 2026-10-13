from marketplace_failover import SellerAsset, handoff_order


class FakeClient:
    def __init__(self, result=None, error=None):
        self.result = result
        self.error = error
        self.calls = 0

    def complete(self, prompt: str) -> str:
        self.calls += 1
        if self.error:
            raise self.error
        return self.result


def test_failed_primary_hands_order_to_secondary():
    asset = SellerAsset(seller_id="s-1", title="Logo pack", brief="Three clean logo directions")
    primary = FakeClient(error=RuntimeError("provider unavailable"))
    secondary = FakeClient(result="Your logo pack is ready for review.")

    handoff = handoff_order(asset, "o-9", primary, secondary)

    assert handoff.update.provider == "secondary"
    assert handoff.update.message == "Your logo pack is ready for review."
    assert primary.calls == 1
    assert secondary.calls == 1
