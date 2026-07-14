# Architecture

## Overview

AI Career Agent is a modular job discovery and recommendation system.

The application currently:

1. Collects live job postings from external sources.
2. Converts each posting into a standardized `JobPosting` model.
3. Applies rule-based eligibility filters.
4. Stores qualifying jobs in a SQLite database.
5. Updates existing records without creating duplicates.

## Current Data Flow

```text
Job Source
    ↓
Job Collector
    ↓
JobPosting Model
    ↓
Eligibility Filters
    ↓
Job Repository
    ↓
SQLite Database