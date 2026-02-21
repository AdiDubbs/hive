"""Node definitions for Meeting Prep Agent."""

from framework.graph import NodeSpec

# Node 1: Intake (client-facing)
# Brief conversation to gather meeting details from the user.
intake_node = NodeSpec(
    id="intake",
    name="Meeting Intake",
    description="Gather meeting details: title, attendees, company, your role, and your goal",
    node_type="event_loop",
    client_facing=True,
    max_node_visits=0,
    input_keys=[],
    output_keys=["meeting_title", "attendees", "company", "user_role", "meeting_goal"],
    success_criteria=(
        "All required details have been collected: meeting title, at least one attendee "
        "with their name and company/role, the host company, the user's role, and the "
        "goal for the meeting."
    ),
    system_prompt="""\
You are a meeting intelligence assistant. Help the user prepare for an upcoming meeting.

**STEP 1 — Greet and ask (text only, NO tool calls):**
Ask the user for these details in a friendly, concise message:
1. **Meeting title / context** (e.g. "Sales demo with Acme Corp", "Partnership intro call")
2. **Attendees** — for each person: their name and their company/role
3. **Your company** (the host side)
4. **Your role** (so we can tailor talking points)
5. **Your goal for the meeting** (e.g. "close the deal", "explore a partnership", \
"technical evaluation")

If they give you some details but miss others, ask only for what's missing.
Keep it short — don't over-ask.

**STEP 2 — Once you have all details, confirm and call set_output (one key per call, \
separate turns):**
- set_output("meeting_title", "the meeting title or brief description")
- set_output("attendees", '[{"name": "Jane Smith", "company": "Acme Corp", \
"role": "VP Engineering"}, ...]')
- set_output("company", "the user's company name")
- set_output("user_role", "the user's role")
- set_output("meeting_goal", "what the user wants to achieve")
""",
    tools=[],
)

# Node 2: Research
# Searches the web for each attendee and the target company.
research_node = NodeSpec(
    id="research",
    name="Research",
    description="Research each attendee and their company using web search and scraping",
    node_type="event_loop",
    max_node_visits=0,
    input_keys=["meeting_title", "attendees", "company", "user_role", "meeting_goal"],
    output_keys=["attendee_profiles", "company_profile", "recent_news", "intel_summary"],
    success_criteria=(
        "Every attendee has a profile with at least their professional background. "
        "The company has a summary covering what they do. Recent news from the past "
        "6 months has been gathered. Sources are cited with URLs."
    ),
    system_prompt="""\
You are a meeting intelligence researcher. Research the meeting attendees and their \
company to build a briefing for the user.

Parse the attendees list (it's a JSON string). Work through each person and the company.

**PHASE 1 — Research each attendee:**
For each attendee:
1. web_search("{name} {company} professional background")
2. web_search("{name} {company} LinkedIn")
3. web_scrape the most promising result URL (professional bio, LinkedIn, company team page)
Extract: current role, career history, areas of expertise, any public talks/articles/quotes.

Limit to 2-3 searches per person. Focus on quality over quantity.

**PHASE 2 — Research the company:**
1. web_search("{company} overview products services 2025")
2. web_search("{company} recent news 2025 2026")
3. web_scrape their official website homepage or About page
4. web_scrape 1-2 recent news articles
Extract: what the company does, their products/services, size/stage, recent developments.

**PHASE 3 — Compile findings:**
Use save_data to start a research notes file, append_data to add to it as you gather info.
Keep track of source URLs for each fact.

Important:
- Work in batches of 3-4 tool calls per turn
- After each batch, assess whether you have enough material
- If a URL fails to scrape, move on — don't retry more than once
- Call set_output for each key in a SEPARATE turn (not mixed with other tool calls)

**When done, call set_output (one key at a time, separate turns):**
- set_output("attendee_profiles", '[{"name": "...", "role": "...", "background": "...", \
"expertise": "...", "sources": ["url1", "url2"]}, ...]')
- set_output("company_profile", '{"name": "...", "description": "...", "products": "...", \
"size": "...", "sources": ["url1"]}')
- set_output("recent_news", '[{"headline": "...", "summary": "...", "url": "...", \
"date": "..."}, ...]')
- set_output("intel_summary", "2-3 paragraph synthesis: what you learned that's most \
relevant to the meeting goal, key themes, potential discussion topics")
""",
    tools=[
        "web_search",
        "web_scrape",
        "save_data",
        "append_data",
        "load_data",
        "list_data_files",
    ],
)

