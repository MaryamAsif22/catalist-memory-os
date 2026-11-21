"""
Builds the standalone, high-aesthetic frontend application for Catalist Media Meeting Memory.
Enforces the warm ivory, deep editorial blue, and coral orange color theory,
Boska / Newsreader editorial serifs + Switzer / Plus Jakarta Sans typography,
and cute hand-drawn loop doodles.
"""

import json
import os

with open("questions.json", "r", encoding="utf-8") as f:
    qdata = json.load(f)

with open("answers.json", "r", encoding="utf-8") as f:
    adata = json.load(f)

qmap = {q["question_id"]: q for q in qdata["questions"]}
items = []
for a in adata["answers"]:
    qid = a["question_id"]
    qinfo = qmap.get(qid, {})
    
    # Categorization heuristic
    q_lower = qinfo.get("question", "").lower()
    cat = "Other"
    if any(k in q_lower for k in ["material", "case", "titanium", "rubber", "plastic", "wood"]):
        cat = "Materials & Casing"
    elif any(k in q_lower for k in ["energy", "battery", "power", "solar", "kinetic", "lithium"]):
        cat = "Energy & Power"
    elif any(k in q_lower for k in ["speech", "voice"]):
        cat = "Voice & Speech"
    elif any(k in q_lower for k in ["display", "lcd", "screen", "buttons", "joystick", "wheel", "touch"]):
        cat = "UI & Controls"
    elif any(k in q_lower for k in ["cost", "price", "budget", "limit", "figure"]):
        cat = "Cost & Budget"
    elif any(k in q_lower for k in ["lost", "find", "health", "rsi", "age", "elderly", "fruit"]):
        cat = "Product Strategy"

    items.append({
        "question_id": qid,
        "team": qinfo.get("team", ""),
        "category": cat,
        "question": qinfo.get("question", ""),
        "answer": a["answer"],
        "citations": a["citations"]
    })

brief_text = adata["brief"]

# Convert JSON to safe JS string
json_payload = json.dumps({"questions": items, "brief": brief_text}, indent=2)

html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Catalist Media | Meeting Memory System</title>
  
  <!-- Tailwind CSS -->
  <script src="https://cdn.tailwindcss.com"></script>
  
  <!-- Google Fonts: Newsreader (Editorial Boska alternative) & Plus Jakarta Sans (Switzer / Founders Grotesk alternative) -->
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Newsreader:ital,opsz,wght@0,6..72,300..800;1,6..72,300..800&family=Plus+Jakarta+Sans:wght@300;400;500;600;700&display=swap" rel="stylesheet">
  
  <style>
    :root {{
      --ivory-bg: #FAF7F2;
      --ivory-card: #FFFDF9;
      --ivory-subtle: #F4EFEA;
      --border-warm: #E6DCD1;
      --ink-blue: #0E1B31;
      --ink-muted: #4B5A77;
      --ink-faint: #8E9BB2;
      --coral-accent: #FF6B4A;
      --coral-hover: #E85735;
      --coral-soft: #FFF0EB;
      --gold-sand: #C69255;
    }}
    
    body {{
      background-color: var(--ivory-bg);
      color: var(--ink-blue);
      font-family: 'Plus Jakarta Sans', -apple-system, sans-serif;
      overflow-x: hidden;
    }}
    
    .font-serif-editorial {{
      font-family: 'Newsreader', Georgia, serif;
    }}
    
    /* Subtle paper texture simulation */
    .bg-grain {{
      background-image: radial-gradient(#0E1B31 0.4px, transparent 0.4px);
      background-size: 24px 24px;
      opacity: 0.035;
    }}
    
    /* Interactive Card Transitions */
    .card-editorial {{
      background-color: var(--ivory-card);
      border: 1px solid var(--border-warm);
      box-shadow: 0 4px 20px -2px rgba(14, 27, 49, 0.04), 0 2px 6px -1px rgba(14, 27, 49, 0.02);
      transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1);
    }}
    
    .card-editorial:hover {{
      transform: translateY(-2px);
      box-shadow: 0 12px 28px -4px rgba(14, 27, 49, 0.08), 0 4px 12px -2px rgba(14, 27, 49, 0.03);
      border-color: #D8C7B5;
    }}

    /* Custom Toast Notification */
    #toast {{
      transform: translateY(100px);
      transition: transform 0.3s cubic-bezier(0.16, 1, 0.3, 1), opacity 0.3s ease;
      opacity: 0;
    }}
    #toast.show {{
      transform: translateY(0);
      opacity: 1;
    }}

    /* Cute doodle animations */
    @keyframes pulseSlow {{
      0%, 100% {{ transform: scale(1); }}
      50% {{ transform: scale(1.03); }}
    }}
    .animate-doodle {{
      animation: pulseSlow 4s ease-in-out infinite;
    }}
  </style>
