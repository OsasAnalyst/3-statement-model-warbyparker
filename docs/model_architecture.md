# Model Architecture

## Overview

This model is a 3-statement financial model for Warby Parker (WRBY), built on the company's actual 10-K filings from FY2021 through FY2025. It takes historical financials, calculates the operating ratios that drive the business, and projects the income statement, balance sheet, and cash flow statement forward five years, from FY2026 through FY2030. The three statements are fully linked, so a change in one flows through the other two automatically. The model also includes a Base/Best/Worst scenario structure so the forecast isn't a single fixed path.

## The Income Statement

Revenue for each forecast year compounds off the prior forecast year, not off history. So FY2027 revenue grows off FY2026's projected number, FY2028 off FY2027, and so on. This matters because it means growth assumptions compound the way they would in reality, rather than each year being calculated independently from a fixed historical base.

COGS and operating expenses are driven as a percentage of revenue, using ratios pulled from `01_Assumptions`, which in turn pull from the scenario toggle on `00_Control_Panel`. Interest income is held flat at the FY2025 actual rather than projected off a growing cash balance. I made this choice deliberately to avoid circularity in the model (more on that below).

Tax is calculated with a guard: `IF(pretax income <= 0, 0, pretax income * tax rate)`. This stops the model from calculating a tax benefit in a loss year, which would be misleading given Warby Parker's NOL position. The tax rate itself isn't a straight trend extrapolation, it's modeled as a NOL-utilization ramp. The full reasoning for that is in `assumption_justification.md`, this document is just concerned with how the mechanism works.

Net income is the final output of the income statement, and it's the number that flows into both the cash flow statement and the balance sheet.

## The Balance Sheet

The forecast balance sheet is built from a mix of driver-based projections and roll-forwards, not a single formula pattern.

Accounts receivable, inventory, and accounts payable come from `06_Supporting_Schedules`, where they're calculated using DSO, DIO, and DPO day-count formulas applied to projected revenue and COGS. PP&E also comes from `06_Supporting_Schedules`, as a roll-forward: beginning balance plus capex minus D&A equals ending balance.

Line items with no natural driver (certain other assets and liabilities) are held flat at their FY2025 actual values. This is a deliberate simplification. Projecting immaterial line items with invented drivers adds false precision without adding insight.

On the equity side, accumulated deficit rolls forward each year by adding net income from the income statement. Additional paid-in capital (APIC) grows each year by the stock-based compensation add-back, consistent with how WRBY actually reports SBC as a non-cash equity-settled expense.

Cash on the balance sheet is not an independent projection. It pulls directly from ending cash on the cash flow statement. This is what makes the balance sheet balance, assets equal liabilities plus equity, without any manual plug or override.

## The Cash Flow Statement

The cash flow statement uses the indirect method, starting from net income and adjusting for non-cash items and working capital changes.

**Operating activities:** Starts with net income, adds back D&A and stock-based compensation, then adjusts for the change in AR, inventory, and AP pulled from the balance sheet. An increase in AR or inventory is a cash outflow, an increase in AP is a cash inflow, and the signs are set up to reflect that correctly rather than just linking raw deltas.

**Investing activities:** Capex is pulled from the PP&E roll-forward in `06_Supporting_Schedules` and shown as a cash outflow.

**Financing activities:** Set to zero. Warby Parker carries no material long-term debt, so there's no debt schedule in this model, and there's no assumed equity issuance or share repurchase built into the forecast.

Ending cash for each year is the sum of beginning cash and the net change from all three sections. That ending cash figure is what flows back to the balance sheet.

## The Linkages

This is the part that actually makes it a 3-statement model rather than three separate spreadsheets.

- **Net income** flows from `03_Forecast_IS` to the top of `05_Forecast_CF`, and separately rolls into accumulated deficit on `04_Forecast_BS`.
- **Working capital changes** (AR, inventory, AP) are calculated on the balance sheet side in `06_Supporting_Schedules`, then the period-over-period change is pulled into the operating section of `05_Forecast_CF`.
- **Capex** flows from the PP&E roll-forward in `06_Supporting_Schedules` into the investing section of `05_Forecast_CF`, and the resulting ending PP&E balance also feeds `04_Forecast_BS` directly.
- **Financing activity** is zero across the board, since there's no debt schedule and no assumed equity transactions.
- **Cash** is the closing link. Ending cash on `05_Forecast_CF` feeds the cash line on `04_Forecast_BS`. Nothing on the balance sheet cash line is hardcoded or manually plugged, it's a direct formula reference.

If any one of these links breaks, the balance sheet stops balancing. That's the whole point of building it this way, the model polices itself.

## Supporting Schedules

`06_Supporting_Schedules` holds the two roll-forwards that feed both the balance sheet and the cash flow statement:

- **Working capital schedule:** AR, inventory, and AP calculated from DSO, DIO, and DPO assumptions applied against projected revenue and COGS.
- **PP&E roll-forward:** Beginning balance, plus capex, minus D&A, equals ending balance, validated against the FY2025 historical DIO figure before being extended into the forecast.

There is no debt schedule in this model, since Warby Parker does not carry material long-term debt.

## Validation

`07_Validation` is a consolidated dashboard that checks the model against itself across every forecast year and every scenario. It confirms:

- Assets equal liabilities plus equity, with zero gap, for all five forecast years.
- The same balance check holds under all three scenarios, Base, Best, and Worst.
- Conditional formatting flags anything outside a defined tolerance band, so a break would be visible immediately rather than buried in a cell.

The historical statements in `02_Historical_IS_BS_CF` carry their own QC tie-out blocks. The income statement ties to zero. The balance sheet balances except for an $11K gap in FY2021, which traces back to a rounding artifact in Warby Parker's own filing, not an error in this model. The cash flow statement ties within a $2K rounding gap in FY2024 and FY2025 that carries forward from the same source. Both are documented rather than hidden or forced to zero.

## Scenario Structure

The model handles scenarios two different ways, for two different purposes.

`00_Control_Panel` has a single dropdown (Base/Best/Worst) that drives `01_Assumptions` through SUMIFS formulas keyed off the toggle. This is the live, interactive version, change the dropdown and every downstream tab, including the full forecast and the balance check, recalculates under that scenario.

`08_Scenario_Planner` is built differently on purpose. It runs Base, Best, and Worst as three independent, hardcoded blocks side by side, each with its own mini income statement including interest and tax, plus a FY2030 comparison summary. This lets you see all three outcomes at once without toggling back and forth. Worst case correctly produces a net loss by FY2030, which is the kind of result a scenario range should be able to show.

## Circularity

There is no circularity in this model. The most common source of circularity in a 3-statement model is interest income calculated off a projected average cash balance, which depends on cash flow, which depends on interest income. I avoided that by holding interest income flat at the FY2025 actual rather than tying it to projected cash. This was a deliberate tradeoff: it sacrifices some precision on interest income in later forecast years in exchange for a model with no iterative calculation, no circular reference warnings, and no risk of Excel's iterative calculation settings silently producing different results on different machines.
