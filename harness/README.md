# harness/ — the OSAI exam AI-orchestration kit

Why this exists: 2026 pass reports converge on the same meta — the exam is won
by *steering AI well*, not just by knowing payloads. Enumeration discipline,
fresh-context resets, planner→executor delegation, and evidence captured in the
moment. This folder operationalizes that meta.

```
harness/
├── engage.py            # engagement state tracker (targets/flags/creds/loot/tried)
├── prompts/
│   ├── planner.md       # paste into strongest model: strategy + delegation brain
│   ├── executor.md      # paste into fast model: atomic task runner, anti-scope-creep
│   └── kickoff.md       # context-reset protocol (the 30s fresh-session trick)
└── evidence.md          # per-flag proof checklist (screenshot + replay + paragraph)
```

## The loop

```
        ┌──────────────┐   snapshot (memory)   ┌─────────────┐
        │  PLANNER AI  │ ◄───────────────────  │  engage.py  │
        │ (strong mdl) │ ──atomic tasks────┐   │  (you run)  │
        └──────────────┘                   ▼   └─────────────┘
                                      ┌─────────────┐  ▲
                                      │ EXECUTOR AI │  │ every result logged
                                      │ (fast mdl)  │ ─┘ via tried/flag/loot
                                      └─────────────┘
```

1. Exam starts → `python3 engage.py init exam` and everything runs under
   `bash ../capture.sh exam`.
2. Recon results → `target add` each host, `note` the network relationships.
3. Paste `prompts/planner.md` into your strongest model + the `snapshot`.
4. Planner emits 1-3 atomic tasks → each goes to a separate executor session
   running `prompts/executor.md`.
5. Every result → `tried` / `flag` / `cred` / `loot`. No unlogged attempts.
6. Model degrades or refuses? `kickoff.md` → fresh session in 30 seconds.
7. Per flag: `evidence.md` checklist, no exceptions.

## Scoring sanity (24h format)
ai_vector=15, trad_vector=10, DC proof=5, pass=75. Two chains + standalone +
decoys. `engage.py status` keeps the scoreboard honest; `engage.py next` is the
anti-tunnel-vision device.
