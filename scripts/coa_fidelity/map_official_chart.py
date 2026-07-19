#!/usr/bin/env python3
"""
Deterministic classification of a verbatim official chart (produced by
parse_official_chart.py) onto Kontablo's universal Level-3 ontology
(core/schemas/level3_accounts.yaml).

This is a SEPARATE, reviewable step from parsing on purpose (principle #5,
determinism over stochasticity; principle #3, logic-based mapping via
deterministic scripts, never hardcoded free-text guessing). Classification
is done via longest-prefix-match against a per-jurisdiction rule table
defined in this file -- not inferred by an LLM, and not left as a silent
best-guess: any code with no matching prefix is written out with
kontablo_uuid: null and needs_review: true rather than forced onto the
nearest plausible node.

Statement-only presentation captions (cash-flow reconciliation lines,
statement-of-changes-in-equity movement lines) are NOT postable ledger
accounts and are tagged is_statement_caption: true instead of being forced
onto a Level-3 node.

Usage:
    python3 scripts/coa_fidelity/map_official_chart.py \
        --official localizations/ec/supercias_official_chart.yaml \
        --jurisdiction ec \
        --out localizations/ec/supercias_mapping.yaml
"""
import argparse
import yaml

ONTOLOGY_PATH = "core/schemas/level3_accounts.yaml"

# --- Ecuador (Supercias NIIF Plan de Cuentas) prefix -> Level-3 id rules ---
# Longest-prefix match wins. Prefixes are official CODIGO values (as strings).
# Every prefix here was verified against the parsed official chart before
# being added -- see localizations/ec/supercias_official_chart.yaml.
EC_RULES = {
    # ACTIVO CORRIENTE
    "1010101": "asset.current.cash",
    "1010102": "asset.current.bank",
    "1010103": "asset.current.bank",
    "10102": "asset.noncurrent.investments",   # current financial assets; no dedicated short-term-investment node exists yet
    "1010205": "asset.current.receivables",     # DEUDORES COMERCIALES Y OTRAS CxC NO RELACIONADOS (clientes)
    "1010206": "asset.current.other_receivables",  # CxC relacionados
    "1010207": "asset.current.receivables",     # provision cuentas incobrables (contra, nets against receivables)
    "10103": "asset.current.inventory",
    "10104": "asset.current.prepaid",
    "1010501": "asset.current.vat_input",
    "1010502": "asset.current.withholding_tax",
    "1010503": "asset.current.withholding_tax",
    # ACTIVOS NO CORRIENTES
    "10201": "asset.noncurrent.ppe",
    # 10203 ACTIVOS BIOLOGICOS: no rule -- asset.noncurrent.biological is
    # PLANNED status with no uuid yet (core/schemas/level3_accounts.yaml
    # pending_accounts); left needs_review rather than mapped to a
    # non-existent node. Real ontology gap, tracked in STATUS.yaml.
    "1020401": "asset.noncurrent.goodwill",
    "10204": "asset.noncurrent.intangibles",
    "10206": "asset.noncurrent.investments",
    "10207": "asset.noncurrent.rou_assets",
    "1020806": "asset.noncurrent.investments",
    "1020807": "asset.noncurrent.investments",
    "1020808": "asset.noncurrent.investments",
    "1020809": "asset.noncurrent.investments",
    "1020810": "asset.noncurrent.investments",
    # PASIVO CORRIENTE
    "20101": "liability.current.short_term_debt",
    "20103": "liability.current.payables",
    "20104": "liability.current.short_term_debt",
    "20105": "liability.current.accrued",
    "20106": "liability.current.short_term_debt",
    "2010701": "liability.current.tax",
    "2010702": "liability.current.tax",
    "2010703": "liability.current.payroll",
    "2010704": "liability.current.payroll",
    "2010705": "liability.current.payroll",
    "2010706": "liability.current.accrued",
    "2010707": "liability.current.accrued",
    "20108": "liability.current.payables",
    "20109": "liability.current.short_term_debt",
    "20110": "liability.current.deferred_revenue",
    "20112": "liability.current.payroll",
    "20113": "liability.current.accrued",
    "20114": "liability.current.short_term_debt",
    # PASIVO NO CORRIENTE
    "20201": "liability.noncurrent.lease",
    "20202": "liability.noncurrent.debt",
    "20203": "liability.noncurrent.debt",
    "20204": "liability.noncurrent.debt",
    "20205": "liability.noncurrent.debt",
    "20206": "liability.current.deferred_revenue",
    "20207": "liability.current.payroll",
    "20208": "liability.current.accrued",
    "2020901": "liability.current.deferred_revenue",
    "2020902": "liability.noncurrent.deferred_tax",
    "20210": "liability.noncurrent.debt",
    # PATRIMONIO
    "301": "equity.capital",
    "302": "equity.capital",
    "303": "equity.capital",
    "304": "equity.reserves",
    "305": "equity.reserves",
    "306": "equity.retained",
    "307": "equity.retained",
    # INGRESOS
    "401": "revenue.operating",
    "403": "revenue.other",
    # GASTOS
    "501": "expense.cogs",
    "50201": "expense.admin",   # GASTOS DE VENTA -- no dedicated selling-expense node; see needs_review note
    "50202": "expense.admin",   # GASTOS ADMINISTRATIVOS
    "5020120": "expense.depreciation",
    "5020121": "expense.depreciation",
    "5020220": "expense.depreciation",
    "5020221": "expense.depreciation",
    "5020222": "expense.depreciation",
    "50203": "expense.interest",
    "5020307": "expense.fx_loss",
    "603": "expense.tax",
    "705": "expense.tax",
}

# Prefixes that ARE genuine subtotal/computed rows (not postable accounts,
# not a classification gap) -- excluded from needs_review noise.
SUBTOTAL_PREFIXES = {
    "402", "600", "601", "602", "604", "605", "606", "607",
    "700", "701", "702", "703", "704", "706", "707",
    "80101", "80102",
}

