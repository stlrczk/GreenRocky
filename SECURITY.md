# Security Guidelines

## Sensitive Files

The following files contain sensitive information and should **NEVER** be committed to git:

### Backend
- `backend/.env` - Contains OpenAI API key and other secrets
- `backend/venv/` - Python virtual environment (large, environment-specific)
- `backend/data/embeddings_cache.json` - Generated embeddings (can be large)
- `backend/data/feedback.jsonl` - User feedback data (may contain PII)

### Frontend
- `frontend/.env.local` - Contains API URLs and potentially other config
- `frontend/node_modules/` - Node packages (large, should be installed locally)
- `frontend/.next/` - Build artifacts

## What IS Safe to Commit

### Safe to commit:
- `backend/.env.example` - Template without actual secrets
- `frontend/.env.local.example` - Template without actual secrets
- All source code files (`.py`, `.ts`, `.tsx`, etc.)
- Configuration files (`package.json`, `requirements.txt`, etc.)
- Documentation (`.md` files)
- `backend/data/Tenders_List.json` - Source data (if not sensitive)

## Git Setup

The `.gitignore` file is configured to protect sensitive files. Verify it's working:

```bash
# Check that .env is ignored
git status | grep -i "\.env"
# Should show nothing or only .env.example files

# Check that venv is ignored
git status | grep -i "venv"
# Should show nothing
```

## If You Accidentally Commit Secrets

If you accidentally commit your `.env` file or API key:

### 1. Remove from Git History
```bash
# Remove file from git cache
git rm --cached backend/.env

# Commit the removal
git commit -m "Remove sensitive .env file"
```

### 2. Rotate Your Secrets
**IMPORTANT:** Immediately rotate any exposed credentials:

1. **OpenAI API Key:**
   - Go to https://platform.openai.com/api-keys
   - Revoke the exposed key
   - Generate a new key
   - Update `backend/.env` with new key

2. **Push Changes:**
   ```bash
   git push origin main
   ```

### 3. Clean History (if pushed to remote)
If secrets were pushed to GitHub/GitLab:

```bash
# Use git filter-branch or BFG Repo-Cleaner
# This is complex - consider creating a fresh repo instead
```

## Best Practices

1. **Always use .env files for secrets** - Never hardcode API keys
2. **Check before committing:**
   ```bash
   git diff --staged | grep -i "api.*key"
   ```
3. **Use .example files** - Provide templates without real values
4. **Review .gitignore** - Ensure all sensitive paths are listed
5. **Enable pre-commit hooks** - Automated checks for sensitive data

## Environment Variables Required

### Backend (.env)
```bash
OPENAI_API_KEY=sk-proj-...    # Get from OpenAI platform
CORS_ORIGINS=http://localhost:3000
```

### Frontend (.env.local)
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Questions?

If you're unsure whether a file should be committed, err on the side of caution and don't commit it. You can always add it later.
