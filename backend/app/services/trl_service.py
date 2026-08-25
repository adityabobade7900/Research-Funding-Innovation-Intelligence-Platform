from typing import List, Dict, Any, Optional
from app.schemas.innovation_scoring import TRLEstimationItem

TRL_DESCRIPTIONS = {
    1: ("Basic Principles Observed", "Basic Research"),
    2: ("Technology Concept Formulated", "Basic Research"),
    3: ("Experimental Proof of Concept", "Basic Research / Applied Feasibility"),
    4: ("Technology Validated in Lab", "Laboratory Validation"),
    5: ("Technology Validated in Relevant Environment", "Applied Technology Validation"),
    6: ("Technology Demonstrated in Relevant Environment", "System Demonstration"),
    7: ("System Prototype Demonstrated in Operational Environment", "Pre-Commercial System Demonstration"),
    8: ("Actual System Completed and Qualified", "Commercial / Operational Qualification"),
    9: ("Actual System Proven in Operational Environment", "Full Commercial / Operational Deployment"),
}


class TRLService:
    """
    Deterministic Technology Readiness Level (TRL 1-9) Estimation Engine.
    Evaluates empirical scientific publication maturity, patent disclosure lifecycle,
    grant status, multi-jurisdiction protection, and assignee industrial engagement.
    """

    @classmethod
    def estimate_trl(
        cls,
        pub_count: int,
        recent_pub_count: int,
        avg_pub_citations: float,
        patent_count: int,
        granted_patent_count: int,
        jurisdiction_count: int,
        assignee_count: int,
        has_industrial_assignee: bool = False,
        active_funding_count: int = 0,
    ) -> TRLEstimationItem:
        """
        Estimates TRL level from 1 to 9 based on rule-based evidence synthesis.
        """
        evidence: List[str] = []

        # Default fallback for completely empty portfolios
        if pub_count == 0 and patent_count == 0:
            return TRLEstimationItem(
                estimated_trl=1,
                trl_stage=TRL_DESCRIPTIONS[1][1],
                trl_name=TRL_DESCRIPTIONS[1][0],
                score=0.0,
                confidence="LOW",
                evidence=["Sparse baseline data: No indexed research publications or patent disclosures recorded."],
            )

        # 1. Evaluate Patent Lifecycle Signals (TRL 4-9)
        if granted_patent_count >= 8 and jurisdiction_count >= 3 and assignee_count >= 3:
            trl = 9
            evidence.append(f"Extensive global patent portfolio ({granted_patent_count} granted patents across {jurisdiction_count} jurisdictions).")
            evidence.append(f"Broad commercial applicant engagement with {assignee_count} distinct assignees.")
        elif granted_patent_count >= 4 and jurisdiction_count >= 3:
            trl = 8
            evidence.append(f"Substantial qualified patent portfolio ({granted_patent_count} granted patents) across multiple international registries ({jurisdiction_count} jurisdictions).")
            if has_industrial_assignee:
                evidence.append("Active corporate/industrial assignees indicate operational integration.")
        elif granted_patent_count >= 2 and (jurisdiction_count >= 2 or has_industrial_assignee):
            trl = 7
            evidence.append(f"Multi-jurisdiction granted patents ({granted_patent_count} grants across {jurisdiction_count} jurisdictions) indicate operational prototype demonstration.")
            if has_industrial_assignee:
                evidence.append("Industrial assignee participation indicates pre-commercial field testing.")
        elif granted_patent_count >= 2 or (granted_patent_count >= 1 and assignee_count >= 2):
            trl = 6
            evidence.append(f"Granted patent disclosures ({granted_patent_count} grants) with collaborative assignee participation ({assignee_count} assignees).")
            evidence.append("Demonstrates component/subsystem validation in a relevant environment.")
        elif granted_patent_count >= 1:
            trl = 5
            evidence.append(f"Initial granted patent protection ({granted_patent_count} grant) confirms functional technology validation in a relevant environment.")
        elif patent_count >= 1:
            trl = 4
            evidence.append(f"Active patent disclosures ({patent_count} pending applications) indicate laboratory component/subsystem validation.")
        else:
            # 2. Evaluate Academic / Publication Signals (TRL 1-3)
            if pub_count >= 5 or avg_pub_citations >= 15.0:
                trl = 3
                evidence.append(f"Substantial peer-reviewed publications ({pub_count} papers) with strong citation impact (average {avg_pub_citations:.1f} citations) establish experimental proof of concept.")
            elif pub_count >= 2 or avg_pub_citations >= 5.0:
                trl = 2
                evidence.append(f"Documented research publications ({pub_count} papers) demonstrate technology concept formulation and analytical validation.")
            else:
                trl = 1
                evidence.append(f"Early-stage academic publications ({pub_count} paper) document fundamental scientific principles.")

        # Supporting evidence items
        if pub_count > 0 and trl >= 4:
            evidence.append(f"Supported by {pub_count} foundational research publications (average {avg_pub_citations:.1f} citations).")

        if active_funding_count > 0:
            evidence.append(f"Aligned with {active_funding_count} active funding opportunity streams.")

        # Determine confidence
        total_data_points = pub_count + patent_count
        if total_data_points >= 6 and len(evidence) >= 2:
            confidence = "HIGH"
        elif total_data_points >= 2:
            confidence = "MEDIUM"
        else:
            confidence = "LOW"

        trl_name, trl_stage = TRL_DESCRIPTIONS[trl]
        score = round((float(trl) / 9.0) * 100.0, 2)

        return TRLEstimationItem(
            estimated_trl=trl,
            trl_stage=trl_stage,
            trl_name=trl_name,
            score=score,
            confidence=confidence,
            evidence=evidence,
        )