# --- Mexico (SAT Anexo 24 Código Agrupador) prefix -> Level-3 id rules ---
# Longest-prefix match wins. Codes follow SAT hierarchical structure.
# Every prefix below was verified against the parsed official chart
# (localizations/mx/sat_official_chart.yaml, all 1,079 codes read verbatim)
# before being added here -- NOT against the pre-fidelity-sweep 0.1.0-draft,
# whose code numbering does not match the current (2026-01-13) SAT chart.
#
# Contra-accounts (allowances, obsolescence/impairment reserves, accumulated
# depreciation/amortization, sales/purchase returns) are deliberately left
# OUT of this table -- same convention as EC/SYSCOHADA -- because Kontablo's
# ontology has no dedicated contra-asset/contra-revenue/contra-expense node
# yet; merging them into the gross node they offset would distort gross-vs-
# net presentation. They fall through to needs_review honestly.
#
# Level-1 (3-digit) header codes are mapped directly only when every child
# subaccount shares one clear theme (e.g. 101 Caja). Where a level-1 header
# bundles heterogeneous content (e.g. 202 Cuentas por pagar a corto plazo
# mixes bank notes, general payables, accrued interest and dividends), the
# header itself is left OUT of MX_RULES so the parent_codes fallback in
# classify() correctly marks it is_aggregate=true, and only the specific
# leaf subaccounts are mapped.
MX_RULES = {
    # ACTIVO A CORTO PLAZO
    # Caja / Bancos
    "101": "asset.current.cash",
    "101.01": "asset.current.cash",
    "102": "asset.current.bank",
    "102.01": "asset.current.bank",
    "102.02": "asset.current.bank",
    # Inversiones / Otros instrumentos financieros -- no dedicated short-term
    # investment node exists; asset.noncurrent.investments is the closest fit
    # (same fallback EC uses for "activos financieros" current bucket).
    "103": "asset.noncurrent.investments",
    "103.01": "asset.noncurrent.investments",
    "103.02": "asset.noncurrent.investments",
    "103.03": "asset.noncurrent.investments",
    "104": "asset.noncurrent.investments",
    "104.01": "asset.noncurrent.investments",
    # Clientes (trade receivables)
    "105": "asset.current.receivables",
    "105.01": "asset.current.receivables",
    "105.02": "asset.current.receivables",
    "105.03": "asset.current.receivables",
    "105.04": "asset.current.receivables",
    # Cuentas y documentos por cobrar a corto plazo (incl. interest receivable)
    "106": "asset.current.receivables",
    "106.01": "asset.current.receivables",
    "106.02": "asset.current.receivables",
    "106.03": "asset.current.receivables",
    "106.04": "asset.current.receivables",
    "106.05": "asset.current.receivables",
    "106.06": "asset.current.receivables",
    "106.07": "asset.current.receivables",
    "106.08": "asset.current.receivables",
    "106.09": "asset.current.receivables",
    "106.10": "asset.current.receivables",
    # Deudores diversos (officers, shareholders, related parties, other)
    "107": "asset.current.other_receivables",
    "107.01": "asset.current.other_receivables",
    "107.02": "asset.current.other_receivables",
    "107.03": "asset.current.other_receivables",
    "107.04": "asset.current.other_receivables",
    "107.05": "asset.current.other_receivables",
    # 108 Estimación de cuentas incobrables: CONTRA-ASSET (allowance for
    # doubtful accounts). No rule -- falls through to needs_review rather
    # than being merged into asset.current.receivables. Real ontology gap.
    # Pagos anticipados (prepaid expenses)
    "109": "asset.current.prepaid",
    "109.01": "asset.current.prepaid",
    "109.02": "asset.current.prepaid",
    "109.03": "asset.current.prepaid",
    "109.04": "asset.current.prepaid",
    "109.05": "asset.current.prepaid",
    "109.06": "asset.current.prepaid",
    "109.07": "asset.current.prepaid",
    "109.08": "asset.current.prepaid",
    "109.09": "asset.current.prepaid",
    "109.10": "asset.current.prepaid",
    "109.11": "asset.current.prepaid",
    "109.12": "asset.current.prepaid",
    "109.13": "asset.current.prepaid",
    "109.14": "asset.current.prepaid",
    "109.15": "asset.current.prepaid",
    "109.16": "asset.current.prepaid",
    # 109.21 Pérdida por deterioro de pagos anticipados: CONTRA-ASSET
    # (accumulated impairment against prepaid). No rule -- needs_review.
    "109.22": "asset.current.prepaid",  # Derechos fiduciarios -- imperfect fit, no better node
    "109.23": "asset.current.prepaid",
    # Subsidio al empleo / Crédito al diésel / Otros estímulos -- credits to
    # be applied, treated as prepaid-like assets (no dedicated tax-credit node)
    "110": "asset.current.prepaid",
    "110.01": "asset.current.prepaid",
    "111": "asset.current.prepaid",
    "111.01": "asset.current.prepaid",
    "112": "asset.current.prepaid",
    "112.01": "asset.current.prepaid",
    # 113 Impuestos a favor: header is a MIXED bucket (VAT + ISR + IETU + IDE
    # + IA + employment subsidy + overpayment + other) -- left unmapped so it
    # is caught by parent_codes aggregate detection. Only the clearly-typed
    # leaves are mapped; IETU/IDE/IA (distinct, mostly-repealed tax regimes)
    # and the generic "other" leaves are left needs_review rather than forced
    # into vat_input.
    "113.01": "asset.current.vat_input",       # IVA a favor
    "113.02": "asset.current.withholding_tax",  # ISR a favor
    "113.06": "asset.current.prepaid",          # Subsidio al empleo
    # Pagos provisionales (provisional/advance ISR payments)
    "114": "asset.current.prepaid",
    "114.01": "asset.current.prepaid",
    # Inventario
    "115": "asset.current.inventory",
    "115.01": "asset.current.inventory",
    "115.02": "asset.current.inventory",
    "115.03": "asset.current.inventory",
    "115.04": "asset.current.inventory",
    "115.05": "asset.current.inventory",
    "115.06": "asset.current.inventory",
    "115.07": "asset.current.inventory",
    # 116 Estimación de inventarios obsoletos y de lento movimiento:
    # CONTRA-ASSET (inventory obsolescence allowance). No rule -- needs_review.
    # Obras en proceso de inmuebles (real-estate WIP, inventory-like)
    "117": "asset.current.inventory",
    "117.01": "asset.current.inventory",
    # 118 Impuestos acreditables PAGADOS -- already paid and creditable now.
    # Genuine input-tax credit (VAT and, by extension, IEPS treated the same
    # functional way: an already-paid, already-creditable consumption tax).
    "118": "asset.current.vat_input",
    "118.01": "asset.current.vat_input",
    "118.02": "asset.current.vat_input",
    "118.03": "asset.current.vat_input",
    "118.04": "asset.current.vat_input",
    # 119 Impuestos acreditables POR PAGAR: NOT yet creditable -- Mexican VAT
    # operates on a cash-flow basis (LIVA Art. 1-B/5), so tax invoiced but
    # not yet paid to the counterparty is not yet an input-tax credit. This
    # is a distinct concept from 118 and does not fit asset.current.vat_input
    # (which represents tax already creditable). No rule -- needs_review.
    # Anticipo a proveedores (advances to suppliers)
    "120": "asset.current.prepaid",
    "120.01": "asset.current.prepaid",
    "120.02": "asset.current.prepaid",
    "120.03": "asset.current.prepaid",
    "120.04": "asset.current.prepaid",
    # Otros activos a corto plazo
    "121": "asset.current.other_receivables",
    "121.01": "asset.current.other_receivables",

    # ACTIVO A LARGO PLAZO
    # PPE categories (land, buildings, machinery, vehicles, furniture,
    # computing/communication equipment, railways, vessels, planes, tooling,
    # renewable-energy equipment, other fixed assets, WIP, improvements)
    "151": "asset.noncurrent.ppe",
    "151.01": "asset.noncurrent.ppe",
    "152": "asset.noncurrent.ppe",
    "152.01": "asset.noncurrent.ppe",
    "153": "asset.noncurrent.ppe",
    "153.01": "asset.noncurrent.ppe",
    "154": "asset.noncurrent.ppe",
    "154.01": "asset.noncurrent.ppe",
    "155": "asset.noncurrent.ppe",
    "155.01": "asset.noncurrent.ppe",
    "156": "asset.noncurrent.ppe",
    "156.01": "asset.noncurrent.ppe",
    "157": "asset.noncurrent.ppe",
    "157.01": "asset.noncurrent.ppe",
    # 158 Activos biológicos, vegetales y semovientes: NO rule --
    # asset.noncurrent.biological is PLANNED status with no uuid yet (same
    # ontology gap EC hit at 10203) -- needs_review, not folded into ppe.
    "159": "asset.noncurrent.ppe",
    "159.01": "asset.noncurrent.ppe",
    "160": "asset.noncurrent.ppe",
    "160.01": "asset.noncurrent.ppe",
    "161": "asset.noncurrent.ppe",
    "161.01": "asset.noncurrent.ppe",
    "162": "asset.noncurrent.ppe",
    "162.01": "asset.noncurrent.ppe",
    "163": "asset.noncurrent.ppe",
    "163.01": "asset.noncurrent.ppe",
    "164": "asset.noncurrent.ppe",
    "164.01": "asset.noncurrent.ppe",
    "165": "asset.noncurrent.ppe",
    "165.01": "asset.noncurrent.ppe",
    "166": "asset.noncurrent.ppe",
    "166.01": "asset.noncurrent.ppe",
    "167": "asset.noncurrent.ppe",
    "167.01": "asset.noncurrent.ppe",
    "168": "asset.noncurrent.ppe",
    "168.01": "asset.noncurrent.ppe",
    "169": "asset.noncurrent.ppe",
    "169.01": "asset.noncurrent.ppe",
    "170": "asset.noncurrent.ppe",
    "170.01": "asset.noncurrent.ppe",
    # 171 Depreciación acumulada de activos fijos: CONTRA-ASSET. No rule.
    # 172 Pérdida por deterioro acumulado de activos fijos: CONTRA-ASSET. No rule.
    # 173-175, 177, 181, 182 (Gastos diferidos / pre-operativos / regalías /
    # instalación / otros activos diferidos): legacy Mexican-GAAP deferred-
    # charge concepts with no clean IFRS-anchored Kontablo equivalent --
    # left needs_review as an honest gap rather than guessed.
    "176": "asset.noncurrent.intangibles",  # Activos intangibles
    "176.01": "asset.noncurrent.intangibles",
    "178": "asset.noncurrent.intangibles",  # Investigación y desarrollo de mercado (capitalized R&D)
    "178.01": "asset.noncurrent.intangibles",
    "179": "asset.noncurrent.intangibles",  # Marcas y patentes
    "179.01": "asset.noncurrent.intangibles",
    "180": "asset.noncurrent.goodwill",     # Crédito mercantil
    "180.01": "asset.noncurrent.goodwill",
    # 183 Amortización acumulada de activos diferidos: CONTRA-ASSET. No rule.
    # 184 Depósitos en garantía: no clean node (long-term refundable deposit,
    # not investments, not prepaid) -- needs_review.
    # 185 Impuestos diferidos (deferred tax ASSET): no dedicated deferred-tax
    # -asset node exists (only liability.noncurrent.deferred_tax does) --
    # mapping an asset here onto the liability node would be wrong. needs_review.
    # 186 Cuentas y documentos por cobrar a largo plazo: no noncurrent
    # receivables node exists; forcing into asset.current.receivables would
    # misstate current vs noncurrent. needs_review.
    # 187 Participación de los trabajadores en las utilidades diferidas
    # (deferred PTU, asset side): no dedicated node -- needs_review.
    "188": "asset.noncurrent.investments",  # Inversiones permanentes en acciones (subsidiaries/associates)
    "188.01": "asset.noncurrent.investments",
    "188.02": "asset.noncurrent.investments",
    "188.03": "asset.noncurrent.investments",
    # 189 Estimación por deterioro de inversiones permanentes en acciones:
    # CONTRA-ASSET. No rule.
    "190": "asset.noncurrent.investments",  # Otros instrumentos financieros (long-term)
    "190.01": "asset.noncurrent.investments",
    # 191 Otros activos a largo plazo: too generic to force -- needs_review.

    # PASIVO A CORTO PLAZO
    "201": "liability.current.payables",  # Proveedores (trade payables)
    "201.01": "liability.current.payables",
    "201.02": "liability.current.payables",
    "201.03": "liability.current.payables",
    "201.04": "liability.current.payables",
    # 202 Cuentas por pagar a corto plazo: MIXED header (bank notes, general
    # payables, accrued interest, dividends) -- left unmapped so parent_codes
    # marks it is_aggregate; leaves classified individually below.
    "202.01": "liability.current.short_term_debt",  # Documentos por pagar bancario y financiero nacional
    "202.02": "liability.current.short_term_debt",  # ...extranjero
    "202.03": "liability.current.payables",         # Documentos y cuentas por pagar nacional
    "202.04": "liability.current.payables",         # ...extranjero
    "202.05": "liability.current.payables",         # ...nacional parte relacionada
    "202.06": "liability.current.payables",         # ...extranjero parte relacionada
    "202.07": "liability.current.accrued",          # Intereses por pagar nacional
    "202.08": "liability.current.accrued",          # ...extranjero
    "202.09": "liability.current.accrued",          # ...nacional parte relacionada
    "202.10": "liability.current.accrued",          # ...extranjero parte relacionada
    "202.11": "liability.current.accrued",          # Dividendo por pagar nacional
    "202.12": "liability.current.accrued",          # ...extranjero
    # 203 Cobros anticipados a corto plazo: every child is "cobrado por
    # anticipado" (collected in advance) -- this is deferred revenue, not
    # an accrued liability. Header is single-themed, mapped directly.
    "203": "liability.current.deferred_revenue",
    "203.01": "liability.current.deferred_revenue",
    "203.02": "liability.current.deferred_revenue",
    "203.03": "liability.current.deferred_revenue",
    "203.04": "liability.current.deferred_revenue",
    "203.05": "liability.current.deferred_revenue",
    "203.06": "liability.current.deferred_revenue",
    "203.07": "liability.current.deferred_revenue",
    "203.08": "liability.current.deferred_revenue",
    "203.09": "liability.current.deferred_revenue",
    "203.10": "liability.current.deferred_revenue",
    "203.11": "liability.current.deferred_revenue",
    "203.12": "liability.current.deferred_revenue",
    "203.13": "liability.current.deferred_revenue",
    "203.14": "liability.current.deferred_revenue",
    "203.15": "liability.current.deferred_revenue",
    "203.16": "liability.current.deferred_revenue",
    "203.17": "liability.current.deferred_revenue",
    "203.18": "liability.current.deferred_revenue",
    # 204 Instrumentos financieros a corto plazo: generic short-term
    # financial-instrument liability, no clean node -- needs_review.
    # 205 Acreedores diversos a corto plazo (miscellaneous creditors:
    # shareholders, related parties, other) -- closest fit is payables.
    "205": "liability.current.payables",
    "205.01": "liability.current.payables",
    "205.02": "liability.current.payables",
    "205.03": "liability.current.payables",
    "205.04": "liability.current.payables",
    "205.05": "liability.current.payables",
    "205.06": "liability.current.payables",
    # 206 Anticipo de cliente (customer advances): deferred revenue.
    "206": "liability.current.deferred_revenue",
    "206.01": "liability.current.deferred_revenue",
    "206.02": "liability.current.deferred_revenue",
    "206.03": "liability.current.deferred_revenue",
    "206.04": "liability.current.deferred_revenue",
    "206.05": "liability.current.deferred_revenue",
    # 207 Impuestos trasladados (VAT/IEPS charged to customers, output tax)
    "207": "liability.current.vat_output",
    "207.01": "liability.current.vat_output",  # IVA trasladado
    "207.02": "liability.current.vat_output",  # IEPS trasladado
    # 208 Impuestos trasladados COBRADOS: output tax charged AND collected --
    # a genuine payable to the tax authority.
    "208": "liability.current.vat_output",
    "208.01": "liability.current.vat_output",
    "208.02": "liability.current.vat_output",
    # 209 Impuestos trasladados NO cobrados: charged but not yet collected --
    # under cash-basis VAT this is not yet owed to the tax authority (mirror
    # of the 119 nuance on the asset side). No rule -- needs_review.
    # 210 Provisión de sueldos y salarios por pagar (payroll accrual: salary,
    # vacation, aguinaldo, savings fund, etc.)
    "210": "liability.current.payroll",
    "210.01": "liability.current.payroll",
    "210.02": "liability.current.payroll",
    "210.03": "liability.current.payroll",
    "210.04": "liability.current.payroll",
    "210.05": "liability.current.payroll",
    "210.06": "liability.current.payroll",
    "210.07": "liability.current.payroll",
    # 211 Provisión de contribuciones de seguridad social por pagar (IMSS,
    # SAR, INFONAVIT) -- employer social-security/payroll obligation, NOT a
    # withheld tax.
    "211": "liability.current.payroll",
    "211.01": "liability.current.payroll",
    "211.02": "liability.current.payroll",
    "211.03": "liability.current.payroll",
    # 212 Provisión de impuesto estatal sobre nómina por pagar (state payroll
    # tax provision) -- payroll-related.
    "212": "liability.current.payroll",
    "212.01": "liability.current.payroll",
    # 213 Impuestos y derechos por pagar: MIXED header (VAT, IEPS, ISR, state
    # payroll tax, state/municipal tax, fees, other) -- left unmapped;
    # leaves classified individually. "Derechos por pagar" (government
    # fees/duties) is a distinct concept from tax and is left needs_review.
    "213.01": "liability.current.vat_output",  # IVA por pagar
    "213.02": "liability.current.vat_output",  # IEPS por pagar
    "213.03": "liability.current.tax",         # ISR por pagar
    "213.04": "liability.current.payroll",     # Impuesto estatal sobre nómina por pagar
    "213.05": "liability.current.tax",         # Impuesto estatal y municipal por pagar
    "213.07": "liability.current.tax",         # Otros impuestos por pagar
    # 214 Dividendos por pagar: no dedicated node, accrued is closest fit.
    "214": "liability.current.accrued",
    "214.01": "liability.current.accrued",
    # 215 PTU por pagar (statutory employee profit-sharing payable) --
    # employee-benefit obligation, payroll-related.
    "215": "liability.current.payroll",
    "215.01": "liability.current.payroll",
    "215.02": "liability.current.payroll",
    "215.03": "liability.current.payroll",
    # 216 Impuestos retenidos (ISR/IVA/IMSS withholdings payable to the
    # authorities) -- genuine withholding-tax payable.
    "216": "liability.current.tax",
    "216.01": "liability.current.tax",
    "216.02": "liability.current.tax",
    "216.03": "liability.current.tax",
    "216.04": "liability.current.tax",
    "216.05": "liability.current.tax",
    "216.06": "liability.current.tax",
    "216.07": "liability.current.tax",
    "216.08": "liability.current.tax",
    "216.09": "liability.current.tax",
    "216.10": "liability.current.tax",
    "216.11": "liability.current.tax",
    "216.12": "liability.current.tax",
    # 217 Pagos realizados por cuenta de terceros: agency/pass-through
    # liability, no dedicated node -- needs_review.
    # 218 Otros pasivos a corto plazo: too generic to force -- needs_review.

    # PASIVO A LARGO PLAZO
    # 251 Acreedores diversos a largo plazo: no dedicated long-term
    # miscellaneous-payable node; liability.noncurrent.debt is closest.
    "251": "liability.noncurrent.debt",
    "251.01": "liability.noncurrent.debt",
    "251.02": "liability.noncurrent.debt",
    "251.03": "liability.noncurrent.debt",
    "251.04": "liability.noncurrent.debt",
    "251.05": "liability.noncurrent.debt",
    "251.06": "liability.noncurrent.debt",
    # 252 Cuentas por pagar a largo plazo: MIXED header -- left unmapped;
    # leaves classified individually. Long-term dividends payable (252.15/16)
    # is an unusual fit for "debt" and is left needs_review rather than forced.
    "252.01": "liability.noncurrent.debt",  # Documentos bancarios y financieros nacional
    "252.02": "liability.noncurrent.debt",  # ...extranjero
    "252.03": "liability.noncurrent.debt",  # Documentos y cuentas por pagar nacional
    "252.04": "liability.noncurrent.debt",  # ...extranjero
    "252.05": "liability.noncurrent.debt",  # ...nacional parte relacionada
    "252.06": "liability.noncurrent.debt",  # ...extranjero parte relacionada
    "252.07": "liability.noncurrent.debt",  # Hipotecas por pagar nacional
    "252.08": "liability.noncurrent.debt",  # ...extranjero
    "252.09": "liability.noncurrent.debt",  # ...nacional parte relacionada
    "252.10": "liability.noncurrent.debt",  # ...extranjero parte relacionada
    "252.11": "liability.noncurrent.debt",  # Intereses por pagar a largo plazo nacional
    "252.12": "liability.noncurrent.debt",  # ...extranjero
    "252.13": "liability.noncurrent.debt",  # ...nacional parte relacionada
    "252.14": "liability.noncurrent.debt",  # ...extranjero parte relacionada
    "252.17": "liability.noncurrent.debt",  # Otras cuentas y documentos por pagar a largo plazo
    # 253 Cobros anticipados a largo plazo: same "deferred revenue" theme as
    # 203, but only a CURRENT deferred_revenue node exists in the ontology --
    # forcing a long-term balance into it would misstate current vs
    # noncurrent. Left needs_review as an honest gap.
    # 254 Instrumentos financieros a largo plazo: needs_review (same
    # ambiguity as 204).
    # 255 Pasivos por beneficios a los empleados a largo plazo (long-term
    # employee benefits, e.g. pension obligations): no dedicated long-term
    # employee-benefit node; liability.current.payroll is CURRENT only and
    # would misstate current vs noncurrent. needs_review.
    # 256 Otros pasivos a largo plazo: too generic -- needs_review.
    # 257 Participación de los trabajadores en las utilidades diferida
    # (deferred PTU, long-term): needs_review.
    # 258 Obligaciones contraídas de fideicomisos: needs_review.
    "259": "liability.noncurrent.deferred_tax",  # Impuestos diferidos (deferred tax liability)
    "259.01": "liability.noncurrent.deferred_tax",
    "259.02": "liability.noncurrent.deferred_tax",
    "259.03": "liability.noncurrent.deferred_tax",
    # 260 Pasivos diferidos: too generic (distinct from the specific
    # deferred-tax node above) -- needs_review.

    # CAPITAL CONTABLE (Equity)
    "301": "equity.capital",  # Capital social
    "301.01": "equity.capital",
    "301.02": "equity.capital",
    "301.03": "equity.capital",
    "301.04": "equity.capital",
    "301.05": "equity.capital",
    "302.01": "equity.capital",   # Patrimonio
    "302.02": "equity.capital",   # Aportación patrimonial
    "302.03": "equity.retained",  # Déficit o remanente del ejercicio -- current-period result, not capital
    "303": "equity.reserves",     # Reserva legal
    "303.01": "equity.reserves",
    "304": "equity.retained",     # Resultado de ejercicios anteriores (prior years' retained earnings)
    "304.01": "equity.retained",
    "304.02": "equity.retained",
    "304.03": "equity.retained",
    "304.04": "equity.retained",
    "305": "equity.retained",     # Resultado del ejercicio (current period result)
    "305.01": "equity.retained",
    "305.02": "equity.retained",
    "305.03": "equity.retained",
    "306": "equity.reserves",     # Otras cuentas de capital (generic catch-all)
    "306.01": "equity.reserves",

    # INGRESOS (Revenue)
    "401": "revenue.operating",
    "401.01": "revenue.operating",
    "401.02": "revenue.operating",
    "401.03": "revenue.operating",
    "401.04": "revenue.operating",
    "401.05": "revenue.operating",
    "401.06": "revenue.operating",
    "401.07": "revenue.operating",
    "401.08": "revenue.operating",
    "401.09": "revenue.operating",
    "401.10": "revenue.operating",
    "401.11": "revenue.operating",
    "401.12": "revenue.operating",
    "401.13": "revenue.operating",
    "401.14": "revenue.operating",
    "401.15": "revenue.operating",
    "401.16": "revenue.operating",
    "401.17": "revenue.operating",
    "401.18": "revenue.operating",
    "401.19": "revenue.operating",
    "401.20": "revenue.operating",
    "401.21": "revenue.operating",
    "401.22": "revenue.operating",
    "401.23": "revenue.operating",
    "401.24": "revenue.operating",
    "401.25": "revenue.operating",
    "401.26": "revenue.operating",
    "401.27": "revenue.operating",
    "401.28": "revenue.operating",
    "401.29": "revenue.operating",
    "401.30": "revenue.operating",
    "401.31": "revenue.operating",
    "401.32": "revenue.operating",
    "401.33": "revenue.operating",
    "401.34": "revenue.operating",
    "401.35": "revenue.operating",
    "401.36": "revenue.operating",
    "401.37": "revenue.operating",
    "401.38": "revenue.operating",
    "401.39": "revenue.operating",
    "401.40": "revenue.operating",
    "401.41": "revenue.operating",
    # 402 Devoluciones, descuentos o bonificaciones sobre ingresos:
    # CONTRA-REVENUE (sales returns/discounts). No rule -- needs_review,
    # same convention as the contra-asset accounts above.
    "403": "revenue.other",
    "403.01": "revenue.other",
    "403.02": "revenue.other",
    "403.03": "revenue.other",
    "403.04": "revenue.other",
    "403.05": "revenue.other",

    # COSTOS (Cost of Goods Sold)
    "501": "expense.cogs",  # Costo de venta y/o servicio
    "501.01": "expense.cogs",
    "501.02": "expense.cogs",
    "501.03": "expense.cogs",
    "501.04": "expense.cogs",
    "501.05": "expense.cogs",
    "501.06": "expense.cogs",
    "501.07": "expense.cogs",
    "501.08": "expense.cogs",
    "502": "expense.cogs",  # Compras
    "502.01": "expense.cogs",
    "502.02": "expense.cogs",
    "502.03": "expense.cogs",
    "502.04": "expense.cogs",
    # 503 Devoluciones, descuentos o bonificaciones sobre compras:
    # CONTRA-EXPENSE (purchase returns/discounts). No rule -- needs_review,
    # same contra-account convention as above (not merged into expense.cogs).
    "504": "expense.cogs",       # Otras cuentas de costos (header + overhead leaves)
    "504.01": "expense.cogs",    # Gastos indirectos de fabricación
    "504.02": "expense.cogs",
    "504.03": "expense.cogs",
    "504.04": "expense.cogs",    # Otras cuentas de costos incurridos
    "504.05": "expense.cogs",
    "504.06": "expense.cogs",
    "504.07": "expense.depreciation",  # Depreciación de edificios (production PPE)
    "504.08": "expense.depreciation",
    "504.09": "expense.depreciation",
    "504.10": "expense.depreciation",
    "504.11": "expense.depreciation",
    "504.12": "expense.depreciation",
    "504.13": "expense.depreciation",
    "504.14": "expense.depreciation",
    "504.15": "expense.depreciation",
    "504.16": "expense.depreciation",
    "504.17": "expense.depreciation",
    "504.18": "expense.depreciation",
    "504.19": "expense.depreciation",
    "504.20": "expense.depreciation",
    "504.21": "expense.depreciation",
    "504.22": "expense.depreciation",
    "504.23": "expense.depreciation",
    "504.24": "expense.depreciation",
    "504.25": "expense.cogs",    # Otras cuentas de costos
    # 505 Costo de activo fijo (gain/loss basis on PPE disposal): not an
    # operating cost of sale; no dedicated disposal-loss node -- needs_review.

    # GASTOS (Operating Expenses)
    # 601 Gastos generales / 602 Gastos de venta: broad payroll+admin-style
    # expense lists. No dedicated payroll-expense or selling-expense node
    # exists in the ontology (only balance-sheet liability.current.payroll
    # does) -- expense.admin is the closest available fit, consistent with
    # EC's "no dedicated selling-expense node" precedent.
    "601": "expense.admin",
    "601.01": "expense.admin", "601.02": "expense.admin", "601.03": "expense.admin",
    "601.04": "expense.admin", "601.05": "expense.admin", "601.06": "expense.admin",
    "601.07": "expense.admin", "601.08": "expense.admin", "601.09": "expense.admin",
    "601.10": "expense.admin", "601.11": "expense.admin", "601.12": "expense.admin",
    "601.13": "expense.admin", "601.14": "expense.admin", "601.15": "expense.admin",
    "601.16": "expense.admin", "601.17": "expense.admin", "601.18": "expense.admin",
    "601.19": "expense.admin", "601.20": "expense.admin", "601.21": "expense.admin",
    "601.22": "expense.admin", "601.23": "expense.admin", "601.24": "expense.admin",
    "601.25": "expense.admin", "601.26": "expense.admin", "601.27": "expense.admin",
    "601.28": "expense.admin", "601.29": "expense.admin", "601.30": "expense.admin",
    "601.31": "expense.admin", "601.32": "expense.admin", "601.33": "expense.admin",
    "601.34": "expense.admin", "601.35": "expense.admin", "601.36": "expense.admin",
    "601.37": "expense.admin", "601.38": "expense.admin", "601.39": "expense.admin",
    "601.40": "expense.admin", "601.41": "expense.admin", "601.42": "expense.admin",
    "601.43": "expense.admin", "601.44": "expense.admin", "601.45": "expense.admin",
    "601.46": "expense.admin", "601.47": "expense.admin", "601.48": "expense.admin",
    "601.49": "expense.admin", "601.50": "expense.admin", "601.51": "expense.admin",
    "601.52": "expense.admin", "601.53": "expense.admin", "601.54": "expense.admin",
    "601.55": "expense.admin", "601.56": "expense.admin", "601.57": "expense.admin",
    "601.58": "expense.admin", "601.59": "expense.admin", "601.60": "expense.admin",
    "601.61": "expense.admin", "601.62": "expense.admin", "601.63": "expense.admin",
    "601.64": "expense.admin", "601.65": "expense.admin", "601.66": "expense.admin",
    "601.67": "expense.admin", "601.68": "expense.admin", "601.69": "expense.admin",
    "601.70": "expense.admin", "601.71": "expense.admin", "601.72": "expense.admin",
    "601.73": "expense.admin", "601.74": "expense.admin", "601.75": "expense.admin",
    "601.76": "expense.admin", "601.77": "expense.admin", "601.78": "expense.admin",
    "601.79": "expense.admin", "601.80": "expense.admin", "601.81": "expense.admin",
    "601.82": "expense.admin", "601.83": "expense.admin", "601.84": "expense.admin",
    "602": "expense.admin",
    "602.01": "expense.admin", "602.02": "expense.admin", "602.03": "expense.admin",
    "602.04": "expense.admin", "602.05": "expense.admin", "602.06": "expense.admin",
    "602.07": "expense.admin", "602.08": "expense.admin", "602.09": "expense.admin",
    "602.10": "expense.admin", "602.11": "expense.admin", "602.12": "expense.admin",
    "602.13": "expense.admin", "602.14": "expense.admin", "602.15": "expense.admin",
    "602.16": "expense.admin", "602.17": "expense.admin", "602.18": "expense.admin",
    "602.19": "expense.admin", "602.20": "expense.admin", "602.21": "expense.admin",
    "602.22": "expense.admin", "602.23": "expense.admin", "602.24": "expense.admin",
    "602.25": "expense.admin", "602.26": "expense.admin", "602.27": "expense.admin",
    "602.28": "expense.admin", "602.29": "expense.admin", "602.30": "expense.admin",
    "602.31": "expense.admin", "602.32": "expense.admin", "602.33": "expense.admin",
    "602.34": "expense.admin", "602.35": "expense.admin", "602.36": "expense.admin",
    "602.37": "expense.admin", "602.38": "expense.admin", "602.39": "expense.admin",
    "602.40": "expense.admin", "602.41": "expense.admin", "602.42": "expense.admin",
    "602.43": "expense.admin", "602.44": "expense.admin", "602.45": "expense.admin",
    "602.46": "expense.admin", "602.47": "expense.admin", "602.48": "expense.admin",
    "602.49": "expense.admin", "602.50": "expense.admin", "602.51": "expense.admin",
    "602.52": "expense.admin", "602.53": "expense.admin", "602.54": "expense.admin",
    "602.55": "expense.admin", "602.56": "expense.admin", "602.57": "expense.admin",
    "602.58": "expense.admin", "602.59": "expense.admin", "602.60": "expense.admin",
    "602.61": "expense.admin", "602.62": "expense.admin", "602.63": "expense.admin",
    "602.64": "expense.admin", "602.65": "expense.admin", "602.66": "expense.admin",
    "602.67": "expense.admin", "602.68": "expense.admin", "602.69": "expense.admin",
    "602.70": "expense.admin", "602.71": "expense.admin", "602.72": "expense.admin",
    "602.73": "expense.admin", "602.74": "expense.admin", "602.75": "expense.admin",
    "602.76": "expense.admin", "602.77": "expense.admin", "602.78": "expense.admin",
    "602.79": "expense.admin", "602.80": "expense.admin", "602.81": "expense.admin",
    "602.82": "expense.admin", "602.83": "expense.admin", "602.84": "expense.admin",
    # 603 Gastos de administración: genuine administrative expenses (payroll,
    # fees, rent, utilities) -- same structure as 601/602, NOT a tax account.
    "603": "expense.admin",
    "603.01": "expense.admin", "603.02": "expense.admin", "603.03": "expense.admin",
    "603.04": "expense.admin", "603.05": "expense.admin", "603.06": "expense.admin",
    "603.07": "expense.admin", "603.08": "expense.admin", "603.09": "expense.admin",
    "603.10": "expense.admin", "603.11": "expense.admin", "603.12": "expense.admin",
    "603.13": "expense.admin", "603.14": "expense.admin", "603.15": "expense.admin",
    "603.16": "expense.admin", "603.17": "expense.admin", "603.18": "expense.admin",
    "603.19": "expense.admin", "603.20": "expense.admin", "603.21": "expense.admin",
    "603.22": "expense.admin", "603.23": "expense.admin", "603.24": "expense.admin",
    "603.25": "expense.admin", "603.26": "expense.admin", "603.27": "expense.admin",
    "603.28": "expense.admin", "603.29": "expense.admin", "603.30": "expense.admin",
    "603.31": "expense.admin", "603.32": "expense.admin", "603.33": "expense.admin",
    "603.34": "expense.admin", "603.35": "expense.admin", "603.36": "expense.admin",
    "603.37": "expense.admin", "603.38": "expense.admin", "603.39": "expense.admin",
    "603.40": "expense.admin", "603.41": "expense.admin", "603.42": "expense.admin",
    "603.43": "expense.admin", "603.44": "expense.admin", "603.45": "expense.admin",
    "603.46": "expense.admin", "603.47": "expense.admin", "603.48": "expense.admin",
    "603.49": "expense.admin", "603.50": "expense.admin", "603.51": "expense.admin",
    "603.52": "expense.admin", "603.53": "expense.admin", "603.54": "expense.admin",
    "603.55": "expense.admin", "603.56": "expense.admin", "603.57": "expense.admin",
    "603.58": "expense.admin", "603.59": "expense.admin", "603.60": "expense.admin",
    "603.61": "expense.admin", "603.62": "expense.admin", "603.63": "expense.admin",
    "603.64": "expense.admin", "603.65": "expense.admin", "603.66": "expense.admin",
    "603.67": "expense.admin", "603.68": "expense.admin", "603.69": "expense.admin",
    "603.70": "expense.admin", "603.71": "expense.admin", "603.72": "expense.admin",
    "603.73": "expense.admin", "603.74": "expense.admin", "603.75": "expense.admin",
    "603.76": "expense.admin", "603.77": "expense.admin", "603.78": "expense.admin",
    "603.79": "expense.admin", "603.80": "expense.admin", "603.81": "expense.admin",
    "603.82": "expense.admin",
    # 604 Gastos de fabricación: same payroll/admin-style list but tagged for
    # the manufacturing/factory function -- factory overhead is a cost of
    # production, so this belongs in COGS, not admin.
    "604": "expense.cogs",
    "604.01": "expense.cogs", "604.02": "expense.cogs", "604.03": "expense.cogs",
    "604.04": "expense.cogs", "604.05": "expense.cogs", "604.06": "expense.cogs",
    "604.07": "expense.cogs", "604.08": "expense.cogs", "604.09": "expense.cogs",
    "604.10": "expense.cogs", "604.11": "expense.cogs", "604.12": "expense.cogs",
    "604.13": "expense.cogs", "604.14": "expense.cogs", "604.15": "expense.cogs",
    "604.16": "expense.cogs", "604.17": "expense.cogs", "604.18": "expense.cogs",
    "604.19": "expense.cogs", "604.20": "expense.cogs", "604.21": "expense.cogs",
    "604.22": "expense.cogs", "604.23": "expense.cogs", "604.24": "expense.cogs",
    "604.25": "expense.cogs", "604.26": "expense.cogs", "604.27": "expense.cogs",
    "604.28": "expense.cogs", "604.29": "expense.cogs", "604.30": "expense.cogs",
    "604.31": "expense.cogs", "604.32": "expense.cogs", "604.33": "expense.cogs",
    "604.34": "expense.cogs", "604.35": "expense.cogs", "604.36": "expense.cogs",
    "604.37": "expense.cogs", "604.38": "expense.cogs", "604.39": "expense.cogs",
    "604.40": "expense.cogs", "604.41": "expense.cogs", "604.42": "expense.cogs",
    "604.43": "expense.cogs", "604.44": "expense.cogs", "604.45": "expense.cogs",
    "604.46": "expense.cogs", "604.47": "expense.cogs", "604.48": "expense.cogs",
    "604.49": "expense.cogs", "604.50": "expense.cogs", "604.51": "expense.cogs",
    "604.52": "expense.cogs", "604.53": "expense.cogs", "604.54": "expense.cogs",
    "604.55": "expense.cogs", "604.56": "expense.cogs", "604.57": "expense.cogs",
    "604.58": "expense.cogs", "604.59": "expense.cogs", "604.60": "expense.cogs",
    "604.61": "expense.cogs", "604.62": "expense.cogs", "604.63": "expense.cogs",
    "604.64": "expense.cogs", "604.65": "expense.cogs", "604.66": "expense.cogs",
    "604.67": "expense.cogs", "604.68": "expense.cogs", "604.69": "expense.cogs",
    "604.70": "expense.cogs", "604.71": "expense.cogs", "604.72": "expense.cogs",
    "604.73": "expense.cogs", "604.74": "expense.cogs", "604.75": "expense.cogs",
    "604.76": "expense.cogs", "604.77": "expense.cogs", "604.78": "expense.cogs",
    "604.79": "expense.cogs", "604.80": "expense.cogs", "604.81": "expense.cogs",
    "604.82": "expense.cogs",
    # 605 Mano de obra directa (direct labor): clearly a cost of production.
    "605": "expense.cogs",
    "605.01": "expense.cogs", "605.02": "expense.cogs", "605.03": "expense.cogs",
    "605.04": "expense.cogs", "605.05": "expense.cogs", "605.06": "expense.cogs",
    "605.07": "expense.cogs", "605.08": "expense.cogs", "605.09": "expense.cogs",
    "605.10": "expense.cogs", "605.11": "expense.cogs", "605.12": "expense.cogs",
    "605.13": "expense.cogs", "605.14": "expense.cogs", "605.15": "expense.cogs",
    "605.16": "expense.cogs", "605.17": "expense.cogs", "605.18": "expense.cogs",
    "605.19": "expense.cogs", "605.20": "expense.cogs", "605.21": "expense.cogs",
    "605.22": "expense.cogs", "605.23": "expense.cogs", "605.24": "expense.cogs",
    "605.25": "expense.cogs", "605.26": "expense.cogs", "605.27": "expense.cogs",
    "605.28": "expense.cogs", "605.29": "expense.cogs", "605.30": "expense.cogs",
    "605.31": "expense.cogs",
    # 606 Facilidades administrativas fiscales: simplified-regime tax
    # deduction facility -- Mexico-specific tax-technical concept, no clean
    # node (NOT depreciation, despite the old draft's stale mapping).
    # needs_review.
    # 607 Participación de los trabajadores en las utilidades (PTU expense,
    # P&L side): employee profit-sharing, unrelated to interest expense
    # (despite the old draft's stale mapping) -- no dedicated node.
    # needs_review.
    # 608/609 Participación en resultados de subsidiarias/asociadas
    # (equity-method investment income/loss): no dedicated node -- needs_review.
    # 610 Participación de los trabajadores en las utilidades diferida
    # (deferred PTU expense): needs_review.
    "611": "expense.tax",  # Impuesto Sobre la renta (ISR expense)
    "611.01": "expense.tax",
    "611.02": "expense.tax",
    # 612 Gastos no deducibles para CUFIN: tax-technical adjustment concept,
    # no clean node -- needs_review.
    "613": "expense.depreciation",  # Depreciación contable (book depreciation expense)
    "613.01": "expense.depreciation",
    "613.02": "expense.depreciation",
    "613.03": "expense.depreciation",
    "613.04": "expense.depreciation",
    "613.05": "expense.depreciation",
    "613.06": "expense.depreciation",
    "613.07": "expense.depreciation",
    "613.08": "expense.depreciation",
    "613.09": "expense.depreciation",
    "613.10": "expense.depreciation",
    "613.11": "expense.depreciation",
    "613.12": "expense.depreciation",
    "613.13": "expense.depreciation",
    "613.14": "expense.depreciation",
    "613.15": "expense.depreciation",
    "613.16": "expense.depreciation",
    "613.17": "expense.depreciation",
    "613.18": "expense.depreciation",
    "614": "expense.depreciation",  # Amortización contable -- bucketed with depreciation, no dedicated node
    "614.01": "expense.depreciation",
    "614.02": "expense.depreciation",
    "614.03": "expense.depreciation",
    "614.04": "expense.depreciation",
    "614.05": "expense.depreciation",
    "614.06": "expense.depreciation",
    "614.07": "expense.depreciation",
    "614.08": "expense.depreciation",
    "614.09": "expense.depreciation",
    "614.10": "expense.depreciation",

    # RESULTADO INTEGRAL DE FINANCIAMIENTO (Financial result) and other
    # income/expense. 701 (Gastos financieros) and 703 (Otros gastos) are
    # EXPENSE accounts -- the old draft's mapping had them backwards into
    # revenue.other; fixed here. 705/706/707 do not exist in the real chart
    # (chart ends at 704, then jumps to 800) -- not carried forward.
    "701.01": "expense.fx_loss",  # Pérdida cambiaria
    "701.02": "expense.fx_loss",  # ...nacional parte relacionada
    "701.03": "expense.fx_loss",  # ...extranjero parte relacionada
    "701.04": "expense.interest",  # Intereses a cargo bancario nacional
    "701.05": "expense.interest",
    "701.06": "expense.interest",
    "701.07": "expense.interest",
    "701.08": "expense.interest",
    "701.09": "expense.interest",
    "701.10": "expense.interest",  # Comisiones bancarias
    "701.11": "expense.interest",  # Otros gastos financieros
    "702": "revenue.other",  # Productos financieros (FX gains, interest income)
    "702.01": "revenue.other",
    "702.02": "revenue.other",
    "702.03": "revenue.other",
    "702.04": "revenue.other",
    "702.05": "revenue.other",
    "702.06": "revenue.other",
    "702.07": "revenue.other",
    "702.08": "revenue.other",
    "702.09": "revenue.other",
    "702.10": "revenue.other",
    # 703 Otros gastos: losses on PPE disposal and share sales -- an EXPENSE,
    # not revenue. No dedicated disposal-loss node -- needs_review (NOT
    # forced into revenue.other, which is backwards).
    "704": "revenue.other",  # Otros productos (gains on disposal, tax-incentive income, debt cancellation)
    "704.01": "revenue.other",
    "704.02": "revenue.other",
    "704.03": "revenue.other",
    "704.04": "revenue.other",
    "704.05": "revenue.other",
    "704.06": "revenue.other",
    "704.07": "revenue.other",
    "704.08": "revenue.other",
    "704.09": "revenue.other",
    "704.10": "revenue.other",
    "704.11": "revenue.other",
    "704.12": "revenue.other",
    "704.13": "revenue.other",
    "704.14": "revenue.other",
    "704.15": "revenue.other",
    "704.16": "revenue.other",
    "704.17": "revenue.other",
    "704.18": "revenue.other",
    "704.19": "revenue.other",
    "704.20": "revenue.other",
    "704.21": "revenue.other",
    "704.22": "revenue.other",
    "704.23": "revenue.other",

    # 800-899 CUENTAS DE ORDEN (order/memorandum accounts: UFIN, CUFIN,
    # CUFINRE, CUCA, inflation adjustments, tax-loss carryforwards, consigned
    # merchandise, import VAT/IEPS credit facilities) are genuinely off-
    # balance-sheet, non-postable reference accounts -- handled by
    # classify()'s jurisdiction-aware order-account prefix ("8" for mx, same
    # role EC's "9" prefix plays), NOT mapped here.
}


