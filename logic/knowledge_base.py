import os
import yaml
from typing import Dict, Any, Optional

class KnowledgeBase:
    """
    Loads and manages localized accounting standards.
    """
    
    def __init__(self, base_path: str = "localizations"):
        self.base_path = base_path
        self.standards = {}
        self._load_all()

    def _load_all(self):
        """Loads all YAML files in the localizations directory."""
        if not os.path.exists(self.base_path):
            return

        for country_dir in os.listdir(self.base_path):
            path = os.path.join(self.base_path, country_dir)
            if os.path.isdir(path):
                for file in os.listdir(path):
                    if file.endswith(".yaml"):
                        with open(os.path.join(path, file), 'r') as f:
                            data = yaml.safe_load(f)
                            # Store by country and standard name
                            country = data.get("metadata", {}).get("country", country_dir)
                            # YAML 1.1 parses bare NO (Norway), ON, etc. as booleans;
                            # fall back to the directory name for any non-string value.
                            if not isinstance(country, str):
                                country = country_dir
                            country = country.upper()
                            if country not in self.standards:
                                self.standards[country] = {}
                            self.standards[country][file.replace(".yaml", "")] = data

    def valid_uuids(self) -> set:
        """Set of every Kontablo UUID the loaded ontology actually contains.
        This is the membership boundary the Deterministic Boundary Library
        enforces: an agent-proposed UUID outside this set must never be
        accepted as a mapping."""
        if not hasattr(self, "_valid_uuids"):
            uuids = set()
            for country_data in self.standards.values():
                for std_data in country_data.values():
                    for mapping in std_data.get("mappings", {}).values():
                        u = mapping.get("kontablo_uuid")
                        if u:
                            uuids.add(str(u).lower())
            self._valid_uuids = uuids
        return self._valid_uuids

    def has_uuid(self, uuid: str) -> bool:
        """True iff the UUID exists in the loaded ontology graph."""
        return str(uuid).strip().lower() in self.valid_uuids()

    def get_mapping(self, country: str, code: str) -> Optional[Dict[str, Any]]:
        """Returns the mapping for a specific code in a country."""
        country_data = self.standards.get(country.upper(), {})
        # Look in all available standards for that country
        for std_name, std_data in country_data.items():
            mappings = std_data.get("mappings", {})
            if code in mappings:
                return mappings[code]
        return None

    def get_all_country_mappings(self, country: str) -> Dict[str, Any]:
        """Returns all mappings for a country."""
        return self.standards.get(country.upper(), {})
