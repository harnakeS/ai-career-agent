# Roadmap

## Version 0.1 — Core Job Collection

- [x] Create standardized `JobPosting` model
- [x] Create base collector interface
- [x] Implement first live collector
- [x] Configure SQLite database
- [x] Create jobs table
- [x] Implement insert and update behavior
- [x] Prevent duplicate job records
- [x] Add basic eligibility filters
- [x] Add unit tests for filtering
- [ ] Create reusable job-processing pipeline

## Version 0.2 — Ten-Company Monitoring

- [ ] Support multiple collectors in one run
- [ ] Add company configuration
- [ ] Add Greenhouse collector
- [ ] Add Lever collector
- [ ] Add Workday collector
- [ ] Track ten selected companies
- [ ] Add retry handling
- [ ] Add structured logging
- [ ] Detect inactive or closed jobs
- [ ] Add collector tests

## Version 0.3 — Candidate Matching

- [ ] Create structured candidate profile
- [ ] Parse resume content
- [ ] Extract skills and experience requirements
- [ ] Add deterministic match scoring
- [ ] Add semantic embedding similarity
- [ ] Rank jobs by relevance
- [ ] Store match scores in the database

## Version 0.4 — AI Recommendation Layer

- [ ] Add structured LLM scoring
- [ ] Generate strengths and gaps
- [ ] Produce evidence-grounded recommendations
- [ ] Add RAG over resume sections
- [ ] Validate LLM output with Pydantic
- [ ] Add confidence scores
- [ ] Add cost and latency tracking

## Version 0.5 — Alerts and Dashboard

- [ ] Add email notifications
- [ ] Prevent duplicate alerts
- [ ] Build Streamlit dashboard
- [ ] Add application-status tracking
- [ ] Add filtering by company, score, location, and date
- [ ] Add application links
- [ ] Add analytics

## Version 0.6 — Evaluation

- [ ] Build a manually labeled job dataset
- [ ] Compare keyword, embedding, and LLM approaches
- [ ] Measure precision, recall, and F1 score
- [ ] Track false-positive recommendations
- [ ] Tune alert thresholds

## Version 1.0 — Deployment

- [ ] Migrate from SQLite to PostgreSQL
- [ ] Add pgvector
- [ ] Containerize with Docker
- [ ] Deploy scheduled collection jobs
- [ ] Deploy dashboard
- [ ] Add production logging and monitoring
- [ ] Document installation and usage