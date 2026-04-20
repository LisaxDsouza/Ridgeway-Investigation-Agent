# 6:10 Assistant: Ridgeway Site Overnight Intelligence Platform

6:10 (lame name I know) Assistant is an AI-native overnight operations intelligence platform designed for Ridgeway Site. It transforms raw overnight signals (sensor telemetry, access control, vehicle tracking, and drone logs) into a structured morning briefing for site operations leads.

The platform acts as an **Investigation Engine**, proactively clustering signals and using AI agents to form hypotheses, identify harmless disturbances, and flag escalations before the morning shift begins.

---

## 🛠 Tech Stack

- **Backend**: FastAPI (Python 3.11), SQLAlchemy, PostgreSQL, Scikit-learn (DBSCAN).
- **AI Agent**: Groq LPU (**Llama 3.1 8B / 70B**) with intelligent rate-limit handling and fallback logic.
- **Frontend**: Next.js 16 (App Router), **MapLibre GL JS**, Tailwind CSS, Zustand, Framer Motion.
- **Infrastructure**: Docker & Docker Compose (Full Stack), PostgreSQL 15.

---

## 🚀 Zero-to-Hero Setup (Fresh Clone)

The entire platform—including installation, database seeding, and service orchestration—is automated. 

1.  **Run the Setup Script**:
    ```powershell
    .\setup.ps1
    ```

2.  **Configure Environment**:
    The script will create a `.env` file for you if it's missing. Open it and add your `GROQ_API_KEY`.

3.  **Run Setup Again**:
    Once your key is added, run `.\setup.ps1` again. It will skip installation and jump straight to booting the platform.

### Access:
- **Frontend**: [http://localhost:3000](http://localhost:3000)
- **Maya API**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **Database**: `localhost:5433` (PostgreSQL)

---

## 🛠 Manual Development Setup

### 1. Prerequisites
- **Python 3.11+**
- **Node.js 20+**
- **Docker** (Required for the database)
- **Groq API Key** (Obtain at [console.groq.com](https://console.groq.com))

### 2. Backend Setup
1. Navigate to the backend directory:
   ```bash
   cd backend
   ```
2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Setup environment:
   ```bash
   cp .env.example .env
   # Update GROQ_API_KEY and DATABASE_URL
   ```
5. Launch the API server:
   ```bash
   uvicorn app.main:app --reload
   ```

### 3. Frontend Setup
1. Navigate to the frontend directory:
   ```bash
   cd ../frontend
   ```
2. Install dependencies:
   ```bash
   npm install
   ```
3. Run the development server:
   ```bash
   npm run dev
   ```

### 4. Database & Seeding
1. Start the database (if not using the full Docker stack):
   ```bash
   docker-compose up -d db
   ```
2. Seed with the latest forensic scenarios:
   ```bash
   cd backend
   python seed/bulk_scenarios.py
   ```

---

## 🧠 Forensic Intelligence Engine

The platform features a highly resilient investigation loop powered by **Groq**:

- **Intelligent Fallback**: To prevent downtime during peak usage, the system uses `llama-3.1-8b-instant` as the primary engine (due to higher rate limits) and features automatic fallback logic if a model reaches its token or request limit.
- **Investigation Steps**:
  1. **Signal Ingestion**: Overnight events are stored in PostgreSQL.
  2. **Spatial Clustering**: DBSCAN groups co-located events into potential incidents.
  3. **Agent Loop**: The Groq agent calls tools (Weather, Spatial, Drone) to verify context.
  4. **Synthesis**: Finalized incidents are compiled into a 5-question morning briefing.

---

## 📂 Project Structure

```text
ridgeway/
├── backend/
│   ├── app/
│   │   ├── agent/       # Forensic investigation logic & orchestrator
│   │   ├── routers/     # API endpoints (Chat, Incidents, MCP)
│   │   └── services/    # Business logic (Briefing generation)
│   ├── seed/            # Seed scripts and bulk incident scenarios
│   └── Dockerfile       # Backend build config
├── frontend/
│   ├── app/             # Next.js App Router (Forensic Dashboard)
│   ├── components/      # UI components (Situation Map, Incident Chat)
│   └── Dockerfile       # Production Next.js build
└── docker-compose.yml   # Multi-container orchestration
```

---

## 📄 License
Built by Lisa Hazel Dsouza :p

