# OSAI Exam Report — OS-XXXXX

> OffSec documentation requirements are strict: every step, every command,
> console output, and screenshots per stage. A technically competent reader
> must be able to replicate your attacks copy/paste. Missing screenshots =
> reduced or zero points, and the submission is FINAL.

- **Student:** <name>
- **OSID:** OS-XXXXX
- **Exam date:** <date>
- **Report deadline:** exam end + 24h (automatic fail if late)

---

## 1. Executive Summary

Short overview: targets compromised, key vulnerabilities, attack paths taken,
final score expectation per machine.

## 2. Scope & Environment

- Entry points: <public IP/host per chain>
- Chains: Chain A (3 hosts), Chain B (3 hosts), Standalone AI host, DC flag
- Note the two intentionally-not-vulnerable machines if identified (no points).

## 3. Attack Chain A

### 3.1 Host A1 — <IP/hostname> — <vector type: AI (15 pts) / traditional (10 pts)>

**Reconnaissance**
- Command: `<exact command>`
- Output: `<paste console output>`
- Screenshot: `![A1-recon](screenshots/A1-recon-01.png)`

**Vulnerability identification**
- Finding, evidence, why it's exploitable.

**Exploitation**
- Every command in order, full output, screenshot per stage.
- If using an existing script/exploit: source link + copy of code + ALL modifications documented.

**Post-exploitation / privilege escalation**
- Same rigor. Proof file: `cat proof.txt` output + screenshot.

### 3.2 Host A2 — ...
### 3.3 Host A3 — ...

## 4. Attack Chain B

(Same structure as Chain A: B1, B2, B3.)

## 5. Standalone AI Host (15 pts)

AI-focused vector: payload, conversation transcript (as text!), screenshots,
why the attack worked.

## 6. Domain Controller — flag (5 pts, submit once)

Which chain route was used, proof of flag.

## 7. Vulnerability Summary

| Host | Vulnerability | Vector | Severity | Points |
|------|---------------|--------|----------|--------|
| A1   |               |        |          |        |

## 8. Tools & Code Appendix

Every script/exploit used: source link, full code, modifications. Include your
AI-assistance workflow notes (prompts used are part of your process — keep
them, they're admissible and expected).

---

## Submission checklist (DO NOT SKIP)

- [ ] Report exported as **PDF**
- [ ] Named `OSAI-OS-XXXXX-Exam-Report.pdf`
- [ ] Archived: `7z a OSAI-OS-XXXXX-Exam-Report.7z OSAI-OS-XXXXX-Exam-Report.pdf` (NO password)
- [ ] Only the PDF inside the .7z
- [ ] Archive < 100MB
- [ ] `md5sum` of local file compared to the hash shown after upload
- [ ] Uploaded within 24h of exam end
- [ ] All screenshots present — re-read the PDF end-to-end before submitting
