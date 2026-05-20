"""
config/constants.py
────────────────────
PSX universe, sector maps, news queries, and the EARNINGS SENSITIVITY MAP.

The sensitivity map is what separates this program from a news aggregator.
It tells the AI exactly which macro variables hit which sector's income
statement, and HOW — so explanations are technically accurate, not generic.
"""

from __future__ import annotations

# ─── PSX Universe ─────────────────────────────────────────────────────────────

PSX_TICKERS: dict[str, str] = {
    # Energy & Refining
    "OGDC":   "Oil & Gas Development Company",
    "PPL":    "Pakistan Petroleum Limited",
    "PSO":    "Pakistan State Oil",
    "SNGP":   "Sui Northern Gas Pipelines",
    "SSGC":   "Sui Southern Gas Company",
    "APL":    "Attock Petroleum Limited",
    "ATRL":   "Attock Refinery Limited",
    "NRL":    "National Refinery Limited",
    # Banking & Finance
    "HBL":    "Habib Bank Limited",
    "MCB":    "MCB Bank Limited",
    "UBL":    "United Bank Limited",
    "ABL":    "Allied Bank Limited",
    "BAFL":   "Bank Alfalah Limited",
    "BAHL":   "Bank AL Habib Limited",
    "MEBL":   "Meezan Bank Limited",
    "NBP":    "National Bank of Pakistan",
    "FABL":   "Faysal Bank Limited",
    "AKBL":   "Askari Bank Limited",
    # Fertiliser
    "EFERT":  "Engro Fertilizers",
    "FFC":    "Fauji Fertilizer Company",
    "FFBL":   "Fauji Fertilizer Bin Qasim",
    "FATIMA": "Fatima Fertilizer",
    # Cement
    "LUCK":   "Lucky Cement",
    "DGKC":   "D.G. Khan Cement",
    "MLCF":   "Maple Leaf Cement",
    "PIOC":   "Pioneer Cement",
    "CHCC":   "Cherat Cement",
    "KOHC":   "Kohat Cement",
    # Textile
    "NML":    "Nishat Mills Limited",
    "NCL":    "Nishat (Chunian) Limited",
    "GATM":   "Gul Ahmed Textile Mills",
    "ILP":    "Interloop Limited",
    # Technology
    "SYS":    "Systems Limited",
    "TRG":    "TRG Pakistan",
    "AVN":    "Avanceon Limited",
    "NETSOL": "NetSol Technologies",
    # Power
    "HUBC":   "Hub Power Company",
    "KAPCO":  "Kot Addu Power Company",
    "NCPL":   "Nishat Power Limited",
    "KEL":    "K-Electric Limited",
    # Conglomerate
    "ENGRO":  "Engro Corporation",
    # FMCG
    "NESTLE": "Nestlé Pakistan",
    "UNITY":  "Unity Foods Limited",
    "COLG":   "Colgate-Palmolive Pakistan",
    "PSMC":   "Pak Suzuki Motor Company",
    # Pharma
    "SEARL":  "The Searle Company",
    "ABOT":   "Abbott Laboratories Pakistan",
    "GLAXO":  "GlaxoSmithKline Pakistan",
}

TICKER_SUFFIX = ".KA"

SECTOR_MAP: dict[str, list[str]] = {
    "Energy & Refining":  ["OGDC", "PPL", "PSO", "SNGP", "SSGC", "APL", "ATRL", "NRL"],
    "Banking & Finance":  ["HBL", "MCB", "UBL", "ABL", "BAFL", "BAHL", "MEBL", "NBP", "FABL", "AKBL"],
    "Fertiliser":         ["EFERT", "FFC", "FFBL", "FATIMA"],
    "Cement":             ["LUCK", "DGKC", "MLCF", "PIOC", "CHCC", "KOHC"],
    "Textile":            ["NML", "NCL", "GATM", "ILP"],
    "Technology":         ["SYS", "TRG", "AVN", "NETSOL"],
    "Power & Utilities":  ["HUBC", "KAPCO", "NCPL", "KEL"],
    "Conglomerate":       ["ENGRO"],
    "FMCG & Consumer":    ["NESTLE", "UNITY", "COLG", "PSMC"],
    "Pharmaceutical":     ["SEARL", "ABOT", "GLAXO"],
}

