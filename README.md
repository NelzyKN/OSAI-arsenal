# osai-arsenal

AI red team toolkit aligned to the OffSec **AI-300 (OSAI)** syllabus — v2.
For authorized use only: AI-300 labs, the OSAI exam, and infrastructure you
own or are explicitly permitted to test.

**New in v2:** `harness/` — the exam-grade AI-orchestration kit (planner/executor
prompts, `engage.py` state tracker with snapshot/reset protocol, evidence
discipline checklist). Built from 2026 pass-report meta: enumeration first,
context resets beat arguing, log every attempt, verify before documenting.
See `harness/README.md`.

## What's in v1

```
osai-arsenal/
├── arsenal.py            # CLI entry point (recon / probe / corpus)
├── modules/
│   ├── recon.py          # AI service discovery + fingerprinting
│   └── llmprobe.py       # LLM payload harness with refusal/bypass flagging
├── payloads/             # attack corpus, one theme per file
│   ├── direct_injection.txt
│   ├── system_prompt_extraction.txt
│   ├── agent_memory_tool_abuse.txt
│   ├── indirect_rag_poisoning.txt
│   ├── mcp_tool_surface.txt
│   └── multi_agent_a2a.txt
├── templates/
│   └── report_template.md  # OSAI report skeleton + submission checklist
└── capture.sh            # timestamped full-session logging (run: bash capture.sh <label>)
```

## Syllabus map

| AI-300 module | Tool / corpus |
|---|---|
| Reconnaissance for AI Targets | `arsenal.py recon` — probes Ollama, vLLM, Gradio, MLflow, Jupyter, Qdrant, Milvus, LiteLLM, MCP-over-HTTP, TF/Torch serving and more; fingerprints models & collections |
| Attacking AI Agents | `direct_injection.txt`, `system_prompt_extraction.txt`, `agent_memory_tool_abuse.txt` via `arsenal.py probe` |
| Multi-Agent & A2A | `multi_agent_a2a.txt` |
| Exploiting RAG Pipelines | `indirect_rag_poisoning.txt` (includes retrieval canaries) |
| MCP & Tool Surfaces | `mcp_tool_surface.txt` (enumeration, poisoned descriptions, shadowing) |
| Report / documentation | `templates/report_template.md` + `capture.sh` |

## Quickstart

```bash
pip install -r requirements.txt

# see what's in the corpus
python3 arsenal.py corpus

# discover AI services (single host, CIDR, or file of hosts)
python3 arsenal.py recon 10.10.10.0/24 -o recon.json
python3 arsenal.py recon 10.10.10.5 -t 1.5

# fire a payload corpus at an LLM endpoint
python3 arsenal.py probe http://10.10.10.5:11434/api/generate \
    payloads/system_prompt_extraction.txt --fmt ollama --model llama3
python3 arsenal.py probe http://10.10.10.6:8000/v1/chat/completions \
    payloads/direct_injection.txt --fmt openai --model target-model

# log everything for the report (commands + output, timestamped)
bash capture.sh chainA-host1
```

`probe` flags each reply `REFUSED` / `POSSIBLE_BYPASS` / `REVIEW` and appends
full request/response pairs to a JSONL file — screenshot the console output
for the report, then mine the JSONL for the winning payloads.

## Roadmap (next builds before October)

- **RAG poisoning lab** — local vector DB + poisoned doc corpus to practice retrieval manipulation and canary placement
- **Embedding inversion notebook** — module 6 practice: recover text/data from embedding leaks
- **Rogue MCP server** — a deliberately malicious MCP server to rehearse tool-poisoning and rug-pull attacks end to end
- **Supply-chain lab** — scanner for malicious pickle/safetensors artifacts and dependency tampering
- **Report auto-builder** — turn `capture.sh` logs + JSONL into a pre-filled report skeleton
