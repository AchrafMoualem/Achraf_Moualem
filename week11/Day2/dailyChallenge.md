# 911 AI Triage Agent — Design Document

---

## 1. Environment Definition

The agent perceives three inputs at the start of every call:

- **Symptom transcript** — voice-to-text or typed description of what the caller is experiencing
- **Caller location** — GPS coordinates or a street address provided by the caller or pulled from the phone system
- **Caller identity & medical history** — name, date of birth, and any prior records on file (allergies, conditions, medications)

---

## 2. Tools

| Tool | What it consumes | What it returns |
|---|---|---|
| **Symptom Checker API** (e.g. Infermedica) | Symptom keywords, age, sex | Probable conditions, red-flag flags |
| **Triage Scoring Model** (fine-tuned LLM) | Full symptom transcript + condition list | Urgency score 0–100 |
| **Ambulance Dispatch API** (internal) | Location, urgency level, patient notes | Estimated arrival time, unit ID |

---

## 3. State Schema

The agent keeps the following fields in memory for the duration of the call:

```json
{
  "caller_id": "string",
  "contact_number": "string",
  "location": "string",
  "medical_history": ["string"],
  "reported_symptoms": ["string"],
  "urgency_score": 0,
  "urgency_level": "High | Medium | Low",
  "actions_taken": ["string"],
  "call_timestamp": "ISO 8601 string"
}
```

---

## 4. Decision-Making Process

```
START
  │
  ▼
Receive transcript + location + identity
  │
  ▼
Call Symptom Checker API
  → extract symptom keywords and red-flag conditions
  │
  ▼
Call Triage Scoring Model
  → receive urgency score (0–100)
  │
  ├── Score >= 70 → HIGH
  │     → Dispatch ambulance immediately via Dispatch API
  │     → Log action to state
  │
  ├── Score 40–69 → MEDIUM
  │     → Advise caller to go to nearest urgent care
  │     → Provide address and estimated wait time
  │     → Log action to state
  │
  └── Score < 40 → LOW
        → Provide self-care instructions
        → Advise to call back if symptoms worsen
        → Log action to state
  │
  ▼
END — save full state to incident log
```

---

## 5. Agent Classification

**Chosen architecture: Hybrid**

The agent uses a reactive layer for immediate danger signals (e.g. caller says "not breathing" → skip scoring, dispatch instantly) and a deliberative layer for all other cases, where it queries tools, builds a picture of the situation, and reasons through urgency before acting.

It maintains state across the call so that each tool call is informed by everything learned so far. It also plans ahead — for example, it pre-fetches the nearest hospital before announcing a recommendation — rather than reacting blindly to each input in isolation.

---

## 6. Comparison to a Reactive Agent

A purely **Reactive** agent would skip state and planning entirely — each input triggers a fixed rule with no memory of what came before.

| Dimension | Hybrid (chosen) | Reactive |
|---|---|---|
| **Memory** | Full state stored and updated throughout the call | No memory — each input handled independently |
| **Planning** | Queries multiple tools, reasons over combined results | Matches input directly to a pre-written rule |
| **Tool invocation** | Tools called in sequence, results inform each other | Tools (if any) called once per trigger, in isolation |
| **Speed** | Slightly slower — multi-step reasoning adds latency | Very fast — near-instant rule lookup |
| **Reliability** | Higher — context reduces misclassification | Lower — one ambiguous phrase can cause a wrong dispatch |
| **Intelligence** | Can handle complex, multi-symptom scenarios | Struggles with anything outside the rule set |

---

## 7. Reflection

**What fails if the agent does not maintain state?**

Without state, the agent cannot connect information shared at different points in the call — for example, if a caller mentions chest pain early on and then reports dizziness two minutes later, a stateless agent treats these as unrelated events and may score each one too low to trigger a dispatch. It also cannot track what actions have already been taken, which risks sending duplicate ambulances or giving conflicting advice within the same call.

**Why are external tools essential in an EMR dispatch scenario?**

No single language model has reliable, real-time access to a caller's medical records, live ambulance availability, or up-to-date hospital locations — all of which change by the minute. External APIs provide ground-truth, structured data that the agent could not safely hallucinate: getting a patient's allergy history wrong or dispatching to an unavailable unit could directly cost a life. Tools turn the agent from a conversational interface into an operational system that is actually connected to the real world.
