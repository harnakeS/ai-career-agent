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

- [x] Create structured candidate profile
- [x] Build deterministic rule-based matcher
- [x] Integrate deterministic scoring into the processing pipeline
- [x] Persist match scores in the database
- [x] Refactor deterministic scoring into reusable category components
- [x] Add category-level score breakdowns
- [ ] Improve category weighting
- [ ] Add education matching
- [ ] Add certification matching
- [ ] Add citizenship matching
- [ ] Add experience matching
- [ ] Add semantic embedding similarity
- [ ] Combine rule and embedding scores

## Version 0.4 — AI Recommendation Layer

- [ ] Integrate LLM evaluation
- [ ] Generate strengths and gaps
- [ ] Generate "Apply / Consider / Skip" recommendations
- [ ] Add RAG over resume sections
- [ ] Validate LLM output with Pydantic
- [ ] Add confidence scores
- [ ] Compare LLM recommendations with rule-based scoring

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

## Long-Term Vision

- [ ] Support 100+ companies
- [ ] Multiple resume profiles (AI, Backend, Data, etc.)
- [ ] Personalized application tracker
- [ ] Resume optimization suggestions for each job
- [ ] Cover letter generation
- [ ] Interview preparation based on job description
- [ ] Recruiter analytics dashboard
- [ ] Cloud deployment (Azure)