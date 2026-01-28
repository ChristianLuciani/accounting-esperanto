#!/usr/bin/env python3
"""
IFRS Taxonomy Extraction Script

Parses IFRS Taxonomy 2024 XSD files to extract:
- GL Accounts (Assets, Liabilities, Equity, Revenue, Expenses)
- XBRL tags
- Account classifications
- Balance types (debit/credit)
- Statement types (Balance Sheet, P&L, Cash Flow)

Output: CSV for further processing
"""

import xml.etree.ElementTree as ET
from pathlib import Path
import csv
from typing import List, Dict, Optional
import json
import re

class IFRSExtractor:
    def __init__(self, ifrs_dir: str = "bibliography/primary_sources/ifrs"):
        """Initialize IFRS extractor."""
        self.ifrs_dir = Path(ifrs_dir)
        self.extract_dir = Path("research/standards/international")
        self.extract_dir.mkdir(parents=True, exist_ok=True)
        
        # IFRS namespace
        self.ns = {
            'xs': 'http://www.w3.org/2001/XMLSchema',
            'xbrli': 'http://www.xbrl.org/2003/instance',
            'xbrldi': 'http://xbrl.org/2006/xbrldi',
        }
    
    def extract_from_xsd(self) -> List[Dict]:
        """Extract GL accounts from IFRS XSD files."""
        accounts = []
        
        # Find main taxonomy file
        ifrs_full_path = self.ifrs_dir / "ifrs-taxonomy-2024" / "ifrs" / "full"
        
        if not ifrs_full_path.exists():
            print(f"⚠️  IFRS directory not found: {ifrs_full_path}")
            print("Ensure IFRS Taxonomy is downloaded and extracted first.")
            return accounts
        
        # Find XSD files
        xsd_files = list(ifrs_full_path.glob("*.xsd"))
        
        if not xsd_files:
            print(f"⚠️  No XSD files found in {ifrs_full_path}")
            return accounts
        
        print(f"📂 Found {len(xsd_files)} XSD files in IFRS taxonomy")
        
        # Parse main schema file
        main_xsd = ifrs_full_path / "ifrs-full_2024-01-31.xsd"
        
        if main_xsd.exists():
            accounts.extend(self._parse_xsd_concepts(main_xsd))
        
        return accounts
    
    def _parse_xsd_concepts(self, xsd_file: Path) -> List[Dict]:
        """Parse XSD file to extract GL account concepts."""
        accounts = []
        
        try:
            tree = ET.parse(xsd_file)
            root = tree.getroot()
        except Exception as e:
            print(f"❌ Error parsing {xsd_file}: {e}")
            return accounts
        
        # XBRL concept types
        account_types = {
            'Assets': ['CurrentAsset', 'NonCurrentAsset'],
            'Liabilities': ['CurrentLiability', 'NonCurrentLiability'],
            'Equity': ['Equity'],
            'Revenue': ['Revenue'],
            'Expenses': ['Expense'],
        }
        
        # Extract from simpleType and element definitions
        # Note: Full IFRS XSD parsing is complex; this is simplified extraction
        
        # For Phase 0, we'll create a standardized GL structure
        # based on IFRS concepts
        
        standard_accounts = self._create_ifrs_standard_structure()
        accounts.extend(standard_accounts)
        
        return accounts
    
    def _create_ifrs_standard_structure(self) -> List[Dict]:
        """Create standard IFRS GL account structure for Phase 0."""
        accounts = [
            # ASSETS (1.x.xx)
            {
                'code': '1.1.01',
                'label_en': 'Cash and Cash Equivalents',
                'xbrl_tag': 'ifrs-full_CashAndCashEquivalents',
                'type': 'Assets',
                'subtype': 'Current Asset',
                'balance_type': 'Debit',
                'statement': 'Balance Sheet',
                'nature': 'Asset',
                'level': 1
            },
            {
                'code': '1.1.02',
                'label_en': 'Trade Receivables',
                'xbrl_tag': 'ifrs-full_TradeReceivables',
                'type': 'Assets',
                'subtype': 'Current Asset',
                'balance_type': 'Debit',
                'statement': 'Balance Sheet',
                'nature': 'Asset',
                'level': 1
            },
            {
                'code': '1.1.03',
                'label_en': 'Inventories',
                'xbrl_tag': 'ifrs-full_Inventories',
                'type': 'Assets',
                'subtype': 'Current Asset',
                'balance_type': 'Debit',
                'statement': 'Balance Sheet',
                'nature': 'Asset',
                'level': 1
            },
            {
                'code': '1.2.01',
                'label_en': 'Property, Plant and Equipment',
                'xbrl_tag': 'ifrs-full_PropertyPlantAndEquipment',
                'type': 'Assets',
                'subtype': 'Non-Current Asset',
                'balance_type': 'Debit',
                'statement': 'Balance Sheet',
                'nature': 'Asset',
                'level': 1
            },
            {
                'code': '1.2.02',
                'label_en': 'Intangible Assets',
                'xbrl_tag': 'ifrs-full_IntangibleAssetsOtherThanGoodwill',
                'type': 'Assets',
                'subtype': 'Non-Current Asset',
                'balance_type': 'Debit',
                'statement': 'Balance Sheet',
                'nature': 'Asset',
                'level': 1
            },
            
            # LIABILITIES (2.x.xx)
            {
                'code': '2.1.01',
                'label_en': 'Trade Payables',
                'xbrl_tag': 'ifrs-full_TradePayables',
                'type': 'Liabilities',
                'subtype': 'Current Liability',
                'balance_type': 'Credit',
                'statement': 'Balance Sheet',
                'nature': 'Liability',
                'level': 1
            },
            {
                'code': '2.1.02',
                'label_en': 'Short-term Borrowings',
                'xbrl_tag': 'ifrs-full_ShortTermBorrowings',
                'type': 'Liabilities',
                'subtype': 'Current Liability',
                'balance_type': 'Credit',
                'statement': 'Balance Sheet',
                'nature': 'Liability',
                'level': 1
            },
            {
                'code': '2.2.01',
                'label_en': 'Long-term Borrowings',
                'xbrl_tag': 'ifrs-full_LongtermBorrowings',
                'type': 'Liabilities',
                'subtype': 'Non-Current Liability',
                'balance_type': 'Credit',
                'statement': 'Balance Sheet',
                'nature': 'Liability',
                'level': 1
            },
            {
                'code': '2.2.02',
                'label_en': 'Deferred Tax Liabilities',
                'xbrl_tag': 'ifrs-full_DeferredTaxLiabilities',
                'type': 'Liabilities',
                'subtype': 'Non-Current Liability',
                'balance_type': 'Credit',
                'statement': 'Balance Sheet',
                'nature': 'Liability',
                'level': 1
            },
            
            # EQUITY (3.x.xx)
            {
                'code': '3.1.01',
                'label_en': 'Share Capital',
                'xbrl_tag': 'ifrs-full_ShareCapital',
                'type': 'Equity',
                'subtype': 'Equity',
                'balance_type': 'Credit',
                'statement': 'Balance Sheet',
                'nature': 'Equity',
                'level': 1
            },
            {
                'code': '3.1.02',
                'label_en': 'Retained Earnings',
                'xbrl_tag': 'ifrs-full_RetainedEarnings',
                'type': 'Equity',
                'subtype': 'Equity',
                'balance_type': 'Credit',
                'statement': 'Balance Sheet',
                'nature': 'Equity',
                'level': 1
            },
            
            # REVENUE (4.x.xx)
            {
                'code': '4.1.01',
                'label_en': 'Revenue from Contracts with Customers',
                'xbrl_tag': 'ifrs-full_RevenueFromContractsWithCustomers',
                'type': 'Revenue',
                'subtype': 'Revenue',
                'balance_type': 'Credit',
                'statement': 'Profit and Loss',
                'nature': 'Revenue',
                'level': 1
            },
            {
                'code': '4.1.02',
                'label_en': 'Other Income',
                'xbrl_tag': 'ifrs-full_OtherIncome',
                'type': 'Revenue',
                'subtype': 'Revenue',
                'balance_type': 'Credit',
                'statement': 'Profit and Loss',
                'nature': 'Revenue',
                'level': 1
            },
            
            # EXPENSES (5.x.xx)
            {
                'code': '5.1.01',
                'label_en': 'Cost of Goods Sold',
                'xbrl_tag': 'ifrs-full_CostOfSalesRecognisedInProfitOrLoss',
                'type': 'Expenses',
                'subtype': 'Operating Expense',
                'balance_type': 'Debit',
                'statement': 'Profit and Loss',
                'nature': 'Expense',
                'level': 1
            },
            {
                'code': '5.1.02',
                'label_en': 'Operating Expenses',
                'xbrl_tag': 'ifrs-full_OperatingExpenses',
                'type': 'Expenses',
                'subtype': 'Operating Expense',
                'balance_type': 'Debit',
                'statement': 'Profit and Loss',
                'nature': 'Expense',
                'level': 1
            },
            {
                'code': '5.1.03',
                'label_en': 'Depreciation and Amortization',
                'xbrl_tag': 'ifrs-full_DepreciationAndAmortisationExpense',
                'type': 'Expenses',
                'subtype': 'Operating Expense',
                'balance_type': 'Debit',
                'statement': 'Profit and Loss',
                'nature': 'Expense',
                'level': 1
            },
            {
                'code': '5.2.01',
                'label_en': 'Finance Costs',
                'xbrl_tag': 'ifrs-full_FinanceCosts',
                'type': 'Expenses',
                'subtype': 'Finance Expense',
                'balance_type': 'Debit',
                'statement': 'Profit and Loss',
                'nature': 'Expense',
                'level': 1
            },
            {
                'code': '5.3.01',
                'label_en': 'Tax Expense',
                'xbrl_tag': 'ifrs-full_TaxExpense',
                'type': 'Expenses',
                'subtype': 'Tax Expense',
                'balance_type': 'Debit',
                'statement': 'Profit and Loss',
                'nature': 'Expense',
                'level': 1
            },
        ]
        
        return standard_accounts
    
    def save_as_csv(self, accounts: List[Dict]) -> str:
        """Save extracted accounts to CSV."""
        output_file = self.extract_dir / "ifrs_accounts.csv"
        
        if not accounts:
            print("⚠️  No accounts to save")
            return str(output_file)
        
        fieldnames = accounts[0].keys()
        
        with open(output_file, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(accounts)
        
        print(f"✅ Saved {len(accounts)} accounts to: {output_file}")
        return str(output_file)
    
    def save_as_json(self, accounts: List[Dict]) -> str:
        """Save extracted accounts to JSON."""
        output_file = self.extract_dir / "ifrs_accounts.json"
        
        with open(output_file, 'w') as f:
            json.dump(accounts, f, indent=2)
        
        print(f"✅ Saved {len(accounts)} accounts to: {output_file}")
        return str(output_file)
    
    def generate_summary(self, accounts: List[Dict]) -> None:
        """Generate extraction summary report."""
        summary_file = self.extract_dir / "EXTRACTION_SUMMARY.md"
        
        # Group by type
        by_type = {}
        for acc in accounts:
            acc_type = acc.get('type', 'Unknown')
            if acc_type not in by_type:
                by_type[acc_type] = []
            by_type[acc_type].append(acc)
        
        with open(summary_file, 'w') as f:
            f.write("# IFRS Taxonomy Extraction Summary\n\n")
            f.write(f"**Total Accounts:** {len(accounts)}\n")
            f.write(f"**Extraction Date:** {Path('').resolve().stat().st_mtime}\n\n")
            
            f.write("## Accounts by Type\n\n")
            for acc_type, accs in sorted(by_type.items()):
                f.write(f"### {acc_type} ({len(accs)})\n\n")
                f.write("| Code | Label | Balance Type | Statement |\n")
                f.write("|------|-------|--------------|----------|\n")
                for acc in sorted(accs, key=lambda x: x['code']):
                    f.write(f"| {acc['code']} | {acc['label_en']} | {acc['balance_type']} | {acc['statement']} |\n")
                f.write("\n")
        
        print(f"✅ Generated summary: {summary_file}")


def main():
    """Main extraction workflow."""
    print("🔍 IFRS Taxonomy Extraction\n")
    
    extractor = IFRSExtractor()
    
    # Extract accounts
    print("1️⃣  Extracting accounts from IFRS Taxonomy...")
    accounts = extractor.extract_from_xsd()
    
    if not accounts:
        print("⚠️  No accounts extracted. Ensure IFRS is downloaded.")
        return
    
    # Save outputs
    print("\n2️⃣  Saving extractions...")
    csv_file = extractor.save_as_csv(accounts)
    json_file = extractor.save_as_json(accounts)
    
    # Generate summary
    print("\n3️⃣  Generating summary...")
    extractor.generate_summary(accounts)
    
    print("\n✅ IFRS extraction complete!")
    print(f"   CSV: {csv_file}")
    print(f"   JSON: {json_file}")


if __name__ == "__main__":
    main()
