#!/usr/bin/env python3
"""
osai-arsenal — AI red team toolkit aligned to OffSec AI-300 (OSAI).

Subcommands:
  recon    discover AI services (Ollama, vLLM, MLflow, Jupyter, vector DBs, MCP...)
  probe    fire a payload corpus at an LLM endpoint, flag refusals vs bypasses
  corpus   list payload files and counts

For AUTHORIZED lab / exam use only (AI-300 labs, OSAI exam, your own infra).
"""
import argparse
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from modules import recon, llmprobe  # noqa: E402


def corpus(args):
    pdir = HERE / "payloads"
    files = sorted(pdir.glob("*.txt"))
    if not files:
        print("[-] no payload files found in payloads/")
        return
    print(f"[*] payload corpus ({pdir})")
    for f in files:
        count = sum(
            1 for line in f.read_text().splitlines()
            if line.strip() and not line.strip().startswith("#")
        )
        print(f"    {f.name:40s} {count:3d} payloads")


def main():
    ap = argparse.ArgumentParser(
        prog="arsenal",
        description="osai-arsenal: AI red team toolkit aligned to OffSec AI-300 (OSAI)",
    )
    sub = ap.add_subparsers(dest="cmd", required=True)

    r = sub.add_parser("recon", help="discover AI services on target hosts")
    r.add_argument("targets", help="single host, CIDR, or path to a file of hosts")
    r.add_argument("-p", "--ports", help="extra ports to check, comma-separated")
    r.add_argument("-t", "--timeout", type=float, default=2.0, help="socket timeout (s)")
    r.add_argument("-o", "--output", help="write findings to a JSON file")
    r.set_defaults(func=recon.run)

    l = sub.add_parser("probe", help="send a payload corpus to an LLM endpoint")
    l.add_argument("url", help="endpoint URL (e.g. http://host:11434/api/generate)")
    l.add_argument("payloads", help="payload file from payloads/ (or any text file)")
    l.add_argument("--fmt", choices=["openai", "ollama", "raw"], default="openai",
                   help="request format to speak")
    l.add_argument("--model", default=None, help="model name if the API needs one")
    l.add_argument("--timeout", type=float, default=30.0)
    l.add_argument("--delay", type=float, default=0.0, help="delay between requests (s)")
    l.add_argument("-o", "--output", default="probe_results.jsonl",
                   help="JSONL results file (appended)")
    l.set_defaults(func=llmprobe.run)

    c = sub.add_parser("corpus", help="list payload corpus contents and counts")
    c.set_defaults(func=corpus)

    args = ap.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
