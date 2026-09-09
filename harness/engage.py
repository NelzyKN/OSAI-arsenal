#!/usr/bin/env python3
"""engage.py — OSAI engagement state tracker.

The exam's silent killer is lost context: after hours of attacks, neither you
nor your AI assistant remembers what's been tried. This keeps the whole
engagement in one JSON file and emits compact snapshots to paste into any
(fresh) AI session. Zero dependencies, stdlib only.

Usage:
  python3 engage.py init <exam_label>
  python3 engage.py target add 10.10.10.5 [--role foothold] [--notes "..."]
  python3 engage.py target update 10.10.10.5 --status owned
  python3 engage.py flag add 10.10.10.5 ai_vector 15 "prompt-inj dump of sys prompt"
  python3 engage.py cred add user:pass@10.10.10.5 [--source "config.ps1"]
  python3 engage.py loot add 10.10.10.5 "/path/file" "what it contained"
  python3 engage.py tried 10.10.10.5 "dirsearch /api" "404 wall"     # rabbit-hole log
  python3 engage.py note "private net 10.10.20.0/24 reachable via .5"
  python3 engage.py status                                            # scoreboard
  python3 engage.py snapshot                                          # paste into fresh AI session
  python3 engage.py next                                              # what hasn't been tried

State file: engage-<label>.json in the current directory. Back it up with your
capture.sh logs — it is your engagement memory.
"""
import json, sys, os, time

def state_path(label):
    return f"engage-{label}.json"

def load():
    p = find_state()
    if not p:
        die("no engagement state found — run: python3 engage.py init <label>")
    with open(p) as f:
        return json.load(f), p

def find_state():
    for f in sorted(os.listdir('.')):
        if f.startswith('engage-') and f.endswith('.json'):
            return f
    return None

def save(s, p):
    s['updated'] = time.strftime('%H:%M:%S')
    with open(p, 'w') as f:
        json.dump(s, f, indent=2)

def die(msg):
    print(f"[-] {msg}")
    sys.exit(1)

def score(s):
    return sum(f['points'] for f in s['flags'])

# --- commands ---------------------------------------------------------------

def cmd_init(label):
    p = state_path(label)
    if os.path.exists(p):
        die(f"{p} already exists")
    s = {
        'label': label,
        'created': time.strftime('%Y-%m-%d %H:%M:%S'),
        'updated': time.strftime('%H:%M:%S'),
        'targets': [],      # {ip, role, status, notes, tried:[{what,result}]}
        'flags': [],        # {host, kind, points, how, ts}
        'creds': [],        # {cred, source, ts}
        'loot': [],         # {host, path, what, ts}
        'notes': [],        # {text, ts}
    }
    save(s, p)
    print(f"[+] engagement '{label}' initialized -> {p}")
    print("[i] tip: run everything under  bash ../capture.sh " + label)

def cmd_target(args):
    s, p = load()
    if args[0] == 'add':
        ip = args[1]
        if any(t['ip'] == ip for t in s['targets']):
            die(f"{ip} already tracked")
        role = opt(args, '--role', 'unknown')
        notes = opt(args, '--notes', '')
        s['targets'].append({'ip': ip, 'role': role, 'status': 'discovered',
                             'notes': notes, 'tried': []})
        save(s, p)
        print(f"[+] target {ip} ({role})")
    elif args[0] == 'update':
        ip, status = args[1], opt(args, '--status', None)
        t = next((t for t in s['targets'] if t['ip'] == ip), None) or die(f"{ip} not tracked")
        if status:
            t['status'] = status
        n = opt(args, '--notes', None)
        if n:
            t['notes'] = (t['notes'] + ' | ' + n).strip(' |')
        save(s, p)
        print(f"[+] {ip} -> {t['status']}")

def cmd_flag(args):
    s, p = load()
    # flag add <host> <kind> <points> <how>
    host, kind, pts, how = args[2], args[3], int(args[4]), ' '.join(args[5:])
    s['flags'].append({'host': host, 'kind': kind, 'points': pts, 'how': how,
                       'ts': time.strftime('%H:%M:%S')})
    save(s, p)
    print(f"[+] FLAG {kind} on {host} (+{pts}) — total {score(s)}/100, need 75")
    print("[!] evidence: screenshot NOW, then  python3 engage.py loot add ...  and log the exact replay command")

def cmd_cred(args):
    s, p = load()
    cred = args[2]
    s['creds'].append({'cred': cred, 'source': opt(args, '--source', ''),
                       'ts': time.strftime('%H:%M:%S')})
    save(s, p)
    print(f"[+] cred {cred}")

def cmd_loot(args):
    s, p = load()
    host, path = args[2], args[3]
    what = ' '.join(args[4:])
    s['loot'].append({'host': host, 'path': path, 'what': what,
                      'ts': time.strftime('%H:%M:%S')})
    save(s, p)
    print(f"[+] loot {host}:{path}")

