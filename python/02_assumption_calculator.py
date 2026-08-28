from pathlib import Path
from datetime import date

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
DOCS_DIR = PROJECT_ROOT / "docs"

HISTORICAL_YEARS = [2021, 2022, 2023, 2024, 2025]
FORECAST_YEARS = [2026, 2027, 2028, 2029, 2030]

STATEMENT_FILES = {
    "income_statement": DATA_PROCESSED_DIR / "historical_income_statement.csv",
    "balance_sheet": DATA_PROCESSED_DIR / "historical_balance_sheet.csv",
    "cash_flow": DATA_PROCESSED_DIR / "historical_cash_flow.csv",
}


def load_statements():
    statements = {}
    for key, path in STATEMENT_FILES.items():
        if not path.exists():
            raise FileNotFoundError(
                f"{path} not found"
            )
        df = pd.read_csv(path)
        df = df.set_index("line_item")
        statements[key] = df
    return statements


def get_val(statements, statement_key, line_item, year):
    df = statements[statement_key]
    if line_item not in df.index:
        raise KeyError(
            f"'{line_item}' not found in {statement_key}."
        )
    val = df.loc[line_item, str(year)]
    return None if pd.isna(val) else float(val)


RATIO_DEFINITIONS = {
    "revenue_growth_pct": {
        "type": "yoy_growth",
        "statement": "income_statement",
        "line": "Net revenue",
        "label": "Revenue growth %",
    },
    "gross_margin_pct": {
        "type": "pct_of_revenue",
        "statement": "income_statement",
        "line": "Gross profit",
        "label": "Gross margin %",
    },
    "cogs_pct_revenue": {
        "type": "pct_of_revenue",
        "statement": "income_statement",
        "line": "Cost of goods sold",
        "label": "COGS % of revenue",
    },
    "sga_pct_revenue": {
        "type": "pct_of_revenue",
        "statement": "income_statement",
        "line": "Selling, general, and administrative expenses",
        "label": "SG&A % of revenue",
    },
    "operating_margin_pct": {
        "type": "pct_of_revenue",
        "statement": "income_statement",
        "line": "Loss from operations",
        "label": "Operating margin %",
    },
    "net_margin_pct": {
        "type": "pct_of_revenue",
        "statement": "income_statement",
        "line": "Net income (loss)",
        "label": "Net margin %",
    },
    "effective_tax_rate_pct": {
        "type": "tax_rate",
        "numerator_line": "Provision for income taxes",
        "denominator_line": "Income (loss) before income taxes",
        "label": "Effective tax rate % (flagged where pretax income <= 0)",
    },
    "dso_days": {
        "type": "days_over_revenue",
        "balance_sheet_line": "Accounts receivable, net",
        "label": "DSO (days sales outstanding)",
    },
    "dio_days": {
        "type": "days_over_cogs",
        "balance_sheet_line": "Inventory",
        "label": "DIO (days inventory outstanding)",
    },
    "dpo_days": {
        "type": "days_over_cogs",
        "balance_sheet_line": "Accounts payable",
        "label": "DPO (days payable outstanding)",
    },
    "capex_pct_revenue": {
        "type": "pct_of_revenue_abs",
        "statement": "cash_flow",
        "line": "Purchases of property and equipment",
        "label": "Capex % of revenue",
    },
    "da_pct_revenue": {
        "type": "pct_of_revenue",
        "statement": "cash_flow",
        "line": "Depreciation and amortization",
        "label": "D&A % of revenue",
    },
    "sbc_pct_revenue": {
        "type": "pct_of_revenue",
        "statement": "cash_flow",
        "line": "Stock-based compensation",
        "label": "Stock-based comp % of revenue",
    },
}


def calculate_ratio(statements, ratio_key, definition, year):
    rtype = definition["type"]

    if rtype == "yoy_growth":
        prior_year = year - 1
        if prior_year not in HISTORICAL_YEARS:
            return None
        current = get_val(statements, definition["statement"], definition["line"], year)
        prior = get_val(statements, definition["statement"], definition["line"], prior_year)
        if current is None or prior is None or prior == 0:
            return None
        return (current - prior) / prior

    if rtype in ("pct_of_revenue", "pct_of_revenue_abs"):
        revenue = get_val(statements, "income_statement", "Net revenue", year)
        value = get_val(statements, definition["statement"], definition["line"], year)
        if revenue is None or value is None or revenue == 0:
            return None
        if rtype == "pct_of_revenue_abs":
            value = abs(value)
        return value / revenue

    if rtype == "tax_rate":
        numerator = get_val(statements, "income_statement", definition["numerator_line"], year)
        denominator = get_val(statements, "income_statement", definition["denominator_line"], year)
        if numerator is None or denominator is None or denominator <= 0:
            return None  # not economically meaningful - pretax loss year
        return numerator / denominator

    if rtype == "days_over_revenue":
        revenue = get_val(statements, "income_statement", "Net revenue", year)
        balance = get_val(statements, "balance_sheet", definition["balance_sheet_line"], year)
        if revenue is None or balance is None or revenue == 0:
            return None
        return balance / revenue * 365

    if rtype == "days_over_cogs":
        cogs = get_val(statements, "income_statement", "Cost of goods sold", year)
        balance = get_val(statements, "balance_sheet", definition["balance_sheet_line"], year)
        if cogs is None or balance is None or cogs == 0:
            return None
        return balance / cogs * 365

    raise ValueError(f"Unknown ratio type: {rtype}")


