"""Currency tables shared by the harness.

``JCCY`` maps an ISO 3166-1 alpha-2 jurisdiction to its ISO 4217 currency;
``FX`` gives USD-per-unit **pinned** synthetic 2026 rates. These tables are
shared by the deterministic engine (``core.engine``) and the validation runner
(``scripts/mass_consolidation_v2.py``), so they live in the harness package
rather than in either consumer.

``FX`` is deliberately frozen: the validation harness must reproduce
byte-identical results for the claims-evidence gate, so it always prices in
these pinned rates. For a *runtime* deployment that needs current market rates,
see ``core.harness.fx_provider`` — a pluggable provider (ECB/Frankfurter →
open.er-api → this static table as offline fallback). ``FX`` is the offline,
deterministic last resort of that chain.
"""

from __future__ import annotations

from typing import Dict

# Currency per jurisdiction (ISO) and USD-per-unit FX (synthetic 2026 rates).
JCCY: Dict[str, str] = {"ae":"AED","ar":"ARS","br":"BRL","ca":"CAD","cn":"CNY","co":"COP",
        "de":"EUR","es":"EUR","fr":"EUR","il":"ILS","in":"INR","jp":"JPY",
        "mx":"MXN","ng":"NGN","pa":"USD","ru":"RUB","sa":"SAR","tr":"TRY",
        "uk":"GBP","us":"USD","ve":"VES","vn":"VND","za":"ZAR",
        "sn":"XOF","ci":"XOF","kr":"KRW","lb":"LBP","ec":"USD",
        # --- additional Tier-2 jurisdictions (no ontology local_codes) ---
        "it":"EUR","pl":"PLN","id":"IDR","gr":"EUR","cl":"CLP","pe":"PEN",
        "ma":"MAD","kz":"KZT","eg":"EGP","ke":"KES","ph":"PHP","pk":"PKR",
        "ch":"CHF","dz":"DZD","ro":"RON","be":"EUR",
        "cz":"CZK","sk":"EUR","hu":"HUF","bg":"BGN",
        "ua":"UAH","tn":"TND","by":"BYN",
        "rs":"RSD","hr":"EUR","si":"EUR","at":"EUR","lu":"EUR","mc":"EUR",
        "md":"MDL","gr":"EUR",
        # --- OHADA member currencies (SYSCOHADA) ---
        "bj":"XOF","bf":"XOF","ml":"XOF","ne":"XOF","tg":"XOF","gw":"XOF",
        "cm":"XAF","cf":"XAF","td":"XAF","cg":"XAF","gq":"XAF","ga":"XAF",
        "km":"KMF","cd":"CDF"}
FX: Dict[str, float] = {"AED":0.27,"ARS":0.0011,"BRL":0.20,"CAD":0.73,"CNY":0.14,"COP":0.00025,
      "EUR":1.08,"ILS":0.27,"INR":0.012,"JPY":0.0067,"MXN":0.058,"NGN":0.00065,
      "RUB":0.011,"SAR":0.27,"TRY":0.030,"GBP":1.27,"USD":1.0,"VES":0.027,
      "VND":0.00004,"ZAR":0.054,"XOF":0.00165,"KRW":0.00073,"LBP":0.0000112,
      "PLN":0.25,"IDR":0.000062,"CLP":0.0011,"PEN":0.27,"MAD":0.10,"KZT":0.0021,
      "EGP":0.021,"KES":0.0078,"PHP":0.018,"PKR":0.0036,"CHF":1.13,
      "XAF":0.00165,"KMF":0.0022,"CDF":0.00035,"DZD":0.0074,"RON":0.22,
      "CZK":0.043,"HUF":0.0028,"BGN":0.55,"UAH":0.024,"TND":0.32,"BYN":0.31,
      "RSD":0.0092,"MDL":0.057}
