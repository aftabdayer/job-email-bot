# Automated Job Email Bot — GitHub Actions Setup

Sends 25 personalised cold emails daily to real HR contacts.
Runs automatically every morning at 9:00 AM IST. 100% free.

---

## One-time setup (takes 10 minutes)

### Step 1 — Create a GitHub account
Go to github.com and sign up free if you don't have one.

### Step 2 — Create a new repository
- Click the + icon (top right) → New repository
- Name it: job-email-bot
- Set it to PRIVATE (important — keeps your data safe)
- Click Create repository

### Step 3 — Upload these files
Upload both files to the repo root:
- job_bot_real_hrlist.py
- .github/workflows/daily_email.yml  ← GitHub needs this exact folder structure

To upload:
- Click "Add file" → "Upload files"
- For the workflow file, you need to create the folder manually:
  - Click "Add file" → "Create new file"
  - Type the name as: .github/workflows/daily_email.yml
  - Paste the contents of daily_email.yml into the editor
  - Click Commit

### Step 4 — Add your Gmail credentials as Secrets
This keeps your password OUT of the code file completely.

- Go to your repo → Settings → Secrets and variables → Actions
- Click "New repository secret"
- Add these two secrets:

  Name: GMAIL_ADDRESS
  Value: aftab.jobs2025@gmail.com   ← your job-search Gmail

  Name: GMAIL_APP_PASSWORD
  Value: xxxx xxxx xxxx xxxx        ← your 16-character App Password

### Step 5 — Enable Actions
- Go to the Actions tab in your repo
- Click "I understand my workflows, go ahead and enable them"

That's it. Every day at 9:00 AM IST it will:
1. Send 25 emails to HRs from your list
2. Skip anyone already emailed
3. Send follow-ups to anyone who didn't reply after 5 days

---

## How to test it immediately (without waiting for 9 AM)
- Go to Actions tab → Daily Job Email Bot → Run workflow → Run workflow
- It will run right now and you'll see the logs

---

## How to check if it's working
- Go to Actions tab → you'll see a green tick for each successful daily run
- Check your job-search Gmail's Sent folder — you'll see all outgoing emails

---

## How to get your Gmail App Password
1. Go to myaccount.google.com
2. Security → 2-Step Verification → turn it ON
3. Search "App Passwords" in the search bar
4. Select Mail → Generate
5. Copy the 16-character password → paste it as the GMAIL_APP_PASSWORD secret

---

## Important notes
- Keep the repo PRIVATE so your HR list stays private
- The database file (aftab_contacted.db) resets each run on GitHub Actions
  This means the "already contacted" tracking won't persist between days on GitHub
  Solution: run it from your laptop once, then use GitHub only as backup
  OR see the advanced section below

## Advanced — Persistent database (so no one gets emailed twice across days)
GitHub Actions doesn't save files between runs by default.
To fix this, the script commits the database back to the repo after each run.
Add these lines to daily_email.yml after the "Run email bot" step:

      - name: Save database back to repo
        run: |
          git config user.email "actions@github.com"
          git config user.name "GitHub Actions"
          git add aftab_contacted.db
          git diff --staged --quiet || git commit -m "Update contacted DB"
          git push
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
