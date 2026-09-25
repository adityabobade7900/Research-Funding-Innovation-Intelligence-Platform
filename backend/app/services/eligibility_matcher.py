from datetime import datetime, timezone
from typing import List, Optional, Set, Dict, Any

from app.models.funding import FundingOpportunity
from app.models.profile import Profile
from app.schemas.funding import EligibilityEvaluationResult


class EligibilityMatcher:
    """
    Deterministic, rule-based, and explainable eligibility evaluation engine for research funding opportunities.
    Computes compatibility across research domains, thematic keywords, geography, institution type, and opportunity lifecycle.
    """

    # Configurable deterministic scoring weights
    WEIGHT_DOMAIN: float = 35.0
    WEIGHT_KEYWORDS: float = 25.0
    WEIGHT_GEOGRAPHY: float = 20.0
    WEIGHT_INSTITUTION: float = 10.0
    WEIGHT_STATUS_DEADLINE: float = 10.0

    @classmethod
    def evaluate(
        cls,
        profile: Profile,
        opportunity: FundingOpportunity,
        evaluation_time: Optional[datetime] = None
    ) -> EligibilityEvaluationResult:
        """
        Evaluates a researcher's profile against a specific funding opportunity.
        Returns a structured, transparent, and explainable evaluation result.
        """
        now = evaluation_time or datetime.now(timezone.utc)

        matched_criteria: List[str] = []
        failed_criteria: List[str] = []
        warnings: List[str] = []
        missing_information: List[str] = []
        reasons: List[str] = []

        total_score: float = 0.0
        hard_failure: bool = False

        # =========================================================================
        # 1. Opportunity Lifecycle & Deadline (Weight: 10 pts)
        # =========================================================================
        status_score = 0.0
        opp_status = (opportunity.status or "open").lower()
        if opp_status in ["closed", "archived", "expired"]:
            failed_criteria.append(f"Opportunity is currently {opp_status.upper()}")
            reasons.append(f"Application window is closed (status: {opp_status})")
            hard_failure = True
        else:
            matched_criteria.append(f"Opportunity status is active ({opp_status})")
            status_score += 5.0

        if opportunity.application_deadline:
            deadline = opportunity.application_deadline
            if deadline.tzinfo is None:
                deadline = deadline.replace(tzinfo=timezone.utc)

            if deadline < now:
                failed_criteria.append("Application deadline has passed")
                reasons.append(f"Deadline expired on {deadline.strftime('%Y-%m-%d')}")
                hard_failure = True
            else:
                days_left = (deadline - now).days
                matched_criteria.append(f"Application deadline is open ({days_left} days remaining)")
                reasons.append(f"Deadline is valid until {deadline.strftime('%Y-%m-%d')}")
                status_score += 5.0
        else:
            matched_criteria.append("Application deadline is rolling / open")
            status_score += 5.0

        total_score += status_score

        # =========================================================================
        # 2. Research Domain Compatibility (Weight: 35 pts)
        # =========================================================================
        domain_score = 0.0
        opp_domains = {d.name.strip().lower() for d in opportunity.domains if d.name}
        profile_domains = {d.name.strip().lower() for d in profile.domains if d.name}

        if not opp_domains:
            # Opportunity has no explicit domain constraints
            matched_criteria.append("Research domain: Unrestricted / open to interdisciplinary research")
            reasons.append("Opportunity does not specify strict domain exclusions")
            domain_score = 25.0
        else:
            if not profile_domains:
                missing_information.append("Researcher profile has no research domains defined")
                warnings.append("Domain compatibility could not be verified due to missing profile domains")
                reasons.append("Profile lacks domain taxonomy entries")
                domain_score = 10.0
            else:
                matching_domains = profile_domains.intersection(opp_domains)
                if matching_domains:
                    domain_names_display = ", ".join([d.title() for d in matching_domains])
                    matched_criteria.append(f"Research domain match: {domain_names_display}")
                    reasons.append(f"Researcher domain aligns with opportunity focus ({domain_names_display})")
                    domain_score = cls.WEIGHT_DOMAIN
                else:
                    opp_domain_display = ", ".join([d.title() for d in opp_domains])
                    prof_domain_display = ", ".join([d.title() for d in profile_domains])
                    failed_criteria.append(
                        f"Research domain mismatch: Requires [{opp_domain_display}], profile lists [{prof_domain_display}]"
                    )
                    reasons.append("Primary research domain does not align with targeted funding domains")
                    domain_score = 0.0
                    hard_failure = True

        total_score += domain_score

        # =========================================================================
        # 3. Keyword, Interest & Technology Area Overlap (Weight: 25 pts)
        # =========================================================================
        keyword_score = 0.0
        # Aggregate profile keywords & interests
        profile_tokens: Set[str] = set()
        for kw in profile.keywords:
            if kw.keyword:
                profile_tokens.add(kw.keyword.strip().lower())
        for intr in profile.interests:
            if intr.interest_area:
                profile_tokens.add(intr.interest_area.strip().lower())
        for ta in profile.technology_areas:
            if ta.area_name:
                profile_tokens.add(ta.area_name.strip().lower())

        # Aggregate opportunity keywords & text
        opp_tokens: Set[str] = {k.keyword.strip().lower() for k in opportunity.keywords if k.keyword}
        opp_text = f"{opportunity.title or ''} {opportunity.description or ''} {opportunity.funding_program or ''}".lower()

        if not profile_tokens:
            missing_information.append("Researcher profile lacks keywords, research interests, or technology areas")
            warnings.append("Cannot compute specific topic overlap score without profile keywords")
            reasons.append("Add keywords to your profile to improve thematic matching")
            keyword_score = 5.0
        else:
            matched_keywords: List[str] = []
            for token in profile_tokens:
                if token in opp_tokens or (len(token) >= 3 and token in opp_text):
                    matched_keywords.append(token)

            if matched_keywords:
                sample_kws = ", ".join([k.title() for k in matched_keywords[:4]])
                matched_criteria.append(f"Thematic keyword & interest overlap ({len(matched_keywords)} matches: {sample_kws})")
                reasons.append(f"Strong topic alignment on keywords: {sample_kws}")
                keyword_score = min(cls.WEIGHT_KEYWORDS, 10.0 + len(matched_keywords) * 5.0)
            else:
                warnings.append("Low direct keyword/topic overlap between profile and opportunity description")
                reasons.append("Opportunity text does not explicitly mention your specified research interests")
                keyword_score = 5.0

        total_score += keyword_score

        # =========================================================================
        # 4. Geographic Eligibility (Weight: 20 pts)
        # =========================================================================
        geo_score = 0.0
        geo_restriction = (opportunity.geographic_restrictions or "").strip().lower()

        is_global_opp = (
            not geo_restriction
            or "global" in geo_restriction
            or "worldwide" in geo_restriction
            or "unrestricted" in geo_restriction
            or "international" in geo_restriction
        )

        if is_global_opp:
            matched_criteria.append("Geographic eligibility: Open globally or unrestricted")
            reasons.append("No geographic limitations apply to this opportunity")
            geo_score = cls.WEIGHT_GEOGRAPHY
        else:
            # Extract user's geographic signals from institution/affiliation
            user_affiliations = [
                profile.institution or "",
                profile.department or "",
            ]
            if hasattr(profile, "country") and profile.country:
                user_affiliations.append(profile.country)
            for ah in profile.academic_histories:
                if ah.institution:
                    user_affiliations.append(ah.institution)
            for rh in profile.research_histories:
                if rh.organization:
                    user_affiliations.append(rh.organization)

            combined_affil = " ".join(user_affiliations).lower()

            if not combined_affil.strip():
                missing_information.append("Researcher profile lacks institution and country affiliation")
                warnings.append(f"Geographic restriction [{opportunity.geographic_restrictions}] could not be verified")
                reasons.append("Please update your institution/affiliation details to verify country eligibility")
                geo_score = 8.0
            else:
                is_us_opp = "united states" in geo_restriction or "us" in geo_restriction or "usa" in geo_restriction
                is_eu_opp = "eu" in geo_restriction or "europe" in geo_restriction or "horizon" in geo_restriction

                US_KEYWORDS = ["united states", "usa", "u.s.", "u.s.a.", "mit", "stanford", "harvard", "caltech", "berkeley", "princeton", "yale", "columbia", "carnegie", "georgia tech", "purdue", "texas", "michigan", "illinois", "chicago", "cornell", "penn", "northwestern", "johns hopkins", "ucla", "ucsb", "ucsd", "ucsf", "national lab"]
                EU_KEYWORDS = ["europe", "european", "germany", "france", "italy", "spain", "netherlands", "belgium", "switzerland", "sweden", "denmark", "norway", "finland", "austria", "poland", "oxford", "cambridge", "max planck", "cnrs", "eth zurich", "eth", "inria", "sorbonne", "tum", "ku leuven", "cern"]

                is_user_us = any(u in combined_affil for u in US_KEYWORDS)
                is_user_eu = any(e in combined_affil for e in EU_KEYWORDS)

                if is_us_opp and is_user_us:
                    matched_criteria.append(f"Geographic eligibility satisfied: {opportunity.geographic_restrictions}")
                    reasons.append("Researcher affiliation matches required geographic jurisdiction (US)")
                    geo_score = cls.WEIGHT_GEOGRAPHY
                elif is_eu_opp and is_user_eu:
                    matched_criteria.append(f"Geographic eligibility satisfied: {opportunity.geographic_restrictions}")
                    reasons.append("Researcher affiliation matches required geographic jurisdiction (EU/Europe)")
                    geo_score = cls.WEIGHT_GEOGRAPHY
                elif is_us_opp and is_user_eu:
                    failed_criteria.append(f"Geographic restriction mismatch: Requires [{opportunity.geographic_restrictions}]")
                    reasons.append("Opportunity restricted to US entities; profile indicates European affiliation")
                    hard_failure = True
                    geo_score = 0.0
                elif is_eu_opp and is_user_us:
                    failed_criteria.append(f"Geographic restriction mismatch: Requires [{opportunity.geographic_restrictions}]")
                    reasons.append("Opportunity restricted to EU entities; profile indicates US affiliation")
                    hard_failure = True
                    geo_score = 0.0
                else:
                    matched_criteria.append(f"Geographic eligibility tentatively satisfied: {opportunity.geographic_restrictions}")
                    reasons.append("Affiliation appears compatible with geographic requirements")
                    geo_score = 15.0

        total_score += geo_score

        # =========================================================================
        # 5. Institution Eligibility (Weight: 10 pts)
        # =========================================================================
        inst_score = 0.0
        eligible_inst = (opportunity.eligible_institutions or "").strip().lower()

        if not eligible_inst or "unrestricted" in eligible_inst or "all" in eligible_inst:
            matched_criteria.append("Institution eligibility: Open to all research and academic institutions")
            reasons.append("No restrictive organizational constraints")
            inst_score = cls.WEIGHT_INSTITUTION
        else:
            user_inst = (profile.institution or "").strip().lower()
            if not user_inst:
                missing_information.append("Researcher profile does not specify primary institution")
                warnings.append(f"Institution type [{opportunity.eligible_institutions}] cannot be definitively verified")
                reasons.append("Add your primary institution to confirm organizational eligibility")
                inst_score = 5.0
            else:
                is_academic = any(a in user_inst for a in ["university", "college", "institute", "school", "faculty", "academy", "lab"])
                if is_academic:
                    matched_criteria.append(f"Institution type compatible: Higher Education & Academic Research ({profile.institution})")
                    reasons.append("Organization type meets eligibility criteria")
                    inst_score = cls.WEIGHT_INSTITUTION
                else:
                    matched_criteria.append(f"Institution affiliation listed: {profile.institution}")
                    inst_score = 8.0

        total_score += inst_score

        # Normalize score
        final_score = round(max(0.0, min(100.0, total_score)), 1)

        # =========================================================================
        # Final Determination (Transparent, Explainable Status)
        # =========================================================================
        is_empty_profile = (
            not profile_domains
            and not profile_tokens
            and not (profile.institution or "").strip()
        )

        if hard_failure:
            eligible = False
            eligibility_status = "INELIGIBLE"
        elif is_empty_profile or (not profile_domains and not profile_tokens):
            eligible = False
            eligibility_status = "INSUFFICIENT_DATA"
            reasons.insert(0, "Insufficient researcher profile data to determine definitive eligibility")
        elif final_score >= 50.0:
            eligible = True
            eligibility_status = "ELIGIBLE"
            reasons.insert(0, f"Profile demonstrates strong alignment ({final_score}% match) with opportunity criteria")
        else:
            eligible = False
            eligibility_status = "CONDITIONAL"
            reasons.insert(0, f"Partial alignment ({final_score}% match); review specific domain and keyword requirements")

        return EligibilityEvaluationResult(
            opportunity_id=opportunity.id,
            opportunity_title=opportunity.title,
            eligible=eligible,
            eligibility_status=eligibility_status,
            compatibility_score=final_score,
            matched_criteria=matched_criteria,
            failed_criteria=failed_criteria,
            warnings=warnings,
            missing_information=missing_information,
            reasons=reasons
        )
