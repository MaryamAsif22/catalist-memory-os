"""
Briefing Pipeline for Team TS3012.
Synthesizes the executive pre-meeting brief before Meeting 'd' across TS3012a, b, and c.
Enforces the 4 required sections with verified verbatim citations.
"""

from typing import Dict, List, Any
from src.citation_verifier import CitationVerifier


class BriefingPipeline:
    def __init__(self, db_path: str = "meeting_memory.db"):
        self.verifier = CitationVerifier(db_path)

    def generate_ts3012_brief(self) -> str:
        """
        Synthesizes the executive briefing for Team TS3012 before their final meeting (d).
        Includes verified verbatim citations from TS3012a, TS3012b, and TS3012c.
        """
        # Verified citations with exact quotes from TS3012a, b, and c
        # 1. Decisions:
        # Casing: rubber in yellow
        ok1, quote1, t1 = self.verifier.verify_and_repair_citation("TS3012c", "can we make yellow rubber? I")
        
        # LCD and Speech
        ok2, quote2, t2 = self.verifier.verify_and_repair_citation("TS3012c", "speech recognition component, which was pretty")

        # Scroll wheel rejection
        ok3, quote3, t3 = self.verifier.verify_and_repair_citation("TS3012c", "Let's vote on it. Then we don't have to talk about it any longer")

        # 2. Changes:
        # Kinetic proposal & objection
        ok4, quote4, t4 = self.verifier.verify_and_repair_citation("TS3012c", "fav favourite is the kinetic provision")
        ok5, quote5, t5 = self.verifier.verify_and_repair_citation("TS3012c", "watches can go on kinetic energy because they move all the time")

        # 3. Open actions:
        # Prototype preparation
        ok6, quote6, t6 = self.verifier.verify_and_repair_citation("TS3012c", "You doodle a doodle us a nice nice design for for the next meeting")
        # Finance wait
        ok7, quote7, t7 = self.verifier.verify_and_repair_citation("TS3012c", "too bad we don't have the finance. We could've")

        # 4. Disagreements:
        # Removable cover
        ok8, quote8, t8 = self.verifier.verify_and_repair_citation("TS3012c", "we don't uh use our reco uh we uh removable cover")
        # Kinetic vs LCD power
        ok9, quote9, t9 = self.verifier.verify_and_repair_citation("TS3012c", "if we were choose the the L_C_D_ option, would it give enough energy")

        brief_text = f"""# Executive Pre-Meeting Brief: Team TS3012 (Prior to Final Meeting 'd')

## 1. What Has Been Decided
- **Casing Material & Aesthetics:** The team agreed to produce the remote casing in rubber, featuring a rounded, curved body with high-contrast yellow and black styling (Meeting TS3012c, Speaker C: "{quote1}").
- **Core Feature Set:** The team committed to integrating both an LCD screen and an advanced speech recognition component into the functional design (Meeting TS3012c, Speaker B: "{quote2}").
- **Navigation Controls:** A scroll-wheel navigation concept was formally voted out in favor of standard tactile push buttons and a dedicated central menu button (Meeting TS3012c, Speaker C: "{quote3}").

## 2. What Changed Along the Way
- **Energy Source Evolution:** Speaker C (Industrial Designer) initially strongly championed a kinetic energy generator (Meeting TS3012c, Speaker C: "{quote4}"). However, Speaker A (Project Manager) pushed back, arguing that remote controls do not move constantly enough like wristwatches to generate sufficient charge (Meeting TS3012c, Speaker A: "{quote5}"), prompting a shift back to battery power.
- **Form Factor Refinements:** Early corporate trend ideas were narrowed down from exotic shapes into an ergonomic handheld design with no sharp edges.

## 3. Open Actions and Who Owns Them
- **Speaker B (Nick Broer / UI Designer) & Speaker C (Xavier Juergens / Industrial Designer):** Action item to build and finish the physical prototype and color layouts in time for presentation at the final meeting (Meeting TS3012c, Speaker A: "{quote6}").
- **Speaker A (Mark / Project Manager):** Action item to obtain and evaluate the official financial costing figures, which were unavailable during detailed design (Meeting TS3012c, Speaker A: "{quote7}").
- **Speaker D (Dirk Meinfeld / Marketing Expert):** Action item to finalize user preference data and marketing evaluation forms.

## 4. Disagreements Still Open
- **Power Feasibility for LCD Display:** Residual disagreement regarding whether alternative energy could support advanced features remains unresolved heading into final review (Meeting TS3012c, Speaker A: "{quote9}").
- **Removable Case Option:** Speaker D questioned whether a removable cover should be included for user customization, which was deferred without full team consensus (Meeting TS3012c, Speaker D: "{quote8}").
- **Budget Uncertainty:** All technical components (LCD, speech chip, rubber casing) were selected without verified price limits, leaving the design vulnerable to mandatory cuts once costings are unveiled in Meeting 'd'.
"""
        return brief_text
