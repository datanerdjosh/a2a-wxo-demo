# A2A Agent → IBM watsonx Orchestrate: Step-by-Step Demo Guide

Connect an external A2A-compliant agent to IBM watsonx Orchestrate SaaS so Orchestrate can delegate tasks to it as a sub-agent (collaborator). This demo uses a minimal hardcoded "Hello World" agent — no LLM required — to prove the connection works end-to-end.

---

## What You Need

| Requirement | Notes |
|---|---|
| Python 3.9+ | `python3 --version` to check |
| ngrok | Free account at [ngrok.com](https://ngrok.com). Install: `brew install ngrok/ngrok/ngrok` |
| IBM watsonx Orchestrate SaaS | Trial or paid tenant on IBM Cloud |
| If you are an IBMer, you can use a TechZone watsonx Orchestrate reservation |

---

## Project Structure

```
a2a-wxo-demo/
├── server.py          # The A2A agent server
├── requirements.txt   # Python dependencies
└── chat.html          # Optional browser chat UI for direct testing
```

---

## Step 1 — Set Up the Python Environment

```bash
cd a2a-wxo-demo
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

---

## Step 2 — Start the A2A Server

```bash
python3 server.py
```

You should see:
```
Hello World Agent (A2A 0.3.0) listening on http://127.0.0.1:9999
```

Leave this terminal open.

**Verify it works locally (optional):**
```bash
curl http://localhost:9999/.well-known/agent.json
```
Should return the Agent Card JSON with `"protocolVersion": "0.3.0"`.

> **If you get "Address already in use":** Run `lsof -ti:9999 | xargs kill -9` then retry.

---

## Step 3 — Expose the Server via ngrok

Open a **second terminal** and run:

```bash
ngrok http 9999
```

Copy the **HTTPS Forwarding URL** from the output — it looks like:
```
https://abc123.ngrok-free.app
```

Leave this terminal open.

**Verify it's reachable publicly (optional):**
```bash
curl https://<your-ngrok-url>/.well-known/agent.json
```

> **If ngrok says the endpoint is already online:** Your previous tunnel is still alive and the URL hasn't changed. Skip this step and use the existing URL.

> **Important:** On a free ngrok account, the URL changes every time you restart ngrok. Always copy the fresh URL from the terminal.

---

## Step 4 — Create a Connection in Orchestrate

Before importing the agent, Orchestrate requires a named credential entry even for servers with no real authentication.

1. In Orchestrate, click the Hamburger icon in the upper left corner go to **Manage → Security → Connections**
2. Click **Add connection**
3. Fill in:
   - **Connection ID:** `hello-world-a2a`
   - **Display name:** `Hello World A2A`
   - **Description:** anything
4. Click **Save and continue**
5. On "Configure draft environment":
   - **Authentication type:** Bearer token
   - **Token:** `noauth`
6. Click **Save and continue**
7. On "Configure live environment": same values — Bearer token / `noauth`
8. Save

---

## Step 5 — Import the External Agent
With the product evolving and changing over time, how you import an agent might be slightly different. I have provided two paths below.

** PATH 1 ** 
Click the Hamburger icon in the upper left corner. If you have the **Agent Directory** within the **AI Gateway**, follow these steps to get to the point where you are important the agent.
1. Click the Hamburger icon in the upper left corner go to **AI Gateway → Agent Directory**
2. Click **Add agent**
3. Fill in the Details step:

   | Field | Value |
   |---|---|
   | **Purpose** | Import for use and observability |
   | **External protocol** | External agent via A2A protocol |
   | **A2A protocol version** | `0.3.0` |
   | **Service instance URL** | your ngrok HTTPS URL (no trailing space, no trailing slash) |

4. Fill in **Define new agent**:
   - **Name:** `Hello World Agent` (or anything)
   - **Description:** anything

5. Click **Next** to the Connection step:
   - Select the connection you created in Step 4: `Hello World A2A`

6. Click **Save**

The agent will appear in your Agents list.


** PATH 2 ** 
If you do NOT have the **Agent Directory**, you will need to follow these steps.
1. Create an Agent. This is the one that will be collaborating with your A2A agent. You do not need Knowledge or Tools. Example information below.
   > Agent Name: *A2A Test Agent*
   > Description: *A2A collaborator agent used for testing an external agent*
   > Instructions: *When the user says hello or asks for a greeting, delegate to the Hello World Agent.*
2. On the Agents tab, click Add Agents.
3. Import and Register an External Agent.
4. Select External Agent and click Next.
5. Fill in the Details step:

   | Field | Value |
   |---|---|
   | **External protocol** | External agent via A2A protocol |
   | **A2A protocol version** | `0.3.0` |
   | **Service instance URL** | your ngrok HTTPS URL (no trailing space, no trailing slash) |

4. Fill in **Define new agent**:
   - **Name:** `Hello World Agent` (or anything)
   - **Description:** anything

5. Click **Next** to the Connection step:
   - Select the connection you created in Step 4: `Hello World A2A`

6. Click **Save**

The agent will appear in your Agents list.

---

## Step 6 — Test in Orchestrate

1. If you haven't already created a collaborator agent for the Hello World Agent, open or create an agent in the **Agent Builder** before testing.
2. Add **Hello World Agent** as a collaborator
3. In the agent's instructions, add:
   > *When the user says hello or asks for a greeting, delegate to the Hello World Agent.*
4. Open the agent's **Draft Preview** chat
5. Send: `hello`
6. When prompted **Connect to app → Hello World A2A**, enter `noauth` as the bearer token and click **Connect**

You should receive:
```
Hello, World! I have received your request (Hello)
```

---

## Step 7 — Make your demo even better

Once you have tested out your A2A agent and have several chats, you can extend your demo by incorporating elements from the Agentic Control Plane.

** AGENT ANALYTICS **
1. Navigate to the **Agent Analytics** for your A2A Test Agent via the Adoption section within the Agentic Control Plane or through the Analyze option on the Orchestrate menu.
2. Once you are looking at the analytics for the agent, navigate to the Conversations tab so you can see more granular details for the conversations that you've had with your agent.
3. If you click the **Debug** option on a chat, you can get down to the trace level detail of those conversations.

** CONTROLS **
1. Another option is to set a Control (kind of like a real-time guardrail) on the agent. To access Controls, you can navigate to **Security and Risk** from the home page and then select **View All** next to Recent Controls.
2. Create Control
3. Select PII Filter or Content Guardrails depending on the time of guardrail/control you'd like to showcase. For example, we'll go with PII Filter.
4. How you set up the Control is up to you but one recommendation is to create a SSN filter where the Enforcement type is both Input and Output, Detection type is Detect SSN, and select all Enforcement Modes.
5. Apply the control to both the Collaborator agent and the A2A agent.
6. Test the control by chatting with the collaborator agent and showcasing how the control you implemented works.

---

## Restarting the Demo

Every time you restart (new terminal session, machine reboot, etc.):

1. **Start the server:** `cd a2a-wxo-demo && source .venv/bin/activate && python3 server.py`
2. **Start ngrok:** `ngrok http 9999`
3. If the ngrok URL changed, re-import the agent in Orchestrate with the new URL (or update the existing agent's service URL)

---

## Key Technical Notes

These were discovered through testing — not obvious from the A2A or Orchestrate documentation:

| Issue | Resolution |
|---|---|
| Orchestrate only supports A2A protocol `0.2.1` and `0.3.0` | Use `a2a-sdk==0.3.0`, not the latest `1.x` |
| Orchestrate posts to `POST /` (the root of your service URL) | Mount the handler at `rpc_url='/'`, not `/a2a/v1` |
| Orchestrate always uses the streaming endpoint | Set `streaming: True` in the Agent Card capabilities |
| A connection entry is required even with no real auth | Create a bearer token connection with a placeholder value |
| Trailing space in the service URL causes a parse error | Paste carefully — no trailing space or slash |
