import re
import sys
import time
from pathlib import Path
from io import StringIO
from datetime import date
from xml.etree import ElementTree as ET

import requests
import pandas as pd



CIK_RAW = "1504776" 
CIK_PADDED = CIK_RAW.zfill(10)

SUBMISSIONS_URL = f"https://data.sec.gov/submissions/CIK{CIK_PADDED}.json"
FILING_BASE = f"https://www.sec.gov/Archives/edgar/data/{CIK_RAW}"

HEADERS = {"User-Agent": "Osaretin Idiagbonmwen oidiagbonmwen@gmail.com"}

TARGET_FISCAL_YEARS = [2021, 2022, 2023, 2024, 2025]
TARGET_FORM = "10-K"
REQUEST_DELAY_SECONDS = 0.3 

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_RAW_DIR = PROJECT_ROOT / "data" / "raw"
DATA_RAW_CACHE_DIR = DATA_RAW_DIR / "edgar_filings" 
DATA_PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"

STATEMENT_KEYWORDS = {
    "income_statement": ["statements of operations", "statement of operations",
                          "statements of income", "statement of income"],
    "balance_sheet": ["balance sheets", "balance sheet"],
    "cash_flow": ["statements of cash flows", "statement of cash flows"],
}

STATEMENT_OUTPUT_NAMES = {
    "income_statement": "historical_income_statement.csv",
    "balance_sheet": "historical_balance_sheet.csv",
    "cash_flow": "historical_cash_flow.csv",
}


ALIAS_MAP = {
    "income_statement": {
        "Income (loss) before income taxes": [
            "(Loss) income before income taxes",
            "Income (loss) before income taxes",
            "Loss before income taxes",
        ],
        "Net income (loss)": [
            "Net (loss) income",
            "Net income (loss)",
            "Net loss",
        ],
        "Interest and other income (loss), net": [
            "Interest and other (loss) income, net",
            "Interest and other income (loss), net",
            "Interest and other income, net",
        ],
        "Total comprehensive income (loss)": [
            "Total comprehensive (loss) income",
            "Total comprehensive income (loss)",
            "Total comprehensive loss",
        ],
    },
    "balance_sheet": {

    },
    "cash_flow": {
        "Net cash provided by (used in) operating activities": [1
            "Net cash (used in) provided by operating activities",
            "Net cash provided by (used in) operating activities",
            "Net cash provided by operating activities",
        ],
        "Net cash provided by (used in) financing activities": [
            "Net cash (used in) provided by financing activities",
            "Net cash provided by (used in) financing activities",
            "Net cash provided by financing activities",
        ],
        "Net increase (decrease) in cash and cash equivalents": [
            "Net (decrease) increase in cash and cash equivalents",
            "Net increase (decrease) in cash and cash equivalents",
            "Net increase in cash and cash equivalents",
        ],
        "Net loss": [
            "Net (loss) income",
            "Net income (loss)",
            "Net loss",
        ],
        "Payment for tender offer": [
            "Payment for Tender Offer",
            "Payment for tender offer",
        ],
        "Asset impairment charges": [
            "Asset Impairment Charges",
            "Asset impairment charges",
        ],
    },
}


