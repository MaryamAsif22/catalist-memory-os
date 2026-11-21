"""
Query Planner & Decomposer for Catalist Media Meeting Memory System.
Deconstructs multi-hop questions into phased sub-queries, identifies target teams,
and resolves cross-meeting entity references.
"""

import re
from typing import Dict, List, Optional, Any


STOPWORDS = {
    "the", "a", "an", "and", "or", "of", "to", "in", "for", "with", "on", "at", "by",
    "from", "about", "what", "which", "who", "when", "where", "why", "how", "did",
    "does", "was", "were", "is", "are", "team", "their", "they", "them", "first",
    "second", "last", "end", "final", "between", "meetings", "remote", "design"
}


class QueryPlanner:
    def __init__(self):
        pass

    def extract_team_id(self, question_text: str, default_team: Optional[str] = None) -> Optional[str]:
        """Extracts the 6-character team ID (e.g. TS3006, ES2003, IS1002)."""
        match = re.search(r"\b([A-Z]{2}\d{4})\b", question_text)
        if match:
            return match.group(1)
        return default_team

    def decompose_query(self, question_id: str, question_text: str, team_id: str) -> Dict[str, Any]:
        """
        Decomposes a question into structured retrieval targets across phases.
        """
        # Clean text and extract core content words
        words = re.findall(r"[A-Za-z0-9_]+", question_text.lower())
        content_words = [w for w in words if w not in STOPWORDS and len(w) > 2]

        # Specific domain entity mappings
        domain_synonyms = {
            "lcd": ["lcd", "screen", "display", "l_c_d_"],
            "speech": ["speech", "voice", "recognition", "talk"],
            "material": ["case", "casing", "material", "rubber", "plastic", "wood", "titanium"],
            "energy": ["energy", "battery", "power", "solar", "kinetic", "lithium"],
            "cost": ["cost", "budget", "price", "euros", "expensive", "cut", "limit"],
            "lost": ["lost", "find", "locate", "beeper", "beep"],
            "buttons": ["buttons", "wheel", "joystick", "navigation", "keypad"],
            "fruit": ["fruit", "vegetable", "banana", "shape", "curve"],
        }

        expanded_keywords = set(content_words)
        for term, synonyms in domain_synonyms.items():
            if term in words or any(s in words for s in synonyms):
                expanded_keywords.update(synonyms)

        # Formulate FTS5 query string
        fts_query = " OR ".join(f'"{kw}"' for kw in list(expanded_keywords)[:10])

        return {
            "question_id": question_id,
            "team_id": team_id,
            "raw_question": question_text,
            "keywords": list(expanded_keywords),
            "fts_query": fts_query,
            "early_phases": ["a", "b"],
            "late_phases": ["c", "d"]
        }