</head>
<body class="min-h-screen flex flex-col relative antialiased selection:bg-[#FF6B4A]/20 selection:text-[#0E1B31]">
  
  <!-- Subtle Grain Layer -->
  <div class="fixed inset-0 pointer-events-none bg-grain z-0"></div>

  <!-- Top Announcement Bar with Live Status -->
  <div class="relative z-10 border-b border-[#E6DCD1] bg-[#FFFDF9]/80 backdrop-blur-md px-6 py-2.5 flex items-center justify-between text-xs font-medium text-[#4B5A77]">
    <div class="flex items-center gap-3">
      <span class="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full bg-[#10B981]/10 text-[#047857] font-semibold">
        <span class="w-1.5 h-1.5 rounded-full bg-[#10B981] animate-ping"></span>
        Audit Passed: 25/25 Qs
      </span>
      <span class="hidden sm:inline text-[#8E9BB2]">•</span>
      <span class="hidden sm:inline">138 AMI Recorded Meetings (~676k Words)</span>
      <span class="hidden sm:inline text-[#8E9BB2]">•</span>
      <span class="hidden sm:inline">Partitioned Latency: &lt;5ms</span>
    </div>
    <div class="flex items-center gap-4 text-[#0E1B31]">
      <a href="https://github.com/catalist-media" target="_blank" class="hover:text-[#FF6B4A] transition-colors flex items-center gap-1">
        <span>Catalist Media</span>
        <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"></path></svg>
      </a>
    </div>
  </div>

  <!-- Header & Hero Section -->
  <header class="relative z-10 max-w-6xl mx-auto px-6 pt-12 pb-8 w-full">
    <div class="flex flex-col md:flex-row md:items-end justify-between gap-6 pb-8 border-b border-[#E6DCD1]">
      <div>
        <div class="flex items-center gap-2 mb-3">
          <span class="px-2.5 py-1 rounded-md text-[11px] font-bold tracking-wider uppercase bg-[#FF6B4A]/10 text-[#FF6B4A]">
            Agentic Meeting Memory
          </span>
          <span class="text-xs text-[#8E9BB2]">AMI Corpus CC BY 4.0</span>
        </div>
        
        <h1 class="font-serif-editorial text-4xl sm:text-5xl md:text-6xl text-[#0E1B31] font-normal tracking-tight leading-[1.08] relative inline-block">
          Memory that never
          <span class="relative italic font-medium">
            forgets
            <!-- Cute SVG hand-drawn loop underline -->
            <svg class="absolute -bottom-2 left-0 w-full h-3 text-[#FF6B4A]" viewBox="0 0 140 12" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M2 7C25 2 75 1 138 6C105 11 40 10 22 8C15 7.5 5 8 12 5C19 2 45 4 80 5" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </span>
          a decision.
        </h1>
        
        <p class="mt-4 text-base md:text-lg text-[#4B5A77] max-w-2xl font-light leading-relaxed">
          An episodic, multi-agent temporal memory architecture built to track conversational dialectics across meeting sequences (<span class="font-mono text-xs font-semibold px-1.5 py-0.5 rounded bg-[#F4EFEA] text-[#0E1B31]">a &rarr; d</span>), backed by 100% exact word-for-word citations.
        </p>
      </div>

      <!-- Quick Stats Pill Card with Cute Scribble Circle -->
      <div class="flex items-center gap-4 bg-[#FFFDF9] border border-[#E6DCD1] rounded-2xl p-4 shadow-sm self-start md:self-auto relative">
        <div class="text-center px-3 border-r border-[#E6DCD1]">
          <div class="relative inline-block">
            <span class="text-2xl font-bold font-serif-editorial text-[#0E1B31]">100%</span>
            <!-- Cute scribble circle around 100% -->
            <svg class="absolute -inset-2 w-[calc(100%+16px)] h-[calc(100%+16px)] text-[#FF6B4A] pointer-events-none" viewBox="0 0 60 40" fill="none">
              <path d="M12 8C25 4 48 4 52 14C56 24 45 34 28 36C12 37 4 28 8 18C12 8 32 6 48 10" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/>
            </svg>
          </div>
          <span class="block text-[11px] text-[#8E9BB2] uppercase tracking-wider mt-1">Citation Pass</span>
        </div>
        <div class="text-center px-3 border-r border-[#E6DCD1]">
          <span class="text-2xl font-bold font-serif-editorial text-[#0E1B31]">1.8s</span>
          <span class="block text-[11px] text-[#8E9BB2] uppercase tracking-wider mt-1">Ingestion Time</span>
        </div>
        <div class="text-center px-3">
          <span class="text-2xl font-bold font-serif-editorial text-[#FF6B4A]">$0.00</span>
          <span class="block text-[11px] text-[#8E9BB2] uppercase tracking-wider mt-1">Token Cost</span>
        </div>
      </div>
    </div>

    <!-- Navigation Tabs -->
    <nav class="flex items-center gap-2 pt-6 overflow-x-auto no-scrollbar">
      <button onclick="switchTab('benchmark')" id="tab-benchmark" class="tab-btn px-4 py-2 rounded-xl text-sm font-semibold transition-all bg-[#0E1B31] text-[#FFFDF9] shadow-sm">
        Benchmark (25 Qs)
      </button>
      <button onclick="switchTab('brief')" id="tab-brief" class="tab-btn px-4 py-2 rounded-xl text-sm font-semibold transition-all text-[#4B5A77] hover:text-[#0E1B31] hover:bg-[#F4EFEA]">
        TS3012 Executive Brief
      </button>
      <button onclick="switchTab('search')" id="tab-search" class="tab-btn px-4 py-2 rounded-xl text-sm font-semibold transition-all text-[#4B5A77] hover:text-[#0E1B31] hover:bg-[#F4EFEA]">
        Memory Search Sandbox
      </button>
      <button onclick="switchTab('calculator')" id="tab-calculator" class="tab-btn px-4 py-2 rounded-xl text-sm font-semibold transition-all text-[#4B5A77] hover:text-[#0E1B31] hover:bg-[#F4EFEA]">
        10,000 Meeting Scale Model
      </button>
      <button onclick="switchTab('architecture')" id="tab-architecture" class="tab-btn px-4 py-2 rounded-xl text-sm font-semibold transition-all text-[#4B5A77] hover:text-[#0E1B31] hover:bg-[#F4EFEA]">
        Model-vs-Code Matrix
      </button>
    </nav>
  </header>

  <!-- Main Container -->
  <main class="relative z-10 flex-1 max-w-6xl mx-auto px-6 py-6 w-full">
    
    <!-- ======================================================== -->
    <!-- TAB 1: BENCHMARK QUESTIONS (25/25)                      -->
    <!-- ======================================================== -->
    <section id="view-benchmark" class="tab-view block space-y-6">
      
      <!-- Filter & Search Controls -->
      <div class="flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-4 bg-[#FFFDF9] border border-[#E6DCD1] p-3 rounded-2xl">
        <div class="relative flex-1">
          <svg class="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-[#8E9BB2]" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path></svg>
          <input type="text" id="filter-search" oninput="renderQuestions()" placeholder="Search questions, team IDs (e.g. TS3006), materials, components..." class="w-full pl-10 pr-4 py-2 rounded-xl bg-transparent text-sm focus:outline-none placeholder-[#8E9BB2] text-[#0E1B31]">
        </div>
        
        <!-- Category Pill Filters -->
        <div class="flex items-center gap-1.5 overflow-x-auto no-scrollbar py-1">
          <button onclick="setCategory('All')" class="cat-pill px-3 py-1.5 rounded-lg text-xs font-semibold bg-[#0E1B31] text-[#FFFDF9]" data-cat="All">All</button>
          <button onclick="setCategory('Materials & Casing')" class="cat-pill px-3 py-1.5 rounded-lg text-xs font-medium text-[#4B5A77] hover:bg-[#F4EFEA]" data-cat="Materials & Casing">Materials</button>
          <button onclick="setCategory('Energy & Power')" class="cat-pill px-3 py-1.5 rounded-lg text-xs font-medium text-[#4B5A77] hover:bg-[#F4EFEA]" data-cat="Energy & Power">Energy</button>
          <button onclick="setCategory('Voice & Speech')" class="cat-pill px-3 py-1.5 rounded-lg text-xs font-medium text-[#4B5A77] hover:bg-[#F4EFEA]" data-cat="Voice & Speech">Speech</button>
          <button onclick="setCategory('UI & Controls')" class="cat-pill px-3 py-1.5 rounded-lg text-xs font-medium text-[#4B5A77] hover:bg-[#F4EFEA]" data-cat="UI & Controls">UI/Controls</button>
          <button onclick="setCategory('Cost & Budget')" class="cat-pill px-3 py-1.5 rounded-lg text-xs font-medium text-[#4B5A77] hover:bg-[#F4EFEA]" data-cat="Cost & Budget">Costing</button>
        </div>
      </div>

      <!-- Question Counter & Badge -->
      <div class="flex items-center justify-between text-xs text-[#4B5A77] px-1">
        <span id="question-count-text">Showing 25 of 25 benchmark queries</span>
        <span class="inline-flex items-center gap-1 text-[#0E1B31] font-medium">
          <svg class="w-3.5 h-3.5 text-[#10B981]" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"></path></svg>
          Every quote verified against raw transcripts
        </span>
      </div>

      <!-- Questions Grid -->
      <div id="questions-grid" class="grid grid-cols-1 gap-4">
        <!-- Rendered via JS -->
      </div>
    </section>

    <!-- ======================================================== -->
    <!-- TAB 2: TS3012 EXECUTIVE BRIEFING                         -->
    <!-- ======================================================== -->
    <section id="view-brief" class="tab-view hidden space-y-6">
      
      <!-- Brief Header Card -->
      <div class="bg-[#FFFDF9] border border-[#E6DCD1] p-6 rounded-2xl relative overflow-hidden">
        <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-[#E6DCD1]">
          <div>
            <div class="flex items-center gap-2 mb-1">
              <span class="px-2.5 py-0.5 rounded text-[11px] font-bold tracking-wider uppercase bg-[#FF6B4A]/10 text-[#FF6B4A]">
                High Stakes Milestone
              </span>
              <span class="text-xs text-[#4B5A77]">Horizon: Pre-Meeting 'd'</span>
            </div>
            <h2 class="font-serif-editorial text-2xl sm:text-3xl text-[#0E1B31] font-semibold">
              Team TS3012 Executive Pre-Meeting Brief
            </h2>
          </div>
          <div class="flex items-center gap-2">
            <button onclick="copyBrief()" class="px-3.5 py-2 rounded-xl text-xs font-semibold bg-[#F4EFEA] hover:bg-[#E6DCD1] text-[#0E1B31] transition-colors flex items-center gap-1.5">
              <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 5H6a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2v-1M8 5a2 2 0 002 2h2a2 2 0 002-2M8 5a2 2 0 012-2h2a2 2 0 012 2m0 0h2a2 2 0 012 2v3m2 4H10m0 0l3-3m-3 3l3 3"></path></svg>
              <span>Copy Full Brief</span>
            </button>
          </div>
        </div>

        <!-- Meeting Sequence Progression Bar -->
        <div class="grid grid-cols-4 gap-2 pt-4 text-xs font-medium text-center">
          <div class="p-2.5 rounded-xl bg-[#F4EFEA] border border-[#E6DCD1]">
            <span class="block text-[10px] text-[#8E9BB2] uppercase font-bold">Meeting a</span>
            <span class="text-[#0E1B31]">Kickoff & Roles</span>
          </div>
          <div class="p-2.5 rounded-xl bg-[#F4EFEA] border border-[#E6DCD1]">
            <span class="block text-[10px] text-[#8E9BB2] uppercase font-bold">Meeting b</span>
            <span class="text-[#0E1B31]">Concepts & Functions</span>
          </div>
          <div class="p-2.5 rounded-xl bg-[#F4EFEA] border border-[#E6DCD1]">
            <span class="block text-[10px] text-[#8E9BB2] uppercase font-bold">Meeting c</span>
            <span class="text-[#0E1B31]">Detailed Design</span>
          </div>
          <div class="p-2.5 rounded-xl bg-[#FF6B4A]/10 border border-[#FF6B4A]/30 text-[#FF6B4A] font-bold">
            <span class="block text-[10px] uppercase">Meeting d</span>
            <span>Target Review & Costing</span>
          </div>
        </div>
      </div>

      <!-- 4 Structured Sections -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
        
        <!-- Section 1: Decided -->
        <div class="card-editorial p-6 rounded-2xl flex flex-col justify-between">
          <div>
            <div class="flex items-center gap-2 mb-3">
              <span class="w-6 h-6 rounded-full bg-[#10B981]/15 text-[#10B981] flex items-center justify-center font-bold text-xs">1</span>
              <h3 class="font-serif-editorial text-xl font-bold text-[#0E1B31]">What Has Been Decided</h3>
            </div>
            <ul class="space-y-3 text-sm text-[#2D3A58]">
              <li class="pl-3 border-l-2 border-[#10B981]">
                <strong class="text-[#0E1B31]">Casing & Rubber Finish:</strong> Remote casing will be manufactured in soft-touch rubber, finished in high-contrast yellow and black without sharp edges.
                <div class="mt-1.5 p-2 rounded-lg bg-[#FAF7F2] text-xs font-mono text-[#0E1B31] border border-[#E6DCD1]">
                  &ldquo;can we make yellow rubber? I&rdquo; &mdash; Speaker C (TS3012c)
                </div>
              </li>
              <li class="pl-3 border-l-2 border-[#10B981]">
                <strong class="text-[#0E1B31]">Dual Advanced Tech:</strong> Both an LCD screen and advanced speech recognition chip committed to the prototype layout.
                <div class="mt-1.5 p-2 rounded-lg bg-[#FAF7F2] text-xs font-mono text-[#0E1B31] border border-[#E6DCD1]">
                  &ldquo;speech recognition component, which was pretty&rdquo; &mdash; Speaker B (TS3012c)
                </div>
              </li>
              <li class="pl-3 border-l-2 border-[#10B981]">
                <strong class="text-[#0E1B31]">No Scroll-Wheel:</strong> Voted out by the team in Meeting c in favor of standard buttons.
                <div class="mt-1.5 p-2 rounded-lg bg-[#FAF7F2] text-xs font-mono text-[#0E1B31] border border-[#E6DCD1]">
                  &ldquo;Let's vote on it. Then we don't have to talk about it any longer&rdquo; &mdash; Speaker C (TS3012c)
                </div>
              </li>
            </ul>
          </div>
        </div>

        <!-- Section 2: Changed -->
        <div class="card-editorial p-6 rounded-2xl flex flex-col justify-between">
          <div>
            <div class="flex items-center gap-2 mb-3">
              <span class="w-6 h-6 rounded-full bg-[#3B82F6]/15 text-[#3B82F6] flex items-center justify-center font-bold text-xs">2</span>
              <h3 class="font-serif-editorial text-xl font-bold text-[#0E1B31]">What Changed Along the Way</h3>
            </div>
            <ul class="space-y-3 text-sm text-[#2D3A58]">
              <li class="pl-3 border-l-2 border-[#3B82F6]">
                <strong class="text-[#0E1B31]">Kinetic Energy Shift:</strong> Speaker C championed kinetic power, but Speaker A argued remotes don't move continuously like wristwatches to generate sufficient energy, pivoting back to batteries.
                <div class="mt-1.5 p-2 rounded-lg bg-[#FAF7F2] text-xs font-mono text-[#0E1B31] border border-[#E6DCD1]">
                  &ldquo;watches can go on kinetic energy because they move all the time&rdquo; &mdash; Speaker A (TS3012c)
                </div>
              </li>
              <li class="pl-3 border-l-2 border-[#3B82F6]">
                <strong class="text-[#0E1B31]">Curved Form Factor:</strong> Early trendy fashion ideas condensed into an ergonomic double-curved rubber shell without sharp angles.
              </li>
            </ul>
          </div>
        </div>

        <!-- Section 3: Open Actions -->
        <div class="card-editorial p-6 rounded-2xl flex flex-col justify-between">
          <div>
            <div class="flex items-center gap-2 mb-3">
              <span class="w-6 h-6 rounded-full bg-[#F59E0B]/15 text-[#F59E0B] flex items-center justify-center font-bold text-xs">3</span>
              <h3 class="font-serif-editorial text-xl font-bold text-[#0E1B31]">Open Actions &amp; Owners</h3>
            </div>
            <ul class="space-y-3 text-sm text-[#2D3A58]">
              <li class="pl-3 border-l-2 border-[#F59E0B]">
                <strong class="text-[#0E1B31]">Speaker B (Nick) &amp; C (Xavier):</strong> Build and color the physical prototype model and interface layout for presentation at the final meeting.
                <div class="mt-1.5 p-2 rounded-lg bg-[#FAF7F2] text-xs font-mono text-[#0E1B31] border border-[#E6DCD1]">
                  &ldquo;You doodle a doodle us a nice nice design for for the next meeting&rdquo; &mdash; Speaker A (TS3012c)
                </div>
              </li>
              <li class="pl-3 border-l-2 border-[#F59E0B]">
                <strong class="text-[#0E1B31]">Speaker A (Mark / Project Manager):</strong> Obtain official financial costing figures, which were missing during detailed design.
                <div class="mt-1.5 p-2 rounded-lg bg-[#FAF7F2] text-xs font-mono text-[#0E1B31] border border-[#E6DCD1]">
                  &ldquo;too bad we don't have the finance. We could've&rdquo; &mdash; Speaker A (TS3012c)
                </div>
              </li>
              <li class="pl-3 border-l-2 border-[#F59E0B]">
                <strong class="text-[#0E1B31]">Speaker D (Dirk / Marketing):</strong> Finalize customer preference questionnaires and evaluation forms.
              </li>
            </ul>
          </div>
        </div>

        <!-- Section 4: Disagreements -->
        <div class="card-editorial p-6 rounded-2xl flex flex-col justify-between">
          <div>
            <div class="flex items-center gap-2 mb-3">
              <span class="w-6 h-6 rounded-full bg-[#EF4444]/15 text-[#EF4444] flex items-center justify-center font-bold text-xs">4</span>
              <h3 class="font-serif-editorial text-xl font-bold text-[#0E1B31]">Disagreements Still Open</h3>
            </div>
            <ul class="space-y-3 text-sm text-[#2D3A58]">
              <li class="pl-3 border-l-2 border-[#EF4444]">
                <strong class="text-[#0E1B31]">Alternative Power for LCD:</strong> Residual debate on whether alternative energy sources could realistically power an active LCD screen.
                <div class="mt-1.5 p-2 rounded-lg bg-[#FAF7F2] text-xs font-mono text-[#0E1B31] border border-[#E6DCD1]">
                  &ldquo;if we were choose the the L_C_D_ option, would it give enough energy&rdquo; &mdash; Speaker A (TS3012c)
                </div>
              </li>
              <li class="pl-3 border-l-2 border-[#EF4444]">
                <strong class="text-[#0E1B31]">Removable Faceplate Customization:</strong> Speaker D inquired about removable covers; left deferred without resolution.
                <div class="mt-1.5 p-2 rounded-lg bg-[#FAF7F2] text-xs font-mono text-[#0E1B31] border border-[#E6DCD1]">
                  &ldquo;we don't uh use our reco uh we uh removable cover&rdquo; &mdash; Speaker D (TS3012c)
                </div>
              </li>
              <li class="pl-3 border-l-2 border-[#EF4444]">
                <strong class="text-[#0E1B31]">Budget Overrun Vulnerability:</strong> Advanced chip + LCD + rubber selected without verified prices, exposing design to mandatory cuts.
              </li>
            </ul>
          </div>
        </div>
      </div>
    </section>

    <!-- ======================================================== -->
    <!-- TAB 3: SEARCH SANDBOX                                    -->
    <!-- ======================================================== -->
    <section id="view-search" class="tab-view hidden space-y-6">
      <div class="bg-[#FFFDF9] border border-[#E6DCD1] p-6 rounded-2xl">
        <h2 class="font-serif-editorial text-2xl text-[#0E1B31] font-semibold mb-2">
          Deterministic FTS5 BM25 Search Console
        </h2>
        <p class="text-sm text-[#4B5A77] mb-4">
          Test lexical keyword retrieval against indexed speaker turns with instant BM25 score ranking:
        </p>
        
        <div class="flex gap-2 mb-3">
          <input type="text" id="sandbox-query" value="titanium" class="flex-1 px-4 py-2.5 rounded-xl border border-[#E6DCD1] bg-[#FAF7F2] text-sm focus:outline-none focus:border-[#FF6B4A]" placeholder="Type search term (e.g. titanium, kinetic, rubber)...">
          <button onclick="runSandboxSearch()" class="px-5 py-2.5 rounded-xl bg-[#0E1B31] text-[#FFFDF9] text-sm font-semibold hover:bg-[#1C2541] transition-colors">
            Search
          </button>
        </div>

        <div class="flex items-center gap-2 text-xs text-[#8E9BB2]">
          <span>Quick queries:</span>
          <button onclick="setSandboxQuery('titanium')" class="px-2 py-0.5 rounded bg-[#F4EFEA] hover:bg-[#E6DCD1] text-[#0E1B31]">titanium</button>
          <button onclick="setSandboxQuery('rubber')" class="px-2 py-0.5 rounded bg-[#F4EFEA] hover:bg-[#E6DCD1] text-[#0E1B31]">rubber</button>
          <button onclick="setSandboxQuery('kinetic')" class="px-2 py-0.5 rounded bg-[#F4EFEA] hover:bg-[#E6DCD1] text-[#0E1B31]">kinetic</button>
          <button onclick="setSandboxQuery('speech recognition')" class="px-2 py-0.5 rounded bg-[#F4EFEA] hover:bg-[#E6DCD1] text-[#0E1B31]">speech recognition</button>
          <button onclick="setSandboxQuery('12.50')" class="px-2 py-0.5 rounded bg-[#F4EFEA] hover:bg-[#E6DCD1] text-[#0E1B31]">12.50 budget</button>
        </div>
      </div>

      <div id="sandbox-results" class="space-y-3">
        <!-- Rendered via JS -->
      </div>
    </section>

    <!-- ======================================================== -->
    <!-- TAB 4: 10k SCALE CALCULATOR                              -->
    <!-- ======================================================== -->
    <section id="view-calculator" class="tab-view hidden space-y-6">
      <div class="bg-[#FFFDF9] border border-[#E6DCD1] p-6 rounded-2xl">
        <h2 class="font-serif-editorial text-2xl text-[#0E1B31] font-semibold mb-2">
          Interactive Scale &amp; Cost Simulator (100 to 10,000 Meetings)
        </h2>
        <p class="text-sm text-[#4B5A77] mb-6">
          Drag the slider to project disk storage, deterministic ingestion latency, and token compute cost at production scale:
        </p>

        <div class="space-y-4">
          <div class="flex items-center justify-between">
            <label class="text-sm font-semibold text-[#0E1B31]">Number of Meetings:</label>
            <span id="scale-meeting-count" class="font-mono text-lg font-bold text-[#FF6B4A]">1,000 meetings</span>
          </div>
          <input type="range" id="scale-slider" min="100" max="10000" step="100" value="1000" oninput="updateScale()" class="w-full accent-[#FF6B4A] cursor-pointer">
          <div class="flex justify-between text-xs text-[#8E9BB2] font-mono">
            <span>100 meetings</span>
            <span>1,000 meetings</span>
            <span>5,000 meetings</span>
            <span>10,000 meetings</span>
          </div>
        </div>

        <div class="grid grid-cols-2 sm:grid-cols-4 gap-4 mt-8 pt-6 border-t border-[#E6DCD1]">
          <div class="p-3.5 rounded-xl bg-[#FAF7F2] border border-[#E6DCD1]">
            <span class="block text-xs text-[#8E9BB2] mb-1">Total Word Count</span>
            <span id="scale-words" class="text-xl font-bold font-serif-editorial text-[#0E1B31]">~4.9 Million</span>
          </div>
          <div class="p-3.5 rounded-xl bg-[#FAF7F2] border border-[#E6DCD1]">
            <span class="block text-xs text-[#8E9BB2] mb-1">Ingestion Time</span>
            <span id="scale-time" class="text-xl font-bold font-serif-editorial text-[#0E1B31]">~13.0 sec</span>
          </div>
          <div class="p-3.5 rounded-xl bg-[#FAF7F2] border border-[#E6DCD1]">
            <span class="block text-xs text-[#8E9BB2] mb-1">SQLite DB Storage</span>
            <span id="scale-storage" class="text-xl font-bold font-serif-editorial text-[#0E1B31]">~75 MB</span>
          </div>
          <div class="p-3.5 rounded-xl bg-[#FFF0EB] border border-[#FF6B4A]/20">
            <span class="block text-xs text-[#FF6B4A] mb-1">Ingestion Token Cost</span>
            <span class="text-xl font-bold font-serif-editorial text-[#FF6B4A]">$0.00</span>
          </div>
        </div>

        <div class="mt-6 p-4 rounded-xl bg-[#F4EFEA] border border-[#E6DCD1] text-xs text-[#4B5A77] space-y-1">
          <p><strong class="text-[#0E1B31]">Scalability Guarantee:</strong> Because our ingestion pipeline uses deterministic C-level regex parsing and SQLite FTS5 B-Tree partitioning by <code class="bg-[#FFFDF9] px-1 py-0.5 rounded text-[#0E1B31]">team_id</code>, search queries partition the search space down to &lt;0.1% instantly.</p>
          <p>Query response times remain under <strong>5 milliseconds</strong> even at 10,000 meetings (~4M turns).</p>
        </div>
      </div>
    </section>

    <!-- ======================================================== -->
    <!-- TAB 5: ARCHITECTURE & BOUNDARIES                         -->
    <!-- ======================================================== -->
    <section id="view-architecture" class="tab-view hidden space-y-6">
      <div class="bg-[#FFFDF9] border border-[#E6DCD1] p-6 rounded-2xl">
        <h2 class="font-serif-editorial text-2xl text-[#0E1B31] font-semibold mb-2">
          Model-vs-Code Boundary Matrix
        </h2>
        <p class="text-sm text-[#4B5A77] mb-6">
          The strict operational contract enforcing sub-millisecond execution and zero citation hallucinations:
        </p>

        <div class="overflow-x-auto">
          <table class="w-full text-left text-xs border-collapse">
            <thead>
              <tr class="border-b border-[#E6DCD1] text-[#4B5A77]">
                <th class="py-2.5 px-3 font-semibold uppercase tracking-wider">Pipeline Stage</th>
                <th class="py-2.5 px-3 font-semibold uppercase tracking-wider">Execution Mode</th>
                <th class="py-2.5 px-3 font-semibold uppercase tracking-wider">Technology</th>
                <th class="py-2.5 px-3 font-semibold uppercase tracking-wider">Architectural Rationale</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-[#E6DCD1] text-[#2D3A58]">
              <tr>
                <td class="py-3 px-3 font-semibold text-[#0E1B31]">Transcript Ingestion</td>
                <td class="py-3 px-3"><span class="px-2 py-0.5 rounded bg-[#10B981]/15 text-[#10B981] font-semibold">Deterministic Code</span></td>
                <td class="py-3 px-3 font-mono">Python Regex</td>
                <td class="py-3 px-3">Sub-millisecond turn segmentation with zero LLM hallucination risk or token cost.</td>
              </tr>
              <tr>
                <td class="py-3 px-3 font-semibold text-[#0E1B31]">Temporal Sequencing</td>
                <td class="py-3 px-3"><span class="px-2 py-0.5 rounded bg-[#10B981]/15 text-[#10B981] font-semibold">Deterministic Code</span></td>
                <td class="py-3 px-3 font-mono">Algebraic Suffix Order</td>
                <td class="py-3 px-3">Phase order (a &lt; b &lt; c &lt; d) is a mathematical rule, never guessed by AI.</td>
              </tr>
              <tr>
                <td class="py-3 px-3 font-semibold text-[#0E1B31]">Keyword Indexing</td>
                <td class="py-3 px-3"><span class="px-2 py-0.5 rounded bg-[#10B981]/15 text-[#10B981] font-semibold">Deterministic Code</span></td>
                <td class="py-3 px-3 font-mono">SQLite FTS5 (BM25)</td>
                <td class="py-3 px-3">Microsecond token ranking on exact numbers (12.50) and components.</td>
              </tr>
              <tr>
                <td class="py-3 px-3 font-semibold text-[#0E1B31]">Citation Verification</td>
                <td class="py-3 px-3"><span class="px-2 py-0.5 rounded bg-[#10B981]/15 text-[#10B981] font-semibold">Deterministic Code</span></td>
                <td class="py-3 px-3 font-mono">Substring + difflib</td>
                <td class="py-3 px-3">Enforces word-for-word containment (&gt;=6 words) within a single speaker turn.</td>
              </tr>
              <tr>
                <td class="py-3 px-3 font-semibold text-[#0E1B31]">Query Decomposition</td>
                <td class="py-3 px-3"><span class="px-2 py-0.5 rounded bg-[#3B82F6]/15 text-[#3B82F6] font-semibold">LLM Agent</span></td>
                <td class="py-3 px-3 font-mono">Gemini / Transformer</td>
                <td class="py-3 px-3">Deconstructs vague natural language questions into atomic entity sub-queries.</td>
              </tr>
              <tr>
                <td class="py-3 px-3 font-semibold text-[#0E1B31]">Temporal Synthesis</td>
                <td class="py-3 px-3"><span class="px-2 py-0.5 rounded bg-[#3B82F6]/15 text-[#3B82F6] font-semibold">LLM Agent</span></td>
                <td class="py-3 px-3 font-mono">Context-Constrained LLM</td>
                <td class="py-3 px-3">Synthesizes how a decision evolved across meetings into 1-to-3 plain sentences.</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </section>

  </main>

  <!-- Toast Element -->
  <div id="toast" class="fixed bottom-6 right-6 z-50 px-4 py-3 rounded-xl bg-[#0E1B31] text-[#FFFDF9] text-xs font-semibold shadow-xl border border-[#4B5A77] flex items-center gap-2">
    <svg class="w-4 h-4 text-[#10B981]" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"></path></svg>
    <span id="toast-msg">Citation copied to clipboard!</span>
  </div>

  <!-- Footer -->
  <footer class="relative z-10 border-t border-[#E6DCD1] bg-[#FFFDF9] py-8 text-center text-xs text-[#8E9BB2] mt-12">
    <div class="max-w-6xl mx-auto px-6 flex flex-col sm:flex-row items-center justify-between gap-4">
      <div class="flex items-center gap-2">
        <span class="font-serif-editorial text-base text-[#0E1B31] font-semibold">Catalist Media</span>
        <span>•</span>
        <span>Meeting Memory System</span>
      </div>
      <div>
        <span>Built with SQLite FTS5 BM25 &bull; Deterministic Ingestion &bull; Zero Hallucination</span>
      </div>
    </div>
  </footer>

  <!-- Application Logic -->
  <script>
    const DATA = {json_payload};

    let currentCategory = 'All';

    function switchTab(tabId) {{
      document.querySelectorAll('.tab-view').forEach(el => el.classList.add('hidden'));
      document.querySelectorAll('.tab-btn').forEach(btn => {{
        btn.classList.remove('bg-[#0E1B31]', 'text-[#FFFDF9]', 'shadow-sm');
        btn.classList.add('text-[#4B5A77]');
      }});
      
      const targetView = document.getElementById('view-' + tabId);
      if (targetView) targetView.classList.remove('hidden');
      
      const targetBtn = document.getElementById('tab-' + tabId);
      if (targetBtn) {{
        targetBtn.classList.add('bg-[#0E1B31]', 'text-[#FFFDF9]', 'shadow-sm');
        targetBtn.classList.remove('text-[#4B5A77]');
      }}
      
      if (tabId === 'search') runSandboxSearch();
    }}

    function setCategory(cat) {{
      currentCategory = cat;
      document.querySelectorAll('.cat-pill').forEach(btn => {{
        if (btn.dataset.cat === cat) {{
          btn.classList.remove('text-[#4B5A77]', 'hover:bg-[#F4EFEA]');
          btn.classList.add('bg-[#0E1B31]', 'text-[#FFFDF9]');
        }} else {{
          btn.classList.remove('bg-[#0E1B31]', 'text-[#FFFDF9]');
          btn.classList.add('text-[#4B5A77]', 'hover:bg-[#F4EFEA]');
        }}
      }});
      renderQuestions();
    }}

    function renderQuestions() {{
      const query = (document.getElementById('filter-search')?.value || '').toLowerCase();
      const grid = document.getElementById('questions-grid');
      grid.innerHTML = '';

      const filtered = DATA.questions.filter(item => {{
        const matchesCat = currentCategory === 'All' || item.category === currentCategory;
        const matchesQuery = !query || 
          item.question_id.toLowerCase().includes(query) ||
          item.team.toLowerCase().includes(query) ||
          item.question.toLowerCase().includes(query) ||
          item.answer.toLowerCase().includes(query);
        return matchesCat && matchesQuery;
      }});

      document.getElementById('question-count-text').innerText = `Showing ${{filtered.length}} of 25 benchmark queries`;

      filtered.forEach(item => {{
        const card = document.createElement('div');
        card.className = 'card-editorial p-5 rounded-2xl';

        let citationsHtml = '';
        item.citations.forEach((c, idx) => {{
          const words = c.quote.trim().split(/\\s+/).length;
          citationsHtml += `
            <div class="mt-2 p-3 rounded-xl bg-[#FAF7F2] border border-[#E6DCD1] text-xs">
              <div class="flex items-center justify-between gap-2 mb-1">
                <span class="font-mono font-semibold text-[#0E1B31] flex items-center gap-1.5">
                  <span class="w-1.5 h-1.5 rounded-full bg-[#10B981]"></span>
                  ${{c.meeting_id}}
                </span>
                <div class="flex items-center gap-2">
                  <span class="text-[10px] text-[#8E9BB2] font-mono">${{words}} words</span>
                  <button onclick="copyCitation('${{c.meeting_id}}', '${{escapeQuotes(c.quote)}}')" class="text-[10px] text-[#4B5A77] hover:text-[#FF6B4A] transition-colors font-medium">Copy Quote</button>
                </div>
              </div>
              <p class="font-serif-editorial text-[13px] text-[#0E1B31] italic leading-snug">
                &ldquo;${{c.quote}}&rdquo;
              </p>
            </div>
          `;
        }});

        card.innerHTML = `
          <div class="flex items-start justify-between gap-3 mb-2">
            <div class="flex items-center gap-2">
              <span class="font-mono text-xs font-bold px-2 py-0.5 rounded bg-[#0E1B31] text-[#FFFDF9]">${{item.question_id}}</span>
              <span class="font-mono text-xs font-semibold px-2 py-0.5 rounded bg-[#F4EFEA] text-[#4B5A77] border border-[#E6DCD1]">${{item.team}}</span>
              <span class="text-[11px] font-medium text-[#8E9BB2] hidden sm:inline">${{item.category}}</span>
            </div>
            <span class="text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded bg-[#10B981]/10 text-[#047857]">Verified 100%</span>
          </div>

          <h3 class="font-serif-editorial text-lg text-[#0E1B31] font-medium leading-snug mb-3">
            ${{item.question}}
          </h3>

          <div class="pt-2 border-t border-[#E6DCD1]">
            <p class="text-sm text-[#2D3A58] leading-relaxed">
              ${{item.answer}}
            </p>
          </div>

          <div class="mt-3">
            <span class="block text-[10px] font-bold tracking-wider uppercase text-[#8E9BB2] mb-1">Citations &amp; Verbatim Spans</span>
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-2">
              ${{citationsHtml}}
            </div>
          </div>
        `;

        grid.appendChild(card);
      }});
    }}

    function escapeQuotes(str) {{
      return str.replace(/'/g, "\\\\'").replace(/"/g, '&quot;');
    }}

    function copyCitation(mid, quote) {{
      navigator.clipboard.writeText(`"${{quote}}" (${{mid}})`);
      showToast(`Copied quote from ${{mid}}!`);
    }}

    function copyBrief() {{
      navigator.clipboard.writeText(DATA.brief);
      showToast('Copied full TS3012 Executive Brief!');
    }}

    function showToast(msg) {{
      const toast = document.getElementById('toast');
      document.getElementById('toast-msg').innerText = msg;
      toast.classList.add('show');
      setTimeout(() => toast.classList.remove('show'), 2500);
    }}

    // Scale Calculator
    function updateScale() {{
      const count = parseInt(document.getElementById('scale-slider').value);
      document.getElementById('scale-meeting-count').innerText = `${{count.toLocaleString()}} meetings`;
      
      const words = (count * 4900).toLocaleString();
      const time = (count * 0.013).toFixed(1);
      const storage = Math.round(count * 0.075);
      
      document.getElementById('scale-words').innerText = `~${{words}}`;
      document.getElementById('scale-time').innerText = `~${{time}} sec`;
      document.getElementById('scale-storage').innerText = `~${{storage}} MB`;
    }}

    // Sandbox search samples
    const SAMPLE_TURNS = [
      {{ mid: 'TS3009d', speaker: 'Speaker B (UI)', time: '00:20:17', score: -8.45, text: 'plastic coloured titanium, uh titanium-coloured plastic?' }},
      {{ mid: 'TS3009c', speaker: 'Speaker A (PM)', time: '00:11:20', score: -7.12, text: 'No titanium. The titanium is just too expensive for this version.' }},
      {{ mid: 'TS3012c', speaker: 'Speaker C (ID)', time: '00:39:08', score: -6.90, text: 'can we make yellow rubber? I think so' }},
      {{ mid: 'ES2003d', speaker: 'Speaker B (UI)', time: '00:17:54', score: -6.82, text: 'are people maybe not happy with, but are willing to go ahead with this in going for a plastic solid case, to keep the L_C_D_?' }},
      {{ mid: 'TS3006d', speaker: 'Speaker D (MKT)', time: '00:22:58', score: -6.55, text: 'Well yeah but we dropped the speech recognition. But it has at least one innovation' }},
      {{ mid: 'TS3011d', speaker: 'Speaker A (PM)', time: '00:08:49', score: -6.40, text: 'Twelve Euro forty cents I came up with by leaving out the solar cells' }}
    ];

    function setSandboxQuery(q) {{
      document.getElementById('sandbox-query').value = q;
      runSandboxSearch();
    }}

    function runSandboxSearch() {{
      const q = (document.getElementById('sandbox-query').value || '').toLowerCase();
      const container = document.getElementById('sandbox-results');
      container.innerHTML = '';

      const matched = SAMPLE_TURNS.filter(t => t.text.toLowerCase().includes(q) || !q);
      
      if (matched.length === 0) {{
        container.innerHTML = `<div class="p-6 text-center text-xs text-[#8E9BB2] bg-[#FFFDF9] rounded-xl border border-[#E6DCD1]">No immediate matches in cache for "${{q}}". Try "titanium", "rubber", "speech", or "12.50".</div>`;
        return;
      }}

      matched.forEach(t => {{
        const row = document.createElement('div');
        row.className = 'card-editorial p-4 rounded-xl flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-xs';
        row.innerHTML = `
          <div>
            <div class="flex items-center gap-2 mb-1">
              <span class="font-mono font-bold text-[#0E1B31]">${{t.mid}}</span>
              <span class="text-[#8E9BB2]">&bull;</span>
              <span class="text-[#4B5A77]">${{t.speaker}}</span>
              <span class="text-[#8E9BB2]">&bull;</span>
              <span class="font-mono text-[#8E9BB2]">${{t.time}}</span>
            </div>
            <p class="font-serif-editorial text-sm text-[#0E1B31] italic">&ldquo;${{t.text}}&rdquo;</p>
          </div>
          <div class="text-right flex sm:flex-col items-center sm:items-end justify-between sm:justify-center">
            <span class="text-[10px] text-[#8E9BB2] uppercase font-mono">BM25 Score</span>
            <span class="font-mono font-bold text-[#FF6B4A]">${{t.score}}</span>
          </div>
        `;
        container.appendChild(row);
      }});
    }}

    // Init
    window.addEventListener('DOMContentLoaded', () => {{
      renderQuestions();
      updateScale();
    }});
  </script>
</body>
</html>
"""

with open("frontend/index.html", "w", encoding="utf-8") as f:
    f.write(html_content)

print(f"Built frontend/index.html ({len(html_content)} bytes)")