# --- Brazil (RFB SPED Plano de Contas Referencial, L100A + L300A) prefix ->
# Level-3 id rules --------------------------------------------------------
# Longest-prefix match wins. Codes follow the dot-segmented hierarchy
# verbatim from the source (localizations/br/plano_referencial_official_chart.yaml,
# all 1,123 codes -- 732 from L100A "Balanço Patrimonial" + 391 from L300A
# "Demonstração do Resultado").
#
# Unlike EC/MX, Brazil's own source data carries TWO authoritative signals
# EC/MX had to infer via prefix heuristics: TIPO ("S"=Sintética header,
# "A"=Analítica leaf) and an explicit CONTA SUPERIOR parent code. classify()
# uses entry["tipo"] directly for is_aggregate detection instead of a
# parent_codes/SUBTOTAL_PREFIXES guess.
#
# Brazil ALSO marks contra-accounts with a literal "(-)" name prefix, parsed
# into entry["is_contra"] -- but this means something different depending on
# which sheet the code is from, verified against the actual account names,
# not assumed:
#   - In L100A (balance sheet): "(-)" marks genuine contra-asset/contra-
#     liability/contra-equity accounts (allowances, accumulated depreciation/
#     amortization/exhaustion, impairment losses, inventory write-downs,
#     unearned-interest discounts, treasury shares, accumulated losses).
#     These are the same kind of accounts EC/MX/SYSCOHADA leave needs_review
#     because Kontablo has no dedicated contra-node yet -- classify() forces
#     needs_review for every is_contra=true L100A leaf, which BR's reliable
#     is_contra signal makes safe to do generically instead of enumerating
#     every contra code by hand (verified: every is_contra=true code sampled
#     from L100A is a genuine allowance/accumulated/impairment/discount
#     account, never an ordinary expense).
#   - In L300A (P&L): "(-)" is instead Brazil's SIGN CONVENTION for "this
#     line subtracts from Resultado Líquido" -- it marks ordinary COGS/
#     operating-expense/financial-expense lines just as often as genuine
#     contra-revenue (sales deductions). Verified against the parsed chart:
#     3.01.01.07 (Despesas Operacionais -- payroll, rent, utilities) and
#     3.01.01.09 (Outras Despesas Operacionais -- interest, FX loss) are
#     BOTH 100% is_contra=true, yet they are ordinary expense accounts, not
#     an ontology gap. Forcing is_contra->needs_review here would silently
#     dump the entire Despesas section into needs_review noise -- exactly
#     the "don't assume a single signal means the same thing everywhere"
#     trap this round's brief warned about. So for L300A, is_contra is NOT
#     used as a needs_review trigger; only the specific contra-REVENUE
#     prefix (Deduções da Receita Bruta, 3.01.01.01.02 / 3.11.01.01.02) is
#     deliberately left OUT of BR_RULES so it falls through to needs_review
#     via the normal "no rule matched" path -- same convention EC/MX use for
#     their sales-return/discount contra-revenue sections.
BR_RULES = {
    # ===== L100A: ATIVO CIRCULANTE =====
    "1.01.01.01": "asset.current.cash",              # Caixa Geral
    "1.01.01.02": "asset.current.bank",              # Depósitos Bancários à Vista
    "1.01.01.04": "asset.current.cash",              # Numerários em Trânsito
    "1.01.01.05": "asset.noncurrent.investments",    # Títulos e Valores Mobiliários - No País (no dedicated short-term-investment node)
    "1.01.01.06": "asset.noncurrent.investments",    # Valores Mobiliários - Hedge - No País
    "1.01.01.09": "asset.noncurrent.investments",    # Títulos e Valores Mobiliários - No Exterior
    "1.01.01.10": "asset.noncurrent.investments",    # Valores Mobiliários - Hedge - No Exterior
    "1.01.01.40": "asset.current.bank",              # Recursos no Exterior Decorrentes de Exportação
    "1.01.01.99": "asset.current.cash",              # Outras Disponibilidades
    "1.01.02.01": "asset.current.prepaid",           # Adiantamentos (a fornecedores/funcionários/terceiros)
    "1.01.02.02": "asset.current.receivables",       # Duplicatas a Receber
    "1.01.02.03": "asset.current.vat_input",         # Tributos a Recuperar (ICMS/PIS/COFINS/IPI credits)
    "1.01.02.04": "asset.current.withholding_tax",   # Tributos a Compensar (IRRF/IRPJ/CSLL withheld/estimated)
    "1.01.02.09": "asset.current.other_receivables", # Outros Créditos - Circulante
    "1.01.03": "asset.current.inventory",            # Estoques (mercadorias/produtos/imobiliária/rural/serviços/outros)
    "1.01.05": "asset.current.prepaid",              # Despesas do Exercício Seguinte
    # 1.01.10 Ativo Biológico - Circulante: no rule -- asset.noncurrent.biological
    # is PLANNED status with no uuid yet (core/schemas/level3_accounts.yaml
    # pending_accounts), same real ontology gap EC/MX hit. needs_review.
    # 1.01.11 Ativo Não Circulante Mantido para Venda: no rule -- IFRS 5
    # held-for-sale classification has no dedicated Kontablo node (distinct
    # from ordinary PPE). needs_review.

    # ===== L100A: ATIVO NÃO CIRCULANTE =====
    # 1.02.01.01 Créditos e Valores - Longo Prazo: no rule -- only a CURRENT
    # receivables node exists; forcing a long-term balance into it would
    # misstate current vs noncurrent (same principle as MX's "186" gap).
    "1.02.01.02": "asset.noncurrent.investments",    # Títulos e Valores Mobiliários - No País - Longo Prazo
    "1.02.01.03": "asset.noncurrent.investments",    # ...No Exterior - Longo Prazo
    # 1.02.01.05 Ativos Fiscais Diferidos - Longo Prazo: no rule -- this is a
    # deferred tax ASSET; only liability.noncurrent.deferred_tax (a liability
    # node) exists (same gap as MX's "185"). needs_review.
    # 1.02.01.07 Créditos em Contencioso - Longo Prazo: no rule -- no dedicated node.
    # 1.02.01.08 Tributos a Recuperar - Longo Prazo: no rule -- only current
    # vat_input node exists.
    # 1.02.01.09 Despesas Pagas Antecipadamente - Longo Prazo: no rule -- only
    # current prepaid node exists.
    # 1.02.01.10 Ativo Biológico - Longo Prazo: no rule -- same biological gap.
    # 1.02.01.15 Outros Créditos - Longo Prazo: no rule -- only current
    # other_receivables node exists.
    "1.02.02.01": "asset.noncurrent.investments",    # Participações Permanentes - No País
    "1.02.02.02": "asset.noncurrent.investments",    # Participações Permanentes - No Exterior
    # 1.02.02.03 Propriedades para Investimento: no rule -- investment
    # property (IAS 40) is distinct from both PPE and equity-method
    # investments; no dedicated node. needs_review.
    "1.02.02.10": "asset.noncurrent.investments",    # Outros Investimentos Permanentes
    "1.02.03.01": "asset.noncurrent.ppe",            # Imobilizado - Aquisição
    "1.02.03.02": "asset.noncurrent.rou_assets",     # Imobilizado - Bens Objeto de Arrendamento (pairs with the
                                                      # liability.noncurrent.lease node on the passive side)
    # 1.02.03.04 Ativo Biológico de Produção: no rule -- same biological gap.
    "1.02.03.05": "asset.noncurrent.ppe",            # Outros Imobilizados
    "1.02.05.01.21": "asset.noncurrent.goodwill",    # Goodwill – Intangível (exception nested inside Intangível)
    "1.02.05": "asset.noncurrent.intangibles",       # Intangível (marcas, patentes, software, etc.)
    # 1.02.06 Diferido: no rule -- legacy pre-Lei 11.941/2009 Brazilian-GAAP
    # deferred-charge concept, no clean IFRS-anchored equivalent (same kind
    # of gap as MX's "173-182" legacy deferred-charge family). needs_review.

    # ===== L100A: PASSIVO CIRCULANTE =====
    "2.01.01.01": "liability.current.payroll",       # Benefícios e Encargos Sociais - Circulante
    "2.01.01.03": "liability.current.payables",      # Fornecedores - Circulante
    "2.01.01.05": "liability.current.deferred_revenue",  # header says "Contas a Pagar" but every leaf is Adiantamentos de Clientes (customer advances)
    "2.01.01.07": "liability.current.short_term_debt",   # Empréstimos ou Financiamentos - Circulante
    "2.01.01.09": "liability.current.tax",           # Obrigações Fiscais - Circulante
    # 2.01.01.11 / 2.01.01.12 Valores Mobiliários - Hedge: no rule -- derivative
    # hedge liability, no dedicated node.
    "2.01.01.13": "liability.current.short_term_debt",   # Títulos de Dívida - Circulante (debêntures, bonds, notas promissórias)
    "2.01.01.15.01": "liability.current.tax",        # Provisão para o Imposto de Renda
    "2.01.01.15.02": "liability.current.tax",        # Provisão para a CSLL
    "2.01.01.15.03": "liability.current.payroll",    # Férias a Pagar
    "2.01.01.15.04": "liability.current.payroll",    # 13º Salário a Pagar
    "2.01.01.15.05": "liability.current.payroll",    # Provisões de Natureza Trabalhista
    "2.01.01.15.06": "liability.current.tax",        # Provisões de Natureza Tributária
    "2.01.01.15.07": "liability.current.accrued",    # Provisões de Natureza Cível
    "2.01.01.15.28": "liability.current.accrued",    # Outras Provisões
    "2.01.01.17.01": "liability.current.short_term_debt",  # Mútuos - Partes Não Relacionadas - No País
    "2.01.01.17.02": "liability.current.short_term_debt",  # ...No Exterior
    "2.01.01.17.03": "liability.current.short_term_debt",  # Mútuos - Partes Relacionadas - No País
    "2.01.01.17.04": "liability.current.short_term_debt",  # ...No Exterior
    "2.01.01.17.11": "liability.current.deferred_revenue", # Faturamento para Entrega Futura
    "2.01.01.17.12": "liability.current.accrued",    # Juros sobre o Capital Próprio a Pagar
    "2.01.01.17.13": "liability.current.accrued",    # Dividendos a Pagar
    "2.01.01.17.25": "liability.current.payables",   # Direitos Creditórios a Pagar
    "2.01.01.17.60": "liability.current.deferred_revenue", # CPC 47 - Passivos de Contrato
    # 2.01.01.17.09/.10 (contraprestação/passivo contingente - business
    # combination), .15/.16 (conta de controle de custo contratado/orçado -
    # construction contract cost control), .28 (outras obrigações, too
    # generic): no rule -- no dedicated node.
    "2.01.01.19.01": "liability.current.deferred_revenue",  # Receitas Diferidas
    "2.01.01.19.03": "liability.current.deferred_revenue",  # Subvenção Governamental a Apropriar

    # ===== L100A: PASSIVO NÃO-CIRCULANTE =====
    "2.02.01.01.01": "liability.noncurrent.debt",    # Fornecedores - No País - Longo Prazo
    "2.02.01.01.02": "liability.noncurrent.debt",    # ...No Exterior
    "2.02.01.01.03": "liability.noncurrent.debt",    # Credores por Financiamento
    "2.02.01.01.04": "liability.noncurrent.debt",    # Títulos a Pagar
    "2.02.01.01.05": "liability.noncurrent.debt",    # Duplicatas Descontadas
    "2.02.01.01.06": "liability.noncurrent.debt",    # Empréstimos ou Financiamentos - No País
    "2.02.01.01.07": "liability.noncurrent.debt",    # ...No Exterior
    "2.02.01.01.08": "liability.noncurrent.debt",    # Adiantamentos de Contrato de Câmbio
    "2.02.01.01.09": "liability.noncurrent.lease",   # Arrendamento - No País (dedicated lease node)
    "2.02.01.01.10": "liability.noncurrent.lease",   # Arrendamento - No Exterior
    # 2.02.01.01.11/.12 Adiantamentos de Clientes - Longo Prazo: no rule --
    # only a CURRENT deferred_revenue node exists.
    "2.02.01.03": "liability.noncurrent.debt",       # Parcelamentos Fiscais - Longo Prazo
    "2.02.01.05": "liability.noncurrent.deferred_tax",  # Passivos Fiscais Diferidos - Longo Prazo (exact fit)
    "2.02.01.07.01": "liability.noncurrent.debt",    # Debêntures a Pagar - Longo Prazo
    "2.02.01.07.02": "liability.noncurrent.debt",    # Prêmio na Emissão de Debêntures
    "2.02.01.07.04": "liability.noncurrent.debt",    # Notas Promissórias a Pagar
    "2.02.01.07.05": "liability.noncurrent.debt",    # Bonds a Pagar
    "2.02.01.07.06": "liability.noncurrent.debt",    # CRI
    "2.02.01.07.07": "liability.noncurrent.debt",    # CRA
    "2.02.01.07.25": "liability.noncurrent.debt",    # Outros Títulos de Dívida - Custo Amortizado
    "2.02.01.07.28": "liability.noncurrent.debt",    # ...Valor Justo (VJPR)
    # 2.02.01.09 Provisões - Longo Prazo (trabalhista/tributária/cível): no
    # rule -- no dedicated NONCURRENT provision/accrued node exists.
    # 2.02.01.10 Obrigações Fiscais - Longo Prazo: no rule -- only current tax node exists.
    "2.02.01.11.01": "liability.noncurrent.debt",    # Mútuos - Partes Não Relacionadas - No País - LP
    "2.02.01.11.02": "liability.noncurrent.debt",    # ...No Exterior
    "2.02.01.11.03": "liability.noncurrent.debt",    # Mútuos - Partes Relacionadas - No País - LP
    "2.02.01.11.04": "liability.noncurrent.debt",    # ...No Exterior
    "2.02.01.11.22": "liability.noncurrent.debt",    # Direitos Creditórios a Pagar - Longo Prazo
    # 2.02.01.11.10 (passivo contingente), .11/.12 (JCP/dividendos longo
    # prazo -- only current accrued node exists), .13 (AFAC-passivo,
    # genuinely ambiguous equity-vs-liability), .15/.16 (cost control),
    # .28 (generic "other"), .60 (CPC 47 longo prazo -- only current
    # deferred_revenue node exists): no rule -- no dedicated node.
    # 2.02.01.21 Receitas Diferidas - Longo Prazo: no rule -- only current
    # deferred_revenue node exists.

    # ===== L100A: PATRIMÔNIO LÍQUIDO =====
    # NOTE: Patrimônio Líquido is numbered 2.03 -- nested under the same root
    # "2" as Passivo in Brazil's own numbering, NOT given its own top-level
    # root digit the way EC's "3" or MX's "3" are. Verified against the
    # actual parsed chart (2.03 sits alongside 2.01/2.02 as a sibling S-level
    # header under root "2"), not assumed from EC/MX's convention -- see
    # build_erpnext_tree.py's BR-specific reparenting for how this is handled
    # when building the ERPNext tree.
    "2.03.01": "equity.capital",           # Capital Social
    "2.03.02": "equity.reserves",          # Reservas (capital/reavaliação/lucros)
    "2.03.03": "equity.reserves",          # Ajustes de Avaliação Patrimonial (OCI) -- closest fit, "Other Reserves"
    "2.03.04.01.01": "equity.retained",    # Lucros Acumulados e/ou Saldo à Disposição da Assembleia
    "2.03.04": "equity.reserves",          # Outras Contas do PL (generic catch-all, contingent consid., prior-period adjustments)

    # ===== L300A: RESULTADO (Atividade Geral) =====
    "3.01.01.01.01": "revenue.operating",  # Receita Bruta
    # 3.01.01.01.02 Deduções da Receita Bruta: no rule -- CONTRA-REVENUE
    # (sales returns/discounts, ICMS/COFINS/PIS/ISS on sales), same
    # convention as EC/MX/SYSCOHADA's contra-revenue sections. needs_review.
    "3.01.01.03": "expense.cogs",          # Custo dos Bens e Serviços Vendidos
    "3.01.01.05": "revenue.other",         # Outras Receitas Operacionais
    "3.01.01.07.01.14": "expense.tax",           # PIS/PASEP
    "3.01.01.07.01.15": "expense.tax",           # COFINS
    "3.01.01.07.01.16": "expense.tax",           # Demais Impostos, Taxas e Contribuições
    "3.01.01.07.01.23": "expense.depreciation",  # Encargos de Depreciação
    "3.01.01.07.01.24": "expense.depreciation",  # Encargos de Amortização
    "3.01.01.07": "expense.admin",         # Despesas Operacionais (flat payroll/admin-style list;
                                            # no dedicated selling-expense node, same EC/MX precedent)
    "3.01.01.09.01.01": "expense.fx_loss",       # Variações Cambiais Passivas
    "3.01.01.09.01.04": "expense.interest",      # Despesas de Juros sobre o Capital Próprio
    "3.01.01.09.01.05": "expense.interest",      # Despesas de Remuneração de Debêntures
    "3.01.01.09.01.06": "expense.interest",      # Juros com Empréstimos de Partes Vinculadas
    "3.01.01.09.01.07": "expense.interest",      # Despesas Financeiras Relativas a Arrendamento
    "3.01.01.09.01.08": "expense.interest",      # Outras Despesas Financeiras
    "3.01.01.09.01.15": "expense.interest",      # Despesas Financeiras Decorrentes dos Ajustes ao Valor Presente
    "3.01.01.09.01.16": "expense.depreciation",  # Encargos de Depreciação de Bens Objeto de Arrendamento
    "3.01.01.09.01.17": "expense.depreciation",  # Encargos de Amortização de Mais-Valia
    "3.01.01.09.01.18": "expense.admin",         # Aluguéis de Bens Imóveis - Parte Relacionada
    "3.01.01.09.01.19": "expense.admin",         # Aluguéis de Bens Imóveis - Parte Não Relacionada
    "3.01.01.09.01.20": "expense.interest",      # Despesas com Empréstimos de Valores Mobiliários
    "3.01.01.09.01.21": "expense.interest",      # Despesas com Corretagem e Emolumentos
    "3.01.01.09.01.22": "expense.interest",      # Despesas com Deságio na Cessão de Títulos
    "3.01.01.09.01.23": "expense.interest",      # Despesas em Operações de Mútuo - Parte Relacionada
    "3.01.01.09.01.24": "expense.interest",      # ...Parte Não Relacionada
    "3.01.01.09.01.25": "expense.interest",      # Despesas em Outros Passivos Financeiros - Custo Amortizado
    # remaining 3.01.01.09 leaves (trading losses, equity-method losses,
    # impairment losses, OCI reclassifications, fair-value losses on
    # financial/biological/investment-property instruments, generic "outras
    # despesas operacionais"): no rule -- no dedicated node, needs_review.
    # 3.01.01.11 Outras Receitas/Despesas + Resultado de Operações
    # Descontinuadas: no rule -- mixed disposal-gain/loss + discontinued-ops
    # section (same kind of gap as MX's "505"/"703"), no single Level-3 node
    # fits cleanly. needs_review.
    # 3.01.05 Participações (profit-sharing expense -- employees, admins,
    # debenture holders): no rule -- no dedicated node (same gap as MX's
    # "607 PTU"). needs_review.
    "3.02": "expense.tax",                 # Provisão para CSLL e IRPJ (income tax expense)

    # ===== L300A: RESULTADO (Atividade Rural) -- mirrors Atividade Geral 1:1 =====
    "3.11.01.01.01": "revenue.operating",
    # 3.11.01.01.02 Deduções (rural): no rule -- contra-revenue.
    "3.11.01.03": "expense.cogs",
    "3.11.01.05": "revenue.other",
    "3.11.01.07.01.14": "expense.tax",
    "3.11.01.07.01.15": "expense.tax",
    "3.11.01.07.01.16": "expense.tax",
    "3.11.01.07.01.23": "expense.depreciation",
    "3.11.01.07.01.24": "expense.depreciation",
    "3.11.01.07": "expense.admin",
    "3.11.01.09.01.01": "expense.fx_loss",
    "3.11.01.09.01.04": "expense.interest",
    "3.11.01.09.01.05": "expense.interest",
    "3.11.01.09.01.06": "expense.interest",
    "3.11.01.09.01.07": "expense.interest",
    "3.11.01.09.01.08": "expense.interest",
    "3.11.01.09.01.15": "expense.interest",
    "3.11.01.09.01.16": "expense.depreciation",
    "3.11.01.09.01.17": "expense.depreciation",
    "3.11.01.09.01.18": "expense.admin",
    "3.11.01.09.01.19": "expense.admin",
    "3.11.01.09.01.20": "expense.interest",
    "3.11.01.09.01.21": "expense.interest",
    "3.11.01.09.01.22": "expense.interest",
    "3.11.01.09.01.23": "expense.interest",
    "3.11.01.09.01.24": "expense.interest",
    "3.11.01.09.01.25": "expense.interest",
    # 3.11.01.11 (rural discontinued ops), 3.11.05 (rural participações): no rule.
    "3.12": "expense.tax",                 # Provisão CSLL (Atividade Rural)
}


