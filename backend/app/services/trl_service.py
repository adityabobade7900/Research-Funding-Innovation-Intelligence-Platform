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
    Deterministic Technology Readiness Level (TRL 1-9) Estimation Heuristic.
    Informed by NASA/DoD TRL stage definitions. Evaluates empirical scientific
    publication maturity, patent disclosure lifecycle, grant status, multi-jurisdiction
    protection, and assignee industrial engagement as deterministic proxy signals.
    Does not constitute independent operational validation.
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
            evidence.append(f"Portfolio of {granted_patent_count} granted patents across {jurisdiction_count} jurisdictions with {assignee_count} distinct assignees is used by the deterministic project TRL heuristic as a proxy signal for the TRL 9 threshold. This does not constitute independent operational deployment, commercial operation, or mission success.")
        elif granted_patent_count >= 4 and jurisdiction_count >= 3:
            trl = 8
            evidence.append(f"Qualified portfolio of {granted_patent_count} granted patents across {jurisdiction_count} jurisdictions is used by the deterministic project TRL heuristic as a proxy signal for the TRL 8 threshold. This does not constitute independent operational qualification or commercial operation.")
            if has_industrial_assignee:
                evidence.append("Corporate/industrial assignees provide empirical proxy signals within the heuristic, but do not provide independent proof of operational deployment.")
        elif granted_patent_count >= 2 and (jurisdiction_count >= 2 or has_industrial_assignee):
            trl = 7
            evidence.append(f"Multi-jurisdiction granted patents ({granted_patent_count} grants across {jurisdiction_count} jurisdictions) are used by the deterministic project TRL heuristic as a proxy signal for the TRL 7 threshold. This does not constitute independent operational prototype validation.")
            if has_industrial_assignee:
                evidence.append("Industrial assignee participation serves as an empirical proxy signal within the heuristic; this does not constitute independent operational field validation.")
        elif granted_patent_count >= 2 or (granted_patent_count >= 1 and assignee_count >= 2):
            trl = 6
            evidence.append(f"Granted patent disclosures ({granted_patent_count} grants) with collaborative assignee participation ({assignee_count} assignees) are used by the deterministic project TRL heuristic as a proxy signal for the TRL 6 threshold. This does not constitute independent validation in a relevant environment.")
        elif granted_patent_count >= 1:
            trl = 5
            evidence.append(f"One granted patent provides evidence of formal patent protection and is used by the deterministic project TRL heuristic as a signal for the TRL 5 threshold. This does not constitute independent operational validation.")
        elif patent_count >= 1:
            trl = 4
            evidence.append(f"Active patent disclosures ({patent_count} application disclosures) provide evidence of technical disclosure and are used by the deterministic project TRL heuristic as a proxy signal for the TRL 4 laboratory validation threshold. This does not constitute independent laboratory validation.")
        else:
            # 2. Evaluate Academic / Publication Signals (TRL 1-3)
            if pub_count >= 5 or avg_pub_citations >= 15.0:
                trl = 3
                evidence.append(f"Peer-reviewed research publications ({pub_count} papers) with citation impact (average {avg_pub_citations:.1f} citations) are used by the deterministic project TRL heuristic as a proxy signal for the TRL 3 experimental proof-of-concept threshold.")
            elif pub_count >= 2 or avg_pub_citations >= 5.0:
                trl = 2
                evidence.append(f"Documented research publications ({pub_count} papers) demonstrate technology concept formulation and are used by the deterministic project TRL heuristic as a proxy signal for the TRL 2 threshold.")
            else:
                trl = 1
                evidence.append(f"Early-stage academic publication evidence ({pub_count} paper) documents fundamental scientific principles corresponding to the TRL 1 threshold.")

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
