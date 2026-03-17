from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass

from dotenv import load_dotenv
from huggingface_hub import InferenceClient


@dataclass(frozen=True)
class Probe:
    kind: str  # ner|embed|textgen|docqa|img2text
    model_id: str


def main() -> None:
    load_dotenv()
    token = os.getenv("HF_API_TOKEN")
    if not token:
        raise SystemExit("HF_API_TOKEN is not set")

    client = InferenceClient(api_key=token)

    probes = [
        Probe("ner", "dslim/bert-base-NER"),
        Probe("embed", "sentence-transformers/all-MiniLM-L6-v2"),
        # Candidates that previously returned 410 in our environment (kept for visibility)
        Probe("ner", "yashpwr/resume-ner-bert-v2"),
        Probe("embed", "TechWolf/JobBERT-v2"),
        Probe("textgen", "Qwen/Qwen2.5-7B-Instruct"),
        Probe("textgen", "numind/NuExtract-1.5"),
        Probe("textgen", "mistralai/Mistral-7B-Instruct-v0.1"),
    ]

    results: dict[str, dict] = {}

    for p in probes:
        start = time.time()
        try:
            body_preview = ""
            status = 200
            if p.kind == "ner":
                out = client.token_classification(
                    "John Doe worked at Microsoft. Email john@example.com",
                    model=p.model_id,
                    aggregation_strategy="simple",
                )
                body_preview = json.dumps(out[:2] if isinstance(out, list) else out)[:400]
            elif p.kind == "embed":
                out = client.feature_extraction("python docker aws", model=p.model_id)
                # only preview vector shape/first numbers
                if isinstance(out, list) and out and isinstance(out[0], (int, float)):
                    body_preview = json.dumps(out[:8])[:400]
                elif isinstance(out, list) and out and isinstance(out[0], list):
                    body_preview = json.dumps(out[0][:8])[:400]
                else:
                    body_preview = str(type(out))[:400]
            elif p.kind == "textgen":
                out = client.text_generation(
                    "Return ONLY JSON: {\"email\": \"john@example.com\"}",
                    model=p.model_id,
                    max_new_tokens=64,
                    temperature=0.0,
                    return_full_text=False,
                )
                body_preview = (out or "")[:400]
            else:
                status = 400
                body_preview = "unsupported probe kind"
            dt_ms = int((time.time() - start) * 1000)
            results[f"{p.kind}:{p.model_id}"] = {
                "status": status,
                "ms": dt_ms,
                "body_preview": body_preview,
            }
        except Exception as e:  # noqa: BLE001
            dt_ms = int((time.time() - start) * 1000)
            results[f"{p.kind}:{p.model_id}"] = {
                "status": None,
                "ms": dt_ms,
                "error": str(e),
            }

        # Small delay to avoid rate limiting
        time.sleep(0.4)

    out_path = "hf_model_probe_results.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    print(out_path)


if __name__ == "__main__":
    main()
