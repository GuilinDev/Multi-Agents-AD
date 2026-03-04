# CareLoop Agent Simulation — Virtual Nursing Home

A multi-agent simulation of a memory care facility, inspired by Stanford's [Generative Agents](https://arxiv.org/abs/2304.03442).

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│              Sunrise Memory Care Center                  │
│                                                         │
│  25 AI Patients ──→ Real CareLoop API ←── 8 AI Staff   │
│  (behavior gen)     (event/protocol)    (report/act)    │
│                          │                              │
│                    Evaluator Agent                       │
│                  (coverage + quality)                    │
└─────────────────────────────────────────────────────────┘
```

## Agents

### 🧓 Patient Agents (25)
- Each has a unique dementia profile (diagnosis, stage, personality, behaviors)
- Behaviors triggered by: time of day, environment, triggers, intervention history
- Covers: Alzheimer's, Vascular, Lewy Body, FTD, Parkinson's, Mixed, PCA, Alcohol-Related
- Stages: mild (2), moderate (15), severe (8)
- 30+ distinct behavior types

### 👩‍⚕️ Caregiver Agents (8)
- 3 skill levels: expert, intermediate, novice
- Different reporting quality (expert=clinical detail, novice=vague/uncertain)
- Day/Evening/Night shift coverage
- Call real CareLoop API endpoints

### 📊 Evaluator Agent
- Scenario coverage tracking (target: 80%)
- Protocol compliance checking
- Response quality scoring (0-100)
- Safety-critical event assessment

## Quick Start

```bash
# Run locally (requires CareLoop API running on localhost:8000)
cd /path/to/memowell-ai
python -m simulation.run_simulation --shift day

# Run against Railway deployment
python -m simulation.run_simulation --shift day --railway

# Run all three shifts
python -m simulation.run_simulation --shift day
python -m simulation.run_simulation --shift evening
python -m simulation.run_simulation --shift night

# Quiet mode (less output)
python -m simulation.run_simulation --shift day --quiet

# Custom time steps (default 30 min, smaller = more events)
python -m simulation.run_simulation --shift day --time-step 15
```

## Patient Roster

| # | Name | Diagnosis | Stage | Key Behaviors |
|---|------|-----------|-------|---------------|
| 1 | Margaret Chen | Alzheimer's | Moderate | Sundowning, refusal to eat |
| 2 | Robert Wilson | Alzheimer's | Severe | Wandering, aggression, exit-seeking |
| 3 | Dorothy Liu | Vascular | Mild | Repetitive questions, emotional lability |
| 4 | Harold Park | Lewy Body | Moderate | Hallucinations, fall risk (NO antipsychotics!) |
| 5 | Eleanor Suzuki | FTD | Moderate | Disinhibition, compulsive eating, pica |
| 6 | James O'Brien | Alzheimer's | Mild | Sleep disturbance, anxiety, denial |
| 7 | Betty Nakamura | Mixed | Severe | Dysphagia, skin breakdown, comfort care |
| 8 | George Kim | Alzheimer's | Moderate | Medication refusal, paranoia |
| 9 | Florence Martinez | Parkinson's | Moderate | Freezing gait, depression, fall risk |
| 10 | Walter Brown | Alzheimer's | Severe | Night agitation, PTSD, loud vocalizations |
| 11 | Helen Patel | Alzheimer's | Moderate | Purposeful wandering, role confusion |
| 12 | Arthur Wong | Alzheimer's | Moderate | Mealtime agitation, weight loss |
| 13 | Iris Thompson | Vascular | Moderate | Emotional lability, incontinence |
| 14 | Samuel Jackson | Lewy Body | Severe | Hallucinations, syncope, autonomic dysfunction |
| 15 | Catherine Ross | Alzheimer's | Moderate | Object attachment (dolls), separation anxiety |
| 16 | Frank Nguyen | FTD (PPA) | Moderate | Progressive aphasia, frustration |
| 17 | Ruth Anderson | Alzheimer's | Moderate | Hoarding, bathing refusal |
| 18 | Edward Davis | Alcohol-Related | Moderate | Confabulation, balance, alcohol-seeking |
| 19 | Gladys Cooper | Alzheimer's | Severe | End-of-life, singing, palliative care |
| 20 | Oscar Petrov | PCA | Moderate | Visual-spatial deficits, fall risk |
| 21 | Mabel Zhang | Alzheimer's | Moderate | Bilingual reversion, art-seeking |
| 22 | Thomas Lee | Early-Onset AD | Moderate | Pacing, anger, technology-seeking |
| 23 | Pearl Williams | Alzheimer's | Moderate | Shadowing, singing loudly |
| 24 | Victor Huang | bvFTD | Moderate | Sexual disinhibition, boundary violations |
| 25 | Lillian Foster | Alzheimer's | Moderate | Pica (plants), excessive sleepiness |

## Staff Roster

| # | Name | Role | Shift | Skill | Specialty |
|---|------|------|-------|-------|-----------|
| 1 | Lisa Chen | CNA | Day | Expert | Medication admin, behavioral mgmt |
| 2 | Marcus Johnson | CNA | Day | Intermediate | De-escalation, male residents |
| 3 | Sarah Miller | RN | Day | Expert | Clinical assessment, charge nurse |
| 4 | Amy Torres | CNA | Evening | Intermediate | Sundowning mgmt, music therapy |
| 5 | David Park | CNA | Night | Novice | Learning, may miss clinical signs |
| 6 | Nina Williams | RN | Night | Expert | Emergency response, night charge |
| 7 | Jennifer Liu | CNA | Day | Novice | Bilingual Mandarin, gentle |
| 8 | Carlos Reyes | CNA | Evening | Intermediate | Physical activities, bathing |

## Evaluation Metrics

- **Scenario Coverage**: % of 30+ behavior types triggered and handled
- **Protocol Quality**: Specificity, actionability, safety of CareLoop recommendations
- **Caregiver Variance**: How skill level affects reporting and outcomes
- **Safety-Critical Response**: Higher bar for dangerous events (falls, aggression, elopement)
- **Handoff Completeness**: Does shift report capture all events?

## References

1. Park, J.S., et al. "Generative Agents: Interactive Simulacra of Human Behavior." UIST 2023.
2. "ACE: Agentic Context Engineering." Stanford, 2025.
3. "ScalingEval: No-Human-in-the-Loop Multi-Agent Evaluation." NeurIPS Workshop, 2025.
