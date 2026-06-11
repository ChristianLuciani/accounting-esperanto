import yaml
import os
from typing import List, Optional
from ..models.kontablo import KontabloAccount, StatementType, AccountNature

class OntologyService:
    def __init__(self, schema_path: str):
        self.schema_path = schema_path
        self.accounts = self._load_accounts()

    def _load_accounts(self) -> List[KontabloAccount]:
        if not os.path.exists(self.schema_path):
            return []
        
        with open(self.schema_path, 'r') as f:
            # Use safe_load_all to skip potential frontmatter or handle separate docs
            data = list(yaml.safe_load_all(f))
            
        accounts_data = []
        for doc in data:
            if doc and 'level3' in doc:
                accounts_data.extend(doc['level3'])
        
        accounts = []
        for acc in accounts_data:
            try:
                accounts.append(KontabloAccount(
                    id=acc['id'],
                    uuid=acc['uuid'],
                    label_en=acc['label_en'],
                    label_es=acc.get('label_es'),
                    ifrs_tag=acc['ifrs_tag'],
                    nature=AccountNature(acc['nature']),
                    statement=StatementType(acc['statement']),
                    level=acc['level'],
                    parent=acc.get('parent'),
                    is_aggregate=acc.get('is_aggregate', False),
                    optional=acc.get('optional', False),
                    local_codes=acc.get('local_codes')
                ))
            except Exception as e:
                print(f"Error parsing account {acc.get('id')}: {e}")
                
        return accounts

    def list_accounts(self, level: Optional[int] = None, nature: Optional[str] = None, statement: Optional[str] = None) -> List[KontabloAccount]:
        result = self.accounts
        if level:
            result = [a for a in result if a.level == level]
        if nature:
            result = [a for a in result if a.nature == nature]
        if statement:
            result = [a for a in result if a.statement == statement]
        return result

    def get_account(self, account_id: str) -> Optional[KontabloAccount]:
        for acc in self.accounts:
            if acc.id == account_id:
                return acc
        return None
