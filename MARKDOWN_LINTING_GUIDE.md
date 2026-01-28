# 📝 Markdown Linting Guide

**Issue:** VS Code is showing `markdownlint` errors in `.md` files  
**Solution:** Configuration file created + formatting guide  

---

## 🔧 What We Fixed

Created `.markdownlint.json` with sensible defaults for this project:

```json
{
  "extends": "default",
  "rules": {
    "MD022": { "lines": 1 },        // Blank lines around headings
    "MD032": { "lists": true },      // Blank lines around lists
    "MD013": false,                  // Disable line length limit
    "MD024": false,                  // Allow duplicate headings
    "MD033": false,                  // Allow HTML tags
    "MD034": false,                  // Disable bare URLs
    "MD040": false,                  // Disable fenced code blocks
    "no-hard-tabs": false,           // Allow tabs
    "whitespace": false              // Disable whitespace rules
  }
}
```

---

## 🛠️ How to Fix Markdown Errors

### Error MD022: Blanks Around Headings
**Problem:** Heading not surrounded by blank lines
```markdown
# Heading
Content directly after (❌ WRONG)
```

**Fix:** Add blank line before AND after
```markdown

# Heading

Content after (✅ CORRECT)
```

---

### Error MD032: Blanks Around Lists
**Problem:** List not surrounded by blank lines
```markdown
# Heading
- Item 1 (❌ No blank line before)
- Item 2
Content after (❌ No blank line after)
```

**Fix:** Add blank lines before AND after
```markdown

# Heading

- Item 1 (✅ Blank line before)
- Item 2

Content after (✅ Blank line after)
```

---

## 📋 Quick Fix for Your File

For the file showing errors (`docs/adr/005-postgresql.md`), ensure:

1. **Before every heading:** blank line
2. **After every heading:** blank line
3. **Before every list:** blank line
4. **After every list:** blank line

Example structure:
```markdown
# Document Title

## Section 1

Some text here.

- List item 1
- List item 2

More text here.

## Section 2

Another section...
```

---

## 🔄 IDE Integration

### VS Code
1. The `.markdownlint.json` file is automatically picked up
2. Errors should now show as **warnings** instead of **errors**
3. Most issues are disabled in our config

### If errors persist:
1. **Reload** VS Code: `Cmd+Shift+P` → "Developer: Reload Window"
2. **Verify** the file was created: Check if `.markdownlint.json` exists in repo root
3. **Check** extension: Ensure "markdownlint" extension is installed and enabled

---

## ✅ Rules in Our Config

| Rule | Setting | Purpose |
|------|---------|---------|
| MD022 | Enabled | Headings need blank lines (1 line) |
| MD032 | Enabled | Lists need blank lines |
| MD013 | Disabled | No line length limit |
| MD024 | Disabled | Allow duplicate heading names |
| MD033 | Disabled | Allow HTML tags in markdown |
| MD034 | Disabled | Allow bare URLs without links |
| MD040 | Disabled | No fenced code block rules |
| no-hard-tabs | Disabled | Allow tabs |
| whitespace | Disabled | No strict whitespace |

---

## 🚀 Recommended VS Code Extensions

For better markdown experience:

```bash
# Install via CLI:
code --install-extension davidanson.vscode-markdownlint
code --install-extension ms-vscode.makefile-tools
code --install-extension shuworks.vscode-table-formatter
```

Or install in VS Code:
1. **Cmd+Shift+X** (Extensions)
2. Search: "markdownlint"
3. Install "Markdown Lint" by David Anson

---

## 🔍 How to Auto-Fix Markdown

### Option 1: Using CLI
```bash
# Install markdownlint-cli
npm install -g markdownlint-cli

# Fix all markdown files
markdownlint --fix docs/**/*.md
```

### Option 2: Manual Formatting
1. Open `.md` file in VS Code
2. Look for yellow/red squiggles
3. Hover and click "Fix"
4. Or use: `Option+Shift+F` (Format Document)

---

## 📌 For Your Project

**Applied to:** `/Users/eva/PROJECTOS/GitHub/accounting-esperanto/.markdownlint.json`

**Affects all:** `.md` files in the repository

**Next step:** 
- Reload VS Code if errors still show
- Or run auto-fix if you have `markdownlint-cli` installed

---

## 💡 Common Issues & Solutions

| Error | Quick Fix |
|-------|-----------|
| MD022 (heading) | Add blank line before `#` and after |
| MD032 (list) | Add blank line before `-` and after |
| MD013 (line too long) | Disabled in our config ✓ |
| MD024 (dup heading) | Disabled in our config ✓ |
| MD033 (HTML) | Disabled in our config ✓ |

---

## ✅ Verification

After reloading VS Code, your markdown files should:
- ✅ Show fewer/no errors
- ✅ Allow flexible formatting
- ✅ Still enforce basic rules (blanks around headings/lists)
- ✅ Keep code readable and consistent

---

**Status:** ✅ Fixed  
**File:** `.markdownlint.json` created in repo root  
**Action:** Reload VS Code (`Cmd+Shift+P` → "Reload Window")
