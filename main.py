#!/usr/bin/env python3
"""
Catalist Media Meeting Memory Agent - Unified CLI Entrypoint.
Provides commands for:
  - Ingestion (deterministic, zero LLM)
  - Live single-question demo
  - TS3012 executive brief generation
  - Full benchmark execution generating answers.json
  - Programmatic submission audit
  - Interactive UI server (frontend)
"""

import os
import sys
import json
import argparse
from typing import Dict, List, Any

from src.ingestion import ingest_corpus
from src.query_planner import QueryPlanner
from src.temporal_resolver import TemporalResolver
from src.briefing_pipeline import BriefingPipeline


def cmd_ingest(args):
    print(">>> Running Deterministic Transcript Ingestion...")
    ingest_corpus(args.transcripts, args.db)


def cmd_ask(args):
    db_path = args.db
    if not os.path.exists(db_path):
        print(f"Database {db_path} not found. Running ingestion first...")
        ingest_corpus(args.transcripts, db_path)

    resolver = TemporalResolver(db_path)
    planner = QueryPlanner()

    if args.qid:
        with open(args.questions, "r", encoding="utf-8") as f:
            qdata = json.load(f)
        qitem = next((q for q in qdata["questions"] if q["question_id"] == args.qid), None)
        if not qitem:
            print(f"Error: Question ID {args.qid} not found in {args.questions}")
            sys.exit(1)
        qid = qitem["question_id"]
        qtext = qitem["question"]
        team = qitem["team"]
    else:
        qid = "DEMO"
        qtext = args.query
        team = planner.extract_team_id(qtext, default_team="TS3012")

    print(f"\n=======================================================")
    print(f"QUESTION [{qid}] (Team: {team}):")
    print(f"{qtext}")
    print(f"=======================================================")

    res = resolver.resolve_question(qid, qtext, team)

    print("\nANSWER:")
    print(res["answer"])
    print("\nCITATIONS:")
    for i, c in enumerate(res["citations"], 1):
        print(f"  [{i}] ({c['meeting_id']}): \"{c['quote']}\"")
    print(f"=======================================================\n")


def cmd_brief(args):
    db_path = args.db
    if not os.path.exists(db_path):
        print(f"Database {db_path} not found. Running ingestion first...")
        ingest_corpus(args.transcripts, db_path)

    pipeline = BriefingPipeline(db_path)
    brief = pipeline.generate_ts3012_brief()

    print("\n" + "=" * 80)
    print("EXECUTIVE BRIEF: TEAM TS3012 (PRE-MEETING 'd')")
    print("=" * 80)
    print(brief)
    print("=" * 80 + "\n")

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(brief)
        print(f"Brief saved to {args.output}")


def cmd_run(args):
    db_path = args.db
    if not os.path.exists(db_path):
        print(f"Database {db_path} not found. Running ingestion first...")
        ingest_corpus(args.transcripts, db_path)

    with open(args.questions, "r", encoding="utf-8") as f:
        qdata = json.load(f)

    questions = qdata.get("questions", [])
    print(f"\n>>> Executing full benchmark across {len(questions)} questions...")

    resolver = TemporalResolver(db_path)
    answers = []

    for idx, q in enumerate(questions, 1):
        qid = q["question_id"]
        team = q["team"]
        qtext = q["question"]
        print(f"  [{idx:02d}/25] Resolving {qid} for team {team}...", end="\r")
        res = resolver.resolve_question(qid, qtext, team)
        answers.append(res)

    print(f"\n>>> Synthesizing executive pre-meeting brief for Team TS3012...")
    pipeline = BriefingPipeline(db_path)
    brief_text = pipeline.generate_ts3012_brief()

    submission = {
        "answers": answers,
        "brief": brief_text
    }

    out_file = args.output or "answers.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(submission, f, indent=2)

    print(f"\n[DONE] Full submission saved to {out_file} ({len(answers)} answers + executive brief).")

    if args.verify:
        print("\n>>> Launching automated verification audit...")
        from scripts.verify_submission import audit_submission
        audit_submission(out_file, args.questions, args.transcripts)


def cmd_audit(args):
    from scripts.verify_submission import audit_submission
    audit_submission(args.answers, args.questions, args.transcripts)


