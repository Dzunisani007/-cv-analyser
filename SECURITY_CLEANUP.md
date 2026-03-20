# Security Cleanup Commands

## 1. Force push to remove .env from remote repository
```bash
git push origin --force --all
git push origin --force --tags
```

## 2. Add .env to .gitignore to prevent future commits
```bash
echo ".env" >> .gitignore
git add .gitignore
git commit -m "security: add .env to gitignore"
git push origin main
```

## 3. Create .env.example with placeholders
```bash
cp .env .env.example
# Now edit .env.example and replace actual values with placeholders
```

## 4. Verify .env is not tracked
```bash
git status
# Should show .env as untracked
```

## 5. Rotate your database password IMMEDIATELY
- Go to Render dashboard
- Find your PostgreSQL database
- Change the password for recruitment_deploy_user
- Update your local .env with the new password

## 6. Check if credentials are still exposed
- Go to GitGuardian dashboard
- Verify the incident is resolved
- Check commit history to ensure .env is gone
