import sqlite3, json, re

with open('scripts/build_sleek_frontend.py', 'r', encoding='utf-8') as f:
    code = f.read()

# 1. Update the data prep block
old_data_prep = """items_json = json.dumps(items)
brief_json = json.dumps(brief)"""

new_data_prep = """items_json = json.dumps(items)
brief_json = json.dumps(brief)

# Connect to meeting_memory.db to extract real indexed turns across all 138 meetings
import sqlite3
from collections import defaultdict

conn = sqlite3.connect('meeting_memory.db')
c = conn.cursor()

# Collect all cited quotes from benchmark and expansion
cited_by_mid = defaultdict(list)
for item in items:
    for cit in item.get('citations', []):
        cited_by_mid[cit['meeting_id']].append(cit['quote'])

c.execute('SELECT DISTINCT meeting_id FROM turns ORDER BY meeting_id')
all_mids = [r[0] for r in c.fetchall()]

db_turns_full = {}
for mid in all_mids:
    db_turns_full[mid] = []
    seen_indices = set()

    # 1. Add cited turns first if applicable
    if mid in cited_by_mid:
        for q in cited_by_mid[mid]:
            first_words = ' '.join(q.split()[:4])
            c.execute('SELECT turn_index, speaker, timestamp, text FROM turns WHERE meeting_id = ? AND text LIKE ? LIMIT 1', (mid, f'%{first_words}%'))
            row = c.fetchone()
            if row and row[0] not in seen_indices:
                seen_indices.add(row[0])
                clean_text = row[3].replace('"', '&quot;').strip()
                db_turns_full[mid].append({
                    'idx': row[0],
                    'spk': row[1],
                    'time': row[2],
                    'text': clean_text[:180],
                    'is_citation': True
                })

    # 2. Add other contextual substantive turns
    c.execute('SELECT turn_index, speaker, timestamp, text FROM turns WHERE meeting_id = ? AND word_count > 12 ORDER BY turn_index ASC LIMIT 6', (mid,))
    for row in c.fetchall():
        if row[0] not in seen_indices and len(db_turns_full[mid]) < 6:
            seen_indices.add(row[0])
            clean_text = row[3].replace('"', '&quot;').strip()
            db_turns_full[mid].append({
                'idx': row[0],
                'spk': row[1],
                'time': row[2],
                'text': clean_text[:180],
                'is_citation': False
            })

    db_turns_full[mid].sort(key=lambda x: x['idx'])

db_turns_json = json.dumps(db_turns_full)

# Build optgroups for all 138 meetings grouped by team
teams_map = defaultdict(list)
for mid in all_mids:
    team = mid[:-1]
    teams_map[team].append(mid)

optgroups = []
for team, mids in sorted(teams_map.items()):
    opts = ''.join([f'<option value="{m}" {"selected" if m=="TS3012c" else ""}>Meeting {m}</option>' for m in mids])
    optgroups.append(f'<optgroup label="Team {team}">{opts}</optgroup>')

db_options_html = '\\n'.join(optgroups)"""

if old_data_prep in code:
    code = code.replace(old_data_prep, new_data_prep, 1)
    print("Replaced data prep block.")
else:
    print("WARNING: old_data_prep not found.")

# 2. Replace static select options
old_select = """        <select id="db-select-meeting" onchange="loadDbTurns()" class="px-4 py-2 rounded-full border border-[#E8E2D8] bg-[#F8F6F0] text-xs font-mono font-bold text-[#0B132B]">
          <option value="TS3012c">Meeting TS3012c</option>
          <option value="TS3006d">Meeting TS3006d</option>
          <option value="TS3009d">Meeting TS3009d</option>
          <option value="ES2003d">Meeting ES2003d</option>
          <option value="TS3011d">Meeting TS3011d</option>
        </select>"""

new_select = """        <select id="db-select-meeting" onchange="loadDbTurns()" class="px-4 py-2 rounded-full border border-[#E8E2D8] bg-[#F8F6F0] text-xs font-mono font-bold text-[#0B132B] focus:outline-none focus:border-[#FF4D26]">
          {db_options_html}
        </select>"""

if old_select in code:
    code = code.replace(old_select, new_select, 1)
    print("Replaced select dropdown with dynamic optgroups.")
else:
    print("WARNING: old_select not found.")

# 3. Replace the static DB_TURNS object with {db_turns_json}
pattern = r"const DB_TURNS = \{\{.*?\}\};\s+function loadDbTurns\(\)"
sub_replacement = "const DB_TURNS = {db_turns_json};\n\n    function loadDbTurns()"
code, n_subs = re.subn(pattern, sub_replacement, code, flags=re.DOTALL)
print(f"Replaced DB_TURNS object: {n_subs} occurrence(s).")

with open('scripts/build_sleek_frontend.py', 'w', encoding='utf-8') as f:
    f.write(code)

print("Patch complete.")
