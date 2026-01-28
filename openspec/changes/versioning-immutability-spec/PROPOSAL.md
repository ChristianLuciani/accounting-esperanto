# OpenSpec: Versioning & Immutability Specification

**Change ID:** versioning-immutability-spec  
**Status:** Proposal  
**Date:** January 27, 2026  
**Phase:** Phase 0 (Concept), Phase 3 (Implementation)

---

## 📋 Proposal: Tracking Changes & Ensuring Immutability

### Problem
- Version "0.1.0" exists but no change protocol
- Can't track who changed what and why
- No immutability guarantee (anyone could modify accounts)
- Critical for audit trail

### Solution
- **Phase 0:** Document versioning protocol (concept only)
- **Phase 3:** Implement blockchain anchoring for immutability

### Current Scope: Phase 0 (Concept Documentation)

---

## 🎯 Design: Version Protocol

### Semantic Versioning for Kontablo

```
MAJOR.MINOR.PATCH

Example: 0.1.2

- MAJOR: Breaking changes (UUID deprecated, etc.)
- MINOR: New features (new Level 3 accounts)
- PATCH: Bug fixes (corrected XBRL tag)
```

### Version Rules

```yaml
versioning_protocol:
  
  # Rule 1: Never change UUIDs
  immutable_properties:
    - uuid: "NEVER CHANGE - is permanent identifier"
    - code: "MAY CHANGE - is display/human-readable"
    - label_en: "MAY CHANGE - better wording"
  
  # Rule 2: Breaking changes = MAJOR bump
  breaking_changes:
    - Delete a UUID
    - Change UUID of existing account
    - Remove country from mapping
    - Change aggregation formula fundamentally
  
  trigger_major_bump: "any_breaking_change"
  example: "0.1.0 → 1.0.0"
  
  # Rule 3: New features = MINOR bump
  non_breaking_changes:
    - Add new Level 3 accounts
    - Add country mapping
    - Add language (new label_es)
    - Clarify label (better wording)
  
  trigger_minor_bump: "any_new_feature"
  example: "0.1.0 → 0.2.0"
  
  # Rule 4: Corrections = PATCH bump
  bug_fixes:
    - Fix XBRL tag typo
    - Correct aggregation formula (was wrong)
    - Fix translation error
  
  trigger_patch_bump: "bug_fix"
  example: "0.1.0 → 0.1.1"
```

---

## 📝 Change Log Format

### CHANGELOG.md Structure

```markdown
# Kontablo Specification Changelog

## [0.2.0] - 2026-02-15 (Hypothetical Future)

### Added
- Colombia PUC country mapping (120+ accounts)
- Panama DGI/SMV mapping (100+ accounts)
- Spanish translations for all Level 3 accounts
- Portuguese translations for Brazil

### Changed
- Updated Mexico SAT codes for 2026 fiscal year
- Refined Cash aggregation rule based on expert feedback

### Fixed
- Corrected XBRL tag for ifrs-full:GoodwillImpairment
- Fixed typo in label_en for account 2.1.08

### Deprecated
- Old format YAML (use JSON schema instead)

---

## [0.1.0] - 2026-01-27 (Current)

### Added
- Initial Level 1-2 account structure
- Level 3 accounts (80-100 accounts)
- Mexico SAT mapping
- Simple aggregation rules (SUM, AVG, WEIGHTED_SUM)
- Versioning protocol (this document)

### To-Do (Phase 2+)
- Conditional aggregation logic
- Blockchain anchoring implementation
```

---

## 🏷️ Version Metadata in Accounts

### Each Account Tracks Its History

```yaml
account:
  uuid: "550e8400-e29b-41d4-a716-446655440000"
  code: "1.1.01"
  label_en: "Cash and Cash Equivalents"
  
  # Version tracking
  version_info:
    introduced_in: "0.1.0"    # First appearance
    current_version: "0.1.0"  # Still current
    deprecated_in: null       # Not deprecated
    removed_in: null          # Not removed
  
  # Change history
  change_history:
    - version: "0.1.0"
      date: "2026-01-27"
      change: "Initial creation"
      author: "kontablo-ai"
      source: "IFRS extraction"
    
    # Hypothetical future changes
    - version: "0.2.0"
      date: "2026-02-15"
      change: "Added Spanish & Portuguese labels"
      author: "eva@kontablo.org"
      source: "Expert review"
    
    - version: "0.2.1"
      date: "2026-02-20"
      change: "Fixed XBRL tag (was 'ifrs-full:CashAndEquivalent', now 'ifrs-full:CashAndCashEquivalents')"
      author: "eva@kontablo.org"
      source: "XBRL compliance check"
  
  # Auditable properties
  audit_info:
    created_by: "kontablo-ai"
    created_date: "2026-01-27T14:32:00Z"
    last_modified_by: "eva@kontablo.org"
    last_modified_date: "2026-02-20T10:15:00Z"
    git_commit_hash: "abc123def456..."  # Link to git commit
    reviewed_by: "eva"
    review_date: "2026-01-27"
```

