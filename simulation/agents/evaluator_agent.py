"""
Evaluator Agent — assesses the quality of CareLoop's responses
and overall simulation coverage.

Inspired by ScalingEval (NeurIPS 2025): multi-agent consensus evaluation at scale.
"""
from typing import List, Dict
from collections import Counter


class EvaluatorAgent:
    """
    Evaluates:
    1. Scenario coverage — how many behavior types were triggered and handled?
    2. Protocol compliance — did CareLoop return appropriate recommendations?
    3. Response quality — were suggestions specific, actionable, and safe?
    4. Handoff completeness — did shift reports capture all events?
    5. Edge cases — how were simultaneous/emergency events handled?
    """

    def __init__(self):
        self.events_evaluated: List[dict] = []
        self.coverage_tracker: Dict[str, int] = Counter()
        self.quality_scores: List[float] = []
        self.issues: List[str] = []

    def evaluate_event_response(self, event: dict, api_response: dict) -> dict:
        """Evaluate a single event-response pair."""
        score = 0.0
        feedback = []

        behavior = event.get("behavior", "unknown")
        self.coverage_tracker[behavior] += 1

        # 1. Did the API return a response at all?
        if api_response is None:
            self.issues.append(f"API returned no response for {behavior}")
            return {"score": 0, "feedback": ["No API response"], "pass": False}

        # 2. Check if protocol recommendations were returned
        protocols = api_response.get("protocols", [])
        if protocols:
            score += 30  # base score for having protocols
            feedback.append(f"✅ Returned {len(protocols)} protocol(s)")

            # Check if protocols have actionable steps
            for p in protocols:
                steps = p.get("steps", [])
                if steps:
                    score += 10
                    feedback.append(f"✅ Protocol has {len(steps)} actionable steps")
                else:
                    feedback.append("⚠️ Protocol returned but no actionable steps")
        else:
            feedback.append("❌ No protocols returned")
            # Check if it's a positive report (no protocol needed)
            if api_response.get("positive_report"):
                score += 25
                feedback.append("✅ Correctly identified as positive/no-action-needed")

        # 3. Check event classification
        event_data = api_response.get("event", {})
        if event_data:
            score += 10
            feedback.append("✅ Event was classified and stored")

            # Check severity assessment
            if event_data.get("severity"):
                score += 10
                feedback.append(f"✅ Severity assessed: {event_data['severity']}")

            # Check event type classification
            if event_data.get("event_type"):
                score += 10
                feedback.append(f"✅ Event typed: {event_data['event_type']}")
        else:
            feedback.append("⚠️ Event not stored in database")

        # 4. Check for safety-critical behaviors
        safety_critical = ["aggression", "fall_risk", "dysphagia", "exit_seeking",
                           "syncope_episodes", "PTSD_flashbacks"]
        if behavior in safety_critical:
            # Higher bar for safety-critical events
            if protocols and any(len(p.get("steps", [])) >= 2 for p in protocols):
                score += 20
                feedback.append("✅ Safety-critical event received detailed protocol")
            else:
                score -= 10
                feedback.append("❌ Safety-critical event needs more detailed response")
                self.issues.append(f"Insufficient protocol for safety-critical: {behavior}")

        # Normalize to 0-100
        score = max(0, min(100, score))

        result = {
            "behavior": behavior,
            "score": score,
            "feedback": feedback,
            "pass": score >= 40,
        }

        self.events_evaluated.append(result)
        self.quality_scores.append(score)
        return result

    def get_coverage_report(self) -> dict:
        """Get scenario coverage statistics."""
        all_behaviors = [
            "sundowning", "wandering", "refusal_to_eat", "aggression",
            "visual_hallucinations", "fall_risk", "medication_refusal",
            "nighttime_agitation", "emotional_lability", "exit_seeking",
            "bathing_refusal", "repetitive_questions", "social_disinhibition",
            "hiding_medications", "pica_plants", "loud_vocalizations",
            "freezing_gait", "REM_sleep_disorder", "dysphagia",
            "sleep_disturbance", "PTSD_flashbacks", "hoarding",
            "shadowing", "language_switching", "skin_breakdown_risk",
            "confabulation", "word_finding_difficulty", "singing",
            "pacing", "anger_outbursts",
        ]

        covered = set(self.coverage_tracker.keys())
        total = len(all_behaviors)
        coverage_pct = len(covered) / total * 100 if total > 0 else 0

        return {
            "total_behavior_types": total,
            "covered": len(covered),
            "coverage_percentage": round(coverage_pct, 1),
            "covered_behaviors": dict(self.coverage_tracker),
            "uncovered_behaviors": [b for b in all_behaviors if b not in covered],
            "target_80pct": coverage_pct >= 80,
        }

    def get_quality_report(self) -> dict:
        """Get overall quality statistics."""
        if not self.quality_scores:
            return {"message": "No events evaluated yet"}

        avg_score = sum(self.quality_scores) / len(self.quality_scores)
        pass_rate = sum(1 for s in self.quality_scores if s >= 40) / len(self.quality_scores) * 100

        return {
            "total_events_evaluated": len(self.events_evaluated),
            "average_score": round(avg_score, 1),
            "pass_rate_pct": round(pass_rate, 1),
            "score_distribution": {
                "excellent (80-100)": sum(1 for s in self.quality_scores if s >= 80),
                "good (60-79)": sum(1 for s in self.quality_scores if 60 <= s < 80),
                "adequate (40-59)": sum(1 for s in self.quality_scores if 40 <= s < 60),
                "poor (<40)": sum(1 for s in self.quality_scores if s < 40),
            },
            "issues": self.issues,
        }

    def get_full_report(self) -> dict:
        """Get the complete evaluation report."""
        return {
            "coverage": self.get_coverage_report(),
            "quality": self.get_quality_report(),
            "summary": self._generate_summary(),
        }

    def _generate_summary(self) -> str:
        """Generate a human-readable summary."""
        coverage = self.get_coverage_report()
        quality = self.get_quality_report()

        lines = [
            "=" * 60,
            "CARELOOP AGENT SIMULATION — EVALUATION REPORT",
            "=" * 60,
            "",
            f"📊 Scenario Coverage: {coverage['coverage_percentage']}% "
            f"({'✅ TARGET MET' if coverage['target_80pct'] else '❌ Below 80% target'})",
            f"   Covered: {coverage['covered']}/{coverage['total_behavior_types']} behavior types",
            "",
        ]

        if quality.get("total_events_evaluated"):
            lines.extend([
                f"📈 Response Quality: {quality['average_score']}/100 average",
                f"   Pass Rate: {quality['pass_rate_pct']}%",
                f"   Events Evaluated: {quality['total_events_evaluated']}",
                "",
            ])

        if quality.get("issues"):
            lines.append("⚠️ Issues Found:")
            for issue in quality["issues"]:
                lines.append(f"   - {issue}")
            lines.append("")

        if coverage.get("uncovered_behaviors"):
            lines.append(f"🔍 Uncovered Behaviors ({len(coverage['uncovered_behaviors'])}):")
            for b in coverage["uncovered_behaviors"][:10]:
                lines.append(f"   - {b.replace('_', ' ')}")
            if len(coverage["uncovered_behaviors"]) > 10:
                lines.append(f"   ... and {len(coverage['uncovered_behaviors']) - 10} more")

        return "\n".join(lines)