def build_historical_ratios(statements):
    rows = {}
    for ratio_key, definition in RATIO_DEFINITIONS.items():
        row = {}
        for year in HISTORICAL_YEARS:
            row[str(year)] = calculate_ratio(statements, ratio_key, definition, year)
        rows[ratio_key] = row

    df = pd.DataFrame(rows).T
    df.index.name = "driver"
    return df


def historical_stats(ratios_df, ratio_key):
    row = ratios_df.loc[ratio_key]
    values_by_year = {int(y): row[y] for y in row.index if pd.notna(row[y])}
    years_sorted = sorted(values_by_year.keys())

    last_actual = values_by_year.get(years_sorted[-1]) if years_sorted else None
    last_2 = [values_by_year[y] for y in years_sorted[-2:]] if len(years_sorted) >= 2 else []
    last_3 = [values_by_year[y] for y in years_sorted[-3:]] if len(years_sorted) >= 3 else []

    return {
        "last_actual": last_actual,
        "avg_last_2": sum(last_2) / len(last_2) if last_2 else None,
        "avg_last_3": sum(last_3) / len(last_3) if last_3 else None,
    }


def linear_path(start, end, years):
    n = len(years)
    if n == 1:
        return {years[0]: end}
    return {
        years[i]: start + (end - start) * i / (n - 1)
        for i in range(n)
    }