DATA_NOTES = [
    {
        "category": "2021 IPO Transition",
        "statement": "Balance Sheet",
        "years": "2021 -> 2022",
        "raw_labels": [
            "Redeemable convertible preferred stock, $.0001 par value, zero and "
            "54,507,243 shares authorized; zero and 54,041,904 shares issued and "
            "outstanding as of December 31, 2021 and 2020, respectively",
            "Total stockholders\u2019 deficit",
            "Total stockholders\u2019 equity",
            "Total liabilities, redeemable convertible preferred stock, and "
            "stockholders\u2019 deficit",
            "Total liabilities and stockholders\u2019 equity",
        ],
        "explanation": (
            "WRBY carried redeemable convertible preferred stock and a "
            "stockholders' deficit through FY2021. Following the IPO, the "
            "preferred stock converted to common stock, and the balance "
            "sheet moved from a deficit ('Total stockholders' deficit') to "
            "positive stockholders' equity ('Total stockholders' equity') "
            "starting FY2022. This is a real capital-structure event, not "
            "a labeling change - call it out explicitly in the model."
        ),
    },
    {
        "category": "2021 IPO Transition",
        "statement": "Income Statement",
        "years": "2021 - 2025",
        "raw_labels": [
            "Deemed dividend upon redemption of redeemable convertible preferred stock",
            "Net loss attributable to common stockholders",
            "Net Income (Loss) Available to Common Stockholders, Basic, Total",
            "Net Income (Loss) Available to Common Stockholders, Diluted, Total",
        ],
        "explanation": (
            "The deemed dividend relates to the preferred stock "
            "redemption/conversion and tapers off after 2023. Separately, "
            "the EPS-relevant 'available to common stockholders' line was "
            "reported as a single figure through 2023, then split into "
            "Basic and Diluted total lines from 2024 onward - a "
            "presentation change, not a new item."
        ),
    },
    {
        "category": "2021 IPO Transition",
        "statement": "Cash Flow Statement",
        "years": "2021 - 2023",
        "raw_labels": [
            "Borrowings from Credit Facility",
            "Repayment of Credit Facility",
            "Proceeds from repayment of related party loans",
            "Related party loans issued in connection with stock option exercises",
            "Issuance of Series F and Series G redeemable convertible preferred "
            "stock, net of issuance costs",
            "Cancellation of options for consideration",
            "Payment for Tender Offer",
            "Payment for tender offer",
        ],
        "explanation": (
            "Pre-IPO financing activity: a credit facility that was drawn "
            "and repaid, related-party loans (common in pre-IPO equity "
            "compensation structures) that wound down, Series F/G "
            "preferred stock issuances that later converted at IPO, and a "
            "tender offer tied to the IPO-era liquidity event. None of "
            "this recurs from 2024 onward."
        ),
    },
    {
        "category": "New Programs / Policies",
        "statement": "Cash Flow Statement",
        "years": "2023 - 2025",
        "raw_labels": [
            "Amortization of cloud-based software implementation costs",
            "Investment in optical equipment company",
        ],
        "explanation": (
            "New from FY2023: a capitalized cloud-software amortization "
            "policy (consistent with ASU 2018-15 adoption timing seen at "
            "many filers) and a new minority investment in an optical "
            "equipment company. Both are additions to the business, not "
            "gaps in earlier data."
        ),
    },
    {
        "category": "New Programs / Policies",
        "statement": "Cash Flow Statement",
        "years": "2021 - 2025",
        "raw_labels": [
            "Proceeds from Stock Plans",
            "Proceeds from shares issued in connection with ESPP",
            "Proceeds from stock option and warrant exercises",
            "Proceeds from stock option exercises",
        ],
        "explanation": (
            "Equity compensation cash inflows were reported under broader "
            "labels through 2023, then split out an explicit ESPP line "
            "from 2024 - consistent with an employee stock purchase plan "
            "either launching or becoming material enough to break out "
            "separately. Warrant exercises don't appear after 2023, "
            "implying outstanding warrants were exercised or expired."
        ),
    },
    {
        "category": "Presentation Change",
        "statement": "Balance Sheet",
        "years": "2021 - 2025",
        "raw_labels": [
            "Operating Lease, Liability, Current",
            "Operating Lease, Liability, Noncurrent",
            "Operating Lease, Right-of-Use Asset",
            "Current lease liabilities",
            "Non-current lease liabilities",
            "Right-of-use lease assets",
            "Deferred rent",
        ],
        "explanation": (
            "Same underlying lease balances, relabeled by the filer over "
            "time. 'Deferred rent' is a pre-ASC-842-style concept that "
            "phases out as the lease liability/ROU asset presentation "
            "takes over. Treat these as the same economic items across "
            "years when building the balance sheet roll-forward."
        ),
    },
    {
        "category": "Presentation Change",
        "statement": "Cash Flow Statement",
        "years": "2021 - 2025",
        "raw_labels": [
            "Cash paid for amounts included in the measurement of lease liabilities",
            "Increase (Decrease) in Right-of-use Lease Assets and Current and "
            "Non-current Lease Liabilities",
            "Lease assets and liabilities",
            "Deferred rent",
        ],
        "explanation": (
            "The cash-flow side of the same lease presentation change "
            "above: the operating-activities adjustment for leases was "
            "reported as one combined 'Increase (Decrease)' line in "
            "2022-2023, then reported as 'Lease assets and liabilities' "
            "from 2024. Same underlying adjustment, different label."
        ),
    },
    {
        "category": "Working Capital & Equity Compensation Timing",
        "statement": "Cash Flow Statement",
        "years": "varies",
        "raw_labels": [
            "Other current liabilities",
            "Other financing activity",
            "Employee tax withholding remitted in connection with exercise or "
            "release of equity awards",
            "Shares withheld for taxes on stock-based compensation",
            "Repurchase of stock",
        ],
        "explanation": (
            "Smaller working-capital and equity-award-settlement lines "
            "that only appear in the years they were material enough (or "
            "occurred at all) to break out separately - common for "
            "line items tied to one-off treasury activity or changes in "
            "how equity award tax withholding was settled. Not every "
            "company reports these every year even when small amounts "
            "exist; they roll into a broader 'other' line instead."
        ),
    },
    {
        "category": "Episodic / Non-Recurring Items",
        "statement": "Cash Flow Statement",
        "years": "2022 - 2025",
        "raw_labels": [
            "Asset Impairment Charges",
            "Asset impairment charges",
        ],
        "explanation": (
            "Asset impairment charges (store leases, ROU assets, or "
            "similar) were recorded FY2022-2025 but not FY2021 - "
            "impairments are recognized when triggered, not on a "
            "recurring schedule, so a genuinely retail-growth year with "
            "no impairment triggers (2021) legitimately has none."
        ),
    },
]