def load_ontology_nodes():
    """Real, UUID-bearing Level-3 nodes only. The ontology file is split
    across multiple '---'-separated YAML documents (core list under the
    'level3:' key, then bare-list continuation docs for liabilities/equity/
    revenue/expense, then a dict under 'extended_core:'). A trailing
    'pending_accounts:' doc lists DRAFT/RESEARCH/PLANNED ids with NO uuid --
    those are deliberately excluded: mapping onto a node that doesn't exist
    yet would be exactly the kind of silent guess this pipeline exists to
    avoid.
    """
    node_uuid = {}
    for doc in yaml.safe_load_all(open(ONTOLOGY_PATH, encoding="utf-8")):
        items = None
        if isinstance(doc, list):
            items = doc
        elif isinstance(doc, dict) and "level3" in doc:
            items = doc["level3"]
        elif isinstance(doc, dict) and "extended_core" in doc:
            items = doc["extended_core"]
        for it in items or []:
            if isinstance(it, dict) and it.get("uuid"):
                node_uuid[it["id"]] = it["uuid"]
    return node_uuid


def longest_prefix_match(code, rules):
    best = None
    for prefix, node_id in rules.items():
        if code.startswith(prefix) and (best is None or len(prefix) > len(best[0])):
            best = (prefix, node_id)
    return best[1] if best else None