# Node 3: Brief (client-facing)
# Builds and delivers an HTML meeting briefing document.
brief_node = NodeSpec(
    id="brief",
    name="Meeting Brief",
    description="Generate and deliver an HTML meeting briefing with profiles and talking points",
    node_type="event_loop",
    client_facing=True,
    max_node_visits=0,
    input_keys=[
        "meeting_title",
        "attendees",
        "company",
        "user_role",
        "meeting_goal",
        "attendee_profiles",
        "company_profile",
        "recent_news",
        "intel_summary",
    ],
    output_keys=["delivery_status", "next_action"],
    success_criteria=(
        "An HTML briefing file has been saved and served to the user. The brief includes "
        "attendee profiles, company summary, recent news, talking points, and suggested "
        "questions. The user has acknowledged receipt."
    ),
    system_prompt="""\
Write a meeting briefing as an HTML file and present it to the user.

**CRITICAL: Build the file in multiple append_data calls. NEVER write the entire HTML \
in a single save_data call — it will exceed the output token limit.**

IMPORTANT: save_data and append_data require TWO separate arguments: filename and data.
Call like: save_data(filename="brief.html", data="<html>...")
Do NOT include data_dir in tool calls — it is auto-injected.

Parse all JSON input keys before writing (attendee_profiles, company_profile, recent_news).

**PROCESS (follow exactly):**

**Step 1 — Write HTML head + meeting overview (save_data):**
```
save_data(filename="brief.html", data="<!DOCTYPE html>\\n<html>...")
```
Include: DOCTYPE, head with ALL styles below, opening body, h1 with meeting title, \
date stamp, and the Meeting Overview section (goal, your role, your company, attendee list).

**CSS to use (copy exactly):**
```
body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;max-width:860px;\
margin:0 auto;padding:40px;line-height:1.7;color:#222;background:#fff}
h1{font-size:1.9em;color:#1a1a2e;border-bottom:3px solid #4361ee;padding-bottom:12px}
h2{font-size:1.35em;color:#1a1a2e;margin-top:40px;padding-top:20px;\
border-top:1px solid #e0e0e0}
h3{font-size:1.1em;color:#333;margin-top:24px}
p{margin:10px 0}
.meta{color:#666;font-size:0.95em;margin-bottom:30px}
.overview{background:#f0f4ff;padding:20px 24px;border-radius:8px;margin:24px 0;\
border-left:4px solid #4361ee}
.attendee-card{background:#fafafa;border:1px solid #e8e8e8;border-radius:8px;\
padding:20px;margin:16px 0}
.attendee-card h3{margin-top:0;color:#4361ee}
.tag{display:inline-block;background:#e8ecff;color:#4361ee;font-size:0.8em;\
padding:2px 8px;border-radius:4px;margin:2px}
.news-item{border-left:3px solid #e0e0e0;padding-left:14px;margin:12px 0}
.talking-points{background:#f0fff4;border:1px solid #c3e6cb;border-radius:8px;\
padding:20px;margin:16px 0}
.talking-points li{margin:8px 0}
.questions{background:#fff8e1;border:1px solid #ffe082;border-radius:8px;\
padding:20px;margin:16px 0}
.questions li{margin:8px 0}
.source{color:#999;font-size:0.8em}
.source a{color:#4361ee;text-decoration:none}
.footer{text-align:center;color:#aaa;border-top:1px solid #eee;padding-top:20px;\
margin-top:50px;font-size:0.82em}
```

**Step 2 — Append attendee profiles (append_data):**
```
append_data(filename="brief.html", data="<h2>Attendee Profiles</h2>...")
```
For each attendee, write a card with: name, current role/company, career background, \
areas of expertise, any notable articles/talks. Include source URLs as small links.

**Step 3 — Append company intelligence (append_data):**
```
append_data(filename="brief.html", data="<h2>Company Intelligence</h2>...")
```
Include: company description, products/services, recent news items (last 6 months), \
any notable developments relevant to the meeting goal.

**Step 4 — Append talking points and questions (append_data):**
```
append_data(filename="brief.html", data="<h2>Talking Points</h2>...")
```

Generate based on the intel_summary and meeting_goal:
- **Talking Points**: 5-7 specific, tailored points based on what you learned. \
  Each should be grounded in something specific about the company or attendee.
- **Suggested Questions**: 6-8 open-ended questions to ask, ranked by priority. \
  Tailor to the meeting_goal and what you learned about attendees.

Use the .talking-points and .questions CSS classes.

**Step 5 — Append footer (append_data):**
```
append_data(filename="brief.html", data="<div class='footer'>...")
```
Include: "Generated by Meeting Prep Agent · Hive Framework" and closing `</body></html>`.

**Step 6 — Serve the file:**
```
serve_file_to_user(filename="brief.html", label="Meeting Briefing", open_in_browser=true)
```

**Step 7 — Present to user (text only, NO tool calls):**
Print the file_path from serve_file_to_user so the user can reopen it. Give a 3-4 \
sentence summary of the key intel. Ask if they have questions or want to prep another meeting.

**Step 8 — After the user responds:**
Answer follow-up questions if any. When ready, call set_output:
- set_output("delivery_status", "completed")
- set_output("next_action", "new_meeting")   — if they want another meeting prep
- set_output("next_action", "done")          — if they're finished
""",
    tools=["save_data", "append_data", "serve_file_to_user"],
)

__all__ = [
    "intake_node",
    "research_node",
    "brief_node",
]
