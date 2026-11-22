#!/usr/bin/env python3
"""
main.py - Unified Production CLI & Application Entrypoint for Catalist Meeting Intelligence OS.

Commands:
  - serve   : Launch the high-aesthetic editorial UI + fixed intelligence engine
  - ask     : Query the multi-meeting intelligence agent with verbatim citations
  - brief   : Output the verified pre-meeting executive brief for Team TS3012
  - run     : Execute full 25-question benchmark evaluation generating answers.json
  - audit   : Run compliance, substring citation verification, and leakage audit
  - ingest  : Ingest raw transcripts into the high-performance SQLite store
"""

import os
import sys
import json
import argparse
import subprocess
from pathlib import Path

# Auto-delegate to local .venv if run with system Python without venv activated
def _maybe_reexec_in_venv():
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        return
    venv_py = Path(__file__).resolve().parent / ".venv" / "Scripts" / "python.exe"
    if venv_py.exists() and sys.executable.lower() != str(venv_py).lower():
        sys.exit(subprocess.call([str(venv_py)] + sys.argv))

_maybe_reexec_in_venv()

try:
    from dotenv import load_dotenv
    load_dotenv(override=True)
except ImportError:
    pass


def cmd_serve(args):
    """Launch the unified web application server."""
    from app import run_server
    port = getattr(args, "port", 8000)
    no_open = getattr(args, "no_open", False)
    run_server(port=port, open_browser=not no_open)


def cmd_ask(args):
    """Interactive / programmatic single-question query."""
    from src.agent import MeetingAgent

    agent = MeetingAgent()
    qid = args.qid or "CUSTOM_QUERY"
    qtext = args.query or ""

    if args.qid:
        with open(args.questions, "r", encoding="utf-8") as f:
            qdata = json.load(f)
        qitem = next((q for q in qdata["questions"] if q["question_id"] == args.qid), None)
        if not qitem:
            print(f"[Error] Question ID {args.qid} not found in {args.questions}")
            sys.exit(1)
        qid = qitem["question_id"]
        qtext = qitem["question"]
        team = qitem.get("team")
    else:
        team = getattr(args, "team", None) or agent.retriever.extract_team_id(qtext)

    print(f"\n" + "=" * 65)
    print(f"QUESTION [{qid}] (Team: {team or 'GLOBAL'}):")
    print(f"{qtext}")
    print("=" * 65)

    res = agent.answer_question({
        "question_id": qid,
        "team": team,
        "question": qtext
    })

    print("\nANSWER:")
    print(res["answer"])
    print("\nCITATIONS:")
    for idx, c in enumerate(res.get("citations", []), 1):
        print(f"  [{idx}] ({c['meeting_id']}): \"{c['quote']}\"")
    print(f"\nSynthesizer: {res.get('synthesizer')} | Latency: {res.get('latency_sec', 0.0)}s")
    print("=" * 65 + "\n")


def cmd_brief(args):
    """Display the pre-meeting executive brief for Team TS3012."""
    brief_text = ""
    if os.path.exists("answers.json"):
        with open("answers.json", "r", encoding="utf-8") as f:
            adata = json.load(f)
            brief_text = adata.get("brief", "")

    if not brief_text:
        from src.brief import generate_ts3012_brief
        brief_text = generate_ts3012_brief()

    print("\n" + "=" * 75)
    print("EXECUTIVE BRIEF: TEAM TS3012 (PRE-MEETING 'd')")
    print("=" * 75)
    print(brief_text)
    print("=" * 75 + "\n")

    if getattr(args, "output", None):
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(brief_text)
        print(f"Brief saved to {args.output}")


def cmd_run(args):
    """Run evaluation benchmark across all 25 questions."""
    from run import run_evaluation
    run_evaluation(team_filter=getattr(args, "team", None), fresh=getattr(args, "fresh", False))


def cmd_audit(args):
    """Run verification audit against evaluation benchmarks."""
    from eval_benchmarks import evaluate_answers_file
    evaluate_answers_file()


def cmd_ingest(args):
    """Deterministic transcript corpus ingestion."""
    from src.ingest import ingest_corpus
    ingest_corpus(args.transcripts, args.db)


def main():
    parser = argparse.ArgumentParser(description="Catalist Meeting Intelligence OS - Master CLI")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Serve
    p_serve = subparsers.add_parser("serve", help="Launch interactive UI frontend dashboard")
    p_serve.add_argument("--port", type=int, default=8000, help="Port to serve on (default: 8000)")
    p_serve.add_argument("--no-open", action="store_true", help="Do not automatically open browser")

    # Ask
    p_ask = subparsers.add_parser("ask", help="Live single-question demo")
    p_ask.add_argument("--qid", help="Benchmark Question ID (e.g. Q01 to Q25)")
    p_ask.add_argument("--query", help="Custom freeform question")
    p_ask.add_argument("--team", help="Optional Team ID filter (e.g. TS3006)")
    p_ask.add_argument("--questions", default="questions.json", help="Path to questions.json")

    # Brief
    p_brief = subparsers.add_parser("brief", help="Generate TS3012 executive brief")
    p_brief.add_argument("--output", help="Optional output text file path")

    # Run
    p_run = subparsers.add_parser("run", help="Run full benchmark across questions")
    p_run.add_argument("--team", help="Filter evaluation to specific team")
    p_run.add_argument("--fresh", action="store_true", help="Regenerate all answers from scratch")

    # Audit
    p_audit = subparsers.add_parser("audit", help="Run verification audit on answers.json")

    # Ingest
    p_ingest = subparsers.add_parser("ingest", help="Deterministic ingestion of transcripts")
    p_ingest.add_argument("--transcripts", default="transcripts", help="Path to transcripts")
    p_ingest.add_argument("--db", default="data/meeting_store.db", help="Path to output database")

    args = parser.parse_args()
    if not args.command:
        # Default behavior: run serve
        cmd_serve(argparse.Namespace(port=8000, no_open=False))
        return

    if args.command == "serve":
        cmd_serve(args)
    elif args.command == "ask":
        cmd_ask(args)
    elif args.command == "brief":
        cmd_brief(args)
    elif args.command == "run":
        cmd_run(args)
    elif args.command == "audit":
        cmd_audit(args)
    elif args.command == "ingest":
        cmd_ingest(args)


if __name__ == "__main__":
    main()
