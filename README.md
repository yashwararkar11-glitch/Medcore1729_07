# Medcore1729_07
THIS IS MY PROJECT
# 🩺 AI Health & Diagnostic Workspace

An offline-capable, 100% privacy-first healthcare and wellness platform built for hackathons. This application bridges the gap between raw medical reports, medical scans, and actionable patient insights by leveraging local open-weight vision-language models.

---

## 🚀 Key Features

1. **📄 Medical Report Analysis:** Upload lab reports (PDF or images) to extract values, identify abnormal readings, and summarize health indicators.
2. **🔍 Detailed Diagnostics & Visual Anomaly Highlighting:** Translates raw scans into a structured diagnostic breakdown covering **Abnormal Symptoms**, **Condition Names**, **Root Causes**, and **Actionable Solutions**, complete with side-by-side original vs. annotated visual indicator images.
3. **⚖️ AI-Powered Image Comparison:** Upload multiple scans or images to compare side-by-side, generating comprehensive reports detailing image descriptions, key similarities, important differences, unique features, visual changes, and semantic similarity scoring.
4. **🥗 Indian Diet & Grocery Planner:** Tailored regional Indian meal suggestions based on available ingredients, daily budget tracking, and automated grocery list generation with built-in health safety guardrails.
5. **💬 AI Health Chat Assistant:** Conversational AI chat interface featuring conversation memory, context retention, and suggested starter prompts.
6. **🌐 Multilingual Accessibility:** Seamless, persistent dynamic dictionary translation supporting **English**, **Hindi**, and **Marathi**.

---

## 🏗️ Architecture & Technology Stack

* **Backend:** FastAPI (`main.py`) for high-performance asynchronous request handling, file uploads, and routing.
* **Frontend:** Streamlit (`app.py`) for a modern dashboard layout, sidebar navigation, metric cards, and responsive side-by-side comparison interfaces.
* **AI Engine & Local Model:** Powered locally via **Ollama** using open-weight vision-language models (e.g., `qwen3-vl:4b`).
* **Processing Utilities:** 
  * PyMuPDF (`fitz`) in `logic.py` for digital PDF text extraction and image conversion.
  * Pillow (`PIL`) for programmatic image manipulation and bounding box anomaly annotations.

---

## 🔒 Privacy & Compliance
* **Zero Cloud Dependency:** Runs entirely offline via Ollama on local hardware. No sensitive patient health data ever leaves your device, ensuring total privacy compliance.
* **Open-Weight Transparency:** Built entirely using open-weight models under open licenses (such as Apache 2.0), perfectly satisfying open-source hackathon requirements.

---

## 🛠️ Installation & Local Setup

### Step 1: Clone or Open Project Folder
Navigate to your project directory:
```bash
cd medcore