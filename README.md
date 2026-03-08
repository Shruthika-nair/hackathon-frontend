# SafeWalk
### Crowdsourced Pedestrian Safety Navigation

> **Navigation apps show you the fastest route. SafeWalk shows you the safest one.**

SafeWalk is a crowdsourced map layer that lets users report pedestrian hazards — broken sidewalks, open manholes, flooded streets, poor lighting, and more — and receive safety-optimised walking routes that avoid them.

Built for Indian cities. Built for everyone who walks.

---

## Tech Stack

- **Frontend:** Streamlit + Folium + OpenStreetMap
- **Backend:** Python + FastAPI
- **Database:** PostgreSQL + PostGIS (via Supabase)
- **Auth:** JWT tokens

---

## Quick Start

```bash
# 1. Copy environment config
cp .env.example .env
# Add your Supabase keys to .env

# 2. Install backend
cd backend
pip install -r requirements.txt

# 3. Run backend
uvicorn src.main:app --reload

# 4. In a new terminal — install & run frontend
cd frontend
pip install -r requirements.txt
streamlit run app.py
```

Backend: `http://localhost:8000` | Frontend: `http://localhost:8501`

---

## Project Structure

```
safewalk/
├── backend/
│   ├── src/
│   │   ├── main.py              # FastAPI endpoints
│   │   └── services/
│   │       └── safety_score.py  # Safety algorithm
│   └── requirements.txt
├── frontend/
│   ├── app.py                   # Streamlit + Folium map
│   └── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

---

## Team — Random Forest Rangers

| Name | Role |
|---|---|
| Vishaal S | Backend, Database & Safety Algorithm |
| Arun Balaji | Backend, Documentation & Project Manager |
| Shruthika Nair | Frontend & Map Interface |
| Ishitha Ilan | UI/UX Design & Accessibility |

---

## License

MIT License
