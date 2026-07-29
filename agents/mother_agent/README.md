# FamilyAI – Grocery Agent (Mother Agent)

An intelligent backend system that manages household groceries using autonomous agents, machine learning, and LLM-powered recommendations.

This project is one module of the **FamilyAI** ecosystem, where each family member owns an independent agent. The Grocery Agent is designed for the Mother role and manages inventory, purchasing, consumption analysis, expiry monitoring, shopping planning, recipe suggestions, waste prevention, and demand forecasting.

---

# Project Overview

The Grocery Agent continuously monitors household grocery activities.

Instead of only storing grocery records, it observes purchasing patterns, predicts future consumption, detects shortages, monitors expiry dates, recommends recipes, prevents food waste, and prepares smart shopping plans.

This backend is built using FastAPI and is designed to integrate with the Father (Finance), Children, and Grandparents agents in the future.

---

# Features

## Inventory Agent

- Add grocery items
- View current inventory
- Track stock quantity

---

## Purchase History Agent

- Store purchase history
- Maintain purchase records
- Analyze buying behavior

---

## Consumption Analyzer Agent

- Record daily consumption
- Calculate average daily usage
- Estimate remaining days
- Generate AI recommendations using Groq LLM

---

## Smart Shopping Planner Agent

Automatically generates shopping suggestions when stock becomes low.

Example

Milk
Current Stock : 1
Suggested Purchase : 4

---

## Scheduler Agent

Runs automatic grocery checks at scheduled intervals.

Current implementation:

- Daily inventory scan
- Automatic shopping list generation

Future:

- Daily reports
- Weekly reports
- Monthly analytics

---

## Expiry Tracker Agent

Stores expiry dates.

Automatically identifies

- Expired items
- Near-expiry items
- Safe items

---

## Recipe Agent

Suggests recipes using available groceries.

Example

Available:

- Rice
- Tomato
- Onion
- Egg

Suggested Recipe

Tomato Egg Fried Rice

---

## Waste Prevention Agent

Analyzes

- Near-expiry foods
- Unused groceries

Provides suggestions to reduce food waste.

---

## Price Tracker Agent

Compares prices between stores.

(Currently backend ready.
Future version will connect with real grocery APIs.)

---

## Demand Forecasting (ML)

Machine Learning module predicts future grocery demand based on historical consumption.

Current model

- Linear Regression

Future upgrades

- Random Forest
- XGBoost
- LSTM
- Prophet

---

# Technology Stack

Backend

- Python
- FastAPI
- SQLAlchemy
- SQLite

AI

- Groq API
- Llama Models

Machine Learning

- Scikit-learn
- Pandas
- NumPy

Scheduler

- APScheduler

API Documentation

- Swagger UI
- OpenAPI

Version Control

- Git
- GitHub

---

# Project Structure

```
agentic_ai/
│
├── app/
│   ├── api/
│   ├── database/
│   ├── jobs/
│   ├── ml/
│   ├── models/
│   ├── scheduler/
│   ├── services/
│   ├── utils/
│   └── main.py
│
├── docs/
├── requirements.txt
├── README.md
└── .env
```

---

# Backend Architecture

```
                    User

                      │
                      │
             FastAPI REST API

                      │

    ┌─────────────────────────────────┐
    │                                 │
Inventory Agent                 Purchase Agent
    │                                 │
    └──────────────┬──────────────────┘
                   │
          Consumption Analyzer
                   │
           Groq Recommendation
                   │
       Shopping Planner Agent
                   │
           Scheduler Service
                   │
     Expiry / Recipe / Waste Agent
                   │
        ML Demand Forecasting
                   │
               SQLite Database
```

---

# API Endpoints

## Inventory

POST

```
/inventory/add
```

GET

```
/inventory/
```

---

## Purchase

POST

```
/purchase/add
```

GET

```
/purchase/history
```

---

## Consumption

POST

```
/consumption/add
```

GET

```
/consumption/history
```

---

## Consumption Analysis

GET

```
/analysis/{item_name}
```

---

## Expiry Tracker

POST

```
/expiry/add
```

GET

```
/expiry/check
```

---

## Recipe Agent

GET

```
/recipe/suggest
```

---

## Waste Prevention

GET

```
/waste/analyze
```

---

## Price Tracker

GET

```
/price/compare
```

---

## Forecast

GET

```
/forecast
```

---

# Installation

Clone repository

```bash
git clone https://github.com/yourusername/familyai-grocery-agent.git
```

Move into project

```bash
cd familyai-grocery-agent
```

Create virtual environment

```bash
python -m venv venv
```

Activate

Windows

```bash
venv\Scripts\activate
```

Linux / Mac

```bash
source venv/bin/activate
```

Install packages

```bash
pip install -r requirements.txt
```

Run

```bash
uvicorn app.main:app --reload
```

Swagger

```
http://127.0.0.1:8000/docs
```

OpenAPI

```
http://127.0.0.1:8000/openapi.json
```

---

# Environment Variables

Create a `.env` file

```
GROQ_API_KEY=your_api_key
DATABASE_URL=sqlite:///family.db
```

---

# Current Workflow

```
User

↓

Inventory Update

↓

Purchase History

↓

Consumption Logging

↓

Consumption Analysis

↓

Groq Recommendation

↓

Shopping Planner

↓

Scheduler

↓

Expiry Check

↓

Recipe Suggestion

↓

Waste Prevention

↓

Demand Forecasting

↓

Dashboard (Future)
```

---

# Future Roadmap

- React Dashboard
- JWT Authentication
- User Accounts
- Family Member Profiles
- OCR Bill Scanner
- Barcode Scanner
- Voice Assistant
- WhatsApp Notifications
- Email Notifications
- Weather-aware Grocery Planning
- Festival-based Grocery Prediction
- Multi-Agent Communication
- Father Agent Integration
- Children Agent Integration
- Grandparents Agent Integration

---

# FamilyAI Ecosystem

```
                   FamilyAI

                       │

    ┌────────────┬──────────────┬──────────────┬──────────────┐

 Father Agent   Mother Agent   Children Agent Grandparent Agent

 (Finance)       (Groceries)     (Education)     (Healthcare)

       │              │               │                │

       └──────────────┴───────────────┴────────────────┘

               Multi-Agent Coordinator

                        │

                  Shared Family Database

                        │

                 Unified React Dashboard
```

---

# Contributors

**Manivelavan K**

Backend Development

Mother (Grocery) Agent

---

# License

This project is developed for educational, research, and hackathon purposes.
