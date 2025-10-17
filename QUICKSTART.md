# Quick Start (Windows) — VTU Internship Watcher

This guide helps you run the project locally in minutes. No prior experience required.

## 1) Install Requirements

- **Python**: Install Python 3.8 or newer from https://www.python.org/downloads/
  - During install, check "Add python.exe to PATH".
- Open Windows Terminal or PowerShell.

## 2) Get the Code

If the project folder is already on your Desktop, skip this step.

```powershell
# Example (only if you don't already have the folder)
# git clone https://github.com/yourusername/vtu-internship-watcher.git
# cd vtu-internship-watcher
```

## 3) Create and Activate a Virtual Environment

```powershell
# From the project folder (contains requirements.txt)
python -m venv .venv

# Activate the venv (PowerShell)
.\.venv\Scripts\Activate.ps1

# If you see an execution policy error, run this once as Admin:
# Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
# Then try activating again.
```

## 4) Install Python Packages

```powershell
pip install --upgrade pip
pip install -r requirements.txt
```

## 5) Set Up Environment Variables

- Copy `.env.example` to `.env` and fill in your details.

```powershell
copy .env.example .env
```

Edit `.env` and set:

```
SENDER_EMAIL=your-email@gmail.com
SENDER_PASSWORD=your-16-char-gmail-app-password
RECIPIENT_EMAIL=recipient@example.com
```

Notes:
- The password must be a **Gmail App Password**, not your normal Gmail password.
  - Create at: https://myaccount.google.com/apppasswords (requires 2-Step Verification).

## 6) Verify Your Setup (Recommended)

Run the test script `test_setup.py` to check environment, dependencies, API connection, and file permissions.

```powershell
python test_setup.py
```

- If it says all tests passed, you're ready.
- If something fails, follow the printed guidance.

## 7) Run the Watcher Once (On-Demand)

This fetches internships now and emails you only for new ones.

```powershell
python internship_watcher.py
```

- Logs: `internship_watcher.log`
- Seen IDs: `seen_internships.json` (auto-created)

## 8) Run on a Schedule (Locally)

Use the built-in scheduler to run every 30 minutes.

```powershell
python run_scheduler.py
```

- Keep the window open to continue scheduling.
- Stop with `Ctrl + C`.
- Logs: `scheduler.log`

## 9) Optional: GitHub Actions (Run in the Cloud)

- Add GitHub repository secrets for `SENDER_EMAIL`, `SENDER_PASSWORD`, `RECIPIENT_EMAIL`.
- Adjust the cron schedule in `.github/workflows/internship-watcher.yml` if needed.

## Common Issues & Fixes

- "Missing email configuration" error when running:
  - Ensure `.env` exists and contains `SENDER_EMAIL`, `SENDER_PASSWORD`, `RECIPIENT_EMAIL`.
  - Ensure venv is active and you run from the project folder.

- PowerShell activation error:
  - Run PowerShell as Admin and execute:
    ```powershell
    Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
    ```

- Email didn't arrive:
  - Check spam folder.
  - Verify you used a Gmail **App Password** in `.env`.
  - Ensure sender and recipient emails are correct.

- API/network errors:
  - Check internet connection and try again later.

## Useful Files

- `requirements.txt` — Python dependencies
- `.env.example` — Template for secrets (copy to `.env`)
- `test_setup.py` — Quick environment and dependency check
- `internship_watcher.py` — Main script (runs now)
- `run_scheduler.py` — Keeps running on a schedule

---

You're set! Start with `python test_setup.py`, then `python internship_watcher.py`.