def sec_get(url):
    time.sleep(REQUEST_DELAY_SECONDS)
    resp = requests.get(url, headers=HEADERS, timeout=30)
    resp.raise_for_status()
    return resp


def get_target_10ks():
    data = sec_get(SUBMISSIONS_URL).json()
    recent = data["filings"]["recent"]

    forms = recent["form"]
    accessions = recent["accessionNumber"]
    report_dates = recent["reportDate"]
    filing_dates = recent["filingDate"]
    primary_docs = recent["primaryDocument"]

    targets = []
    for form, accession, report_date, filing_date, primary_doc in zip(
        forms, accessions, report_dates, filing_dates, primary_docs
    ):
        if form != TARGET_FORM:
            continue
        fiscal_year = int(report_date[:4])
        if fiscal_year not in TARGET_FISCAL_YEARS:
            continue
        targets.append({
            "fiscal_year": fiscal_year,
            "accession": accession,
            "accession_nodash": accession.replace("-", ""),
            "report_date": report_date,
            "filing_date": filing_date,
            "primary_doc": primary_doc,
        })

    targets.sort(key=lambda t: t["fiscal_year"])

    found_years = {t["fiscal_year"] for t in targets}
    missing = set(TARGET_FISCAL_YEARS) - found_years
    if missing:
        print(f"No 10-K found in 'recent' filings for fiscal year(s) "
              f"{sorted(missing)}.")

    return targets


def get_filing_summary_reports(accession_nodash):
    url = f"{FILING_BASE}/{accession_nodash}/FilingSummary.xml"
    xml_text = sec_get(url).text
    root = ET.fromstring(xml_text)

    reports = []
    for report in root.iter("Report"):
        short_name = (report.findtext("ShortName") or "").strip()
        html_file = (report.findtext("HtmlFileName") or "").strip()
        menu_category = (report.findtext("MenuCategory") or "").strip()
        if short_name and html_file:
            reports.append({
                "short_name": short_name,
                "html_file": html_file,
                "menu_category": menu_category,
            })
    return reports


