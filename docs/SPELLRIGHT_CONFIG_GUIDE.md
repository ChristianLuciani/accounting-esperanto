# 🔤 Spellright Configuration Guide

**Issue:** VS Code's `spellright` extension flagging valid domain-specific terms  
**Solution:** Created `.spellright.json` configuration file

---

## What We Fixed

Created `.spellright.json` to suppress spellright errors by:

1. **Ignoring domain-specific words:**
   - Project names: `Kontablo`, `OpenSpec`, `Antigravity`, `Infisical`
   - Geographic locations: `Mexico`, `Colombia`, `Panama`
   - Accounting standards: `IFRS`, `SAT`, `DIAN`, `DGI`
   - Technical terms: `blockchain`, `immutability`, `aggregation`, `ontology`

2. **Ignoring patterns:**
   - CamelCase words (e.g., `OpenRouter`, `Cerebras`)
   - All-caps abbreviations (e.g., `XBRL`, `DIAN`)

3. **Disabling in Markdown:**
   - `ignoreWordsInMarkdown: true` - Reduces false positives in `.md` files

---

## How Spellright Works

The `spellright` extension checks:
- English/multiple languages depending on configuration
- Against a built-in dictionary + your custom word list

**Key differences from markdownlint:**
- ✅ **Markdownlint** = formatting rules (blanks around headings, lists)
- ✅ **Spellright** = spell-checking (dictionary-based word validation)

---

## If You Still See Errors

### Option 1: Add More Words
Edit `.spellright.json` and add words to `ignoreWords` array:

```json
"ignoreWords": [
  "mySpecialTerm",
  "anotherDomainWord"
]
```

### Option 2: Disable for Specific Files
VS Code settings (`settings.json`):

```json
{
  "spellright.ignoreFiles": [
    "**/Q3_AGGREGATION_CONSEQUENCES.md"
  ]
}
```

### Option 3: Disable Spellright Entirely
Uninstall or disable the extension if spell-checking isn't needed.

---

## The Config File

**Location:** `.spellright.json` (root of repo)

**Key settings:**
- `language`: "en" - English dictionary
- `ignoreWords`: Array of words to skip
- `ignoreRegexps`: Regex patterns (CamelCase, ALL_CAPS, etc.)
- `ignoreWordsInMarkdown`: Don't check markdown files
- `documentTypes`: Apply to these file types

---

## Common Issues

| Issue | Solution |
|-------|----------|
| Still seeing red squiggles | Reload VS Code (`Cmd+Shift+P` → "Reload Window") |
| Need to ignore a whole category | Use `ignoreRegexps` with pattern |
| Want to allow contractions | They're built-in (e.g., "don't", "you're") |
| Emoji flagged as spelling error | Ignore - spellright can't handle emojis |

---

## Verification

After creating `.spellright.json`:

1. ✅ Reload VS Code
2. ✅ Open `Q3_AGGREGATION_CONSEQUENCES.md`
3. ✅ Spellright errors should be suppressed
4. ✅ You may see a few remaining (legitimate typos)

---

## When to Use Each Tool

| Tool | Purpose | Example |
|------|---------|---------|
| **Markdownlint** | Formatting standards | "Heading must have blank line before it" |
| **Spellright** | Spell-checking | "Aggregation is not a recognized word" |
| **VS Code** built-in | Syntax highlighting | Markdown, code blocks |

---

**Status:** ✅ **Fixed**  
**File:** `.spellright.json` created in repo root  
**Action:** Reload VS Code to apply
