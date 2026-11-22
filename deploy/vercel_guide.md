# Deploying Frontend to Vercel (Step-by-Step Guide)

This guide walks you through deploying the **Next.js Frontend** of the Waste Segregation & Intelligent Route Optimization system to **Vercel** with zero configuration.

---

## Prerequisites
1. A free [GitHub Account](https://github.com/).
2. A free [Vercel Account](https://vercel.com/signup).

---

## Step 1: Push Frontend to GitHub

If you haven't initialized Git yet in the project root:

```bash
cd waste-segregation-route-opt
git init
git add .
git commit -m "feat: complete production waste management web app"
```

Create a new repository on GitHub (e.g., `waste-segregation-route-opt`) and push your code:

```bash
git remote add origin https://github.com/<YOUR_GITHUB_USERNAME>/waste-segregation-route-opt.git
git branch -M main
git push -u origin main
```

---

## Step 2: Import into Vercel

1. Log into your **[Vercel Dashboard](https://vercel.com/dashboard)**.
2. Click **"Add New..."** -> **"Project"**.
3. Select your GitHub repository: `waste-segregation-route-opt`.
4. In the configuration screen:
   - **Framework Preset**: `Next.js` (automatically detected).
   - **Root Directory**: Click **Edit** and set it to:
     ```text
     frontend
     ```
   - **Build Command**: `next build` (default).
   - **Output Directory**: `.next` (default).
   - **Install Command**: `npm install` (default).

---

## Step 3: Configure Environment Variables

Under **Environment Variables**, add:

| Key | Value | Description |
| :--- | :--- | :--- |
| `NEXT_PUBLIC_API_URL` | `https://<YOUR-USERNAME>-<SPACE-NAME>.hf.space` | URL of your deployed Hugging Face FastAPI backend |

> **Note:** If you haven't deployed the backend yet, you can leave it empty or set to `http://localhost:8000`. The frontend includes **automatic graceful client-side fallback**, meaning 100% of the UI (camera, bounding boxes, sample scans, Leaflet map, OR-Tools simulated route, and charts) functions immediately even before the backend is connected!

---

## Step 4: Deploy & Verify

1. Click the blue **"Deploy"** button.
2. Vercel will build the project in ~45 seconds.
3. Once finished, you will receive a public HTTPS URL:
   ```
   https://waste-segregation-route-opt.vercel.app
   ```
4. Anyone on any mobile or desktop device can now open the app with zero installation!
