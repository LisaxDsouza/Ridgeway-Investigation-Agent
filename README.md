# 6:10 Assistant: Ridgeway Site Overnight Intelligence Platform

6:10 Assistant is an AI-native overnight operations intelligence platform designed for Ridgeway Site. It transforms raw overnight signals (sensor telemetry, access control, vehicle tracking, and drone logs) into a structured morning briefing for site operations leads.

The platform acts as an **Investigation Engine**, proactively clustering signals and using AI agents to form hypotheses, identify harmless disturbances, and flag escalations before the morning shift begins.

---

## 🛠 Tech Stack

- **Backend**: FastAPI (Python 3.11), SQLAlchemy, PostgreSQL, Scikit-learn (DBSCAN).
- **AI Agent**: Groq LPU (Llama 3 70B) for sub-second tool-calling investigation.
- **Frontend**: Next.js 14, Mapbox GL JS, Tailwind CSS, Zustand, Vercel AI SDK.
- **Infrastructure**: Docker Compose (Local Database), Railway/Render (Backend), Vercel (Frontend).

---

## 🚀 Getting Started

### 1. Prerequisites
- **Python 3.11+**
- **Node.js 18+**
- **Docker & Docker Compose**
- **Groq API Key** (Obtain at [console.groq.com](https://console.groq.com))
- **Mapbox Public Token** (Obtain at [account.mapbox.com](https://account.mapbox.com))

### 2. Installation

#### Clone the Repository
```bash
git clone <your-repo-url>
cd skylark-morning-brief
```

#### Backend Setup
1. Navigate to the backend directory:
   ```bash
   cd backend
   ```
2. Create a virtual environment and activate it:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Configure environment variables:
   ```bash
   cp .env.example .env
   # Edit .env and add your GROQ_API_KEY
   ```

#### Frontend Setup
1. Navigate to the frontend directory:
   ```bash
   cd ../frontend
   ```
2. Install dependencies:
   ```bash
   npm install
   ```
3. Configure environment variables:
   ```bash
   cp .env.local.example .env.local
   # Edit .env.local and add your NEXT_PUBLIC_MAPBOX_TOKEN
   ```

### 3. Database & Seeding
1. Start the PostgreSQL database using Docker:
   ```bash
   docker-compose up -d
   ```
2. Seed the database with the "Block C" incident scenario:
   ```bash
   cd backend
   python seed/seed.py
   ```

### 4. Running the Project
- **Backend**: `uvicorn app.main:app --reload` (from the `backend` folder)
- **Frontend**: `npm run dev` (from the `frontend` folder)

---

## 📂 Project Structure

```text
ridgeway/
├── backend/
│   ├── app/
│   │   ├── agent/       # Groq investigation orchestrator & prompts
│   │   ├── models/      # SQLAlchemy DB models
│   │   ├── routers/     # API endpoints (Investigate, Incidents)
│   │   └── tools/       # Site investigation tools (Weather, Spatial, Drone)
│   ├── seed/            # Seed scripts and incident scenarios
│   └── Dockerfile       # Production build config
├── frontend/
│   ├── app/             # Next.js App Router (Map, Review Panel, Briefing)
│   ├── components/      # UI components (Mapbox, Incident Cards)
│   └── lib/             # API client & state management (Zustand)
└── docker-compose.yml   # Local development services
```

---

## 🧠 Core Methodology
The system follows an **investigation loop** rather than a simple summary:
1. **Signal Ingestion**: Overnight events are stored in PostgreSQL.
2. **Spatial Clustering**: DBSCAN groups co-located events into potential incidents.
3. **Agent Loop**: For each cluster, the Groq agent calls tools to verify context (Weather, Shifts) and forms a hypothesis.
4. **Human Challenge**: The Ops Lead can "Challenge" AI findings, forcing the agent to re-investigate with specific feedback.
5. **Briefing Assembly**: Finalized incidents are compiled into a 5-question morning briefing.

---

## 📄 License
Confidential - For Skylark Drones Engineering Assignment only.
