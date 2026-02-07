# Purging `.env` from git history (optional, destructive)

If `.env` (or any file with secrets) was previously committed, it will remain in the repository history. Rewriting history is destructive and affects all collaborators. Back up the repository first.

Recommended (fast) approach using the BFG Repo-Cleaner:

1. Install BFG (https://rtyley.github.io/bfg-repo-cleaner/).
2. Run:

```bash
# make a fresh clone to operate on
git clone --mirror <repo-url> repo.git
cd repo.git

# delete all files named .env from history
java -jar bfg.jar --delete-files .env

# clean and push
git reflog expire --expire=now --all
git gc --prune=now --aggressive
git push --force
```

Alternative: git filter-repo (preferred if available):

```bash
git clone --mirror <repo-url> repo.git
cd repo.git
git filter-repo --invert-paths --paths .env
git push --force
```

After rewriting history, inform collaborators to re-clone the repo.
