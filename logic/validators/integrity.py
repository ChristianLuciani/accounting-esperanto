from typing import List
from api.rest.models import MappedAccount

class IntegrityValidator:
    """
    Ensures that the final mapping is consistent and valid.
    """
    
    def validate(self, mapped_accounts: List[MappedAccount]) -> bool:
        """
        Validates the mapping against basic rules.
        """
        for acc in mapped_accounts:
            # 1. UUID format check
            if len(acc.kontablo_uuid) != 36:
                return False
            
            # 2. Check for null mappings
            if acc.kontablo_uuid == "00000000-0000-0000-0000-000000000000":
                # Mark as low confidence but don't fail the whole batch
                continue
                
        return True