def match_statement_reports(reports):
    matches = {}
    for statement_key, keywords in STATEMENT_KEYWORDS.items():
        candidates = [
            r for r in reports
            if r["menu_category"] == "Statements"
            and any(kw in r["short_name"].lower() for kw in keywords)
        ]
        if not candidates:
            candidates = [
                r for r in reports
                if any(kw in r["short_name"].lower() for kw in keywords)
            ]
        matches[statement_key] = candidates[0] if candidates else None
    return matches


def fetch_statement_table(accession_nodash, html_file):
    url = f"{FILING_BASE}/{accession_nodash}/{html_file}"
    html_text = sec_get(url).text
    tables = pd.read_html(StringIO(html_text))
    if not tables:
        raise ValueError(f"No table found in {url}")
    return tables[0]


def clean_statement_df(df):
    df = df.copy()
    df.columns = [str(c).strip() for c in df.columns]

    label_col = df.columns[0]
    df = df.rename(columns={label_col: "line_item"})
    df["line_item"] = (
        df["line_item"]
        .astype(str)
        .str.replace(r"\[\d+\]", "", regex=True)
        .str.strip()
    )

    value_cols = [c for c in df.columns if c != "line_item"]
    for col in value_cols:
        df[col] = df[col].apply(_clean_value)

    df = df[~(df["line_item"].isin(["", "nan"]) & df[value_cols].isna().all(axis=1))]
    df = df.reset_index(drop=True)
    return df


def _clean_value(val):
    if pd.isna(val):
        return None
    s = str(val).strip()
    if s in ("", "nan", "—", "-"):
        return None
    s = re.sub(r"\[\d+\]", "", s)       
    s = s.replace("$", "").strip() 
    negative = s.startswith("(") and s.endswith(")")
    if negative:
        s = s[1:-1].strip()
    s = s.replace(",", "").replace("%", "").strip()
    if s in ("", "—", "-"):
        return None
    try:
        num = float(s)
    except ValueError:
        return val 
    return -num if negative else num


def build_combined_view(per_year_dfs):
    combined = None
    for fiscal_year, df in per_year_dfs.items():
        year_df = df[["line_item"]].copy()
        value_col = [c for c in df.columns if c != "line_item"][0]
        year_df[str(fiscal_year)] = df[value_col].values
        year_df = year_df.groupby("line_item", as_index=False).first()

        combined = year_df if combined is None else combined.merge(
            year_df, on="line_item", how="outer"
        )
    return combined


def drop_header_rows(df):
    year_cols = [c for c in df.columns if c != "line_item"]
    has_any_value = df[year_cols].notna().any(axis=1)
    return df[has_any_value].reset_index(drop=True)


def apply_alias_map(df, statement_key):
    alias_map = ALIAS_MAP.get(statement_key, {})
    year_cols = [c for c in df.columns if c != "line_item"]

    df = df.set_index("line_item")

    for canonical, variants in alias_map.items():
        present_variants = [v for v in variants if v in df.index]
        if len(present_variants) <= 1:
            continue

        merged_row = df.loc[present_variants, year_cols].bfill().iloc[0]
        df = df.drop(index=present_variants)
        df.loc[canonical, year_cols] = merged_row.values

    return df.reset_index().rename(columns={"index": "line_item"})


def get_remaining_mismatches(df):
    year_cols = [c for c in df.columns if c != "line_item"]
    coverage = df[year_cols].notna().sum(axis=1)
    partial = df[coverage < len(year_cols)]
    return partial["line_item"].tolist()


