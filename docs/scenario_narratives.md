# Scenario Narratives

## Purpose

`assumption_justification.md` documents the reasoning behind each individual driver. This document does something different, it tells the story of each scenario as a whole. The point is to explain what has to be true in the real world for Base, Best, or Worst to actually play out, not just list the numbers behind them.

## Base Case

The base case assumes Warby Parker keeps doing roughly what it's already doing, at a decelerating pace. Revenue growth starts at 13.0% in 2026, close to the FY25 actual, and decelerates to 7.0% by 2030. That's a normal maturation curve for a scaling DTC retailer, not a slowdown driven by anything going wrong.

Gross margin stays close to flat, moving from 54.5% to 55.0% over the five years. This reflects a company that's been range-bound on gross margin for years with no clear direction, so the base case doesn't try to invent one.

The real engine of margin improvement in this scenario is SG&A leverage. SG&A falls from 53.5% of revenue in 2026 to 48.0% by 2030. That's a continuation of Warby Parker's actual trend, which dropped SG&A from 85.3% of revenue in FY21 to 54.6% in FY25, but at a slower rate, since most of the easy leverage from scaling a young store base has already been captured.

Put together, operating margin moves from roughly breakeven in 2026 to around 7% by 2030. The tax rate ramps from 8.0% to 24.0% over the same period, not because the statutory rate changes, but because NOL carryforwards stop shielding as much income as the company turns consistently profitable. Working capital and capex assumptions are held close to recent actuals throughout, so none of the improvement in this case comes from balance sheet gymnastics. It comes from the income statement doing what it's already been doing, just more slowly.

This is the scenario where nothing dramatic happens. Warby Parker keeps growing, keeps getting more efficient, and keeps closing the gap to normalized profitability, on the same trajectory it's already on.

## Best Case

The best case doesn't assume a different business, it assumes the current trends hold up longer than they typically would. Revenue growth stays closer to FY24's peak of 15.2%, starting at 15.0% in 2026 and only decelerating to 11.0% by 2030, versus 7.0% in the base case. The story here is that new store productivity and category expansion, contacts and eye exams specifically, keep growth elevated for longer than a typical maturation curve would suggest.

Gross margin actually improves in this case, from 55.0% to 57.0%, driven by mix shift toward higher-margin lens and exam revenue plus supply chain efficiency gains at scale. SG&A leverage also continues at closer to its recent historical pace rather than decelerating, falling to 44.0% of revenue by 2030 versus 48.0% in the base case.

The combined effect is meaningful. Operating margin climbs to roughly 13% by 2030, nearly double the base case. The tax rate stays lower for longer too, reaching only 20.0% by 2030 versus 24.0% in the base case, since faster profitability growth doesn't necessarily mean faster NOL exhaustion if income mix skews favorably.

Working capital and capex assumptions improve modestly in this case as well, inventory days falling faster and payables terms improving as the company gains supplier leverage at scale. None of these are aggressive assumptions on their own. What makes this the best case is that every driver moves in the favorable direction at once, and none of them reverses.

## Worst Case

The worst case is the only scenario where the story is genuinely different, not just slower. Revenue growth roughly halves immediately, from 13.0% in the base case to 8.0% in 2026, then decelerates further to 3.0% by 2030, essentially GDP-like growth. This reflects real competitive or macro pressure on discretionary eyewear spend, not just a more conservative version of the base case trend.

Gross margin compresses back toward Warby Parker's FY21 levels, falling from 53.5% to 51.0% by 2030, as input cost inflation and promotional intensity outpace any efficiency gains. SG&A leverage stalls completely and holds flat at 54.5% of revenue for all five years, since rising marketing spend to defend growth offsets whatever overhead leverage the company might otherwise capture.

This combination is what actually matters. Operating margin, which starts slightly negative in 2026, stays negative and widens to roughly -3.5% by 2030 rather than improving. This is the one scenario where the company does not reach sustained profitability within the forecast window, which is why the tax guard in the model matters here specifically, the `IF(pretax<=0,0,...)` logic keeps this scenario from calculating a nonsensical tax benefit on a growing loss.

Working capital and capex assumptions move against the company too. Inventory days partially revert toward FY22-23 levels, supplier payment terms tighten as the company loses negotiating leverage, and capex as a percentage of revenue actually increases, reflecting continued store buildout or technology spend used to defend growth rather than being pulled back. In a real downturn, a company under margin pressure would typically cut capex, not raise it, so this assumption reflects a specific view that Warby Parker fights for growth rather than retrenching, and that fight costs money without paying off in the margin line.

## What Separates the Scenarios

The single biggest swing factor across all three cases is SG&A leverage, not revenue growth. Revenue growth varies from 3.0% to 11.0% by 2030 across the scenarios, a meaningful range, but SG&A ranges from 44.0% to 54.5% of revenue in the same year, a wider swing in percentage point terms and the main reason operating margin diverges from roughly -3.5% to +13.0% across the three cases.

This is a useful thing to flag to anyone reviewing the model. It means the difference between Warby Parker becoming a durably profitable public company and continuing to struggle isn't primarily a question of how fast it grows. It's a question of whether it can hold the line on operating costs while it grows, which is a controllable, execution-driven variable rather than a market-driven one.

## How This Maps to the Model

The live scenario toggle on `00_Control_Panel` switches the entire forecast between these three cases in one click, and `07_Validation` confirms the balance sheet still ties out under all three. `08_Scenario_Planner` shows all three side by side for direct comparison, including the FY2030 snapshot where the worst case is the only one still showing a net loss. Full driver-level detail behind every number in this document lives in `assumption_justification.md`.
