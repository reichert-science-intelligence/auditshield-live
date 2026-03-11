# AuditShield Live — Architecture

## Overview
AuditShield Live is a Shiny for Python application for HEDIS/RADV chart
audit defense using a 3-source Agentic RAG coordinator and Claude API.

## Repo
- GitHub: reichert-science-intelligence/auditshield-live
- HuggingFace: rreichert-auditshield-live.hf.space

## Tech Stack
Shiny for Python · Supabase · Claude API · ChromaDB ·
Sentence Transformers · Docker

## Key Modules
- agentic_rag_coordinator.py — 3-source RAG orchestration
- validation_engine.py — HEDIS validation logic
- compound_pipeline.py — compound AI audit pipeline
- layer1_document_intelligence.py — document extraction
- layer3_self_correction.py — self-correction loop
- synthetic_chart_generator.py — synthetic test data

## CI
GitHub Actions: ruff · mypy · pytest · pip-audit
