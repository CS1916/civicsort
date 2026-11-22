# Deploying FastAPI Backend to Hugging Face Spaces (Step-by-Step Guide)

This guide walks you through deploying the **Python FastAPI Backend** (with YOLO Computer Vision & Google OR-Tools) to **Hugging Face Spaces** for free public hosting.

---

## Why Hugging Face Spaces?
- **Free 2 vCPU / 16GB RAM** hosting tier.
- Native support for **Docker** containers.
- Perfect for AI models (Ultralytics PyTorch YOLO & Google OR-Tools).
- Provides an instant public HTTPS API URL.

---

## Step 1: Create a New Hugging Face Space

1. Log into [Hugging Face](https://huggingface.co/).
2. In the top right profile dropdown, click **"New Space"**.
3. Fill in the details:
   - **Space Name**: `urban-waste-ai-backend` (or your preferred name).
   - **License**: `MIT` or `Apache 2.0`.
   - **Space SDK**: Select **Docker** -> Choose **Blank**.
   - **Space Hardware**: Free CPU (`2 vCPU · 16 GB RAM`).
   - **Visibility**: `Public`.
4. Click **"Create Space"**.

---

## Step 2: Push Backend Files to Hugging Face

Hugging Face Spaces uses standard Git repositories. Clone your newly created space locally:

```bash
git clone https://huggingface.co/spaces/<YOUR-HF-USERNAME>/urban-waste-ai-backend
```

Copy the contents of `waste-segregation-route-opt/backend/` into this cloned folder:

```text
urban-waste-ai-backend/
├── app/
│   ├── models/
│   │   ├── __init__.py
│   │   └── schemas.py
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── classify.py
│   │   ├── route_optimizer.py
│   │   └── bins.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── yolo_service.py
│   │   ├── vrp_solver.py
│   │   └── osrm_service.py
│   ├── __init__.py
│   ├── config.py
│   └── main.py
├── main.py
├── requirements.txt
├── Dockerfile
└── README.md
```

Add your optional custom YOLO weights file (e.g. `weights/best.pt`) if trained on custom waste datasets, or let the app use the pre-configured `yolov8n.pt` / automatic heuristic computer vision fallback.

Commit and push to Hugging Face:

```bash
cd urban-waste-ai-backend
git add .
git commit -m "feat: deploy YOLO + OR-Tools FastAPI waste management backend"
git push
```

---

## Step 3: Monitor Build & Test Live API

1. In your Hugging Face Space page, navigate to the **"Logs"** tab.
2. The Docker container will install dependencies and start Uvicorn on port `7860`.
3. Once the status badge changes to **"Running"**, click the **"Embed this Space"** or triple-dots menu to find your Direct Space URL:
   ```
   https://<YOUR-HF-USERNAME>-urban-waste-ai-backend.hf.space
   ```
4. Verify endpoints:
   - **Swagger UI**: `https://<YOUR-HF-USERNAME>-urban-waste-ai-backend.hf.space/docs`
   - **Health Check**: `https://<YOUR-HF-USERNAME>-urban-waste-ai-backend.hf.space/health`
   - **Classify Endpoint**: `POST /api/classify-waste`
   - **Route Optimization**: `POST /api/optimize-route`

---

## Step 4: Connect Vercel Frontend to Hugging Face Backend

1. Return to your **Vercel Project Settings** -> **Environment Variables**.
2. Update `NEXT_PUBLIC_API_URL` to your Hugging Face Space URL:
   ```
   NEXT_PUBLIC_API_URL = https://<YOUR-HF-USERNAME>-urban-waste-ai-backend.hf.space
   ```
3. Click **"Redeploy"** in Vercel.
4. Your complete full-stack AI system is now live for global evaluation!
