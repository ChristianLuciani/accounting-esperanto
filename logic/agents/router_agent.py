from typing import Dict, Any
from api.rest.models import MappingRequest

class RouterAgent:
    """
    Analyzes the payload to detect the accounting standard (country, language, currency).
    """
    
    def __init__(self):
        # Known standards and their indicators
        self.standards_indicators = {
            "MX": ["SAT", "Mexico", "MXN", "PESO"],
            "CO": ["PUC", "Colombia", "COP"],
            "PA": ["DGI", "Panama", "PAB", "USD", "Peachtree", "Sage 50"],
            "BR": ["SPED", "Brazil", "BRL", "Real"],
            "FR": ["PCG", "France", "EUR", "Euro"],
            "IL": ["Israel", "ILS", "Shekel", "Hebrew"],
            "RU": ["Russia", "RUB", "Ruble"],
            "UK": ["United Kingdom", "GBP", "Pound"]
        }

    def route(self, request: MappingRequest) -> Dict[str, Any]:
        """
        Infers the country and standard from the request.
        """
        context = request.context
        country = context.country.upper() if context.country else None
        
        # If country is explicitly provided, we trust it (for now)
        if country:
            return {"country": country, "standard": self._get_default_standard(country)}
        
        # Otherwise, infer from names and currency
        # (This would be more complex in production with LLM assistance)
        inferred_country = self._infer_country(request)
        
        return {
            "country": inferred_country,
            "standard": self._get_default_standard(inferred_country)
        }

    def _get_default_standard(self, country: str) -> str:
        defaults = {
            "MX": "SAT",
            "CO": "PUC",
            "PA": "DGI",
            "BR": "SPED",
            "FR": "PCG",
            "RU": "RAS",
            "IL": "IFRS-IL",
            "UK": "UK-GAAP"
        }
        return defaults.get(country, "IFRS-Generic")

    def _infer_country(self, request: MappingRequest) -> str:
        # Simple heuristic for demo
        for acc in request.accounts:
            name = acc.local_name.lower()
            if "caja" in name or "banco" in name:
                return "MX"  # Default Spanish to MX if not specified
        return "UNKNOWN"
