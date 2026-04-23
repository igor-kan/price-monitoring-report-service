from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
from pathlib import Path


@dataclass
class BuildResult:
    output_dir: Path
    item_count: int
    alert_count: int


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build price monitoring reports")
    parser.add_argument("--input", required=True, help="Input CSV path")
    parser.add_argument("--output", default="out", help="Output directory")
    parser.add_argument("--alert-threshold", type=float, default=10.0, help="Percent change threshold")
    return parser.parse_args()


def _pct_change(current: float, previous: float) -> float:
    if previous == 0:
        return 0.0
    return ((current - previous) / previous) * 100.0


def build_report(input_csv: Path, output_dir: Path, alert_threshold: float = 10.0) -> BuildResult:
    if not input_csv.exists():
        raise FileNotFoundError(f"Input CSV not found: {input_csv}")

    rows: list[dict] = []
    with open(input_csv, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        required = {"sku", "vendor", "current_price", "previous_price", "currency"}
        missing = required - set(reader.fieldnames or [])
        if missing:
            raise ValueError(f"Missing headers: {sorted(missing)}")

        for raw in reader:
            current = float(raw["current_price"])
            previous = float(raw["previous_price"])
            change_pct = round(_pct_change(current, previous), 2)
            rows.append(
                {
                    "sku": raw["sku"].strip(),
                    "vendor": raw["vendor"].strip(),
                    "currency": raw["currency"].strip(),
                    "current_price": current,
                    "previous_price": previous,
                    "change_pct": change_pct,
                    "alert": abs(change_pct) >= alert_threshold,
                }
            )

    output_dir.mkdir(parents=True, exist_ok=True)

    with open(output_dir / "price_changes.csv", "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "sku",
                "vendor",
                "currency",
                "current_price",
                "previous_price",
                "change_pct",
                "alert",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)

    alerts = [row for row in rows if row["alert"]]
    with open(output_dir / "alerts.csv", "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["sku", "vendor", "change_pct", "current_price", "previous_price", "currency"],
        )
        writer.writeheader()
        writer.writerows(
            {
                "sku": a["sku"],
                "vendor": a["vendor"],
                "change_pct": a["change_pct"],
                "current_price": a["current_price"],
                "previous_price": a["previous_price"],
                "currency": a["currency"],
            }
            for a in alerts
        )

    summary_lines = [
        "# Price Monitoring Summary",
        "",
        f"Items analyzed: {len(rows)}",
        f"Alert threshold: {alert_threshold:.2f}%",
        f"Alerts triggered: {len(alerts)}",
        "",
        "## Top movers",
    ]
    top = sorted(rows, key=lambda x: abs(x["change_pct"]), reverse=True)[:10]
    for row in top:
        summary_lines.append(
            f"- {row['sku']} ({row['vendor']}): {row['change_pct']}% "
            f"[{row['previous_price']} -> {row['current_price']} {row['currency']}]"
        )

    (output_dir / "weekly_report.md").write_text("\n".join(summary_lines), encoding="utf-8")
    return BuildResult(output_dir=output_dir, item_count=len(rows), alert_count=len(alerts))


def main() -> None:
    args = parse_args()
    result = build_report(Path(args.input), Path(args.output), alert_threshold=args.alert_threshold)
    print(
        f"Generated report -> {result.output_dir} "
        f"(items={result.item_count}, alerts={result.alert_count})"
    )


if __name__ == "__main__":
    main()
