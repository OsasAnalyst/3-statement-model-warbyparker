# Data Extraction Notes - Warby Parker As-Filed Statements (FY2021-2025)

_Generated 2026-08-21 by 01_edgar_data_pull.py._

Source: each fiscal year's 10-K, read from the filing's own rendered statement pages (SEC R-files), not a curated XBRL tag list - so every line item the company reported is captured. Line items whose label only changed because the number's sign flipped (e.g. 'Net loss' vs 'Net income (loss)') were merged into one canonical row; see ALIAS_MAP in 01_edgar_data_pull.py for the exact mapping. Pure section-header rows with no data (e.g. 'Current assets:') were dropped.

The items below did NOT merge cleanly across years, and that's not a data quality issue - each one reflects something that actually happened at the company. Use this as the reference for footnotes/assumptions in the Excel model.

## 2021 IPO Transition

**Balance Sheet** (2021 -> 2022)

- Redeemable convertible preferred stock, $.0001 par value, zero and 54,507,243 shares authorized; zero and 54,041,904 shares issued and outstanding as of December 31, 2021 and 2020, respectively
- Total stockholders’ deficit
- Total stockholders’ equity
- Total liabilities, redeemable convertible preferred stock, and stockholders’ deficit
- Total liabilities and stockholders’ equity

WRBY carried redeemable convertible preferred stock and a stockholders' deficit through FY2021. Following the IPO, the preferred stock converted to common stock, and the balance sheet moved from a deficit ('Total stockholders' deficit') to positive stockholders' equity ('Total stockholders' equity') starting FY2022. This is a real capital-structure event, not a labeling change - call it out explicitly in the model.

**Income Statement** (2021 - 2025)

- Deemed dividend upon redemption of redeemable convertible preferred stock
- Net loss attributable to common stockholders
- Net Income (Loss) Available to Common Stockholders, Basic, Total
- Net Income (Loss) Available to Common Stockholders, Diluted, Total

The deemed dividend relates to the preferred stock redemption/conversion and tapers off after 2023. Separately, the EPS-relevant 'available to common stockholders' line was reported as a single figure through 2023, then split into Basic and Diluted total lines from 2024 onward - a presentation change, not a new item.

**Cash Flow Statement** (2021 - 2023)

- Borrowings from Credit Facility
- Repayment of Credit Facility
- Proceeds from repayment of related party loans
- Related party loans issued in connection with stock option exercises
- Issuance of Series F and Series G redeemable convertible preferred stock, net of issuance costs
- Cancellation of options for consideration
- Payment for Tender Offer
- Payment for tender offer

Pre-IPO financing activity: a credit facility that was drawn and repaid, related-party loans (common in pre-IPO equity compensation structures) that wound down, Series F/G preferred stock issuances that later converted at IPO, and a tender offer tied to the IPO-era liquidity event. None of this recurs from 2024 onward.

## Episodic / Non-Recurring Items

**Cash Flow Statement** (2022 - 2025)

- Asset Impairment Charges
- Asset impairment charges

Asset impairment charges (store leases, ROU assets, or similar) were recorded FY2022-2025 but not FY2021 - impairments are recognized when triggered, not on a recurring schedule, so a genuinely retail-growth year with no impairment triggers (2021) legitimately has none.

## New Programs / Policies

**Cash Flow Statement** (2023 - 2025)

- Amortization of cloud-based software implementation costs
- Investment in optical equipment company

New from FY2023: a capitalized cloud-software amortization policy (consistent with ASU 2018-15 adoption timing seen at many filers) and a new minority investment in an optical equipment company. Both are additions to the business, not gaps in earlier data.

**Cash Flow Statement** (2021 - 2025)

- Proceeds from Stock Plans
- Proceeds from shares issued in connection with ESPP
- Proceeds from stock option and warrant exercises
- Proceeds from stock option exercises

Equity compensation cash inflows were reported under broader labels through 2023, then split out an explicit ESPP line from 2024 - consistent with an employee stock purchase plan either launching or becoming material enough to break out separately. Warrant exercises don't appear after 2023, implying outstanding warrants were exercised or expired.

## Presentation Change

**Balance Sheet** (2021 - 2025)

- Operating Lease, Liability, Current
- Operating Lease, Liability, Noncurrent
- Operating Lease, Right-of-Use Asset
- Current lease liabilities
- Non-current lease liabilities
- Right-of-use lease assets
- Deferred rent

Same underlying lease balances, relabeled by the filer over time. 'Deferred rent' is a pre-ASC-842-style concept that phases out as the lease liability/ROU asset presentation takes over. Treat these as the same economic items across years when building the balance sheet roll-forward.

**Cash Flow Statement** (2021 - 2025)

- Cash paid for amounts included in the measurement of lease liabilities
- Increase (Decrease) in Right-of-use Lease Assets and Current and Non-current Lease Liabilities
- Lease assets and liabilities
- Deferred rent

The cash-flow side of the same lease presentation change above: the operating-activities adjustment for leases was reported as one combined 'Increase (Decrease)' line in 2022-2023, then reported as 'Lease assets and liabilities' from 2024. Same underlying adjustment, different label.

## Working Capital & Equity Compensation Timing

**Cash Flow Statement** (varies)

- Other current liabilities
- Other financing activity
- Employee tax withholding remitted in connection with exercise or release of equity awards
- Shares withheld for taxes on stock-based compensation
- Repurchase of stock

Smaller working-capital and equity-award-settlement lines that only appear in the years they were material enough (or occurred at all) to break out separately - common for line items tied to one-off treasury activity or changes in how equity award tax withholding was settled. Not every company reports these every year even when small amounts exist; they roll into a broader 'other' line instead.
