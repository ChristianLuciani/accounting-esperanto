#!/usr/bin/env python3
"""
Bibliography Verification Script
Validates all research data sources with SHA-256 hashing and metadata tracking.

Usage:
    python scripts/research/verify_bibliography.py
    python scripts/research/verify_bibliography.py --status
    python scripts/research/verify_bibliography.py --verify [source]
"""

import os
import hashlib
import yaml
import json
from pathlib import Path
from datetime import datetime
import argparse
from typing import Dict, List, Optional

class BibliographyVerifier:
    def __init__(self, repo_root: str = None):
        """Initialize bibliography verifier."""
        if repo_root is None:
            repo_root = Path(__file__).parent.parent.parent
        self.repo_root = Path(repo_root)
        self.bib_path = self.repo_root / "bibliography"
        self.primary_sources = self.bib_path / "primary_sources"
        
    def calculate_hash(self, file_path: Path) -> str:
        """Calculate SHA-256 hash of a file."""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    
    def verify_source(self, source_name: str) -> Dict:
        """Verify a single bibliography source."""
        source_path = self.primary_sources / source_name
        
        if not source_path.exists():
            return {
                "source": source_name,
                "status": "NOT_FOUND",
                "path": str(source_path),
                "message": f"Directory not found: {source_path}"
            }
        
        # Find main source file (PDF or ZIP)
        source_files = list(source_path.glob("*.pdf")) + list(source_path.glob("*.zip"))
        
        if not source_files:
            return {
                "source": source_name,
                "status": "NO_FILES",
                "path": str(source_path),
                "message": "No PDF or ZIP files found"
            }
        
        main_file = source_files[0]  # Assume first file is primary
        
        # Calculate hash
        try:
            calculated_hash = self.calculate_hash(main_file)
        except Exception as e:
            return {
                "source": source_name,
                "status": "ERROR",
                "message": f"Failed to calculate hash: {str(e)}"
            }
        
        # Check for metadata
        meta_file = source_path / f"{main_file.stem}.meta.yaml"
        
        result = {
            "source": source_name,
            "file": main_file.name,
            "file_size_mb": round(main_file.stat().st_size / (1024*1024), 2),
            "hash_sha256": calculated_hash,
            "hash_matches": False,
            "metadata_exists": meta_file.exists()
        }
        
        if meta_file.exists():
            try:
                with open(meta_file, 'r') as f:
                    metadata = yaml.safe_load(f)
                    stored_hash = metadata.get("file_hash_sha256", "")
                    result["hash_matches"] = stored_hash == calculated_hash
                    result["metadata"] = metadata
                    result["status"] = "VERIFIED" if result["hash_matches"] else "HASH_MISMATCH"
            except Exception as e:
                result["status"] = "METADATA_ERROR"
                result["message"] = f"Failed to read metadata: {str(e)}"
        else:
            result["status"] = "NO_METADATA"
        
        return result
    
    def verify_all(self) -> Dict:
        """Verify all bibliography sources."""
        sources = [
            "ifrs",
            "mx_sat",
            "co_puc",
            "pa_dgi_smv"
        ]
        
        results = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "repository": str(self.repo_root),
            "sources": {}
        }
        
        for source in sources:
            results["sources"][source] = self.verify_source(source)
        
        return results
    
    def print_status(self, results: Dict) -> None:
        """Print status report."""
        print("\n" + "="*70)
        print("📚 BIBLIOGRAPHY VERIFICATION REPORT")
        print("="*70)
        print(f"Timestamp: {results['timestamp']}")
        print(f"Repository: {results['repository']}\n")
        
        verified_count = 0
        missing_count = 0
        error_count = 0
        
        for source_name, result in results['sources'].items():
            status = result.get('status', 'UNKNOWN')
            
            # Status symbols
            if status == 'VERIFIED':
                symbol = "✅"
                verified_count += 1
            elif status in ['NOT_FOUND', 'NO_FILES', 'NO_METADATA']:
                symbol = "❌"
                missing_count += 1
            else:
                symbol = "⚠️"
                error_count += 1
            
            # Print source line
            file_info = f" ({result.get('file')})" if 'file' in result else ""
            size_info = f" - {result.get('file_size_mb')} MB" if 'file_size_mb' in result else ""
            print(f"{symbol} {source_name.upper()}{file_info}{size_info}")
            
            # Print details
            if status == 'VERIFIED':
                print(f"   ✓ Hash verified: {result['hash_sha256'][:16]}...")
            elif status == 'HASH_MISMATCH':
                print(f"   ✗ Hash mismatch!")
                print(f"   Stored:      {result['metadata'].get('file_hash_sha256', 'N/A')[:16]}...")
                print(f"   Calculated:  {result['hash_sha256'][:16]}...")
            elif status == 'NO_METADATA':
                print(f"   ⚠️  No metadata file - run: verify_bibliography.py --create-metadata {source_name}")
            else:
                print(f"   {result.get('message', 'Unknown status')}")
            print()
        
        # Summary
        print("="*70)
        print(f"Summary: {verified_count} ✅ | {missing_count} ❌ | {error_count} ⚠️")
        print("="*70 + "\n")
    
    def create_metadata_template(self, source_name: str, file_path: Path) -> None:
        """Create metadata YAML template for a source file."""
        calculated_hash = self.calculate_hash(file_path)
        
        metadata = {
            "source_id": f"{source_name}_2024",
            "jurisdiction": self._get_jurisdiction(source_name),
            "type": "primary_standard",
            "authority": self._get_authority(source_name),
            "standard_name": self._get_standard_name(source_name),
            "standard_version": "2024",
            "download_date": datetime.utcnow().isoformat() + "Z",
            "file_name": file_path.name,
            "file_size_mb": round(file_path.stat().st_size / (1024*1024), 2),
            "file_hash_sha256": calculated_hash,
            "file_hash_algorithm": "SHA-256",
            "notes": f"Downloaded for Phase 0 research. Used for Level 3 account extraction."
        }
        
        meta_file = file_path.parent / f"{file_path.stem}.meta.yaml"
        with open(meta_file, 'w') as f:
            yaml.dump(metadata, f, default_flow_style=False, sort_keys=False)
        
        print(f"✅ Created metadata: {meta_file.name}")
        print(f"   Hash: {calculated_hash}")
    
    def _get_jurisdiction(self, source_name: str) -> str:
        """Get jurisdiction from source name."""
        mapping = {
            "ifrs": "international",
            "mx_sat": "mexico",
            "co_puc": "colombia",
            "pa_dgi_smv": "panama"
        }
        return mapping.get(source_name, "unknown")
    
    def _get_authority(self, source_name: str) -> str:
        """Get authority from source name."""
        mapping = {
            "ifrs": "IFRS Foundation",
            "mx_sat": "Servicio de Administración Tributaria (SAT)",
            "co_puc": "Dirección de Impuestos y Aduanas Nacionales (DIAN)",
            "pa_dgi_smv": "Dirección General de Ingresos (DGI)"
        }
        return mapping.get(source_name, "Unknown Authority")
    
    def _get_standard_name(self, source_name: str) -> str:
        """Get standard name from source name."""
        mapping = {
            "ifrs": "IFRS Taxonomy",
            "mx_sat": "Catálogo de Cuentas",
            "co_puc": "Plan Única de Cuentas",
            "pa_dgi_smv": "Plan de Cuentas"
        }
        return mapping.get(source_name, "Unknown Standard")