# Per-jurisdiction leading digit that marks non-postable order/memorandum
# accounts (never real balance-sheet/P&L accounts). EC's Plan de Cuentas
# uses "9"; SAT's código agrupador uses "8" (Cuentas de orden, 800-899) --
# these are NOT the same digit, so this must be looked up per jurisdiction
# rather than hardcoded, or MX's 8xx codes would be silently treated as
# regular postable leaves instead of captions. Brazil's Plano de Contas
# Referencial (L100A/L300A) has no order/memorandum-account section at all
# -- verified against the parsed chart (only roots "1"/"2"/"3" exist) -- so
# no "br" entry is added here; classify()'s br branch below doesn't consult
# this dict.
ORDER_ACCOUNT_PREFIX = {"ec": "9", "mx": "8"}

# The EC-authored subtotal/computed-row heuristic below only reflects EC's
# own chart layout (verified against EC's parsed official chart) and must
# not leak into other jurisdictions' classification -- e.g. MX also happens
# to use codes like "606", "607", "701" for entirely different, genuinely
# postable/needs_review concepts, so applying EC's set to MX would silently
# mislabel them as statement captions instead of the correct needs_review.
# Brazil doesn't need this mechanism at all: TIPO ("S"=Sintética/header,
# "A"=Analítica/leaf) is an authoritative column straight from the source,
# so classify() reads entry["tipo"] directly for br instead of guessing
# header/subtotal rows from a prefix heuristic -- see the br branch below.
JURISDICTION_SUBTOTAL_PREFIXES = {"ec": SUBTOTAL_PREFIXES}

