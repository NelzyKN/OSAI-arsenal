# Evidence discipline — per-flag checklist

The report window is 24h, but pass reports agree: collect DURING, not after.
For every flag, in this order:

1. **Screenshot** the flag in situ (terminal with `cat`, browser, whatever) —
   include the host indicator in frame (prompt shows IP/host) so provenance is
   unambiguous.
2. **Replay command**: the single shortest command that re-reads the flag.
   Paste it into the report draft immediately. If it can't be replayed, the
   finding isn't solid yet — keep working.
3. `python3 engage.py flag add <host> <kind> <points> "<one-line how>"`
4. `python3 engage.py loot add <host> <path> "<what it gave us>"` for the file
   that contained it.
5. **Write the paragraph NOW**: two sentences — what the vuln was, how it
   yielded the flag — into your report skeleton (`templates/report_template.md`).
   Future-you at hour 20 will be grateful.
6. If the flag came from an AI vector (prompt injection, RAG, agent abuse,
   MCP), ALSO save the exact payload: `python3 engage.py note "payload: ..."`.

## Report auto-check before submission
- Every claimed flag has: screenshot + replay command + one-paragraph narrative
- `engage.py status` score ≥ 75 and matches the report's claimed points
- DC proof.txt submitted exactly once
- No finding rests solely on an AI assistant's say-so — all verified by replay
