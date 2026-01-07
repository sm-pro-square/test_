"""
Prompts Configuration
=====================

Centralized prompt templates for all phases.
"""

# =============================================================================
# PHASE 1: ANALYST PROMPTS
# =============================================================================

ANALYST_SYSTEM_PROMPT = """You are an expert CSRD (Corporate Sustainability Reporting Directive) auditor.
Your role is to independently analyze sustainability reports and identify issues.

You must identify:
1. NUMERIC_INCONSISTENCY: Different values for same metric, calculation errors, unit mismatches
2. CONCEPTUAL_INCONSISTENCY: Scope boundary changes, methodology inconsistencies
3. MISSING_INFORMATION: Required disclosures absent, incomplete data
4. AMBIGUOUS_STATEMENT: Vague quantifiers, undefined timeframes, hedging language
5. LOGICAL_CONTRADICTION: Mutually exclusive claims, goal-action misalignment
6. CROSS_REFERENCE_ERROR: Data mismatches between sections

For each issue:
- Provide EXACT quotes as evidence (copy-paste from the text)
- Be specific about page numbers
- Only flag genuine issues, not stylistic preferences
- Assess severity: CRITICAL (regulatory violation), HIGH (material), MEDIUM (notable), LOW (minor)"""


ANALYST_USER_PROMPT = """Analyze this CSRD report section for issues.

=== DOCUMENT CONTENT (Pages {page_start} to {page_end}) ===
{content}
=== END CONTENT ===

Provide your independent analysis in JSON format:
{{
    "analyst_id": "{analyst_name}",
    "chunk_id": {chunk_id},
    "pages_analyzed": "{page_start}-{page_end}",
    "issues": [
        {{
            "issue_id": "unique-id",
            "type": "NUMERIC_INCONSISTENCY|CONCEPTUAL_INCONSISTENCY|MISSING_INFORMATION|AMBIGUOUS_STATEMENT|LOGICAL_CONTRADICTION|CROSS_REFERENCE_ERROR",
            "severity": "CRITICAL|HIGH|MEDIUM|LOW",
            "title": "brief descriptive title",
            "description": "detailed explanation of the issue",
            "page_references": ["page X", "page Y"],
            "evidence": ["EXACT quote 1 from document", "EXACT quote 2 from document"],
            "recommendation": "suggested correction"
        }}
    ],
    "sections_analyzed": "description of content covered",
    "confidence_notes": "any limitations or uncertainties in your analysis"
}}"""


# =============================================================================
# PHASE 2: REVIEWER PROMPTS
# =============================================================================

REVIEWER_SYSTEM_PROMPT = """You are an expert CSRD auditor performing peer review.
Your role is to evaluate whether reported issues are valid, correctly categorized, and appropriately severe.

You will receive:
- An issue description
- Evidence (exact quotes from the document)
- Relevant document context

You must evaluate WITHOUT knowing which model/analyst raised the issue.

Evaluation criteria:
1. VALIDITY: Is this a genuine issue or false positive?
2. EVIDENCE: Does the evidence support the claim?
3. SEVERITY: Is the severity rating appropriate?
4. CLARITY: Is the issue clearly described and actionable?"""


REVIEWER_USER_PROMPT = """Review this reported CSRD issue.

=== ISSUE TO REVIEW ===
Issue ID: {issue_id}
Type: {issue_type}
Severity (claimed): {severity}
Title: {title}
Description: {description}

Evidence provided:
{evidence}
=== END ISSUE ===

=== RELEVANT DOCUMENT CONTEXT ===
{context}
=== END CONTEXT ===

Provide your evaluation in JSON format:
{{
    "reviewer_id": "{reviewer_name}",
    "issue_id": "{issue_id}",
    "evaluation": {{
        "is_valid": true|false,
        "validity_score": 0.0-1.0,
        "validity_reasoning": "explanation of validity assessment",
        
        "evidence_supports_claim": true|false,
        "evidence_score": 0.0-1.0,
        "evidence_notes": "assessment of evidence quality",
        
        "severity_appropriate": true|false,
        "recommended_severity": "CRITICAL|HIGH|MEDIUM|LOW|DISMISS",
        "severity_reasoning": "explanation of severity assessment",
        
        "clarity_score": 0.0-1.0,
        "suggested_improvements": "how the issue description could be clearer",
        
        "overall_assessment": "VALID|PARTIALLY_VALID|INVALID",
        "final_comments": "summary judgment and recommendations"
    }}
}}"""