def main():
    parser = argparse.ArgumentParser(
        description="Verify bibliography sources with SHA-256 hashing"
    )
    parser.add_argument(
        "--status",
        action="store_true",
        help="Show verification status of all sources"
    )
    parser.add_argument(
        "--verify",
        metavar="SOURCE",
        help="Verify a specific source (e.g., ifrs, mx_sat, co_puc, pa_dgi_smv)"
    )
    parser.add_argument(
        "--create-metadata",
        metavar="SOURCE",
        help="Create metadata file for a source"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output as JSON"
    )
    
    args = parser.parse_args()
    
    verifier = BibliographyVerifier()
    
    if args.create_metadata:
        # Find and create metadata for source
        source_path = verifier.primary_sources / args.create_metadata
        files = list(source_path.glob("*.pdf")) + list(source_path.glob("*.zip"))
        if files:
            verifier.create_metadata_template(args.create_metadata, files[0])
        else:
            print(f"❌ No files found in {source_path}")
    
    elif args.verify:
        result = verifier.verify_source(args.verify)
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            verifier.print_status({"timestamp": datetime.utcnow().isoformat() + "Z",
                                  "repository": str(verifier.repo_root),
                                  "sources": {args.verify: result}})
    
    else:  # Default: verify all
        results = verifier.verify_all()
        if args.json:
            print(json.dumps(results, indent=2))
        else:
            verifier.print_status(results)


if __name__ == "__main__":
    main()