def cmd_tried(args):
    s, p = load()
    ip, what, result = args[1], args[2], ' '.join(args[3:])
    t = next((t for t in s['targets'] if t['ip'] == ip), None) or die(f"{ip} not tracked — add it first")
    t['tried'].append({'what': what, 'result': result})
    save(s, p)
    print(f"[+] logged attempt on {ip} (total {len(t['tried'])}) — no re-tries, no rabbit holes")

def cmd_note(args):
    s, p = load()
    s['notes'].append({'text': ' '.join(args[1:]), 'ts': time.strftime('%H:%M:%S')})
    save(s, p)
    print("[+] noted")

def cmd_status():
    s, _ = load()
    pts = score(s)
    bar = '#' * (pts // 5) + '-' * (20 - pts // 5)
    print(f"\n=== {s['label']} | {pts}/100 pts [{bar}] (pass at 75) ===")
    for t in s['targets']:
        print(f"  {t['ip']:<16} {t['role']:<10} {t['status']:<12} tried:{len(t['tried'])}  {t['notes'][:60]}")
    print(f"  flags: {len(s['flags'])}  creds: {len(s['creds'])}  loot: {len(s['loot'])}  notes: {len(s['notes'])}")
    if s['flags']:
        for f in s['flags']:
            print(f"    [{f['ts']}] {f['kind']} @{f['host']} +{f['points']} — {f['how'][:70]}")

def cmd_snapshot():
    s, _ = load()
    print("=== ENGAGEMENT SNAPSHOT — paste into fresh AI session ===")
    print(f"We are in an authorized OffSec OSAI (AI-300) proctored exam engagement, label '{s['label']}'.")
    print(f"Rules of engagement: score 75/100 to pass. AI-vector flags=15pts, traditional=10pts, DC proof=5pts.")
    print(f"Current score: {score(s)}/100. Interactive shell NOT required; file-read of flags suffices.")
    print("Targets:")
    for t in s['targets']:
        print(f"  - {t['ip']} [{t['role']}] status={t['status']} notes={t['notes']}")
        for tr in t['tried']:
            print(f"      tried: {tr['what']} -> {tr['result']}")
    for c in s['creds']:
        print(f"  cred: {c['cred']} (from {c['source']})")
    for f in s['flags']:
        print(f"  flag: {f['kind']} @{f['host']} +{f['points']} via {f['how']}")
    for n in s['notes'][-10:]:
        print(f"  note[{n['ts']}]: {n['text']}")
    print("Do not re-run anything listed under 'tried'. Propose the highest-value UNTRIED attack surface next,")
    print("one concrete step at a time, with exact commands. Verify everything before I document it.")
    print("=== END SNAPSHOT ===")

def cmd_next():
    s, _ = load()
    print("[*] unexplored surface checklist:")
    seen = ' '.join(tr['what'].lower() for t in s['targets'] for tr in t['tried'])
    checks = [
        ('ai-recon',   'model fingerprint /version,/api/tags, model name leak on each foothold'),
        ('sys-prompt', 'system-prompt extraction on every chat/agent endpoint found'),
        ('rag',        'vector store ports (6333/19530/8080), collection enum, poisoned-doc injection'),
        ('agent',      'tool/function-call surface of agents: can they read files/run code/fetch URLs?'),
        ('mcp',        'MCP servers: tools/list, poisoned descriptions, shadowing, rug-pull'),
        ('web',        'classic web: dirs, params, LFI/RFI (file-read flags count!), SSTI, auth bypass'),
        ('smb',        'SMB/LDAP/Kerberos on Windows hosts; cred reuse from loot'),
        ('supply',     'model/dataset artifacts on disk: pickle/safetensors, requirements.txt tampering'),
        ('pivot',      'routes from owned hosts into private net; socks proxy up?'),
    ]
    for tag, what in checks:
        mark = 'x' if tag in seen else ' '
        print(f"  [{mark}] {what}")
    untouched = [t['ip'] for t in s['targets'] if not t['tried'] and t['status'] != 'owned']
    if untouched:
        print(f"  [!] targets with ZERO attempts: {', '.join(untouched)}")
    decoys = [t['ip'] for t in s['targets'] if len(t['tried']) >= 5 and t['status'] != 'owned']
    if decoys:
        print(f"  [?] possible decoys (5+ failed attempts): {', '.join(decoys)} — consider deprioritizing")

def opt(args, flag, default):
    return args[args.index(flag) + 1] if flag in args else default

def main():
    a = sys.argv[1:]
    if not a:
        print(__doc__)
        return
    cmd = a[0]
    if cmd == 'init' and len(a) > 1: cmd_init(a[1])
    elif cmd == 'target' and len(a) > 1: cmd_target(a[1:])
    elif cmd == 'flag': cmd_flag(a)
    elif cmd == 'cred': cmd_cred(a)
    elif cmd == 'loot': cmd_loot(a)
    elif cmd == 'tried': cmd_tried(a)
    elif cmd == 'note': cmd_note(a)
    elif cmd == 'status': cmd_status()
    elif cmd == 'snapshot': cmd_snapshot()
    elif cmd == 'next': cmd_next()
    else:
        print(__doc__)

if __name__ == '__main__':
    main()