ALIAS_MAP: dict[str, str] = {
    "ogdc": "OGDC", "oil": "OGDC", "ppl": "PPL", "pso": "PSO",
    "hbl": "HBL", "habib": "HBL", "mcb": "MCB", "ubl": "UBL",
    "mebl": "MEBL", "meezan": "MEBL", "engro": "ENGRO",
    "efert": "EFERT", "ffc": "FFC", "luck": "LUCK", "lucky": "LUCK",
    "dgkc": "DGKC", "sys": "SYS", "systems": "SYS", "trg": "TRG",
    "hubc": "HUBC", "hub": "HUBC", "nestle": "NESTLE",
    "searl": "SEARL", "nml": "NML", "nishat": "NML",
    "psmc": "PSMC", "suzuki": "PSMC", "kel": "KEL",
    "netsol": "NETSOL", "avn": "AVN", "avanceon": "AVN",
    "ffbl": "FFBL", "fatima": "FATIMA", "akbl": "AKBL",
    "askari": "AKBL", "fabl": "FABL", "faysal": "FABL",
    "bahl": "BAHL", "bafl": "BAFL", "alfalah": "BAFL",
    "nbp": "NBP", "national bank": "NBP", "abl": "ABL", "allied": "ABL",
    "kapco": "KAPCO", "ncpl": "NCPL", "ncl": "NCL",
    "gatm": "GATM", "gul ahmed": "GATM", "ilp": "ILP", "interloop": "ILP",
    "unity": "UNITY", "colg": "COLG", "colgate": "COLG",
    "abot": "ABOT", "abbott": "ABOT", "glaxo": "GLAXO",
    "atrl": "ATRL", "attock": "ATRL", "nrl": "NRL", "sngp": "SNGP", "ssgc": "SSGC",
}

CHART_PERIODS = ["1mo", "3mo", "6mo", "1y", "2y", "5y"]
HEATMAP_TICKERS = ["OGDC", "PPL", "HBL", "MCB", "UBL", "MEBL", "EFERT", "FFC",
                   "LUCK", "ENGRO", "SYS", "HUBC", "NESTLE", "SEARL", "NML", "PSO"]
NEWS_LOOKBACK_DAYS = 30

# ─── NEWS QUERIES ─────────────────────────────────────────────────────────────

SECTOR_NEWS_QUERIES: dict[str, list[str]] = {
    "Energy & Refining":  [
        "Pakistan oil gas OGRA notification", "OGDC PPL PSO Pakistan earnings",
        "Pakistan petroleum circular debt", "Brent crude oil price",
        "Pakistan energy sector upstream", "Pakistan refinery margins",
    ],
    "Banking & Finance":  [
        "SBP monetary policy rate Pakistan", "Pakistan banking sector earnings",
        "Pakistan interest rate MPC decision", "Pakistan bank NPL non-performing loans",
        "Pakistan super tax banking", "SBP policy rate hike cut",
    ],
    "Fertiliser":         [
        "Pakistan urea fertiliser subsidy", "EFERT FFC fertiliser earnings Pakistan",
        "Pakistan urea offtake NFDC", "DAP urea price international",
        "Pakistan fertiliser gas allocation SNGP", "Pakistan agriculture urea demand",
    ],
    "Cement":             [
        "Pakistan cement dispatches APCMA", "Pakistan cement sector earnings",
        "Pakistan construction PSDP CPEC", "coal price cement Pakistan",
        "Pakistan cement retention price bag", "Pakistan housing construction interest rate",
    ],
    "Textile":            [
        "Pakistan textile exports bureau statistics", "Pakistan garment RMG exports",
        "cotton price international Pakistan", "DLTL rebate Pakistan textile",
        "Pakistan textile energy cost", "EU US apparel demand Pakistan",
    ],
    "Technology":         [
        "Pakistan IT exports PSEB monthly", "SYS TRG Pakistan technology earnings",
        "Pakistan software exports freelancer", "SBP Pakistan foreign currency IT",
        "Pakistan tech sector results", "US tech spending global IT",
    ],
    "Power & Utilities":  [
        "Pakistan IPP circular debt NEPRA", "Pakistan electricity tariff determination",
        "HUBC KAPCO Pakistan power earnings", "NEPRA tariff notification",
        "Pakistan energy circular debt IMF", "Pakistan DISCO payments arrears",
    ],
    "Conglomerate":       [
        "Engro Pakistan quarterly results", "ENGRO EFERT LNG Pakistan",
        "Engro fertilizers polymer Pakistan", "Engro corporation earnings dividend",
    ],
    "FMCG & Consumer":    [
        "Pakistan inflation CPI consumer spending", "Pakistan FMCG Nestle Colgate results",
        "palm oil sugar price Pakistan", "Pakistan retail consumer demand",
        "Pakistan budget sales tax FED FMCG",
    ],
    "Pharmaceutical":     [
        "DRAP drug price notification Pakistan", "Pakistan pharma SEARL Abbott results",
        "Pakistan medicine API import cost", "Pakistan pharma sector earnings",
        "DRAP regulatory approval Pakistan",
    ],
}

MACRO_QUERIES: list[str] = [
    "Pakistan IMF programme review tranche",
    "Pakistan rupee dollar PKR USD exchange rate",
    "SBP State Bank Pakistan monetary policy interest rate",
    "Pakistan inflation CPI headline core",
    "Pakistan current account balance surplus deficit",
    "Pakistan fiscal deficit federal budget",
    "Pakistan economy news today",
    "KSE-100 Pakistan stock market rally decline",
    "Pakistan FATF compliance financial",
    "Pakistan foreign exchange reserves SBP",
    "Pakistan political stability economy",
    "Pakistan GDP growth economic outlook IMF World Bank",
    "Dawn business Pakistan economy",
    "Pakistan federal budget revenue expenditure",
]

