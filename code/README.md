# Support Triage Agent - Architecture Overview

## Design Philosophy
This agent uses a modular pipeline architecture with specialized components for safety, classification, retrieval, and response generation.

## Components

### 1. Safety Checker (`safety.py`)
- Detects high-risk keywords (fraud, security, legal)
- Identifies out-of-scope questions
- Determines escalation necessity

### 2. Product Classifier (`classifier.py`)
- Maps tickets to HackerRank/Claude/Visa
- Infers product from content if not specified
- Identifies specific product areas (billing, API, fraud)

### 3. Document Retriever (`retriever.py`)
- Hybrid similarity matching (semantic + keyword)
- Learns from sample tickets
- Prioritizes documented answers over generation

### 4. Response Generator (`response_gen.py`)
- Grounds responses in retrieved docs
- Escalates low-confidence cases
- Provides citations when available

## Decision Flow
1. Check risk → Escalate if high-risk
2. Classify product → Route to correct domain
3. Retrieve docs → Find similar solved cases
4. Generate response → Only if confidence > threshold
5. Escalate otherwise

## Escalation Triggers
- Security/fraud keywords
- Permission override requests  
- Low confidence matches (<40%)
- Unclassified products

## Running the Agent
```bash
pip install -r requirements.txt
python agent.py