# AI Career Agent Roadmap

## Vision

Build an AI-powered career agent that automatically discovers, evaluates, and recommends software engineering opportunities based on a structured understanding of my resume and career goals.

The first objective is to create a production-quality personal career assistant that I can rely on during my own job search.

Commercial SaaS features (authentication, subscriptions, billing, multi-user support, etc.) are intentionally deferred until the personal-use version is complete.

---

# Milestone 1 — Core Backend ✅ Complete

## Goal

Build the core infrastructure required to collect, process, and store job postings.

### Completed

- [x] Standardized `JobPosting` model
- [x] Collector abstraction
- [x] Live Remotive collector
- [x] SQLite database
- [x] SQLAlchemy models
- [x] Repository pattern
- [x] Processing pipeline
- [x] Duplicate detection
- [x] Database persistence
- [x] Unit testing framework
- [x] Project documentation

---

# Milestone 2 — Matching Engine 🚧 In Progress

## Goal

Determine how well a job matches my background before introducing AI.

### Completed

- [x] Structured candidate profile
- [x] Deterministic rule matcher
- [x] Technical skill matching
- [x] Role alignment
- [x] Location alignment
- [x] Early-career scoring
- [x] Category-based scoring components
- [x] Explainable match reasons
- [x] Match score persistence

### Remaining

- [ ] Experience matching
- [ ] Education matching
- [ ] Certification matching
- [ ] Citizenship / work authorization matching
- [ ] Improved category weighting

---

## Milestone 3 — Resume Intelligence 🚧 In Progress

### Completed

- [x] PDF extraction
- [x] Resume text normalization
- [x] Resume section extraction
- [x] Skills parsing
- [x] Education parsing
- [x] Experience parsing
- [x] Project parsing
- [x] Employment classification

### Remaining

- [ ] CandidateProfile Builder
- [ ] Resume → Matching integration
- [ ] Resume version management
- [ ] Multiple resume layouts

---

# Milestone 4 — AI Recommendation Engine

## Goal

Move beyond keyword matching using AI.

### Planned

- [ ] Semantic embeddings
- [ ] Similarity search
- [ ] Hybrid scoring
- [ ] LLM evaluation
- [ ] Explainable AI recommendations
- [ ] Recommendation confidence score

---

# Milestone 5 — Company Monitoring

## Goal

Monitor the companies I actually want to work for.

### Planned

- [ ] Greenhouse collector
- [ ] Lever collector
- [ ] Workday collector
- [ ] Ashby collector
- [ ] SmartRecruiters collector
- [ ] Company configuration
- [ ] Multi-collector execution
- [ ] Closed-job detection

Target companies include:

- Amazon
- Google
- NVIDIA
- Meta
- Apple
- JPMorgan
- Bank of America
- BlackRock
- Barclays
- Johnson & Johnson
- Fiserv
- Wells Fargo
- eBay

---

# Milestone 6 — Notifications

## Goal

Automatically notify me when a worthwhile opportunity appears.

### Planned

- [ ] Email notifications
- [ ] Daily summary
- [ ] High-priority alerts
- [ ] Duplicate-notification prevention
- [ ] Configurable score thresholds

---

# Milestone 7 — Career Dashboard

## Goal

Provide a single interface for managing my job search.

### Planned

- [ ] Streamlit dashboard
- [ ] Search jobs
- [ ] Sort by score
- [ ] Filter by company
- [ ] Filter by location
- [ ] Saved jobs
- [ ] Application tracker
- [ ] Job analytics

---

# Milestone 8 — AI Career Assistant

## Goal

Help prepare high-quality applications.

### Planned

- [ ] Resume optimization
- [ ] Resume gap analysis
- [ ] Cover letter generation
- [ ] Interview preparation
- [ ] Company research summaries
- [ ] Personalized application recommendations

---

# Milestone 9 — Personal MVP ✅

## Goal

A complete system that I can use throughout my own job search.

### Success Criteria

- [ ] Track at least 10 target companies
- [ ] Automatically parse my resume
- [ ] Match jobs using hybrid AI scoring
- [ ] Receive automated notifications
- [ ] Manage applications through the dashboard
- [ ] Generate resume suggestions
- [ ] Generate cover letters
- [ ] Provide interview preparation
- [ ] Run on a scheduled basis without manual intervention

---

# Future (Post-MVP)

Once the personal-use version is complete, the project can evolve into a commercial platform.

Potential future work:

- Multi-user support
- Authentication
- PostgreSQL
- FastAPI backend
- React frontend
- Cloud deployment
- Stripe subscriptions
- Team accounts
- Recruiter analytics
- Enterprise integrations