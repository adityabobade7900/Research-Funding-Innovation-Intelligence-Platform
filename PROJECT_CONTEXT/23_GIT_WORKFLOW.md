# 23_GIT_WORKFLOW.md — Git Version Control & Branching Strategy

## 1. Verified Repository Configuration & Remotes

A direct inspection of the Git configuration reveals two active remotes:

```
origin      https://github.com/springboardmentor3214x/Intelligent-Research1.git (fetch & push)
personal    https://github.com/adityabobade7900/Research-Funding-Innovation-Intelligence-Platform.git (fetch & push)
```

### Active Verified Branches:
- **Local Active Branch:** `feature/aditya-ai-ml` (synced with `personal/main`)
- **Other Local Branches:** `main`
- **Remote Branches on Origin:**
  - `origin/main` (Protected default branch)
  - `origin/feature/aditya-ai-ml`
  - `origin/nalinifrontend` (Frontend collaboration branch)
- **Remote Branches on Personal:**
  - `personal/main`

---

## 2. Core Version Control Commandments

1. **NEVER COMMIT DIRECTLY TO `main`:**  
   The `main` branch is strictly reserved for evaluated, verified production releases. All active development occurs on feature branches.
2. **USE ISOLATED FEATURE BRANCHES:**  
   Branch naming convention: `feature/<developer_name>-<module_topic>` (e.g., `feature/aditya-ai-ml`, `feature/nalini-frontend`).
3. **TEST BEFORE COMMITTING:**  
   Every commit must pass both test suites:
   ```bash
   pytest tests/ -v
   npm test
   ```
4. **NO COMMITTING UNCOMPILED CODE:**  
   Always run `npx next build` in `frontend/` before pushing to guarantee zero TypeScript or ESLint breakage.
5. **ATOMIC, MEANINGFUL COMMITS:**  
   Use standard conventional commit prefixes:
   - `feat:` New feature implementation
   - `fix:` Bug fix
   - `test:` Adding or updating unit tests
   - `docs:` Documentation updates
   - `refactor:` Code improvements without functionality changes
6. **NEVER COMMIT SENSITIVE DATA:**  
   `.env`, `*.log`, `__pycache__`, `venv/`, and `node_modules/` are strictly ignored by `.gitignore`.

---

## 3. Daily Development Git Sequence

### 1. Checkout Feature Branch
```bash
git checkout feature/aditya-ai-ml
```

### 2. Check Working Tree Status
```bash
git status
```

### 3. Stage & Commit Verified Work
```bash
git add <specific_files>
git commit -m "feat(module_name): descriptive summary of changes"
```

### 4. Push to Personal and Origin Remotes
```bash
# Push to personal GitHub repository
git push personal feature/aditya-ai-ml

# Push to internship team repository
git push origin feature/aditya-ai-ml
```

### 5. Create Pull Request (PR)
Navigate to GitHub and open a Pull Request targeting `main`. Ensure all CI checks and peer reviews pass before merging.