---

## 🔄 Deprecation Process

### How to deprecate an account (without breaking things)

```yaml
# Step 1: Mark as deprecated (introduces in minor version)
account:
  uuid: "old-uuid-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
  code: "1.1.01"
  label_en: "Cash (Deprecated)"
  
  version_info:
    deprecated_in: "0.3.0"
    removal_planned_in: "1.0.0"  # Major version
  
  deprecation_notice:
    reason: "Merged with 1.1.02 for simplicity"
    replacement_uuid: "new-uuid-yyyy-yyyy-yyyy-yyyyyyyyyyyy"
    replacement_code: "1.1.02"
    migration_instructions: |
      Old code 1.1.01 will be merged into 1.1.02.
      All old accounts will be automatically reclassified.
      No manual action needed.

# Step 2: Maintain in dual format (during deprecation period)
# Old clients still work, but show warnings

# Step 3: Remove in MAJOR version (breaking change)
# 0.3.0 → 1.0.0: old UUID completely removed
```

---

## 🔐 Phase 0: Blockchain Readiness (Concept)

### UUID Immutability Guarantee

```yaml
blockchain_readiness:
  phase_0_status: "CONCEPT"
  
  what_we_guarantee_now:
    - "UUIDs will never change"
    - "Old versions archived forever in git"
    - "All changes tracked in CHANGELOG.md"
    - "Each version has git commit hash"
  
  what_blockchain_will_add_phase_3:
    - "Immutable proof on Ethereum"
    - "Third-party verification"
    - "Audit trail cannot be modified"
    - "Timestamps sealed on-chain"

  future_blockchain_spec:
    network: "ethereum_or_polygon"
    contract: "KontabloRegistry"
    data_stored: "version_hash"
    
    example:
      version: "0.1.0"
      content_hash: "sha256(all_accounts)"
      blockchain_tx: "0x..."
      stored_on: "ethereum:mainnet"
      timestamp: "2026-01-27T14:32:00Z"
```

---

## 📋 Change Control Process

### How changes get approved (Phase 0)

```
1. Proposal
   └─ Create openspec proposal with change reason

2. Technical Review
   └─ Check for breaking changes
   └─ Validate XBRL tags
   └─ Verify country mappings

3. Expert Review (Eva)
   └─ Domain knowledge check
   └─ Accounting correctness
   └─ Industry best practices

4. Implementation
   └─ Update YAML/JSON files
   └─ Run validation script
   └─ Create git commit

5. Versioning
   └─ Bump version (MAJOR/MINOR/PATCH)
   └─ Update CHANGELOG.md
   └─ Tag git release

6. Archive
   └─ Store old version in archive/
   └─ Keep git history forever
   └─ Document migration path
```

---

## 🔧 Implementation Tasks (Phase 0)

- [x] Create CHANGELOG.md
- [x] Document versioning protocol
- [x] Add version fields to all accounts
- [x] Document deprecation process
- [x] Create change control workflow

### Phase 3 Tasks (Blockchain)

- [ ] Design smart contract
- [ ] Deploy to Ethereum/Polygon
- [ ] Create hash anchoring process
- [ ] Build verification API

---

## ✅ Success Criteria (Phase 0)

- [x] Versioning protocol documented
- [x] Deprecation process defined
- [x] Version tracking in accounts
- [x] Change log exists
- [x] Blockchain concept documented
- [x] No breaking changes in Phase 0

---

## 📅 Timeline

- **Today:** Document this spec
- **Week 1-4:** Maintain as 0.1.0
- **Week 5-8:** Upgrade to 0.2.0 (new features)
- **Month 4+:** Consider 1.0.0 if major changes

**Phase 3 (Weeks 9+):** Blockchain implementation

---

## 📦 Immutability Guarantees by Phase

| Phase | Guarantee | Method | Proof |
|-------|-----------|--------|-------|
| **0** | UUIDs never change | Git + CHANGELOG | Git history |
| **1** | Versions tracked | Semantic versioning | Version tags |
| **2** | Deprecation process | Formal workflow | Approval log |
| **3** | Blockchain anchoring | Smart contract | Ethereum proof |

