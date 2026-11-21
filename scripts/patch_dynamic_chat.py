import re

with open('scripts/build_sleek_frontend.py', 'r', encoding='utf-8') as f:
    code = f.read()

# 1. Remove appending of additional_10_questions.json
old_add_block = """# Integrate the 10 newly mined multi-meeting dialectic questions
if os.path.exists("additional_10_questions.json"):
    with open("additional_10_questions.json", "r", encoding="utf-8") as f_add:
        add_data = json.load(f_add)
        add_qs = add_data.get("questions", [])
        existing_ids = {i["question_id"] for i in items}
        for q in add_qs:
            if q["question_id"] not in existing_ids:
                items.append(q)"""

if old_add_block in code:
    code = code.replace(old_add_block, "# Loaded official 25 benchmark questions")
    print("Removed 10 hardcoded questions from frontend benchmark list.")

# 2. Reset labels to 25
code = code.replace("Explore 35 Dialectic Answers", "Explore 25 Benchmark Answers")
code = code.replace("+35 Qs", "+25 Qs")
code = code.replace("35/35 Validated &bull; 100% Invariant Compliant", "25/25 Validated &bull; 100% Compliant")

# 3. Update generateAgentResponse to call /api/ask first
old_gen_func = """    // 2. High-Performance Benchmarking Assistant with Progressive Word Streaming
    function generateAgentResponse(query) {
      const q = query.toLowerCase().trim();"""

new_gen_func = """    // 2. Live Dynamic Agent & Benchmark Assistant with Progressive Word Streaming
    async function generateAgentResponse(query) {
      const q = query.toLowerCase().trim();

      // Step 1: Call Live Agent Backend API across all 138 transcripts (48,148 turns)
      try {
        const apiResp = await fetch('/api/ask', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ query: query })
        });
        if (apiResp.ok) {
          const apiData = await apiResp.json();
          if (apiData && apiData.answer) {
            streamAgentResponse(apiData, null);
            return;
          }
        }
      } catch (err) {
        console.warn('Backend API unavailable, using client-side fallback:', err);
      }"""

if old_gen_func in code:
    code = code.replace(old_gen_func, new_gen_func)
    print("Updated generateAgentResponse to call live /api/ask endpoint.")
else:
    print("WARNING: old_gen_func not matched exactly.")

with open('scripts/build_sleek_frontend.py', 'w', encoding='utf-8') as f:
    f.write(code)

print("Saved updated build_sleek_frontend.py!")