# ─── EARNINGS SENSITIVITY MAP ─────────────────────────────────────────────────
# The intelligence core of the AI engine.
# For each sector: which variables move earnings, the direction, the exact
# financial mechanism, and estimated magnitude.
# The AI uses this to explain WHY a news event caused THIS size of move.

EARNINGS_SENSITIVITY: dict[str, dict] = {

    "Banking & Finance": {
        "primary_revenue_driver": "Net Interest Margin (NIM) = lending rate minus cost of funds",
        "business_model_plain_english": (
            "Banks borrow money from depositors at a low rate and lend it out at a higher rate. "
            "The gap between those two rates — the Net Interest Margin — is where they make their money. "
            "They also invest heavily in government bonds (T-bills, PIBs) which pay the policy rate."
        ),
        "sensitivities": [
            {
                "variable": "SBP Policy Rate",
                "direction": "MIXED — depends on asset-liability mix",
                "mechanism": (
                    "When SBP raises the policy rate, banks' T-bill and PIB portfolios immediately earn more. "
                    "But deposit costs also rise as savers demand higher returns. The NET effect depends on "
                    "each bank's balance sheet: banks with large fixed-rate loan books see NIM compression; "
                    "banks with large investment portfolios (T-bills) see NIM expansion. "
                    "Islamic banks like MEBL use profit rates tied to KIBOR — they reprice faster. "
                    "A 100bps rate hike typically moves sector NIM by 8-15bps within one quarter."
                ),
                "magnitude": "100bps rate change → 8-15% EPS impact depending on asset-liability structure",
                "simple_explanation": "Higher interest rates = banks earn more on government bonds but also pay more to depositors",
            },
            {
                "variable": "PKR/USD Exchange Rate",
                "direction": "POSITIVE on depreciation for banks with foreign currency books",
                "mechanism": (
                    "Banks holding USD-denominated assets (foreign currency accounts, trade finance, overseas operations) "
                    "book revaluation gains when the rupee falls. HBL and UBL have large overseas presence — "
                    "depreciation translates overseas earnings into more PKR. However, rupee weakness also raises "
                    "NPL risk among importers and dollar-debt borrowers who can't service USD obligations."
                ),
                "magnitude": "10% PKR depreciation → 3-7% EPS uplift for banks with large FC books",
                "simple_explanation": "Banks with dollars earn more PKR when the rupee weakens",
            },
            {
                "variable": "IMF Programme / Super Tax / Fiscal Policy",
                "direction": "NEGATIVE in short term",
                "mechanism": (
                    "IMF conditionality has repeatedly triggered super tax imposition on banks in Pakistan. "
                    "Banks also hold ~60% of assets in government securities — IMF-driven fiscal consolidation "
                    "means government borrows less, shrinking the high-yield T-bill book banks depend on. "
                    "Super tax of 10% on banking sector (as in 2023) is a direct EPS hit of 10-15%."
                ),
                "magnitude": "Super tax announcement → 10-20% single-session price drop historically",
                "simple_explanation": "Government taxing banks more directly cuts their profits",
            },
            {
                "variable": "NPL Ratio / Credit Quality",
                "direction": "NEGATIVE if NPLs rise",
                "mechanism": (
                    "Non-Performing Loans require provisioning that directly hits the P&L. "
                    "Economic slowdown, high inflation reducing consumer income, and energy sector "
                    "circular debt all push NPLs higher. Banks must set aside provisions = lower net profit."
                ),
                "magnitude": "1% rise in NPL ratio → 5-10% provisioning charge on net profit",
                "simple_explanation": "When borrowers can't repay loans, banks have to write off losses",
            },
        ],
        "key_metrics": ["NIM", "CASA ratio", "NPL ratio", "T-bill portfolio size", "ROE", "CAR"],
        "regulators": ["SBP — State Bank of Pakistan", "SECP"],
        "credible_sources": ["SBP website", "Dawn Business", "Business Recorder", "Bloomberg Pakistan"],
    },

    "Energy & Refining": {
        "primary_revenue_driver": "Production volumes × commodity price (USD) × PKR/USD rate",
        "business_model_plain_english": (
            "E&P companies (OGDC, PPL) drill for oil and gas and sell it. Their revenue depends on "
            "how much they produce AND what international oil prices are. Since oil is priced in dollars, "
            "the rupee-dollar rate also matters hugely. Refineries (ATRL, NRL) buy crude and sell "
            "petroleum products — their profit is the 'crack spread' between input and output prices."
        ),
        "sensitivities": [
            {
                "variable": "International Crude Oil / Brent Price",
                "direction": "POSITIVE for E&P, MIXED for refineries",
                "mechanism": (
                    "OGDC and PPL's wellhead prices for oil and gas are linked to Brent via a government formula. "
                    "Higher Brent = higher realized price per barrel = direct revenue uplift with the same costs. "
                    "For refineries, higher crude = higher input cost. Refinery margins depend on whether "
                    "product prices (petrol, HSD) are raised simultaneously by OGRA. If OGRA delays, "
                    "refineries absorb the cost increase and margins collapse."
                ),
                "magnitude": "$10/bbl Brent move → 6-9% EPS change for pure E&P; variable for refineries",
                "simple_explanation": "When global oil prices rise, OGDC and PPL earn more per barrel they produce",
            },
            {
                "variable": "PKR/USD Exchange Rate",
                "direction": "POSITIVE for E&P on depreciation",
                "mechanism": (
                    "Oil revenues are effectively USD-denominated but all costs (salaries, rigs, operations) "
                    "are in PKR. When the rupee depreciates, PKR revenue rises automatically while costs stay flat. "
                    "This is pure margin expansion. OGDC with its large production volumes is the most sensitive "
                    "stock on the KSE-100 to rupee movement — a direct mechanical relationship."
                ),
                "magnitude": "10% PKR depreciation → 8-12% EPS uplift for OGDC, PPL",
                "simple_explanation": "OGDC earns in dollars but spends in rupees — rupee weakness directly boosts profits",
            },
            {
                "variable": "OGRA Pricing Notifications / SROs",
                "direction": "VARIABLE — can be either",
                "mechanism": (
                    "The government controls petroleum product prices and gas tariffs through OGRA. "
                    "A price increase notification is an immediate revenue catalyst. A price freeze "
                    "during rising international prices means companies absorb the loss. "
                    "Circular debt — where WAPDA and DISCOs owe money to the energy chain — "
                    "means OGDC often has PKR 100-200B in receivables that never convert to cash."
                ),
                "magnitude": "Circular debt accumulation reduces effective cash EPS by 15-25%",
                "simple_explanation": "Even when OGDC books profits, the government sometimes delays paying — reducing real cash earned",
            },
        ],
        "key_metrics": ["Brent price", "PKR/USD", "Circular debt total", "Production volumes boed", "OGRA notifications"],
        "regulators": ["OGRA", "Ministry of Energy", "PPIB"],
        "credible_sources": ["OGRA website", "Reuters Energy", "Bloomberg Oil", "Dawn Business", "Business Recorder"],
    },

    "Fertiliser": {
        "primary_revenue_driver": "Urea/DAP tonnes sold × net realised price after subsidy",
        "business_model_plain_english": (
            "Fertiliser companies (EFERT, FFC) make urea from natural gas and sell it to farmers. "
            "The government controls the price farmers pay and also subsidises the gas feedstock. "
            "So two government decisions dominate this sector: the urea price cap and the gas price. "
            "Both are set by bureaucrats, not the market — making this a regulated, policy-driven sector."
        ),
        "sensitivities": [
            {
                "variable": "Government Urea Subsidy / Maximum Retail Price",
                "direction": "CRITICAL — most important single variable",
                "mechanism": (
                    "Government sets the Maximum Retail Price (MRP) for urea. When MRP rises, "
                    "companies earn more per tonne. When government freezes MRP despite rising costs, "
                    "margins collapse. Subsidy removal raises farm-gate prices → farmers buy less urea "
                    "(demand destruction) → volume AND price both fall simultaneously. "
                    "EFERT earns approximately 55-60% of revenue from urea — MRP is existential."
                ),
                "magnitude": "15% subsidy reduction → PKR 8-12 EPS impact on EFERT annually",
                "simple_explanation": "If the government reduces the subsidy it gives farmers to buy fertiliser, farmers buy less — hurting EFERT's sales and profits",
            },
            {
                "variable": "Natural Gas Feedstock Price and Availability",
                "direction": "NEGATIVE if gas price rises or supply cut",
                "mechanism": (
                    "Natural gas is both the raw material AND the energy source for urea production. "
                    "SNGP/SSGC allocate gas to fertiliser plants at concessional rates. "
                    "Gas shortages force partial or full plant shutdowns — fixed costs continue "
                    "on zero production = catastrophic unit economics. "
                    "Gas price hikes raise COGS directly."
                ),
                "magnitude": "10% gas price increase → 5-8% EBITDA margin compression",
                "simple_explanation": "Fertiliser plants run on gas. Less gas or more expensive gas = less production at higher cost",
            },
            {
                "variable": "Agricultural Season Quality (Kharif/Rabi)",
                "direction": "POSITIVE if good season",
                "mechanism": (
                    "Fertiliser demand peaks during Kharif (June-August) and Rabi (Feb-April) planting seasons. "
                    "Good monsoon rains encourage planting → more urea demand. Floods or drought destroy "
                    "crops and farming confidence → demand collapses. Monthly NFDC offtake data "
                    "is the leading indicator — below-season numbers signal trouble quarters ahead."
                ),
                "magnitude": "Poor season → 20-35% volume decline in peak months",
                "simple_explanation": "Good rains = more farming = more fertiliser bought. Floods or drought = opposite",
            },
        ],
        "key_metrics": ["Monthly urea offtake (NFDC)", "Gas allocation notices", "MRP level", "International urea price $/tonne"],
        "regulators": ["Ministry of Industries", "OGRA (gas pricing)", "NFDC"],
        "credible_sources": ["NFDC monthly reports", "Dawn Business", "Business Recorder", "Fertiliser Week"],
    },

    "Cement": {
        "primary_revenue_driver": "Cement dispatches (tonnes) × net retention price per tonne",
        "business_model_plain_english": (
            "Cement companies sell cement to construction projects. Their revenue is simply: "
            "how many bags they sell × what price they get. The price they charge is called the "
            "'retention price' (what the factory gets after distributor margins). "
            "Demand comes from two sources: government infrastructure projects (PSDP, CPEC) "
            "and private housing/construction."
        ),
        "sensitivities": [
            {
                "variable": "PSDP Spending / Government Infrastructure",
                "direction": "POSITIVE if spending rises, NEGATIVE if cut",
                "mechanism": (
                    "Government's Public Sector Development Programme drives bulk cement demand. "
                    "CPEC, motorways, dams, public buildings all require enormous cement volumes. "
                    "When IMF demands fiscal consolidation, PSDP is the first budget line cut — "
                    "cement dispatches fall within 2-3 months. Northern plants (LUCK, PIOC, CHCC) "
                    "are most exposed to CPEC activity; southern plants less so."
                ),
                "magnitude": "20% PSDP cut → 12-18% dispatch volume decline industry-wide",
                "simple_explanation": "When government builds less roads and dams, cement companies sell less cement",
            },
            {
                "variable": "SBP Policy Rate (Mortgage and Construction Finance)",
                "direction": "NEGATIVE if rates rise",
                "mechanism": (
                    "High interest rates kill private housing — the other demand pillar. "
                    "At 22% policy rate (Pakistan's 2023 peak), housing loans became unaffordable "
                    "and real estate developers paused projects. Every 100bps rate cut stimulates "
                    "housing construction demand within 1-2 quarters. "
                    "Rate cuts are the single most reliable cement demand catalyst."
                ),
                "magnitude": "200bps rate cut → 8-15% pickup in private sector cement demand",
                "simple_explanation": "Cheaper loans = more people can afford to build houses = more cement sold",
            },
            {
                "variable": "Coal Price (Newcastle benchmark)",
                "direction": "NEGATIVE if rises",
                "mechanism": (
                    "Coal is 35-45% of cement production cost — the single largest input. "
                    "International coal price spikes (Newcastle benchmark) directly compress margins. "
                    "Pakistani cement plants cannot easily pass through cost increases "
                    "when demand is weak. The 2022 coal price spike (post-Ukraine war) caused "
                    "cement sector EBITDA margins to collapse from 30% to under 15%."
                ),
                "magnitude": "$30/tonne coal price increase → 15-20% EBITDA margin compression",
                "simple_explanation": "Cement kilns burn coal to make cement. When coal gets expensive, profits shrink",
            },
            {
                "variable": "Retention Price / Industry Pricing Power",
                "direction": "POSITIVE if retention price rises",
                "mechanism": (
                    "When capacity utilisation rises above 80%, cement companies can raise prices. "
                    "Monthly retention price data is the leading margin indicator. "
                    "Price per bag above PKR 900 signals sector profitability recovery. "
                    "Price wars (below PKR 750/bag) signal oversupply and margin collapse."
                ),
                "magnitude": "PKR 50/bag retention price increase → 8-12% EBITDA uplift",
                "simple_explanation": "When demand is high, cement companies can charge more per bag — margins improve",
            },
        ],
        "key_metrics": ["Monthly dispatch data (APCMA)", "Retention price per bag", "Coal price Newcastle $/tonne", "PSDP utilisation %"],
        "regulators": ["APCMA (industry association)", "Competition Commission of Pakistan"],
        "credible_sources": ["APCMA monthly data", "Dawn Business", "Business Recorder", "Reuters Commodities"],
    },

    "Technology": {
        "primary_revenue_driver": "USD-denominated export revenues converted at spot PKR/USD rate",
        "business_model_plain_english": (
            "Pakistani IT companies (SYS, TRG) do software work for foreign clients — mostly US and European companies. "
            "They bill in dollars, but pay their employees and offices in rupees. "
            "This means they are naturally 'long dollars' — when the dollar strengthens against the rupee, "
            "their rupee profits automatically increase even if they do the exact same work."
        ),
        "sensitivities": [
            {
                "variable": "PKR/USD Exchange Rate",
                "direction": "STRONGLY POSITIVE on depreciation — highest sensitivity on KSE-100",
                "mechanism": (
                    "Revenue is in USD, costs are in PKR. Depreciation increases PKR revenue "
                    "with zero cost increase. With operating leverage (fixed cost base), "
                    "a 10% depreciation → 10% revenue uplift but only marginal cost increase "
                    "→ EPS uplift of 15-20% due to leverage effect. "
                    "SYS is essentially a PKR/USD proxy trade on the KSE-100."
                ),
                "magnitude": "10% PKR depreciation → 15-20% EPS uplift (operating leverage)",
                "simple_explanation": "SYS earns in dollars. When the dollar becomes worth more rupees, SYS profits in rupees go up automatically",
            },
            {
                "variable": "Global IT Spending / US Tech Sector",
                "direction": "POSITIVE if spending rises",
                "mechanism": (
                    "Pakistani IT companies' clients are US and EU enterprises. "
                    "US tech spending slowdowns (Fed rate hikes reducing capex budgets) "
                    "cause contract delays and hiring freezes at client companies. "
                    "2023 US tech layoffs directly compressed project pipelines for SYS, TRG. "
                    "US ISM Services PMI is the best leading indicator."
                ),
                "magnitude": "US tech recession → 10-20% revenue growth slowdown for Pakistani IT",
                "simple_explanation": "When US companies spend less on technology, they give less work to Pakistani IT firms",
            },
            {
                "variable": "SBP Foreign Currency / Repatriation Rules",
                "direction": "NEGATIVE if restrictive",
                "mechanism": (
                    "SBP regulations on foreign currency retention affect how much USD companies can hold. "
                    "Mandatory conversion rules force companies to sell USD at potentially unfavorable rates. "
                    "These regulations create forex uncertainty that makes earnings less predictable "
                    "and can discourage international clients."
                ),
                "magnitude": "Regulatory — binary policy-specific impact",
                "simple_explanation": "If the government forces IT companies to convert their dollars to rupees immediately, they lose the benefit of holding stronger currency",
            },
        ],
        "key_metrics": ["Monthly IT exports (SBP/PSEB data)", "PKR/USD spot rate", "US ISM Services PMI", "Headcount growth"],
        "regulators": ["PSEB", "SBP (FX rules)", "Ministry of IT"],
        "credible_sources": ["PSEB monthly reports", "SBP statistics", "Dawn Tech", "Bloomberg Technology"],
    },

    "Conglomerate": {
        "primary_revenue_driver": "Weighted consolidated earnings across Fertiliser (EFERT), LNG, Polymer subsidiaries",
        "business_model_plain_english": (
            "Engro Corporation is a holding company that owns stakes in multiple businesses. "
            "The biggest is Engro Fertilizers (EFERT) which makes urea. "
            "Engro also owns an LNG terminal, a polymer/PVC business, and food businesses. "
            "When you buy ENGRO stock, you're buying a piece of all these businesses together."
        ),
        "sensitivities": [
            {
                "variable": "Engro Fertilizers (EFERT) Performance",
                "direction": "POSITIVE — dominant earnings driver",
                "mechanism": (
                    "EFERT contributes 45-55% of ENGRO's consolidated earnings. "
                    "All EFERT sensitivities (urea subsidy, gas price, offtake) "
                    "flow through to ENGRO proportionally. "
                    "ENGRO trades at a holding company discount to sum-of-parts NAV — "
                    "typically 15-25% below the market value of its listed subsidiaries."
                ),
                "magnitude": "1% EFERT EPS change → ~0.5% ENGRO consolidated EPS change",
                "simple_explanation": "ENGRO's biggest business is fertiliser — what happens to EFERT mostly happens to ENGRO",
            },
            {
                "variable": "LNG Terminal Utilisation (Elengy Terminal)",
                "direction": "POSITIVE — stable income",
                "mechanism": (
                    "ENGRO owns the Elengy LNG terminal which charges regasification fees in USD "
                    "under take-or-pay contracts. This is relatively stable, predictable income "
                    "insulated from commodity price swings. Expansion of LNG import capacity "
                    "is a long-term growth driver for Pakistan's gas supply."
                ),
                "magnitude": "Stable — low volatility, USD-denominated fees",
                "simple_explanation": "ENGRO earns a fee every time LNG gas passes through its terminal — stable, dollar income",
            },
        ],
        "key_metrics": ["EFERT quarterly results", "Holding company discount to NAV", "LNG terminal utilisation", "Consolidated DPS"],
        "regulators": ["SECP", "Sector regulators per subsidiary"],
        "credible_sources": ["ENGRO investor relations", "Dawn Business", "Business Recorder"],
    },

    "Power & Utilities": {
        "primary_revenue_driver": "Capacity payments (fixed PKR) + energy payments under Power Purchase Agreements",
        "business_model_plain_english": (
            "IPPs like HUBC and KAPCO sell electricity to the government (WAPDA/DISCOs) under long-term contracts. "
            "The government guarantees them a fixed payment just for having the plant available (capacity payment), "
            "plus a variable payment for electricity actually generated. "
            "The problem: the government often doesn't pay on time — creating 'circular debt'."
        ),
        "sensitivities": [
            {
                "variable": "Circular Debt / Government Payment Delays",
                "direction": "NEGATIVE — the defining structural risk",
                "mechanism": (
                    "IPPs book revenue when they generate electricity. But DISCOs (distribution companies) "
                    "routinely fail to pay — creating growing receivables. This circular debt has reached "
                    "PKR 2.3 trillion+ in Pakistan. Even though P&L looks profitable, cash flow is impaired "
                    "because the government owes but hasn't paid. "
                    "Market applies a discount to IPP earnings quality proportional to receivable aging. "
                    "When circular debt solutions are announced, stocks re-rate sharply upward."
                ),
                "magnitude": "Every PKR 200B circular debt increase → 15-25% stock de-rating",
                "simple_explanation": "HUBC generates electricity and bills the government — but the government often delays payment, so profits on paper don't translate to actual cash",
            },
            {
                "variable": "NEPRA Tariff Determinations",
                "direction": "POSITIVE if tariff raised",
                "mechanism": (
                    "NEPRA sets the price DISCOs can charge consumers. Higher consumer tariffs "
                    "mean DISCOs collect more revenue → can pay IPPs faster → circular debt shrinks. "
                    "Tariff notifications are binary re-rating events. Under IMF pressure, "
                    "Pakistan has been forced to raise electricity tariffs — painful for consumers "
                    "but positive for IPP stocks."
                ),
                "magnitude": "Tariff notification → 5-15% stock re-rating within days",
                "simple_explanation": "When the government raises electricity bills for consumers, it can pay power companies faster",
            },
        ],
        "key_metrics": ["Circular debt total (NEPRA/MoE)", "Receivable days", "Plant load factor %", "NEPRA determination date"],
        "regulators": ["NEPRA", "PPIB", "Ministry of Energy"],
        "credible_sources": ["NEPRA website", "Dawn Business", "Business Recorder", "PPIB reports"],
    },

    "Textile": {
        "primary_revenue_driver": "Export revenue (USD) minus cotton input cost, converted at PKR/USD",
        "business_model_plain_english": (
            "Textile companies buy cotton, spin it into yarn, weave it into fabric, and sew it into garments — "
            "then export to the US, EU, and UK. They earn in dollars (good when rupee is weak) "
            "but their biggest input — cotton — is also priced internationally in dollars. "
            "The more value they add (raw yarn → finished garment), the better their margins."
        ),
        "sensitivities": [
            {
                "variable": "Global Apparel Demand (EU/US Retail)",
                "direction": "POSITIVE if demand strong",
                "mechanism": (
                    "Pakistani textile exports go primarily to EU and US retailers (H&M, Primark, Walmart). "
                    "Western consumer slowdowns directly reduce order books. EU recession → buyers defer "
                    "orders or move to cheaper sources (Bangladesh). "
                    "Monthly PBS export data is the leading indicator — two consecutive months of decline "
                    "usually precedes earnings disappointment."
                ),
                "magnitude": "10% EU apparel demand decline → 15% Pakistani textile revenue impact",
                "simple_explanation": "When Europeans and Americans buy fewer clothes, Pakistani factories get fewer orders",
            },
            {
                "variable": "PKR/USD Exchange Rate",
                "direction": "POSITIVE on depreciation — but partially offset by cotton costs",
                "mechanism": (
                    "Revenue is in USD → depreciation boosts PKR revenue. "
                    "But imported cotton is also in USD → depreciation raises input costs. "
                    "Net benefit depends on value-added ratio: high-value garment exporters (ILP) "
                    "benefit more; pure spinners less so because cotton cost offsets revenue gain."
                ),
                "magnitude": "Net 5-10% EPS uplift per 10% depreciation for integrated mills",
                "simple_explanation": "Weaker rupee helps Pakistani textiles compete on price globally, but also makes imported cotton more expensive",
            },
            {
                "variable": "DLTL / Export Rebate Schemes",
                "direction": "POSITIVE when active",
                "mechanism": (
                    "Government's Drawback of Local Taxes & Levies (DLTL) gives exporters cash back "
                    "on taxes paid in the supply chain. Worth PKR 20-40B annually to the sector. "
                    "IMF pressure to reduce 'export subsidies' risks suspension of DLTL. "
                    "Suspension is an immediate cash flow hit — sectors that depend on it see sharp selloffs."
                ),
                "magnitude": "DLTL suspension → PKR 2-5 EPS impact on large mills",
                "simple_explanation": "The government refunds certain taxes to textile exporters. When it stops, profits drop",
            },
        ],
        "key_metrics": ["Monthly PBS textile exports", "Cotton price NCDEX/international", "EU/US retail PMI", "DLTL disbursement status"],
        "regulators": ["Ministry of Commerce", "APTMA (industry body)"],
        "credible_sources": ["PBS trade data", "Dawn Business", "Business Recorder", "APTMA reports", "Cotton Outlook"],
    },

    "Pharmaceutical": {
        "primary_revenue_driver": "Drug volume × DRAP-approved Maximum Retail Price",
        "business_model_plain_english": (
            "Pharma companies (SEARL, ABOT) manufacture medicines and sell them at prices set by the government regulator DRAP. "
            "They cannot freely raise prices — DRAP must approve. They import raw ingredients (APIs) from China and India "
            "in dollars. So they're squeezed from both sides: revenues capped by regulation, costs rising with dollar."
        ),
        "sensitivities": [
            {
                "variable": "DRAP Drug Price Notifications (MRP changes)",
                "direction": "POSITIVE if MRP raised — most important variable",
                "mechanism": (
                    "DRAP controls Maximum Retail Prices. When MRP is frozen during high inflation, "
                    "real revenue declines while costs rise — margin collapse. "
                    "When DRAP approves MRP increases (even 10%), the high operating leverage means "
                    "EPS impact is amplified — a 10% price increase on existing volumes with flat costs "
                    "flows almost entirely to net profit."
                ),
                "magnitude": "10% MRP increase → 15-20% EPS uplift due to operating leverage",
                "simple_explanation": "Pharma companies can only raise medicine prices when the government allows it. When allowed, profits jump significantly",
            },
            {
                "variable": "PKR/USD (API Import Cost)",
                "direction": "NEGATIVE on depreciation — opposite to IT sector",
                "mechanism": (
                    "Active Pharmaceutical Ingredients (APIs) are imported from China/India in USD. "
                    "Rupee depreciation raises import costs in PKR while revenues remain in PKR (domestic sales). "
                    "This is the exact opposite of the IT sector: pharma is hurt by depreciation. "
                    "Cost increases cannot be immediately passed on — DRAP approval takes time."
                ),
                "magnitude": "10% PKR depreciation → 6-10% COGS increase → 4-8% EPS decline",
                "simple_explanation": "Pharma companies import raw ingredients using dollars. Weaker rupee makes those ingredients more expensive, squeezing profits",
            },
        ],
        "key_metrics": ["DRAP price notifications", "PKR/USD rate", "CPI medical sub-index", "API import costs"],
        "regulators": ["DRAP", "Ministry of National Health Services"],
        "credible_sources": ["DRAP website", "Dawn Health", "Business Recorder", "Reuters Health"],
    },

    "FMCG & Consumer": {
        "primary_revenue_driver": "Sales volume × net selling price (gross price minus trade discounts)",
        "business_model_plain_english": (
            "FMCG companies (Nestlé, Colgate) sell everyday products — food, beverages, personal care. "
            "Volume depends on whether people can afford to buy. Price depends on competition and input costs. "
            "When inflation is high, consumers switch from branded products to cheaper alternatives — "
            "hurting volumes. When input costs rise, margins compress unless prices can be raised."
        ),
        "sensitivities": [
            {
                "variable": "Real Consumer Income / CPI Inflation",
                "direction": "NEGATIVE if inflation high",
                "mechanism": (
                    "High inflation erodes real purchasing power. Consumers trade down from premium "
                    "brands to cheaper alternatives or reduce purchase frequency. "
                    "FMCG companies face a dilemma: raise prices to protect margins but lose volume, "
                    "or hold prices and see margin compression. "
                    "Pakistan's 2022-23 inflation (peaking at 38%) caused historic volume declines across FMCG."
                ),
                "magnitude": "5% real income decline → 3-8% volume decline for premium FMCG",
                "simple_explanation": "When daily items get more expensive, people buy less of branded products — hurting Nestlé's and Colgate's sales volumes",
            },
            {
                "variable": "Input Commodity Prices (Palm Oil, Sugar, Wheat, Packaging)",
                "direction": "NEGATIVE if rises",
                "mechanism": (
                    "FMCG input baskets are commodity-heavy. Palm oil (Nestlé dairy, Unity), "
                    "sugar (confectionery), wheat (biscuits), and packaging (petroleum derivatives) "
                    "are key inputs. International commodity spikes hit COGS "
                    "before price increases can be implemented — margin compression lag of 1-2 quarters."
                ),
                "magnitude": "10% input basket increase → 4-7% EBITDA margin compression",
                "simple_explanation": "When the raw materials Nestlé buys — palm oil, sugar, wheat — get more expensive, profit margins shrink",
            },
            {
                "variable": "Federal Budget / Sales Tax Changes",
                "direction": "NEGATIVE if tax increases",
                "mechanism": (
                    "Budget-time GST/FED increases on FMCG products directly reduce demand "
                    "by raising consumer prices. IMF-driven tax expansion frequently targets "
                    "FMCG sectors previously exempt or on reduced rates. "
                    "Companies absorb part of tax increase to maintain volumes → margin squeeze."
                ),
                "magnitude": "5% new FED → 2-4% volume demand decline (price elasticity)",
                "simple_explanation": "Government taxing everyday products more makes them more expensive and people buy less",
            },
        ],
        "key_metrics": ["CPI urban inflation", "Palm oil/sugar international prices", "PBS retail sales", "Volume growth quarterly"],
        "regulators": ["FBR (taxation)", "Competition Commission of Pakistan", "PSQCA"],
        "credible_sources": ["PBS inflation data", "SBP statistics", "Dawn Business", "Bloomberg Commodities"],
    },
}