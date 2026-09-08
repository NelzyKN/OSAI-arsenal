"""
AI service discovery — maps to AI-300 module: Reconnaissance for AI Targets.

TCP-checks the usual AI/ML ports, then HTTP-probes fingerprint paths and
pulls out the juicy bits (model names, collection names, versions).
"""
import json
import socket
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from ipaddress import ip_network
from pathlib import Path

import requests

requests.packages.urllib3.disable_warnings()

# port -> (likely service, [http probe paths])
AI_PORTS = {
    11434: ("Ollama", ["/api/tags", "/api/version"]),
    7860: ("Gradio", ["/config", "/info"]),
    8000: ("vLLM / LangServe", ["/v1/models", "/docs", "/openapi.json"]),
    8080: ("AI API (generic)", ["/v1/models", "/docs", "/health"]),
    5000: ("MLflow", ["/api/2.0/mlflow/registered-models", "/version"]),
    5001: ("MLflow (alt)", ["/api/2.0/mlflow/registered-models"]),
    8888: ("Jupyter", ["/api", "/api/status", "/tree"]),
    8501: ("Streamlit", ["/", "/healthz"]),
    6333: ("Qdrant", ["/collections", "/cluster"]),
    19530: ("Milvus (gRPC)", []),
    6379: ("Redis / vector cache", []),
    9200: ("Elasticsearch", ["/", "/_cluster/health"]),
    4000: ("LiteLLM proxy", ["/models", "/v1/models", "/health/liveliness"]),
    3000: ("Node / AI app", ["/v1/models", "/api/health", "/health"]),
    3001: ("MCP over HTTP (possible)", ["/sse", "/messages", "/mcp"]),
    9000: ("TorchServe / KServe", ["/models", "/v1/models", "/ping"]),
    9090: ("Inference server", ["/v1/models", "/info", "/health"]),
    8500: ("TF Serving (gRPC)", []),
}


def fingerprint(port, path, resp):
    """Extract the interesting details from a probe response."""
    server = resp.headers.get("Server", "")
    try:
        data = resp.json()
    except ValueError:
        data = None

    if port == 11434 and path == "/api/tags" and isinstance(data, dict):
        names = [m.get("name", "?") for m in data.get("models", [])]
        return "models: " + (", ".join(names) if names else "none")
    if path in ("/v1/models", "/models") and isinstance(data, dict):
        ids = [m.get("id", "?") for m in data.get("data", [])]
        if ids:
            return "models: " + ", ".join(ids)
    if port == 6333 and isinstance(data, dict):
        cols = [c.get("name", "?")
                for c in data.get("result", {}).get("collections", [])]
        return "collections: " + (", ".join(cols) if cols else "none")
    if port == 9200 and isinstance(data, dict) and "version" in data:
        return (f"cluster={data.get('cluster_name', '?')} "
                f"version={data['version'].get('number', '?')}")
    if port == 8888 and isinstance(data, dict) and "version" in data:
        return f"jupyter version={data['version']}"

    if data is not None:
        snippet = json.dumps(data)[:120]
    else:
        snippet = resp.text[:120].replace("\n", " ")
    bits = []
    if server:
        bits.append(f"server={server}")
    if snippet.strip():
        bits.append(f"body={snippet!r}")
    return "  ".join(bits) if bits else "-"


def expand_targets(spec):
    """Accept a single host, a CIDR, or a file with one host per line."""
    p = Path(spec)
    if p.is_file():
        return [line.strip() for line in p.read_text().splitlines()
                if line.strip() and not line.strip().startswith("#")]
    if "/" in spec:
        hosts = [str(h) for h in ip_network(spec, strict=False).hosts()]
        if len(hosts) > 4096:
            sys.exit("[-] CIDR too large (>4096 hosts); split it up.")
        return hosts
    return [spec]


def probe_pair(host, port, service, paths, timeout):
    """TCP check one host:port, then fingerprint over HTTP if it speaks."""
    try:
        with socket.create_connection((host, port), timeout=timeout):
            pass
    except OSError:
        return None
    finding = {"host": host, "port": port, "service": service, "probes": []}
    for path in paths:
        for scheme in ("http", "https"):
            url = f"{scheme}://{host}:{port}{path}"
            try:
                r = requests.get(url, timeout=timeout, verify=False,
                                 allow_redirects=False)
            except requests.RequestException:
                continue
            finding["probes"].append({
                "url": url,
                "status": r.status_code,
                "detail": fingerprint(port, path, r),
            })
            break
    return finding


def run(args):
    targets = expand_targets(args.targets)
    ports = dict(AI_PORTS)
    if args.ports:
        for extra in args.ports.split(","):
            ports[int(extra.strip())] = ("custom", ["/"])
    timeout = args.timeout

    print(f"[*] scanning {len(targets)} host(s) x {len(ports)} ports "
          f"({timeout}s timeout)")
    findings = []
    with ThreadPoolExecutor(max_workers=64) as ex:
        futures = [
            ex.submit(probe_pair, host, port, service, paths, timeout)
            for host in targets
            for port, (service, paths) in ports.items()
        ]
        for fut in as_completed(futures):
            res = fut.result()
            if not res:
                continue
            findings.append(res)
            print(f"[+] {res['host']}:{res['port']}  OPEN  {res['service']}")
            for pr in res["probes"]:
                print(f"      {pr['url']} -> {pr['status']}  {pr['detail']}")

    if not findings:
        print("[-] no AI services identified")
    if args.output:
        Path(args.output).write_text(json.dumps(findings, indent=2))
        print(f"[*] wrote {args.output}")
