# Claude Code Workflow Guidelines

## Context
- **Claude's Environment**: Works in a VM at `/home/user/InvokeAI`
- **Developer's Environment**: Works on local machine (path varies by developer)
- **Shared Repository**: GitHub repository (your fork of InvokeAI)
- **Branch**: Feature branch (typically starts with `claude/`)

---

## When Claude Makes Code Changes

**Claude's Steps:**
1. Make edits in VM
2. Commit changes locally: `git commit -m "description"`
3. **MUST** fetch and rebase: `git pull --rebase origin <branch>`
4. Push to GitHub: `git push origin <branch>`
5. **Explicitly tell developer**: "I've pushed changes to GitHub. Please pull them."

**Developer's Steps:**
1. Pull from GitHub: `git pull origin <branch>`
2. **Verify changes arrived**:
   ```bash
   git log --oneline -3  # Check recent commits
   grep "specific code" path/to/file  # Verify specific changes
   ```
3. If backend code changed: **Restart services** (`invokeai-web`)
4. If frontend code changed: **Rebuild frontend** (`cd invokeai/frontend/web && npx vite build`)
5. **Confirm to Claude**: "Changes pulled and verified. Service restarted."

---

## When Developer Makes Local Changes

**Developer's Steps:**
1. Make edits on local machine
2. Commit changes: `git commit -m "description"`
3. Push to GitHub: `git push origin <branch>`
4. **Tell Claude**: "I've pushed changes to GitHub."

**Claude's Steps:**
1. Pull and rebase: `git pull --rebase origin <branch>`
2. Verify changes: `git log --oneline -3`
3. Confirm: "Changes synced in VM."

---

## Critical Rules

1. **Always Pull Before Push**: Both parties must `git pull --rebase` before pushing to avoid conflicts
2. **Always Verify After Pull**: Don't assume changes arrived - check with `git log` and `grep`
3. **Always Restart After Backend Changes**: Python code changes require restarting `invokeai-web`
4. **Always Rebuild After Frontend Changes**: TypeScript/React changes require `npx vite build`
5. **Communicate**: Explicitly say "I've pushed" and "I've pulled and verified"

---

## Verification Commands

```bash
# Check recent commits
git log --oneline -5

# Check if specific code exists in a file
grep "search term" path/to/file

# Check git status
git status

# See what changed in last commit
git show HEAD --stat

# Compare local with remote
git fetch origin <branch>
git log HEAD..origin/<branch>  # What's on GitHub that I don't have
git log origin/<branch>..HEAD  # What I have that's not on GitHub
```

---

## When Things Get Out of Sync

If you get "diverged branches" or push is rejected:

```bash
# 1. Fetch latest from GitHub
git fetch origin <branch>

# 2. Rebase your changes on top of remote
git pull --rebase origin <branch>

# 3. If conflicts, resolve them, then:
git add <resolved-files>
git rebase --continue

# 4. Push the synced commits
git push origin <branch>
```

---

## Quick Checklist Before Moving On

- [ ] Claude: "I've pushed changes"
- [ ] Developer: Pull changes (`git pull origin <branch>`)
- [ ] Developer: Verify with `git log` and file checks
- [ ] Developer: Restart services if needed
- [ ] Developer: Test and confirm it works
- [ ] Developer: "Verified, ready to proceed"

---

## File Type Changes Requiring Different Actions

| Change Type | Action Required |
|-------------|----------------|
| Python backend (`*.py`) | Restart `invokeai-web` |
| Frontend TypeScript/React (`*.ts`, `*.tsx`) | Rebuild: `cd invokeai/frontend/web && npx vite build` |
| Frontend styling (`*.css`) | Rebuild frontend |
| Configuration (`*.yaml`, `.env`) | Restart `invokeai-web` |
| Documentation (`*.md`) | No restart needed |

---

## Common Issues

### Issue: "Everything up-to-date" but changes not visible
**Solution**:
```bash
git fetch origin <branch>
git log HEAD..origin/<branch>  # See what's missing
git pull origin <branch>
```

### Issue: "diverged branches"
**Solution**: Use rebase workflow (see "When Things Get Out of Sync" above)

### Issue: Changes in VM but not on local machine
**Cause**: Claude forgot to push, or developer forgot to pull
**Solution**:
- Claude runs: `git push origin <branch>`
- Developer runs: `git pull origin <branch>`
