"""
Comprueba que la API key de Gemini funciona y qué modelo tiene cuota.

    uv run python src/scripts/test_gemini_api.py
"""

from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from google import genai

from src.agent.config import DEFAULT_GEMINI_MODEL, get_gemini_model_name
from src.model.settings import get_google_api_key

# Modelos a probar (orden: el de .env primero, luego alternativas free tier)
FALLBACK_MODELS = [
    "gemini-2.5-flash",
    "gemini-2.5-flash-lite",
    "gemini-2.0-flash-lite",
    "gemini-2.0-flash",
    "gemini-1.5-flash",
]


def _mask_key(key: str) -> str:
    if len(key) <= 8:
        return "***"
    return f"{key[:4]}...{key[-4:]}"


def _try_generate(client: genai.Client, model: str) -> tuple[bool, str]:
    try:
        response = client.models.generate_content(
            model=model,
            contents="Responde solo: OK",
        )
        text = (response.text or "").strip()
        return True, text[:80]
    except Exception as exc:
        return False, str(exc)[:300]


def main() -> None:
    key = get_google_api_key()
    configured = get_gemini_model_name()

    print(f"API key cargada: {_mask_key(key)}")
    print(f"Modelo en .env (GEMINI_MODEL): {configured}\n")

    client = genai.Client(api_key=key)

    models_to_try: list[str] = []
    for name in [configured, *FALLBACK_MODELS]:
        if name not in models_to_try:
            models_to_try.append(name)

    print("=== Prueba generate_content por modelo ===\n")
    working: list[str] = []
    for model in models_to_try:
        ok, detail = _try_generate(client, model)
        status = "OK" if ok else "FALLO"
        print(f"[{status}] {model}")
        if ok:
            print(f"       respuesta: {detail}")
            working.append(model)
        else:
            if "429" in detail or "RESOURCE_EXHAUSTED" in detail:
                print("       cuota agotada o free tier = 0 para este modelo")
            elif "404" in detail or "NOT_FOUND" in detail:
                print("       modelo no disponible con tu cuenta")
            else:
                print(f"       {detail}")
        print()

    if working:
        print("Modelos que funcionan ahora:")
        for m in working:
            print(f"  - {m}")
        if configured not in working:
            print(f"\nCambia tu .env a: GEMINI_MODEL={working[0]}")
    else:
        print("Ningún modelo respondió.")
        print(
            "\nPosibles causas:\n"
            "  1. Cuota diaria free tier agotada (espera o activa facturación en Google AI Studio)\n"
            "  2. La clave nueva pertenece al mismo proyecto sin cuota\n"
            "  3. Restricción regional o cuenta sin acceso a Gemini\n"
            "\nMientras tanto puedes probar el pipeline sin LLM:\n"
            "  uv run python src/scripts/run_agent.py --demo"
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
