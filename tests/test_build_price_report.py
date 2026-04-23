from pathlib import Path

from src.build_price_report import build_report


def test_build_report(tmp_path: Path) -> None:
    csv_path = tmp_path / "prices.csv"
    csv_path.write_text(
        "sku,vendor,current_price,previous_price,currency\n"
        "A1,VendorX,20,10,USD\n"
        "A2,VendorY,10,10,USD\n"
    )

    result = build_report(csv_path, tmp_path / "out", alert_threshold=25.0)
    assert result.item_count == 2
    assert result.alert_count == 1
    assert (tmp_path / "out" / "weekly_report.md").exists()
    assert (tmp_path / "out" / "alerts.csv").exists()
