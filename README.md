# 💸 Flowt — AI-Powered Expense Tracker

A beautiful, feature-rich expense tracker built with Python + Streamlit + Gemini AI.

## ✨ Features

- **🔐 User Login** — Email/password registration & authentication
- **😊 Mood-Based Logging** — Tag expenses with your current mood; AI generates a spending-mood insight
- **🤖 AI Spending Coach** — Powered by Gemini 2.0 Flash — personalized insights, custom Q&A
- **🎤 Voice Input** — Use your device's native voice keyboard in the description field
- **📡 Subscription Radar** — AI scans transactions to detect recurring charges
- **📊 Monthly Comparison** — Side-by-side month comparison with delta
- **🎯 Goals & Savings** — Set financial goals, track progress
- **📈 Eye-Catching Charts** — Donut, line, bar, heatmap, category-vs-category
- **🔍 Transaction View** — Filter by date range, category; sort by date, amount
- **🌑 Dark Glassmorphism UI** — Space Grotesk + JetBrains Mono typography

---

## 🚀 Deploy on Streamlit Cloud (Free)

### Step 1 — Upload to GitHub
1. Create a new GitHub repo
2. Upload all files maintaining this structure:
   ```
   your-repo/
   ├── app.py
   ├── requirements.txt
   └── .streamlit/
       └── config.toml
   ```

### Step 2 — Deploy on Streamlit Cloud
1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Sign in with GitHub
3. Click **New app**
4. Select your repo → branch `main` → main file `app.py`
5. Click **Deploy**

### Step 3 — Add Gemini API Key (Optional but recommended)
In the deployed app, go to **Settings** page and paste your Gemini API key.  
Get a free key at: [aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey)

> **Note:** The API key is stored in session only (not persisted). For production,  
> use Streamlit Secrets: add `GEMINI_KEY = "your-key"` in the app's Secrets settings.

---

## 💻 Run Locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

Open `http://localhost:8501` in your browser.

---

## 🗂 File Structure

```
expense_tracker/
├── app.py              # Main application
├── requirements.txt    # Python dependencies
├── .streamlit/
│   └── config.toml    # Dark theme config
└── data/               # Auto-created on first run
    ├── users.json      # User accounts (hashed passwords)
    ├── expenses.json   # Expense records per user
    └── goals.json      # Goals per user
```

> ⚠️ `data/` folder is local-only. On Streamlit Cloud, data resets on redeploy.  
> For persistent cloud storage, integrate with Google Sheets or a free DB (Supabase, PlanetScale).

---

## 🛠 Tech Stack

| Layer | Tech |
|-------|------|
| Frontend | Streamlit + Custom CSS |
| Charts | Plotly Express / Graph Objects |
| AI | Google Gemini 2.0 Flash API |
| Data | JSON files (local) |
| Auth | SHA-256 password hashing |

---

Made with 💜 for Flowt
