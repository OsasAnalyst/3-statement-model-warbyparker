# 3-Statement Financial Model: Warby Parker (WRBY)

A full 3-statement financial model built from Warby Parker's actual SEC filings. The model takes five years of as-filed historicals, derives the operating assumptions that drive the business, and projects the income statement, balance sheet, and cash flow statement forward five years under three scenarios. Everything ties, every formula traces back to a real number, and nothing in the forecast is a guess dressed up as precision.

## Why Warby Parker

I wanted a company with a business model simple enough to model cleanly but with a financial story worth telling. Warby Parker fits both. It's a DTC eyewear retailer with straightforward revenue and cost drivers, it IPO'd in 2021 so there's a clean structural break to account for, and it spent FY2021 through FY2024 losing money before turning its first profitable year in FY2025. That's a real path-to-profitability story, not a flat historical trend, which makes the forecast assumptions actually matter instead of just extrapolating a straight line.

## Data Source

All historical data comes from Warby Parker's 10-K filings on SEC EDGAR, FY2021 through FY2025. I pulled the data using the filing's own rendered statement pages (the SEC's R-files) rather than a curated XBRL tag list, so every line item the company actually reported made it into the dataset, including items that only appear in some years. Structural changes across that period, the IPO transition, lease presentation changes, new SBC programs, are documented in `data/raw/data_extraction_notes.md` rather than quietly merged away.

## The Approach

The model runs in three stages. First, `python/01_edgar_data_pull.py` pulls and cleans the historical statements into structured CSVs. Second, `python/02_assumption_calculator.py` calculates 13 historical operating ratios from that data and builds Base, Best, and Worst forecast assumptions for each one. Third, the Excel workbook takes those assumptions and builds a fully linked 3-statement forecast, income statement drives the balance sheet and cash flow statement, working capital changes and capex flow through cash flow, and ending cash closes the loop back to the balance sheet.

## Key Assumptions

Revenue growth, gross margin, SG&A leverage, and the effective tax rate are the core income statement drivers, each built off Warby Parker's actual FY2021-2025 trend rather than a generic template. Working capital runs on DSO, DIO, and DPO day-count ratios, and PP&E is a straightforward roll-forward of beginning balance plus capex minus depreciation. The effective tax rate is the one driver that isn't a trend extrapolation, it's modeled as a NOL-utilization ramp, since Warby Parker's historical tax ratio is distorted by years of pretax losses. Full reasoning for every driver is in `docs/assumption_justification.md`.

There's no debt schedule in this model. Warby Parker doesn't carry material long-term debt, and the forecast assumes zero financing activity throughout. Interest income is held flat at the FY2025 actual rather than tied to a growing cash balance, a deliberate choice to avoid circularity in the model.

## Scenario Structure

Base, Best, and Worst aren't three versions of the same growth story, they diverge mainly on cost discipline. All three see revenue grow, but SG&A leverage is what separates a company that reaches sustained double-digit operating margins by 2030 from one that's still posting a net loss. Full scenario detail is in `docs/scenario_narratives.md`.

## Project Structure

```
3-statement-model-warbyparker/
│
├── README.md
│
├── data/
│   ├── raw/
│   │   ├── wrby_10k_fy2025.htm
│   │   ├── wrby_10k_fy2022.htm
│   │   └── data_extraction_notes.md
│   └── processed/
│       ├── historical_income_statement.csv
│       ├── historical_balance_sheet.csv
│       ├── historical_cash_flow.csv
│       └── historical_ratios.csv
│
├── python/
│   ├── 01_edgar_data_pull.py
│   └── 02_assumption_calculator.py
│
├── excel/
│   └── wrby_3_statement_model.xlsx
│
├── docs/
│   ├── model_architecture.md
│   ├── assumption_justification.md
│   ├── scenario_narratives.md
│   └── model_limitations.md
│
├── output/
│   └── monthly_board_style_memo.docx
│
└── deliverables/
    └── final_package.zip
```

## How the Pieces Fit Together

Data flows one direction, start to finish. EDGAR filings go into `data/raw`, get parsed into `data/processed`, get turned into assumptions, and those assumptions drive every forecast tab in the Excel workbook. `docs/model_architecture.md` documents the statement linkages in detail, `docs/assumption_justification.md` documents where every driver came from, and `docs/model_limitations.md` is honest about where the model simplifies reality. The board memo in `output/` is the one-page summary version of what the model says, written the way I'd actually present it to leadership.

## Key Outputs

- **`excel/wrby_3_statement_model.xlsx`**: the core deliverable. Eleven tabs covering control panel, assumptions, historicals, five-year forecast, supporting schedules, validation, scenario planning, and a KPI dashboard.
- **`09_Dashboard`**: a board-ready view of revenue, margins, and the FY2030 scenario snapshot.
- **`output/monthly_board_style_memo.docx`**: a one-page CFO-style summary of the forecast, risks, and recommended actions.

## Getting Started

```bash
git clone https://github.com/OsasAnalyst/3-statement-model-warbyparker.git
cd 3-statement-model-warbyparker
pip install pandas requests openpyxl
python python/01_edgar_data_pull.py
python python/02_assumption_calculator.py
```

This regenerates the processed CSVs from EDGAR. The Excel workbook itself was built manually on top of those outputs and is included as-is in `excel/`.

## Future Work

A debt schedule would be the natural next addition if Warby Parker ever takes on material leverage. I'd also like to tie interest income to a projected cash balance properly, using Excel's iterative calculation settings, instead of holding it flat. Beyond that, quarterly seasonality is the biggest simplification in this model and the one I'd tackle next if I extended the forecast granularity below annual.

## Contact

**Osaretin Idiagbonmwen**
Email: idiagbonmwenosaretin@gmail.com
LinkedIn: [linkedin.com/in/osaretin-idiagbonmwen-33ab85339](https://www.linkedin.com/in/osaretin-idiagbonmwen-33ab85339/)
