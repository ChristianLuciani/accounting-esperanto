#!/usr/bin/env bash
# 🔬 Research Command Reference
# 
# Quick access to all research scripts and monitoring commands
# For complete documentation, see bibliography/QUICK_START.md

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Get repository root
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# ============================================================================
# MONITORING COMMANDS
# ============================================================================

monitor_ifrs_download() {
    echo -e "${BLUE}📊 IFRS Download Status:${NC}"
    IFRS_FILE="$REPO_ROOT/bibliography/primary_sources/ifrs/ifrs-taxonomy-2024.zip"
    
    if [ -f "$IFRS_FILE" ]; then
        SIZE_KB=$(du -k "$IFRS_FILE" | cut -f1)
        SIZE_MB=$(echo "scale=2; $SIZE_KB / 1024" | bc)
        PERCENT=$(echo "scale=1; $SIZE_MB / 500 * 100" | bc)
        
        echo "File: $(basename $IFRS_FILE)"
        echo "Size: ${SIZE_MB} MB / 500 MB"
        echo "Progress: ${PERCENT}%"
        
        if (( $(echo "$SIZE_MB >= 499" | bc -l) )); then
            echo -e "${GREEN}✅ Download complete!${NC}"
            return 0
        else
            echo -e "${YELLOW}⏳ Still downloading...${NC}"
            return 1
        fi
    else
        echo -e "${YELLOW}⏳ Download started but file not yet visible${NC}"
        return 1
    fi
}

monitor_country_downloads() {
    echo -e "${BLUE}📊 Country PDFs Status:${NC}"
    
    local FILES=(
        "bibliography/primary_sources/mx_sat/catalogo_cuentas_2024.pdf:Mexico SAT"
        "bibliography/primary_sources/co_puc/puc_2024.pdf:Colombia DIAN"
        "bibliography/primary_sources/pa_dgi_smv/plan_cuentas_2024.pdf:Panama DGI"
    )
    
    for file_pair in "${FILES[@]}"; do
        FILE="${file_pair%:*}"
        LABEL="${file_pair#*:}"
        FULL_PATH="$REPO_ROOT/$FILE"
        
        if [ -f "$FULL_PATH" ]; then
            SIZE=$(du -h "$FULL_PATH" | cut -f1)
            echo -e "${GREEN}✅${NC} $LABEL: $SIZE"
        else
            echo -e "${YELLOW}⏳${NC} $LABEL: Not downloaded"
        fi
    done
}

monitor_all_downloads() {
    echo -e "${BLUE}=== DOWNLOAD MONITORING ===${NC}\n"
    monitor_ifrs_download
    echo
    monitor_country_downloads
    echo
}

# ============================================================================
# EXTRACTION COMMANDS
# ============================================================================

extract_ifrs() {
    echo -e "${BLUE}📖 Extracting IFRS Taxonomy...${NC}"
    python3 "$REPO_ROOT/scripts/research/extract_ifrs.py"
}

run_full_workflow() {
    echo -e "${BLUE}🔄 Running Full Workflow...${NC}"
    python3 "$REPO_ROOT/scripts/research/run_workflow.py"
}

verify_sources() {
    echo -e "${BLUE}🔐 Verifying Bibliography Sources...${NC}"
    python3 "$REPO_ROOT/scripts/research/verify_bibliography.py"
}

verify_source() {
    if [ -z "$1" ]; then
        echo "Usage: research verify-source <ifrs|mx_sat|co_puc|pa_dgi_smv>"
        return 1
    fi
    python3 "$REPO_ROOT/scripts/research/verify_bibliography.py" --verify "$1"
}

create_metadata() {
    if [ -z "$1" ]; then
        echo "Usage: research create-metadata <source_name>"
        return 1
    fi
    python3 "$REPO_ROOT/scripts/research/verify_bibliography.py" --create-metadata "$1"
}

# ============================================================================
# INFORMATION COMMANDS
# ============================================================================

show_status() {
    echo -e "${BLUE}=== RESEARCH STATUS ===${NC}\n"
    
    echo -e "${YELLOW}📥 Downloads:${NC}"
    monitor_all_downloads
    
    if [ -f "$REPO_ROOT/research/STATUS_REPORT.md" ]; then
        echo -e "${YELLOW}📋 Latest Status Report:${NC}"
        head -30 "$REPO_ROOT/research/STATUS_REPORT.md"
        echo "..."
    fi
    
    echo -e "\n${YELLOW}📊 Research Timeline:${NC}"
    echo "Week 1 (Jan 28-Feb 1): Bibliography gathering"
    echo "Week 2 (Feb 3-7): Account extraction"
    echo "Week 3 (Feb 8-12): Mapping & validation"
}

show_extraction_progress() {
    echo -e "${BLUE}=== EXTRACTION PROGRESS ===${NC}\n"
    cat "$REPO_ROOT/research/EXTRACTION_PROGRESS.md"
}

show_quick_start() {
    echo -e "${BLUE}=== QUICK START GUIDE ===${NC}\n"
    cat "$REPO_ROOT/bibliography/QUICK_START.md"
}

show_help() {
    cat << 'EOF'
🔬 RESEARCH COMMAND REFERENCE

MONITORING:
  research monitor         - Check all download progress
  research monitor-ifrs    - Check IFRS download only
  research monitor-pdfs    - Check country PDF downloads

EXTRACTION:
  research extract-ifrs    - Extract IFRS accounts to CSV/JSON
  research workflow        - Run complete workflow coordinator
  research verify          - Verify all sources with SHA-256
  research verify <name>   - Verify specific source (ifrs|mx_sat|co_puc|pa_dgi_smv)
  research create-metadata <name> - Create metadata for source

INFORMATION:
  research status          - Show current research status
  research progress        - Show extraction progress
  research quick-start     - Show download instructions
  research help            - Show this message

EXAMPLES:
  # Monitor download progress
  research monitor
  
  # Extract IFRS once download completes
  research extract-ifrs
  
  # Verify Mexico SAT PDF
  research verify mx_sat
  
  # Check overall progress
  research progress

For more details, see:
  - bibliography/QUICK_START.md - How to download sources
  - research/RESEARCH_EXECUTION_PLAN.md - Full timeline
  - research/EXTRACTION_PROGRESS.md - Current progress
EOF
}

# ============================================================================
# MAIN
# ============================================================================

main() {
    cd "$REPO_ROOT"
    
    case "${1:-help}" in
        # Monitoring
        monitor)
            monitor_all_downloads
            ;;
        monitor-ifrs)
            monitor_ifrs_download
            ;;
        monitor-pdfs)
            monitor_country_downloads
            ;;
        
        # Extraction
        extract-ifrs)
            extract_ifrs
            ;;
        workflow)
            run_full_workflow
            ;;
        verify)
            verify_sources
            ;;
        verify-source)
            verify_source "$2"
            ;;
        create-metadata)
            create_metadata "$2"
            ;;
        
        # Information
        status)
            show_status
            ;;
        progress)
            show_extraction_progress
            ;;
        quick-start)
            show_quick_start
            ;;
        help)
            show_help
            ;;
        *)
            echo -e "${RED}Unknown command: $1${NC}"
            echo "Use 'research help' for command list"
            exit 1
            ;;
    esac
}

main "$@"
