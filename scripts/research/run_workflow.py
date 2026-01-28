#!/usr/bin/env python3
"""
Research Extraction Workflow

Coordinates extraction of accounts from all sources:
1. IFRS Taxonomy (international standard)
2. Mexico SAT (national standard)
3. Colombia DIAN (national standard)
4. Panama DGI (national standard)

Creates mappings and comparative analysis.
"""

import os
import subprocess
import json
import csv
from pathlib import Path
from datetime import datetime
import sys

class ResearchWorkflow:
    def __init__(self):
        self.repo_root = Path(__file__).parent.parent.parent
        self.research_dir = self.repo_root / "research"
        self.bibliography_dir = self.repo_root / "bibliography"
        self.scripts_dir = self.repo_root / "scripts" / "research"
        
        self.log_file = self.research_dir / "WORKFLOW_LOG.md"
        self.progress_file = self.research_dir / "WORKFLOW_PROGRESS.json"
    
    def log(self, message: str, level: str = "INFO") -> None:
        """Log message with timestamp."""
        timestamp = datetime.now().isoformat()
        print(f"[{level}] {message}")
        
        with open(self.log_file, 'a') as f:
            f.write(f"[{timestamp}] [{level}] {message}\n")
    
    def check_ifrs_download(self) -> bool:
        """Check if IFRS has been downloaded and extracted."""
        ifrs_file = self.bibliography_dir / "primary_sources" / "ifrs" / "ifrs-taxonomy-2024.zip"
        ifrs_dir = self.bibliography_dir / "primary_sources" / "ifrs" / "ifrs-taxonomy-2024"
        
        if not ifrs_file.exists():
            self.log("⚠️  IFRS Taxonomy ZIP not found", "WARNING")
            return False
        
        file_size_mb = ifrs_file.stat().st_size / (1024*1024)
        self.log(f"✅ IFRS Taxonomy found: {file_size_mb:.1f} MB", "INFO")
        
        if not ifrs_dir.exists():
            self.log("📦 IFRS needs extraction...", "INFO")
            return self.extract_ifrs_zip()
        
        self.log("✅ IFRS already extracted", "INFO")
        return True
    
    def extract_ifrs_zip(self) -> bool:
        """Extract IFRS Taxonomy ZIP file."""
        self.log("🔄 Extracting IFRS Taxonomy...", "INFO")
        
        ifrs_zip = self.bibliography_dir / "primary_sources" / "ifrs" / "ifrs-taxonomy-2024.zip"
        ifrs_dir = ifrs_zip.parent
        
        try:
            subprocess.run(
                ["unzip", "-q", str(ifrs_zip), "-d", str(ifrs_dir)],
                check=True,
                timeout=120
            )
            self.log("✅ IFRS Taxonomy extracted", "INFO")
            return True
        except subprocess.TimeoutExpired:
            self.log("❌ IFRS extraction timeout", "ERROR")
            return False
        except subprocess.CalledProcessError as e:
            self.log(f"❌ IFRS extraction failed: {e}", "ERROR")
            return False
    
    def run_ifrs_extraction(self) -> bool:
        """Run IFRS account extraction."""
        self.log("📖 Running IFRS extraction script...", "INFO")
        
        extract_script = self.scripts_dir / "extract_ifrs.py"
        
        try:
            result = subprocess.run(
                ["python3", str(extract_script)],
                cwd=str(self.repo_root),
                capture_output=True,
                text=True,
                timeout=300
            )
            
            self.log(result.stdout, "INFO")
            
            if result.returncode != 0:
                self.log(f"❌ IFRS extraction failed: {result.stderr}", "ERROR")
                return False
            
            self.log("✅ IFRS extraction complete", "INFO")
            return True
        
        except Exception as e:
            self.log(f"❌ Error running IFRS extraction: {e}", "ERROR")
            return False
    
    def check_country_files(self) -> dict:
        """Check if country PDFs are downloaded."""
        countries = {
            'mexico': self.bibliography_dir / "primary_sources" / "mx_sat" / "catalogo_cuentas_2024.pdf",
            'colombia': self.bibliography_dir / "primary_sources" / "co_puc" / "puc_2024.pdf",
            'panama': self.bibliography_dir / "primary_sources" / "pa_dgi_smv" / "plan_cuentas_2024.pdf",
        }
        
        status = {}
        for country, filepath in countries.items():
            if filepath.exists():
                size_mb = filepath.stat().st_size / (1024*1024)
                status[country] = {'exists': True, 'size_mb': size_mb}
                self.log(f"✅ {country.upper()} PDF found: {size_mb:.1f} MB", "INFO")
            else:
                status[country] = {'exists': False, 'size_mb': 0}
                self.log(f"⚠️  {country.upper()} PDF not found: {filepath}", "WARNING")
        
        return status
    
    def generate_status_report(self) -> None:
        """Generate current status report."""
        report = self.research_dir / "STATUS_REPORT.md"
        
        # Check downloads
        ifrs_exists = (self.bibliography_dir / "primary_sources" / "ifrs" / "ifrs-taxonomy-2024.zip").exists()
        country_status = self.check_country_files()
        
        with open(report, 'w') as f:
            f.write("# Research Workflow Status\n\n")
            f.write(f"**Last Updated:** {datetime.now().isoformat()}\n\n")
            
            f.write("## Downloads Status\n\n")
            f.write(f"### IFRS Taxonomy\n")
            f.write(f"- Status: {'✅ Downloaded' if ifrs_exists else '⏳ In Progress'}\n")
            f.write(f"- Size: ~500 MB\n")
            f.write(f"- Location: `bibliography/primary_sources/ifrs/`\n\n")
            
            for country, status in country_status.items():
                exists = status['exists']
                size = status['size_mb']
                f.write(f"### {country.upper()}\n")
                f.write(f"- Status: {'✅ Downloaded' if exists else '⏳ Pending'}\n")
                if exists:
                    f.write(f"- Size: {size:.1f} MB\n")
                f.write(f"- Location: `bibliography/primary_sources/{country}_*/`\n\n")
            
            f.write("## Next Steps\n\n")
            if ifrs_exists:
                f.write("1. ✅ IFRS downloaded - ready for extraction\n")
            else:
                f.write("1. ⏳ IFRS download in progress\n")
            
            pending_countries = [c for c, s in country_status.items() if not s['exists']]
            if pending_countries:
                f.write(f"2. ⏳ Download: {', '.join(pending_countries).upper()} PDFs\n")
            else:
                f.write("2. ✅ All PDFs downloaded\n")
            
            f.write("3. Extract and map to Kontablo accounts\n")
            f.write("4. Create comparative analysis\n")
        
        print(f"\n📊 Status report: {report}")
    
    def run_workflow(self) -> None:
        """Execute full research workflow."""
        print("\n" + "="*70)
        print("🔬 RESEARCH EXTRACTION WORKFLOW")
        print("="*70 + "\n")
        
        # Initialize log
        with open(self.log_file, 'w') as f:
            f.write(f"# Workflow Log - {datetime.now().isoformat()}\n\n")
        
        self.log("🚀 Starting research workflow", "INFO")
        
        # Step 1: Check IFRS
        self.log("\n📋 STEP 1: Checking IFRS Taxonomy...", "INFO")
        ifrs_ready = self.check_ifrs_download()
        
        # Step 2: Check country files
        self.log("\n📋 STEP 2: Checking country PDFs...", "INFO")
        country_status = self.check_country_files()
        
        # Step 3: Extract IFRS
        if ifrs_ready:
            self.log("\n📋 STEP 3: Extracting IFRS accounts...", "INFO")
            self.run_ifrs_extraction()
        else:
            self.log("⏳ Waiting for IFRS download to complete", "WARNING")
        
        # Step 4: Generate status
        self.log("\n📋 STEP 4: Generating status report...", "INFO")
        self.generate_status_report()
        
        self.log("\n✅ Workflow checkpoint complete", "INFO")
        self.log("Next: Download country PDFs (Steps in QUICK_START.md)\n", "INFO")


def main():
    """Main entry point."""
    try:
        workflow = ResearchWorkflow()
        workflow.run_workflow()
    except KeyboardInterrupt:
        print("\n⚠️  Workflow interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Workflow error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