SCENARIO_ASSUMPTIONS = {
    "revenue_growth_pct": {
        "base": {"start": 0.130, "end": 0.070,
                 "rationale": "Starts near the FY24-25 average growth rate "
                              "(~14.1%), decelerating to 7% by year 5 - "
                              "typical maturation curve for a scaling DTC "
                              "retailer, consistent with WRBY's own "
                              "deceleration from 15.2% (FY24) to 13.0% (FY25)."},
        "best": {"start": 0.150, "end": 0.110,
                 "rationale": "Holds near FY24's peak growth rate (15.2%) "
                              "and decelerates more slowly - new store "
                              "productivity and category expansion "
                              "(contacts, exams) sustain growth longer."},
        "worst": {"start": 0.080, "end": 0.030,
                  "rationale": "Growth roughly halves from the FY25 rate "
                               "immediately - reflects competitive/macro "
                               "pressure on discretionary eyewear spend, "
                               "decelerating to GDP-like growth by year 5."},
    },
    "gross_margin_pct": {
        "base": {"start": 0.545, "end": 0.550,
                 "rationale": "Roughly flat at the FY25 level (54.0%) "
                              "trending toward the 3-year average (54.6%) "
                              "- gross margin has been range-bound "
                              "54-59% since FY21 with no clear directional "
                              "trend, so flat is the defensible default."},
        "best": {"start": 0.550, "end": 0.570,
                 "rationale": "Gradual improvement via mix shift toward "
                              "higher-margin lens/exam revenue and supply "
                              "chain efficiency at scale."},
        "worst": {"start": 0.535, "end": 0.510,
                  "rationale": "Continued compression from FY21's 58.8% "
                               "peak - input cost inflation and "
                               "promotional intensity outpace efficiency "
                               "gains."},
    },
    "sga_pct_revenue": {
        "base": {"start": 0.535, "end": 0.480,
                 "rationale": "Continues improving from FY25's 54.6% but "
                              "at a decelerating pace - the FY21-25 "
                              "improvement (85.3% -> 54.6%) can't repeat "
                              "at the same rate; diminishing returns to "
                              "operating leverage as the store base "
                              "matures."},
        "best": {"start": 0.530, "end": 0.440,
                 "rationale": "Operating leverage continues at closer to "
                              "the recent pace - marketing efficiency and "
                              "corporate overhead leverage both improve "
                              "further as revenue scales."},
        "worst": {"start": 0.545, "end": 0.545,
                  "rationale": "Leverage gains stall entirely, holding "
                               "flat at the FY25 level - rising marketing "
                               "costs to defend growth offset any further "
                               "corporate overhead leverage."},
    },
    "effective_tax_rate_pct": {
        "base": {"start": 0.08, "end": 0.24,
                 "rationale": "NOT extrapolated from the historical ratio "
                              "(economically meaningless in pretax-loss "
                              "years - see FY25's 46% distortion). Modeled "
                              "instead as a ramp: low cash tax rate while "
                              "NOL carryforwards offset newly-positive "
                              "income, rising toward a normalized ~24% "
                              "effective rate (below the 21% federal "
                              "statutory + state blend, since some NOL "
                              "shield likely remains through year 5)."},
        "best": {"start": 0.05, "end": 0.20,
                 "rationale": "NOLs stretch further / income mix skews to "
                              "lower-tax jurisdictions, keeping the "
                              "effective rate below normalized longer."},
        "worst": {"start": 0.12, "end": 0.27,
                  "rationale": "NOLs exhausted faster than expected as "
                               "income grows quicker than assumed, "
                               "reaching full statutory-plus-state rate "
                               "by year 5."},
    },
    "dso_days": {
        "base": {"start": 1.5, "end": 1.5,
                 "rationale": "Held flat near FY25's 1.4 days - "
                              "receivables are immaterial for a "
                              "cash/card-driven DTC retailer (this line "
                              "is mostly wholesale/insurance "
                              "reimbursement), so it's a low-priority "
                              "driver with minimal forecast impact "
                              "regardless of scenario."},
        "best": {"start": 1.2, "end": 1.2, "rationale": "Marginal improvement; low materiality either way."},
        "worst": {"start": 2.0, "end": 2.0, "rationale": "Marginal deterioration; low materiality either way."},
    },
    "dio_days": {
        "base": {"start": 38.0, "end": 33.0,
                 "rationale": "Continues the strong FY21-25 improvement "
                              "(93 -> 41 days) but at a decelerating pace "
                              "- most of the easy inventory-efficiency "
                              "gains (better demand forecasting, fewer "
                              "SKUs held in excess) have likely already "
                              "been captured."},
        "best": {"start": 38.0, "end": 26.0,
                 "rationale": "Efficiency gains continue at closer to the "
                              "recent pace - further supply chain "
                              "investment pays off."},
        "worst": {"start": 45.0, "end": 50.0,
                  "rationale": "Partial reversion toward the FY22-23 level "
                               "(75-98 days) - supply chain disruption or "
                               "overordering ahead of demand."},
    },
    "dpo_days": {
        "base": {"start": 28.0, "end": 28.0,
                 "rationale": "Held near the FY23-25 average (~27 days) - "
                              "payment terms have been stable since the "
                              "FY21 outlier (50 days, likely a pre-IPO "
                              "working-capital management artifact)."},
        "best": {"start": 30.0, "end": 34.0, "rationale": "Stronger supplier terms negotiated as WRBY's scale/leverage grows."},
        "worst": {"start": 24.0, "end": 22.0, "rationale": "Suppliers tighten terms as competitive pressure on WRBY's margins grows."},
    },
    "capex_pct_revenue": {
        "base": {"start": 0.080, "end": 0.080,
                 "rationale": "Held near the FY23-25 average (~8.0%) - "
                              "consistent with continued store expansion "
                              "and technology investment at a steady "
                              "pace, in line with the last 3 years' range "
                              "(7.7%-8.3%)."},
        "best": {"start": 0.075, "end": 0.070, "rationale": "Slightly more capital-efficient store formats and tech reuse."},
        "worst": {"start": 0.085, "end": 0.100, "rationale": "Accelerated store buildout and/or higher technology spend to defend growth."},
    },
    "da_pct_revenue": {
        "base": {"start": 0.058, "end": 0.058,
                 "rationale": "Held flat near FY24-25 (~5.9%) - D&A has "
                              "risen alongside the growing capex base "
                              "(4.0% -> 5.8% FY21-25) and should stabilize "
                              "once capex and depreciation reach a "
                              "steady-state ratio."},
        "best": {"start": 0.056, "end": 0.054, "rationale": "Modest efficiency as newer, longer-lived assets are added."},
        "worst": {"start": 0.060, "end": 0.065, "rationale": "Continues rising if capex intensity increases (see worst-case capex)."},
    },
    "sbc_pct_revenue": {
        "base": {"start": 0.035, "end": 0.028,
                 "rationale": "Continues declining from FY25's 4.0% but "
                              "levels off - the FY21-25 drop (19.8% -> "
                              "4.0%) reflects pre-IPO grants rolling off "
                              "and won't repeat; expect it to settle near "
                              "a typical public-company steady state "
                              "(2.5-3.5% of revenue)."},
        "best": {"start": 0.032, "end": 0.022, "rationale": "Continues toward the lower end of typical public-company SBC levels."},
        "worst": {"start": 0.038, "end": 0.045, "rationale": "New equity grants increase to retain talent amid competitive hiring pressure."},
    },
}