# Codes that must NEVER inherit a broader prefix's mapping via
# longest_prefix_match, even though a shorter prefix in *_RULES matches
# them -- a single contra-account exception nested inside an otherwise
# single-themed header. E.g. MX's 109 "Pagos anticipados" is genuine
# prepaid and is mapped as a header, but 109.21 "Pérdida por deterioro de
# pagos anticipados" nested under it is a CONTRA-ASSET (accumulated
# impairment) and must not silently inherit 109's asset.current.prepaid
# mapping via prefix match -- it needs to fall through to needs_review,
# same as the other contra-accounts in this file. Empty for br: Brazil's
# per-leaf contra-account exclusion is handled generically via
# entry["is_contra"] in classify()'s br branch (scoped to the L100A sheet
# only -- see BR_RULES's header comment for why L300A's is_contra can't be
# used the same way), not by hand-enumerating exception codes the way MX's
# "109.21" needed.
JURISDICTION_FORCE_NEEDS_REVIEW = {
    "mx": {"109.21"},
}


def classify(entry, rules, parent_codes, jurisdiction=None):
    code = entry["code"]

    if jurisdiction == "br":
        # Brazil's own source data is authoritative for both header/leaf
        # detection (TIPO) and contra-account detection (is_contra, parsed
        # from a literal "(-)" name prefix) -- no prefix-heuristic guessing
        # needed here the way EC/MX require (parent_codes / SUBTOTAL_PREFIXES
        # / JURISDICTION_FORCE_NEEDS_REVIEW), so br takes its own path
        # entirely rather than falling through the shared EC/MX pipeline
        # below.
        if entry.get("tipo") == "S":
            # Sintética: header/rollup row with more granular children in
            # this same chart -- never independently postable. Same role
            # EC/MX's parent_codes fallback plays, but sourced directly from
            # the primary source instead of inferred from code containment.
            return {"kontablo_uuid": None, "kontablo_node": None,
                    "is_statement_caption": False, "is_aggregate": True, "needs_review": False}
        if entry.get("source_sheet") == "L100A" and entry.get("is_contra"):
            # Genuine contra-asset/contra-liability/contra-equity account
            # (allowance, accumulated depreciation/amortization/exhaustion,
            # impairment, inventory write-down, unearned-interest discount,
            # treasury shares, accumulated losses) -- Kontablo has no
            # dedicated contra-node yet, same gap EC/MX/SYSCOHADA leave
            # needs_review. Deliberately scoped to L100A only: in L300A the
            # same is_contra flag just marks "this line subtracts from
            # Resultado Líquido" (ordinary COGS/expense/financial-expense
            # lines are is_contra=true there too) and must NOT trigger this
            # override -- see BR_RULES's header comment for the verified
            # reasoning.
            return {"kontablo_uuid": None, "kontablo_node": None,
                    "is_statement_caption": False, "is_aggregate": False, "needs_review": True}
        node_id = longest_prefix_match(code, rules)
        if node_id:
            return {"kontablo_uuid": None, "kontablo_node": node_id,
                    "is_statement_caption": False, "is_aggregate": False, "needs_review": False}
        return {"kontablo_uuid": None, "kontablo_node": None,
                "is_statement_caption": False, "is_aggregate": False, "needs_review": True}

    oa_prefix = ORDER_ACCOUNT_PREFIX.get(jurisdiction)
    if entry["statement"] in (
        "Estado de Cambios en el Patrimonio",
    ) or (oa_prefix is not None and code[:1] == oa_prefix):
        return {"kontablo_uuid": None, "kontablo_node": None,
                "is_statement_caption": True, "is_aggregate": False, "needs_review": False}
    if code in JURISDICTION_FORCE_NEEDS_REVIEW.get(jurisdiction, set()):
        return {"kontablo_uuid": None, "kontablo_node": None,
                "is_statement_caption": False, "is_aggregate": False, "needs_review": True}
    node_id = longest_prefix_match(code, rules)
    if node_id:
        return {"kontablo_uuid": None, "kontablo_node": node_id,
                "is_statement_caption": False, "is_aggregate": False, "needs_review": False}
    subtotal_prefixes = JURISDICTION_SUBTOTAL_PREFIXES.get(jurisdiction, set())
    is_subtotal = any(code == p or code.startswith(p) and len(code) <= len(p) + 2
                       for p in subtotal_prefixes)
    if is_subtotal:
        return {"kontablo_uuid": None, "kontablo_node": None,
                "is_statement_caption": True, "is_aggregate": False, "needs_review": False}
    if code in parent_codes:
        # Header/rollup row (has more granular children in this same chart) --
        # never independently postable, so it is not a classification gap.
        return {"kontablo_uuid": None, "kontablo_node": None,
                "is_statement_caption": False, "is_aggregate": True, "needs_review": False}
    return {"kontablo_uuid": None, "kontablo_node": None,
            "is_statement_caption": False, "is_aggregate": False, "needs_review": True}


