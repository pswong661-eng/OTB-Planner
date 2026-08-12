"""Assert stock-holding recompute does not mutate editable Act. Sale metrics.

Run: python test_stock_recompute_preserves_act_sale.py
No Excel fixture required — uses a synthetic in-memory collection.
"""
from copy import deepcopy

from otb_engine import MONTHS, _recompute_stock_holding


def _month_vals(fill=0.0, **overrides):
    vals = {m: float(fill) for m in MONTHS}
    vals.update({k: float(v) for k, v in overrides.items()})
    return vals


def _metric(row_idx, year_maps, totals=None):
    entry = {"row_idx": row_idx}
    for yr in ("2023", "2024", "2025", "2026"):
        entry[yr] = year_maps.get(yr, _month_vals(0))
        entry[f"total_{yr}"] = (totals or {}).get(yr)
    return entry


def test_recompute_preserves_act_sale():
    key = ("Test Coll", "Cat", "Seg")
    # Partial year: Jan-Mar have real sales; Apr-Dec are empty (parsed as 0).
    sale_usd_2025 = _month_vals(0, Jan=1000, Feb=2000, Mar=500)
    sale_qty_2025 = _month_vals(0, Jan=10, Feb=20, Mar=5)
    planned_2025 = _month_vals(5000)  # large receipts so closing stock > 0
    received_qty_2025 = _month_vals(500)
    # Flat 1/12 distribution so plan mocks are non-zero for empty months
    dist_2025 = _month_vals(1.0 / 12)

    coll = {
        "_remarks_row": None,
        "Planned Purchases USD": _metric(10, {"2025": planned_2025}),
        "Act. Sale USD": _metric(11, {"2025": sale_usd_2025}),
        "Act. Sale QTY": _metric(12, {"2025": sale_qty_2025}),
        "Act. Goods Received QTY": _metric(13, {"2025": received_qty_2025}),
        "Act. Stock Holding Month-USD": _metric(14, {"2025": _month_vals(0)}),
        "Act. Stock Holding Month-QTY": _metric(15, {"2025": _month_vals(0)}),
        "Sale % Distribution": _metric(16, {"2025": dist_2025}),
        "Planned Sale Target USD": _metric(
            17, {}, totals={"2025": 12000.0}
        ),
    }
    data = {key: coll}
    before_usd = deepcopy(coll["Act. Sale USD"])
    before_qty = deepcopy(coll["Act. Sale QTY"])

    _recompute_stock_holding(data, [key])

    assert coll["Act. Sale USD"] == before_usd, (
        "Act. Sale USD was mutated by stock recompute "
        f"(before={before_usd}, after={coll['Act. Sale USD']})"
    )
    assert coll["Act. Sale QTY"] == before_qty, (
        "Act. Sale QTY was mutated by stock recompute "
        f"(before={before_qty}, after={coll['Act. Sale QTY']})"
    )
    # Sanity: stock holding should still be computed (non-all-zero for 2025)
    sh_usd = coll["Act. Stock Holding Month-USD"]["2025"]
    assert any(float(v) != 0 for v in sh_usd.values()), (
        "expected Stock Holding USD to be recomputed with non-zero values"
    )


if __name__ == "__main__":
    test_recompute_preserves_act_sale()
    print("PASS: Act. Sale USD/QTY unchanged after _recompute_stock_holding")