def build_scenario_assumptions():
    rows = []
    for driver_key, scenarios in SCENARIO_ASSUMPTIONS.items():
        label = RATIO_DEFINITIONS[driver_key]["label"]
        for scenario_name, config in scenarios.items():
            path = linear_path(config["start"], config["end"], FORECAST_YEARS)
            for year, value in path.items():
                rows.append({
                    "driver": driver_key,
                    "driver_label": label,
                    "scenario": scenario_name,
                    "year": year,
                    "value": round(value, 5),
                    "rationale": config["rationale"],
                })
    return pd.DataFrame(rows)


def render_justification_markdown(ratios_df):
    lines = []
    lines.append("# Assumption Justification - WRBY 3-Statement Model")
    lines.append("")
    lines.append(f"_Generated {date.today().isoformat()} "
                 f"from FY2021-2025 as-filed actuals._")
    lines.append("")
    lines.append(
        "Every driver below shows the historical actuals it's based on, "
        "then the Base/Best/Worst forecast assumption with the reasoning "
        "behind it. None of these are pulled from a generic template - "
        "each references WRBY's actual trend."
    )
    lines.append("")

    for driver_key, definition in RATIO_DEFINITIONS.items():
        stats = historical_stats(ratios_df, driver_key)
        lines.append(f"## {definition['label']}")
        lines.append("")

        row = ratios_df.loc[driver_key]
        actuals_line = ", ".join(
            f"FY{y}: {row[str(y)]*100:.1f}%" if pd.notna(row[str(y)])
            and driver_key not in ("dso_days", "dio_days", "dpo_days")
            else (f"FY{y}: {row[str(y)]:.1f} days" if pd.notna(row[str(y)]) else f"FY{y}: n/a")
            for y in HISTORICAL_YEARS
        )
        lines.append(f"**Historical:** {actuals_line}")
        lines.append("")

        if driver_key in SCENARIO_ASSUMPTIONS:
            for scenario_name in ["base", "best", "worst"]:
                config = SCENARIO_ASSUMPTIONS[driver_key][scenario_name]
                is_pct = driver_key not in ("dso_days", "dio_days", "dpo_days")
                unit = "%" if is_pct else " days"
                start_disp = f"{config['start']*100:.1f}%" if is_pct else f"{config['start']:.1f} days"
                end_disp = f"{config['end']*100:.1f}%" if is_pct else f"{config['end']:.1f} days"
                lines.append(f"- **{scenario_name.title()}:** {start_disp} (2026) -> "
                             f"{end_disp} (2030). {config['rationale']}")
            lines.append("")

    return "\n".join(lines)



def run():
    DATA_PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    DOCS_DIR.mkdir(parents=True, exist_ok=True)

    statements = load_statements()

    print("Calculating historical ratios")
    ratios_df = build_historical_ratios(statements)
    ratios_path = DATA_PROCESSED_DIR / "historical_ratios.csv"
    ratios_df.to_csv(ratios_path, encoding="utf-8-sig")
    print(f"Saved: {ratios_path} ({ratios_df.shape[0]} drivers x {ratios_df.shape[1]} years)")

    missing_tax_years = [
        y for y in HISTORICAL_YEARS
        if pd.isna(ratios_df.loc["effective_tax_rate_pct", str(y)])
    ]
    if missing_tax_years:
        print(f"Effective_tax_rate_pct flagged as not meaningful for "
              f"{missing_tax_years} (pretax loss years) - excluded from the "
              f"historical average, not extrapolated into the forecast.")

    for driver_key in SCENARIO_ASSUMPTIONS:
        stats = historical_stats(ratios_df, driver_key)
        print(f"  {driver_key}: last_actual={stats['last_actual']}, "
              f"avg_last_2={stats['avg_last_2']}, avg_last_3={stats['avg_last_3']}")

    scenario_df = build_scenario_assumptions()
    scenario_path = DATA_PROCESSED_DIR / "scenario_assumptions.csv"
    scenario_df.to_csv(scenario_path, index=False, encoding="utf-8-sig")
    print(f"Saved: {scenario_path} ({scenario_df.shape[0]} rows - "
          f"{len(SCENARIO_ASSUMPTIONS)} drivers x 3 scenarios x {len(FORECAST_YEARS)} years)")

    justification_md = render_justification_markdown(ratios_df)
    justification_path = DOCS_DIR / "assumption_justification.md"
    justification_path.write_text(justification_md, encoding="utf-8")
    print(f"Saved: {justification_path}")


if __name__ == "__main__":
    run()