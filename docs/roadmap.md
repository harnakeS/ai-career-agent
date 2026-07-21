# AI Career Agent Roadmap

## Vision

Build an AI-powered career agent that automatically discovers, evaluates, and recommends software engineering opportunities based on a structured understanding of my resume and career goals.

The first objective is to create a production-quality personal career assistant that I can rely on during my own job search.

Commercial SaaS features (authentication, subscriptions, billing, multi-user support, etc.) are intentionally deferred until the personal-use version is complete.

---

## Product Scope

The project focuses on:

- job collection
- structured job understanding
- candidate evidence extraction
- explainable job matching
- job recommendations
- job-specific resume tailoring
- grounded cover-letter generation
- application tracking

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

# Milestone 3 — Resume Intelligence 🚧 In Progress

## Goal

Automatically transform a resume into structured candidate data that drives job matching.

### Completed

- [x] PDF extraction
- [x] Resume text normalization
- [x] Resume section extraction
- [x] Skills parsing
- [x] Education parsing
- [x] Experience parsing
- [x] Project parsing
- [x] Employment-type classification
- [x] CandidateProfile Builder
- [x] Resume-to-matching integration
- [x] Experience aggregation by employment type
- [x] Deterministic target-role inference
- [x] Candidate preferences loaded from JSON

### Remaining

- [ ] Resume version management
- [ ] Multiple resume layouts
- [ ] User review of uncertain employment classifications
- [ ] LLM-assisted fallback extraction

---

## Milestone 4: Structured Job Understanding

### Completed

- Structured job-requirement models
- Requirement categories and importance levels
- LLM-based structured requirement extraction
- Deterministic requirement conversion
- Deterministic experience-duration parsing
- Minimum-experience normalization
- Entry-level requirement detection
- Work-authorization and sponsorship fields
- License and schedule requirement extraction
- Generic vocabulary text normalization
- Category-aware vocabulary concepts
- Vocabulary repository abstraction
- In-memory vocabulary repository
- Runtime vocabulary registration
- Alias-conflict detection
- Dynamic canonical concept resolution
- Requirement normalizer with injected vocabulary
- Vocabulary-aware evidence matching
- Category-isolated evidence comparison
- Explainable direct and alias-based match reasons
- Deterministic experience-duration matching

### Next

- Add education-equivalency matching
- Add certification and license matching rules

### Future Vocabulary Improvements

- SQLite-backed vocabulary repository
- Persistent canonical concepts and aliases
- Vocabulary import and export
- Tracking of newly discovered terms
- Review workflow for proposed aliases
- Provenance for vocabulary mappings
- Confidence or approval status for learned mappings
- User-specific vocabulary extensions

---

# Milestone 5 — Company Monitoring

## Goal

Monitor the companies I actually want to work for.

### Completed

- [x] Provider-neutral company configuration
- [x] Provider-neutral raw job-posting model
- [x] Shared job-source protocol
- [x] Injectable JSON HTTP boundary
- [x] Job-source error hierarchy
- [x] Greenhouse job source
- [x] Greenhouse payload validation
- [x] Live Greenhouse integration verification
- [x] Canonical raw-job conversion
- [x] Timestamp parsing and normalization
- [x] HTML description normalization
- [x] Job-source registry
- [x] Multi-source execution
- [x] Company-level job snapshots
- [x] Caller-controlled repository transactions
- [x] Transactional company persistence
- [x] Persistence failure isolation
- [x] Duplicate persistence verification
- [x] Validated company-source configuration
- [x] Application composition
- [x] Selected-company pipeline
- [x] Real SQLite pipeline verification
- [x] Command-line runner

### Planned

- [ ] Greenhouse pipeline integration
- [ ] Lever job source
- [ ] Workday job source
- [ ] Ashby job source
- [ ] SmartRecruiters job source
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

# Milestone 8 — AI Application Assistant

## Goal

Help prepare high-quality applications.

### Planned

- [ ] Job-specific resume tailoring
- [ ] Resume gap analysis and improvement suggestions
- [ ] Cover letter generation
- [ ] Interview preparation
- [ ] Company research summaries
- [ ] Personalized application recommendations
- [ ] Explain why each requirement matched
- [ ] Show supporting resume evidence
- [ ] Explain missing qualifications

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