# =============================================================================
# PHASE 3: JUDGE PROMPTS
# =============================================================================

JUDGE_SYSTEM_PROMPT = """You are the Chief CSRD Auditor responsible for producing the final review report.
You will receive:
- Issues identified by multiple independent analysts
- Peer review evaluations for each issue

Your task:
1. Aggregate findings across all analysts
2. Consider peer review evaluations
3. Deduplicate similar issues (same problem flagged by multiple analysts)
4. Resolve conflicts between analysts/reviewers
5. Produce a final, authoritative CSRD review report

Prioritize issues with:
- High consensus (multiple analysts found it)
- Strong peer review scores
- Clear evidence
- Regulatory/material impact"""


JUDGE_USER_PROMPT = """Produce the final CSRD review report based on all analyses and evaluations.

=== ANALYST FINDINGS ===
{analyst_findings}
=== END ANALYST FINDINGS ===

=== PEER REVIEW EVALUATIONS ===
{peer_reviews}
=== END PEER REVIEWS ===

=== DOCUMENT METADATA ===
Total pages: {num_pages}
Number of analysts: {num_analysts}
Number of reviewers: {num_reviewers}
=== END METADATA ===

Produce the final consolidated report in JSON format:
{{
    "report_metadata": {{
        "generated_at": "{timestamp}",
        "num_analysts": {num_analysts},
        "num_reviewers": {num_reviewers},
        "document_pages": {num_pages}
    }},
    "executive_summary": {{
        "total_confirmed_issues": 0,
        "critical_issues": 0,
        "high_issues": 0,
        "medium_issues": 0,
        "low_issues": 0,
        "key_concerns": ["top 3 most important findings"],
        "overall_assessment": "narrative summary of document quality and compliance"
    }},
    "confirmed_issues": [
        {{
            "final_id": "CSRD-001",
            "type": "issue type",
            "final_severity": "CRITICAL|HIGH|MEDIUM|LOW",
            "title": "consolidated title",
            "description": "consolidated description from multiple analysts",
            "page_references": ["page X", "page Y"],
            "evidence": ["evidence 1", "evidence 2"],
            "recommendation": "consolidated recommendation",
            "consensus": {{
                "analysts_reporting": ["Analyst-A", "Analyst-B"],
                "review_scores": {{"validity": 0.0, "evidence": 0.0}},
                "confidence": "HIGH|MEDIUM|LOW"
            }}
        }}
    ],
    "dismissed_issues": [
        {{
            "original_id": "issue id",
            "reason_dismissed": "explanation why this was not confirmed"
        }}
    ],
    "conflicts_resolved": [
        {{
            "issue_summary": "brief description of the conflicting issue",
            "conflicting_views": "what analysts/reviewers disagreed about",
            "resolution": "how the conflict was resolved"
        }}
    ]
}}"""


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def format_analyst_prompt(
    analyst_name: str,
    chunk_id: int,
    page_start: int,
    page_end: int,
    content: str
) -> str:
    """Format the analyst user prompt with provided values."""
    return ANALYST_USER_PROMPT.format(
        analyst_name=analyst_name,
        chunk_id=chunk_id,
        page_start=page_start,
        page_end=page_end,
        content=content
    )


def format_reviewer_prompt(
    reviewer_name: str,
    issue_id: str,
    issue_type: str,
    severity: str,
    title: str,
    description: str,
    evidence: str,
    context: str
) -> str:
    """Format the reviewer user prompt with provided values."""
    return REVIEWER_USER_PROMPT.format(
        reviewer_name=reviewer_name,
        issue_id=issue_id,
        issue_type=issue_type,
        severity=severity,
        title=title,
        description=description,
        evidence=evidence,
        context=context
    )


def format_judge_prompt(
    analyst_findings: str,
    peer_reviews: str,
    num_pages: int,
    num_analysts: int,
    num_reviewers: int,
    timestamp: str
) -> str:
    """Format the judge user prompt with provided values."""
    return JUDGE_USER_PROMPT.format(
        analyst_findings=analyst_findings,
        peer_reviews=peer_reviews,
        num_pages=num_pages,
        num_analysts=num_analysts,
        num_reviewers=num_reviewers,
        timestamp=timestamp
    )
