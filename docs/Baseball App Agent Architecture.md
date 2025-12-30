This is a sophisticated architecture. You're moving away from a "dumb" batch processor toward a **State-Driven Event Loop**. By using "Trigger Agents" (Watchdogs) to filter the noise, you're essentially building a "Just-In-Time" (JIT) scouting system.

Here is a structured plan, list of todos, and the research gaps we need to fill.

---

## 🏗️ The Architecture: "The Baseball Brain"

We’ll treat the system as a **Multi-Agent Orchestration** where specific agents are "Sensors" and others are "Processors."

### 1. The Watchdog Layer (Sensors)

* **Frequency:** Every 1–4 hours.
* **Role:** Scan reliable RSS feeds, Twitter/X (via API), and transaction logs.
* **Output:** A "Delta Report" (e.g., "Mookie Betts: 10-day IL, fractured hand").

### 2. The Verification Layer (The Entity Resolver)

* **Role:** The "Will Smith Problem." Uses a reference database (PlayerID/MLB ID) to ensure the delta is mapped to the correct record.
* **Logic:** If "Will Smith" is found, it cross-references the Team/Position before triggering an update.

### 3. The Processor Layer (Deep Research)

* **Role:** Takes the Delta + Existing Report.
* **Action:** Decides if a "Full Re-Scout" (Deep Agent) is needed or just a "Patch" (Minor text update).

---

## ✅ To-Do List

### Phase 1: Data & Entity Integrity

* [ ] **Create a Master Player Registry:** Secure a static list of all active MLB and top-tier MiLB players with unique IDs (MLB ID, FanGraphs ID, or similar).
* [ ] **Build the "Entity Resolver" Agent:** A specialized prompt/service that takes a name + context and returns a unique PlayerID.
* [ ] **Setup Versioning Schema:** Define a database schema for `ScoutingReports`.
* *Rule:* Reports are immutable. `version_v1`, `version_v2`.
* *Metadata:* `trigger_reason`, `source_url`, `timestamp`.



### Phase 2: Agent Development (The Sensors)

* [ ] **Develop "Injury Watchdog":** Prompt for extracting player name, injury type, and expected duration.
* [ ] **Develop "Transaction Watchdog":** Focus on trades, DFA, and MiLB call-up rumors.
* [ ] **Build the "Change Detector":** An agent that compares the *New Info* vs. *Current Report* and outputs a boolean: `update_required: True/False`.

### Phase 3: Prompt Engineering & DSPy

* [ ] **Collect "Gold Standard" Examples:** You need ~50 examples of a "Perfect Scouting Report" to use as a DSPy training set.
* [ ] **Write DSPy Signatures:** Define the input/output types (e.g., `PlayerBio -> ScoutingReport`).
* [ ] **Bootstrap Graders:** Create a "Critic Agent" (using Claude or DeepSeek) to score the Gemini-generated reports.

### Phase 4: Compliance & Lifecycle

* [ ] **Automation Script for Data Deletion:** A cron job that purges any report older than 700 days (to stay safely under the 2-year Gemini TOS limit).
* [ ] **Microservice Setup:** Decide on a framework (LangGraph or PydanticAI) to handle the agent-to-agent communication.

---

## 🧪 Additional Research Needed

### 1. Agent-to-Agent (A2A) Protocols

* **The "Interactions API":** Google just released a new **Interactions API** specifically for Gemini Deep Research. We need to see if it supports "handoffs" or if we need to manage the state in our own middleware.
* **State Management:** Research how to use **LangGraph** or **PydanticAI** to maintain the "Memory" of what an agent found so the next agent doesn't repeat the work.

### 2. Model Benchmarking for "Graders"

* **DeepSeek-V3/R1 vs. Claude 3.5 Sonnet:** We need to test which model is better at catching "Baseball Hallucinations" (e.g., a model saying a pitcher threw 105mph when they didn't).
* **Cost Analysis:** Running Deep Research for every minor injury is expensive. We need to research "Small Model" (Gemini Flash) performance for the Watchdog layer to keep costs down.

### 3. DSPy Reinforcement Loops

* **Optimization Strategy:** Research how to "auto-update" prompts. If a Grader keeps marking a report as "too wordy," how do we programmatically feed that back into the DSPy optimizer?

### 4. Legal & Compliance

* **Terms of Service (Section 4):** Verify if "Grounded Results" (search-enabled reports) have different storage rules than standard LLM outputs. The 2-year rule usually applies to specific "Grounded" data.

---

**Would you like me to draft the first "Entity Resolver" prompt or a schema for how the versioning database should look?**