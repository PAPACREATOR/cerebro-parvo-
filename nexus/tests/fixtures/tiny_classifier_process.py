import json
import sys
import time

request = json.load(sys.stdin)
text = request.get("text", "")
if "TIMEOUT" in text:
    time.sleep(10)
if "MALFORMED" in text:
    print("not-json")
    raise SystemExit(0)
if "INJECT" in text:
    print(json.dumps({"intent": "web", "authority": "CANONICAL"}))
    raise SystemExit(0)

mapping = {
    "WEB": "web",
    "FONTES": "fontes",
    "TRABALHAR": "trabalhar",
    "PERGUNTAR": "perguntar",
    "CALCULAR": "calcular",
    "TEMA": "tema",
    "ARQUIVO": "arquivo",
}
hits = [intent for marker, intent in mapping.items() if marker in text]
print(json.dumps({"intent": hits[0] if len(set(hits)) == 1 else "UNKNOWN"}))