def derive_nature(entry, jurisdiction=None):
    # MX's código agrupador uses eight top-level roots (1 Activo ... 8
    # Cuentas de orden), not EC's five-root scheme this heuristic was
    # written for -- roots "6"/"7"/"8" would silently fall through to
    # `return None`, leaving `nature: null` for the entire Gastos/Resultado
    # financiero/Cuentas de orden series. The parser
    # (parse_sat_codigo_agrupador.py) already derives the correct nature
    # per SAT's actual eight-root convention into entry["nature"] -- use
    # that directly for MX instead of re-deriving via the EC-specific
    # single-digit-root heuristic below.
    if jurisdiction == "mx":
        return entry.get("nature")
    if jurisdiction == "br":
        # NATUREZA: 1=Ativo(Debit), 2=Passivo(Credit), 3=Patrimônio
        # Líquido(Credit), 4=Resultado (mixed within the P&L). This is
        # Brazil's own NATUREZA column, not a bare "root digit determines
        # nature" heuristic borrowed from EC -- verified against the parsed
        # chart: within L300A (natureza=4 for every row), is_contra=true
        # consistently marks the Debit-nature lines (COGS/expense/
        # deduction) and is_contra=false marks the Credit-nature lines
        # (revenue/gain), sampled across both the Atividade Geral and
        # Atividade Rural mirrors.
        natureza = entry.get("natureza")
        if natureza == 1:
            return "Debit"
        if natureza in (2, 3):
            return "Credit"
        if natureza == 4:
            return "Debit" if entry.get("is_contra") else "Credit"
        return None

    root = entry["code"][0]
    sign = entry["sign"]
    if root in ("1", "5"):
        base = "Debit"
    elif root in ("2", "3", "4"):
        base = "Credit"
    else:
        return None
    if sign == "POSITIVO":
        return base
    if sign == "NEGATIVO":
        return "Credit" if base == "Debit" else "Debit"
    return base  # DUAL: default to natural side, not authoritative


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--official", required=True)
    ap.add_argument("--jurisdiction", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    node_uuid = load_ontology_nodes()
    ontology_ids = set(node_uuid)

    if args.jurisdiction == "ec":
        rules = EC_RULES
    elif args.jurisdiction == "mx":
        rules = MX_RULES
    elif args.jurisdiction == "br":
        rules = BR_RULES
    else:
        rules = {}
    official = yaml.safe_load(open(args.official, encoding="utf-8"))

    all_codes = [e["code"] for e in official["accounts"]]
    parent_codes = {
        a for a in all_codes
        if any(b != a and b.startswith(a) for b in all_codes)
    }

    mappings = {}
    stats = {"mapped": 0, "caption": 0, "aggregate": 0, "needs_review": 0}
    for entry in official["accounts"]:
        cls = classify(entry, rules, parent_codes, jurisdiction=args.jurisdiction)
        node_id = cls["kontablo_node"]
        if node_id and node_id not in ontology_ids:
            raise ValueError(f"Rule references unknown ontology id: {node_id}")
        row = {
            "name": entry["name"],
            "nature": derive_nature(entry, jurisdiction=args.jurisdiction),
            "statement": entry["statement"],
            "kontablo_node": node_id,
            "kontablo_uuid": node_uuid.get(node_id),
            "is_statement_caption": cls["is_statement_caption"],
            "is_aggregate": cls["is_aggregate"],
            "needs_review": cls["needs_review"],
        }
        mappings[entry["code"]] = row
        if cls["is_statement_caption"]:
            stats["caption"] += 1
        elif cls["is_aggregate"]:
            stats["aggregate"] += 1
        elif node_id:
            stats["mapped"] += 1
        else:
            stats["needs_review"] += 1

    doc = {
        "metadata": {
            "jurisdiction": args.jurisdiction,
            "authority": official["metadata"]["authority"],
            "source_url": official["metadata"]["source_url"],
            "version": "0.2.0-full-chart",
            "total_official_codes": len(mappings),
            "classified_to_kontablo_node": stats["mapped"],
            "statement_captions_not_postable": stats["caption"],
            "aggregate_header_rows": stats["aggregate"],
            "needs_review_unclassified": stats["needs_review"],
            "note": (
                "Every code from the official chart is present here -- no "
                "hand-picked subset. Classification onto Kontablo's "
                "universal Level-3 ontology is many-to-one by design "
                "(principle: graph, not tree). is_aggregate=true means the "
                "code is a header/rollup row with more granular children in "
                "this same chart (never independently postable). "
                "needs_review=true means no existing Level-3 node fits AND "
                "the code is a genuine leaf; that is an honest ontology gap, "
                "not a silent guess -- see research/coa_fidelity/STATUS.yaml."
            ),
            "generator": "scripts/coa_fidelity/map_official_chart.py",
        },
        "mappings": mappings,
    }
    with open(args.out, "w", encoding="utf-8") as f:
        yaml.safe_dump(doc, f, allow_unicode=True, sort_keys=False, width=100)

    print(f"Total codes: {len(mappings)}")
    print(f"Mapped to a Level-3 node: {stats['mapped']}")
    print(f"Statement captions (not postable): {stats['caption']}")
    print(f"Aggregate/header rows (not postable): {stats['aggregate']}")
    print(f"Needs review (no fitting node): {stats['needs_review']}")
    print(f"Written: {args.out}")


if __name__ == "__main__":
    main()
