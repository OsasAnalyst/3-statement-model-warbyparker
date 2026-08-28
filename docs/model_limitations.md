# Model Limitations

## Purpose

Every model simplifies reality. The value of documenting that isn't to apologize for it, it's to be clear about where the simplifications are, so anyone using this model knows exactly what it's good for and where to be careful. This document covers known data gaps, deliberate modeling simplifications, and the structural boundaries of what a model like this can tell you.

## Data Limitations

**FY2021 balance sheet gap.** The balance sheet in `02_Historical_IS_BS_CF` doesn't tie exactly in FY2021, there's an $11K gap. This traces back to a rounding artifact in Warby Parker's own as-filed 10-K, not an error introduced in this model. It's documented in the QC tie-out block on that tab rather than forced to zero, because forcing it would hide a real discrepancy in the source filing.

**FY2024-2025 cash flow rounding.** The cash flow statement ties within a $2K gap in FY2024 and FY2025 that carries forward from the same kind of filing-level rounding. Same treatment applies, it's disclosed, not masked.

**Five years of history only.** The model is built on FY2021 through FY2025 filings. That's a short window for a company that IPO'd in 2021, which means the historical ratios used to build assumptions are influenced by IPO-specific noise, especially in stock-based compensation and equity structure, that a longer history would have averaged out.

## Modeling Simplifications

**No debt schedule.** Warby Parker doesn't carry material long-term debt, so the model doesn't include one. If that changes in a future filing, this is the first thing that would need to be added, and it isn't currently built to handle it.

**Interest income held flat.** Rather than projecting interest income off a growing cash balance, which would create circularity, the model holds it flat at the FY2025 actual dollar amount for all five forecast years. This avoids an iterative calculation problem, but it also means the model understates interest income in later years if cash actually grows the way the forecast implies. This is a real tradeoff, not a cosmetic one.

**No financing activity assumed.** The model assumes zero debt issuance, zero repayment, and no equity transactions like buybacks or new issuances beyond the stock-based compensation already flowing through APIC. In reality, a growing profitable company might repurchase shares or take on debt to fund expansion. None of that is modeled here.

**Flat line items for immaterial accounts.** Several smaller balance sheet lines with no clear driver are held flat at their FY2025 actual value rather than projected. This is a deliberate choice to avoid inventing false precision on line items that don't move the overall picture, but it does mean those specific lines won't reflect any real change over the forecast period, even if in reality they would.

**Tax rate is a judgment-based ramp, not a formula.** The effective tax rate isn't extrapolated from history, because the historical ratio is distorted by years of pretax losses. Instead it's modeled as a NOL-utilization ramp built on judgment about how quickly carryforwards get used up. This is explained in detail in `assumption_justification.md`, but it's worth repeating here: this is the single most subjective assumption in the model, and a different analyst could reasonably build a different ramp.

**Working capital driven by simple day-count ratios.** AR, inventory, and AP are all projected using DSO, DIO, and DPO applied to revenue and COGS. This is standard practice, but it assumes those relationships stay linear and proportional to revenue, which won't hold perfectly if the business mix shifts meaningfully, for example if wholesale or insurance-reimbursed revenue grows as a share of the total.

## Scenario Limitations

**Base, Best, and Worst are constructed, not statistical.** These three cases were built by taking a view on how each driver would move under different conditions, not by running a Monte Carlo simulation or fitting a distribution to historical volatility. They represent three plausible, internally consistent stories, not a formal probability-weighted range. Actual results could fall outside the Worst case or exceed the Best case.

**Drivers move independently within each scenario.** Each scenario assumes its own consistent story, but the model doesn't enforce every possible correlation between drivers. For example, the Worst case assumes higher capex alongside falling margins, which is a specific view, not a mechanical consequence of one input triggering another. If you disagree with any single driver in a scenario, you can change it without breaking the model, but you should also reconsider whether the surrounding drivers in that scenario still make sense together.

**No macro or competitive inputs.** None of the three scenarios reference external variables directly, consumer spending indices, competitor pricing, interest rate environment, and so on. Those factors are embedded qualitatively in the reasoning behind each driver, but they aren't modeled as inputs that could be swapped out independently.

## What This Model Does Not Do

- It does not produce a valuation. There's no DCF, no comparable company analysis, and no share price target anywhere in this workbook. It forecasts financial statements, not equity value.
- It does not model M&A, new debt issuance, or major capital structure changes. If Warby Parker took on debt or made an acquisition, the model would need to be rebuilt to handle it.
- It does not account for accounting policy changes. If WRBY changes how it recognizes revenue, leases, or SBC in a future filing, the historical ratios this model is built on would need to be revisited.
- It does not incorporate quarterly seasonality. All forecasts are annual. A retailer like Warby Parker has real quarterly seasonality, particularly around holiday periods, that this model doesn't capture.

## Why This Matters

None of these limitations make the model wrong, they define its scope. A 3-statement model built from public filings, with three internally consistent forward scenarios, is a tool for understanding how a company's financial statements are structured and how they'd respond to different operating conditions. It is not a substitute for a full equity research report, and it shouldn't be treated as a precise forecast of what will actually happen. Anyone using this model for a real decision should treat every number in the forecast tabs as a reasoned estimate, not a prediction.
