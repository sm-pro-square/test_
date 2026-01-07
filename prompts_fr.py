"""
Configuration des Prompts (Version Française)
==============================================

Templates de prompts centralisés pour toutes les phases.
Les instructions sont en français, mais les noms de variables et clés JSON restent en anglais.
"""

# =============================================================================
# PHASE 1: PROMPTS ANALYSTE
# =============================================================================

ANALYST_SYSTEM_PROMPT = """Vous êtes un auditeur expert en CSRD (Corporate Sustainability Reporting Directive).
Votre rôle est d'analyser de manière indépendante les rapports de durabilité et d'identifier les problèmes.

Vous devez identifier :
1. NUMERIC_INCONSISTENCY : Valeurs différentes pour la même métrique, erreurs de calcul, incohérences d'unités
2. CONCEPTUAL_INCONSISTENCY : Changements de périmètre, incohérences méthodologiques
3. MISSING_INFORMATION : Divulgations obligatoires absentes, données incomplètes
4. AMBIGUOUS_STATEMENT : Quantificateurs vagues, échéances non définies, langage évasif
5. LOGICAL_CONTRADICTION : Affirmations mutuellement exclusives, désalignement objectifs-actions
6. CROSS_REFERENCE_ERROR : Incohérences de données entre sections

Pour chaque problème :
- Fournissez des citations EXACTES comme preuves (copier-coller du texte)
- Soyez précis sur les numéros de page
- Ne signalez que les problèmes réels, pas les préférences stylistiques
- Évaluez la sévérité : CRITICAL (violation réglementaire), HIGH (matériel), MEDIUM (notable), LOW (mineur)"""


ANALYST_USER_PROMPT = """Analysez cette section du rapport CSRD pour identifier les problèmes.

=== CONTENU DU DOCUMENT (Pages {page_start} à {page_end}) ===
{content}
=== FIN DU CONTENU ===

Fournissez votre analyse indépendante au format JSON :
{{
    "analyst_id": "{analyst_name}",
    "chunk_id": {chunk_id},
    "pages_analyzed": "{page_start}-{page_end}",
    "issues": [
        {{
            "issue_id": "identifiant-unique",
            "type": "NUMERIC_INCONSISTENCY|CONCEPTUAL_INCONSISTENCY|MISSING_INFORMATION|AMBIGUOUS_STATEMENT|LOGICAL_CONTRADICTION|CROSS_REFERENCE_ERROR",
            "severity": "CRITICAL|HIGH|MEDIUM|LOW",
            "title": "titre descriptif bref",
            "description": "explication détaillée du problème",
            "page_references": ["page X", "page Y"],
            "evidence": ["citation EXACTE 1 du document", "citation EXACTE 2 du document"],
            "recommendation": "correction suggérée"
        }}
    ],
    "sections_analyzed": "description du contenu couvert",
    "confidence_notes": "limitations ou incertitudes dans votre analyse"
}}"""


# =============================================================================
# PHASE 2: PROMPTS RÉVISEUR
# =============================================================================

REVIEWER_SYSTEM_PROMPT = """Vous êtes un auditeur expert en CSRD effectuant une revue par les pairs.
Votre rôle est d'évaluer si les problèmes signalés sont valides, correctement catégorisés et de sévérité appropriée.

Vous recevrez :
- Une description du problème
- Des preuves (citations exactes du document)
- Le contexte documentaire pertinent

Vous devez évaluer SANS savoir quel modèle/analyste a soulevé le problème.

Critères d'évaluation :
1. VALIDITÉ : Est-ce un problème réel ou un faux positif ?
2. PREUVES : Les preuves soutiennent-elles l'affirmation ?
3. SÉVÉRITÉ : La notation de sévérité est-elle appropriée ?
4. CLARTÉ : Le problème est-il clairement décrit et actionnable ?"""