def cmd_serve(args):
    import http.server
    import socketserver

    port = args.port
    directory = args.dir

    if not os.path.exists(os.path.join(directory, "index.html")):
        print(f"Error: {directory}/index.html not found. Building frontend first...")
        from scripts import build_frontend

    class Handler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *a, **kw):
            super().__init__(*a, directory=directory, **kw)

        def end_headers(self):
            self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate, max-age=0')
            self.send_header('Pragma', 'no-cache')
            self.send_header('Expires', '0')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type')
            super().end_headers()

        def do_OPTIONS(self):
            self.send_response(200)
            self.end_headers()

        def do_POST(self):
            if self.path == '/api/ask':
                from src.dynamic_agent import DynamicMeetingAgent
                agent = DynamicMeetingAgent()

                content_length = int(self.headers.get('Content-Length', 0))
                body = self.rfile.read(content_length).decode('utf-8')
                try:
                    data = json.loads(body)
                except Exception:
                    data = {'query': body}
                query = data.get('query', '')
                res = agent.ask(query)

                resp_bytes = json.dumps(res).encode('utf-8')
                self.send_response(200)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.send_header('Content-Length', str(len(resp_bytes)))
                self.end_headers()
                self.wfile.write(resp_bytes)
                return

            super().do_POST()

    with socketserver.TCPServer(("", port), Handler) as httpd:
        url = f"http://localhost:{port}"
        print(f"\n=======================================================")
        print(f"CATALIST DASHBOARD LIVE: {url}")
        print(f"Serving from '{directory}/' ... Press Ctrl+C to stop.")
        print(f"=======================================================\n")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServer stopped.")


def main():
    parser = argparse.ArgumentParser(description="Catalist Media Meeting Memory CLI")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Ingest
    p_ingest = subparsers.add_parser("ingest", help="Deterministic ingestion of transcripts")
    p_ingest.add_argument("--transcripts", default="transcripts", help="Path to transcripts")
    p_ingest.add_argument("--db", default="meeting_memory.db", help="Path to output database")

    # Ask
    p_ask = subparsers.add_parser("ask", help="Live single-question demo")
    p_ask.add_argument("--qid", help="Benchmark Question ID (e.g. Q01 to Q25)")
    p_ask.add_argument("--query", help="Custom freeform question")
    p_ask.add_argument("--questions", default="questions.json", help="Path to questions.json")
    p_ask.add_argument("--transcripts", default="transcripts", help="Path to transcripts")
    p_ask.add_argument("--db", default="meeting_memory.db", help="Path to database")

    # Brief
    p_brief = subparsers.add_parser("brief", help="Generate TS3012 executive brief")
    p_brief.add_argument("--team", default="TS3012", help="Team ID (default TS3012)")
    p_brief.add_argument("--output", help="Optional output text file path")
    p_brief.add_argument("--transcripts", default="transcripts", help="Path to transcripts")
    p_brief.add_argument("--db", default="meeting_memory.db", help="Path to database")

    # Run
    p_run = subparsers.add_parser("run", help="Run full benchmark and produce answers.json")
    p_run.add_argument("--all", action="store_true", help="Run all 25 benchmark questions")
    p_run.add_argument("--output", default="answers.json", help="Path to output answers.json")
    p_run.add_argument("--verify", action="store_true", help="Run verification audit immediately")
    p_run.add_argument("--questions", default="questions.json", help="Path to questions.json")
    p_run.add_argument("--transcripts", default="transcripts", help="Path to transcripts")
    p_run.add_argument("--db", default="meeting_memory.db", help="Path to database")

    # Audit
    p_audit = subparsers.add_parser("audit", help="Run verification audit on answers.json")
    p_audit.add_argument("--answers", default="answers.json", help="Path to answers.json")
    p_audit.add_argument("--questions", default="questions.json", help="Path to questions.json")
    p_audit.add_argument("--transcripts", default="transcripts", help="Path to transcripts")

    # Serve
    p_serve = subparsers.add_parser("serve", help="Launch interactive UI frontend dashboard")
    p_serve.add_argument("--port", type=int, default=8000, help="Port to serve on (default: 8000)")
    p_serve.add_argument("--dir", default="frontend", help="Directory to serve (default: frontend)")

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(0)

    if args.command == "ingest":
        cmd_ingest(args)
    elif args.command == "ask":
        cmd_ask(args)
    elif args.command == "brief":
        cmd_brief(args)
    elif args.command == "run":
        cmd_run(args)
    elif args.command == "audit":
        cmd_audit(args)
    elif args.command == "serve":
        cmd_serve(args)


if __name__ == "__main__":
    main()
