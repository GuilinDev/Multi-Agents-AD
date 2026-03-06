# CareLoop AI — One-Pager

> **Multi-Agent AI for Evidence-Based Nursing Home Care**

---

## The Problem: A $200B Crisis Running Blind

**1.3 million Americans** live in nursing homes. The industry spends **$200B/year** (Grand View Research, 2024) — yet clinical decisions are still made on gut instinct, paper logs, and fragmented protocols.

| Pain Point | Data |
|---|---|
| **Staffing crisis** | U.S. needs **3,000+ more nursing homes** by 2030 ("Silver Tsunami") |
| **Care hours declining** | Average nursing care dropped **7%** (4.13→3.85 hrs/day) since 2015 (KFF, 2025) |
| **Protocol compliance** | No standardized way to ensure evidence-based response to behavioral events |
| **AI adoption near-zero** | Healthcare represents **<2% of all AI agent deployments** (Anthropic, 2026) |

The gap is enormous: **$200B market, <2% AI penetration, and a workforce that's shrinking.**

---

## The Solution: CareLoop AI

CareLoop is a **multi-agent simulation platform** that models nursing home care — parsing clinical events, matching evidence-based protocols, and recommending interventions in real time.

**How it works:**
```
Clinical Event → AI Agent Parses → RAG Protocol Match → Intervention Recommendation → Outcome Tracking
  (e.g. sundowning)     (NLP)        (evidence-based)       (actionable steps)         (feedback loop)
```

**This is NOT a chatbot.** CareLoop is a decision-support system that ensures every caregiver response is grounded in published clinical evidence — not LLM hallucination.

---

## Technical Differentiation

| Feature | CareLoop | Typical "Healthcare AI" |
|---|---|---|
| **Multi-model ablation** | 4 LLMs (27-32B range) compared rigorously | Single model, no comparison |
| **Evidence grounding** | RAG over nursing protocols (CDC, CMS, Joanna Briggs) | Prompt-only, hallucination-prone |
| **XAI integration** | Explainable AI robustness validation (in review at *Applied Intelligence*) | Black box |
| **Simulation-first** | Validate before deploying to real patients | Ship and pray |

**Research advantage:** We bridge XAI robustness analysis (under review at *Applied Intelligence*, Springer) with multi-agent caregiving — a combination no existing system offers.

---

## Current Traction

🔬 **Ablation study running now** on NVIDIA DGX Spark (128GB unified memory):
- **4 models × 3 shifts = 12 experiment rounds**
- Models: Nemotron 30B, Qwen 3.5 27B, DeepSeek-R1 32B, Mistral Small 24B
- **204+ simulated events**, 25 patients, 7 event types
- **92% protocol coverage** across simulation runs

📄 **Paper target:** NeurIPS 2026 (Multi-model ablation + XAI robustness bridge)

🌐 **Live demo:** [Railway deployment](https://memowell-next-production.up.railway.app) with real simulation data

---

## Market Timing: Why Now

1. **Anthropic's 2026 Agent Autonomy Report** confirms healthcare AI adoption is embryonic (<2% of agent deployments) — software engineering is ~50%. The healthcare gap = **massive blue ocean**.

2. **CMS staffing mandates** (2024) require minimum nursing hours — facilities need tools to do more with less.

3. **LLM costs dropped 90%+ in 18 months** — running 4 models locally on consumer-grade AI hardware is now feasible.

4. **Regulatory tailwind:** FDA's evolving framework for Clinical Decision Support (CDS) software creates a pathway that didn't exist 2 years ago.

---

## Team

- **Guilin Zhang** — AI/ML researcher, GWU PhD coursework, publications in XAI robustness (Applied Intelligence, under review), quantum-classical ML (arXiv:2511.20922). Building on NVIDIA DGX Spark.
- **Kai Zhao** — [Role/Background]
- **Dr. Dezhi Wu** — Advisor, USC faculty

---

## The Ask

We're looking for:
- **Research collaboration** (clinical validation, IRB access, co-publication)
- **Strategic introductions** to healthcare systems and nursing home operators
- **Early-stage investment** to scale from simulation to pilot deployment

**Contact:** [Kai Zhao — email/LinkedIn]

---

*CareLoop AI — Because every caregiver deserves an evidence-based co-pilot.*