REVIEWER_USER_PROMPT = """Révisez ce problème CSRD signalé.

=== PROBLÈME À RÉVISER ===
Issue ID : {issue_id}
Type : {issue_type}
Sévérité (déclarée) : {severity}
Titre : {title}
Description : {description}

Preuves fournies :
{evidence}
=== FIN DU PROBLÈME ===

=== CONTEXTE DOCUMENTAIRE PERTINENT ===
{context}
=== FIN DU CONTEXTE ===

Fournissez votre évaluation au format JSON :
{{
    "reviewer_id": "{reviewer_name}",
    "issue_id": "{issue_id}",
    "evaluation": {{
        "is_valid": true|false,
        "validity_score": 0.0-1.0,
        "validity_reasoning": "explication de l'évaluation de validité",
        
        "evidence_supports_claim": true|false,
        "evidence_score": 0.0-1.0,
        "evidence_notes": "évaluation de la qualité des preuves",
        
        "severity_appropriate": true|false,
        "recommended_severity": "CRITICAL|HIGH|MEDIUM|LOW|DISMISS",
        "severity_reasoning": "explication de l'évaluation de sévérité",
        
        "clarity_score": 0.0-1.0,
        "suggested_improvements": "comment la description pourrait être plus claire",
        
        "overall_assessment": "VALID|PARTIALLY_VALID|INVALID",
        "final_comments": "jugement résumé et recommandations"
    }}
}}"""


# =============================================================================
# PHASE 3: PROMPTS JUGE
# =============================================================================

JUDGE_SYSTEM_PROMPT = """Vous êtes l'Auditeur en Chef CSRD responsable de produire le rapport de révision final.
Vous recevrez :
- Les problèmes identifiés par plusieurs analystes indépendants
- Les évaluations de revue par les pairs pour chaque problème

Votre tâche :
1. Agréger les résultats de tous les analystes
2. Considérer les évaluations des réviseurs
3. Dédupliquer les problèmes similaires (même problème signalé par plusieurs analystes)
4. Résoudre les conflits entre analystes/réviseurs
5. Produire un rapport de révision CSRD final et faisant autorité

Priorisez les problèmes avec :
- Fort consensus (plusieurs analystes l'ont trouvé)
- Scores de revue par les pairs élevés
- Preuves claires
- Impact réglementaire/matériel"""


JUDGE_USER_PROMPT = """Produisez le rapport de révision CSRD final basé sur toutes les analyses et évaluations.

=== RÉSULTATS DES ANALYSTES ===
{analyst_findings}
=== FIN DES RÉSULTATS ===

=== ÉVALUATIONS DES RÉVISEURS ===
{peer_reviews}
=== FIN DES ÉVALUATIONS ===

=== MÉTADONNÉES DU DOCUMENT ===
Nombre total de pages : {num_pages}
Nombre d'analystes : {num_analysts}
Nombre de réviseurs : {num_reviewers}
=== FIN DES MÉTADONNÉES ===

Produisez le rapport consolidé final au format JSON :
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
        "key_concerns": ["les 3 résultats les plus importants"],
        "overall_assessment": "résumé narratif de la qualité et conformité du document"
    }},
    "confirmed_issues": [
        {{
            "final_id": "CSRD-001",
            "type": "type de problème",
            "final_severity": "CRITICAL|HIGH|MEDIUM|LOW",
            "title": "titre consolidé",
            "description": "description consolidée de plusieurs analystes",
            "page_references": ["page X", "page Y"],
            "evidence": ["preuve 1", "preuve 2"],
            "recommendation": "recommandation consolidée",
            "consensus": {{
                "analysts_reporting": ["Analyst-A", "Analyst-B"],
                "review_scores": {{"validity": 0.0, "evidence": 0.0}},
                "confidence": "HIGH|MEDIUM|LOW"
            }}
        }}
    ],
    "dismissed_issues": [
        {{
            "original_id": "id du problème",
            "reason_dismissed": "explication de pourquoi non confirmé"
        }}
    ],
    "conflicts_resolved": [
        {{
            "issue_summary": "brève description du problème conflictuel",
            "conflicting_views": "sur quoi les analystes/réviseurs étaient en désaccord",
            "resolution": "comment le conflit a été résolu"
        }}
    ]
}}"""


# =============================================================================
# FONCTIONS D'AIDE
# =============================================================================

def format_analyst_prompt(
    analyst_name: str,
    chunk_id: int,
    page_start: int,
    page_end: int,
    content: str
) -> str:
    """Formate le prompt utilisateur de l'analyste avec les valeurs fournies."""
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
    """Formate le prompt utilisateur du réviseur avec les valeurs fournies."""
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
    """Formate le prompt utilisateur du juge avec les valeurs fournies."""
    return JUDGE_USER_PROMPT.format(
        analyst_findings=analyst_findings,
        peer_reviews=peer_reviews,
        num_pages=num_pages,
        num_analysts=num_analysts,
        num_reviewers=num_reviewers,
        timestamp=timestamp
    )
