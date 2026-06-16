"""The three-tier deterministic resolver of the Kontablo harness.

``resolve()`` routes a local account entry to a Kontablo node using only
deterministic logic — no LLM call:

  Tier 1  exact local-code lookup against the Tier-1 reverse index.
  Tier 2  deterministic multilingual keyword rules on the account name.
  Escalate if neither tier resolves (residual -> human via the
          Co-responsibility Architecture). Tier 3 (semantic AI fallback) is
          intentionally not exercised by this deterministic path.

Keeping this in the harness package means every surface (the engine, the gRPC
servicer, the validation runner) shares the exact same Tier-1/Tier-2 rules that
produce the published deterministic-coverage number, so they cannot drift apart
behind the claims-evidence gate.
"""

from __future__ import annotations

# ---------------------------------------------------------------------------
# Tier 2 deterministic multilingual keyword rules (auditable, no AI)
# Each rule: (kontablo_id, [substrings in lowercased local name])
# Languages: en, es, pt, fr, vi, ar, de, ru, ko, tr.
# ---------------------------------------------------------------------------
TIER2_RULES = [
    ("asset.current.crypto",      ["crypto", "bitcoin", "digital asset", "criptomoneda", "token"]),
    ("asset.current.carbon_credits", ["carbon credit", "crédito de carbono", "crédit carbone", "emission allowance"]),
    ("asset.noncurrent.biological", ["biological", "activo biológico", "actif biologique", "livestock", "ganado"]),
    ("liability.current.zakat",   ["zakat", "زكاة"]),
    ("asset.current.cash",        ["cash", "caja", "caisse", "caixa", "efectivo", "tiền mặt", "النقد", "kasse", "касса", "현금", "nakit", "espèces", "petty cash", "cassa", "kasa", "kas", "ταμείο"]),
    ("asset.current.bank",        ["bank", "banco", "banque", "banca", "банк", "은행", "banka", "ngân hàng", "bancos", "البنك", "τράπεζα"]),
    ("asset.current.receivables", ["receivable", "clientes", "clients", "cuentas por cobrar", "contas a receber", "дебитор", "매출채권", "alacak", "phải thu", "debtors", "clienti", "należności", "piutang", "πελάτες", "ذمم مدينة"]),
    ("asset.current.inventory",   ["inventory", "inventario", "stock", "existencias", "estoque", "stocks", "запас", "재고", "stok", "hàng tồn kho", "magazzino", "zapasy", "persediaan"]),
    ("asset.current.vat_input",   ["vat input", "iva acreditable", "iva soportado", "tva déductible", "input vat", "input tax credit"]),
    ("asset.current.prepaid",     ["prepaid", "anticipo", "gastos pagados por anticipado", "charges constatées", "선급"]),
    ("asset.noncurrent.ppe",      ["ppe", "property plant", "propiedad planta", "immobilisations corporelles", "ativo imobilizado", "inmueble", "maquinaria", "основные средства", "유형자산", "maddi duran"]),
    ("asset.noncurrent.intangibles", ["intangible", "intangibles", "immobilisations incorporelles", "무형자산"]),
    ("asset.noncurrent.goodwill", ["goodwill", "fondo de comercio", "écart d'acquisition", "영업권"]),
    ("liability.current.payables", ["payable", "proveedores", "fornecedores", "fournisseurs", "cuentas por pagar", "кредитор", "매입채무", "borç", "phải trả", "fornitori", "zobowiązania", "utang", "προμηθευτές", "موردون"]),
    ("liability.current.vat_output", ["vat output", "iva por pagar", "iva repercutido", "tva collectée", "output vat"]),
    ("liability.current.tax",     ["tax payable", "impuestos por pagar", "impôt", "imposto a pagar", "vergi"]),
    ("liability.current.short_term_debt", ["short-term debt", "deuda corto plazo", "préstamo corto", "empréstimo"]),
    ("liability.noncurrent.debt", ["long-term debt", "deuda largo plazo", "dette", "emprunt", "차입금"]),
    ("liability.current.zakat",   ["zakat", "زكاة"]),
    ("equity.capital",            ["capital", "share capital", "capital social", "자본금", "sermaye"]),
    ("equity.retained",           ["retained", "resultados acumulados", "lucros acumulados", "report à nouveau", "이익잉여금"]),
    ("equity.reserves",           ["reserve", "reservas", "réserves", "yedek"]),
    ("revenue.operating",         ["revenue", "ingresos", "ventas", "receita", "chiffre d'affaires", "doanh thu", "매출", "gelir", "выручка", "ricavi", "przychody", "pendapatan", "έσοδα", "πωλήσεις", "إيرادات", "sales"]),
    ("revenue.other",             ["other income", "otros ingresos", "produits divers"]),
    ("expense.cogs",              ["cogs", "cost of goods", "costo de ventas", "custo", "coût des ventes", "매출원가"]),
    ("expense.admin",             ["administrative", "gastos administrativos", "frais généraux", "despesas administrativas", "판관비"]),
    ("expense.depreciation",      ["depreciation", "depreciación", "amortissement", "depreciação", "감가상각"]),
    ("expense.interest",          ["interest expense", "gastos financieros", "charges d'intérêts", "이자비용"]),
    ("expense.fx_loss",           ["fx loss", "pérdida cambiaria", "perte de change", "diferencia en cambio", "환차손"]),
]


def resolve(entry, jurisdiction, accounts, by_code):
    """Return (kontablo_id, tier, confidence)."""
    code = str(entry["code"])
    # Tier 1: exact local-code lookup
    if code in by_code.get(jurisdiction, {}):
        return by_code[jurisdiction][code], "tier1_exact", 1.0
    # Tier 2: multilingual keyword rules
    name = entry["name"].lower()
    for kid, keys in TIER2_RULES:
        if any(k in name for k in keys):
            if kid in accounts:
                return kid, "tier2_keyword", 0.85
    # Escalate (residual -> CRA human review). Tier 3 AI not run here.
    return None, "escalated", 0.0