def render_notes_markdown():
    lines = []
    lines.append("# Data Extraction Notes - Warby Parker As-Filed Statements (FY2021-2025)")
    lines.append("")
    lines.append(f"_Generated {date.today().isoformat()} by 01_edgar_data_pull.py._")
    lines.append("")
    lines.append(
        "Source: each fiscal year's 10-K, read from the filing's own "
        "rendered statement pages (SEC R-files), not a curated XBRL tag "
        "list - so every line item the company reported is captured. "
        "Line items whose label only changed because the number's sign "
        "flipped (e.g. 'Net loss' vs 'Net income (loss)') were merged "
        "into one canonical row; see ALIAS_MAP in 01_edgar_data_pull.py "
        "for the exact mapping. Pure section-header rows with no data "
        "(e.g. 'Current assets:') were dropped."
    )
    lines.append("")
    lines.append(
        "The items below did NOT merge cleanly across years, and that's "
        "not a data quality issue - each one reflects something that "
        "actually happened at the company. Use this as the reference for "
        "footnotes/assumptions in the Excel model."
    )
    lines.append("")

    categories = sorted(set(n["category"] for n in DATA_NOTES))
    for category in categories:
        lines.append(f"## {category}")
        lines.append("")
        for note in [n for n in DATA_NOTES if n["category"] == category]:
            lines.append(f"**{note['statement']}** ({note['years']})")
            lines.append("")
            for label in note["raw_labels"]:
                lines.append(f"- {label}")
            lines.append("")
            lines.append(note["explanation"])
            lines.append("")

    return "\n".join(lines)


def documented_labels():
    labels = set()
    for note in DATA_NOTES:
        labels.update(note["raw_labels"])
    return labels


def write_data_extraction_notes():
    DATA_RAW_DIR.mkdir(parents=True, exist_ok=True)
    out_path = DATA_RAW_DIR / "data_extraction_notes.md"
    out_path.write_text(render_notes_markdown(), encoding="utf-8")
    return out_path


def run():
    DATA_RAW_CACHE_DIR.mkdir(parents=True, exist_ok=True)
    DATA_PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    targets = get_target_10ks()
    print(f"Found {len(targets)} target 10-K filing(s): "
          f"{[t['fiscal_year'] for t in targets]}")

    per_year_by_statement = {key: {} for key in STATEMENT_KEYWORDS}

    for t in targets:
        fy = t["fiscal_year"]
        accession_nodash = t["accession_nodash"]
        print(f"\nFY{fy} (accession {t['accession']}, filed {t['filing_date']})")

        reports = get_filing_summary_reports(accession_nodash)
        matches = match_statement_reports(reports)

        for statement_key, match in matches.items():
            if match is None:
                print(f"  [{statement_key}] no matching R-file found")
                continue

            print(f"[{statement_key}] using '{match['short_name']}' "
                  f"({match['html_file']})")
            raw_df = fetch_statement_table(accession_nodash, match["html_file"])
            clean_df = clean_statement_df(raw_df)
            per_year_by_statement[statement_key][fy] = clean_df

    for statement_key, per_year_dfs in per_year_by_statement.items():
        if not per_year_dfs:
            continue

        combined = build_combined_view(per_year_dfs)
        combined = drop_header_rows(combined)
        combined = apply_alias_map(combined, statement_key)
        year_cols = [c for c in combined.columns if c != "line_item"]
        for col in year_cols:
            combined[col] = combined[col].apply(_clean_value)

        remaining = get_remaining_mismatches(combined)
        known_labels = documented_labels()
        undocumented = [item for item in remaining if item not in known_labels]

        out_path = DATA_PROCESSED_DIR / STATEMENT_OUTPUT_NAMES[statement_key]
        combined.to_csv(out_path, index=False)
        print(f"[{statement_key}] saved: {out_path} ({combined.shape[0]} line items)")

        if undocumented:
            print(f"[{statement_key}] {len(undocumented)} item(s) still differ across "
                  f"years and aren't in DATA_NOTES yet")
            for item in undocumented:
                print(f"    '{item}'")

    notes_path = write_data_extraction_notes()
    print(f"Saved: {notes_path}")


def main():
    try:
        run()
    except requests.exceptions.RequestException as e:
        print(f"Could not reach SEC EDGAR: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()