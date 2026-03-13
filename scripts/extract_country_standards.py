#!/usr/bin/env python3
"""
Country Standards Extractor using AI.
Este script lee un archivo fuente (ej. texto, CSV o PDF extraído) del catálogo
de cuentas de un país y utiliza el ai_router para extraer un JSON estructurado.

Uso:
    python scripts/extract_country_standards.py --country mx --source path/to/sat_raw.csv
"""

import os
import json
import argparse
from pathlib import Path
from ai_router import router

def get_extraction_prompt(country: str, text_chunk: str) -> str:
    """Generates the prompt for the AI to extract accounts."""
    
    context = ""
    if country == "mx":
        context = "Estás analizando el Anexo 24 del SAT (Catálogo de Cuentas de México)."
    elif country == "co":
        context = "Estás analizando el PUC (Plan Único de Cuentas de Colombia)."
    elif country == "pa":
        context = "Estás analizando el catálogo de cuentas de la DGI/SMV de Panamá."
    
    return f"""
{context}

Tu tarea es extraer todas las cuentas contables de Nivel 1 y Nivel 2 que encuentres en el siguiente texto y devolverlas en formato JSON puramente estructurado, sin texto adicional (ni markdown de código como ```json).

La estructura del JSON debe ser EXACTAMENTE una lista de objetos con estos campos:
[{{
    "code": "Código o número de la cuenta (ej. 101, 101.01)",
    "name": "Nombre oficial de la cuenta",
    "level": "Un número entero (1 para agrupador principal, 2 para subcuenta, etc.)",
    "nature": "Naturaleza de la cuenta (Debit o Credit)",
    "description": "Cualquier descripción o nota incluida (opcional, null si no hay)"
}}]

Texto a analizar:
---
{text_chunk}
---

Devuelve SÓLO la lista JSON en texto plano.
"""

def extract_accounts(country: str, source_path: str, output_path: str):
    print(f"Iniciando extracción para país: {country.upper()}")
    print(f"Leyendo fuente: {source_path}")
    
    try:
        with open(source_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"Error leyendo archivo fuente: {e}")
        return
        
    # En un escenario real con archivos inmensos, dividiríamos `content` en chunks.
    # Por ahora, asumimos que el router puede manejar un archivo razonable o un chunk grande.
    prompt = get_extraction_prompt(country, content)
    
    print("Enviando petición a la IA (esto puede tardar unos segundos dependiendo del tamaño)...")
    try:
        # Usamos priority="volume" (para Cerebras) o priority="speed" para Groq/Gemini.
        # extraction task type
        result = router.complete(
            prompt=prompt,
            task_type="extraction",
            priority="quality",  # Queremos JSON bien formateado
            max_tokens=8000
        )
        
        raw_output = result["content"].strip()
        # Limpiar si el modelo devuelve backticks
        if raw_output.startswith("```json"):
            raw_output = raw_output[7:]
        if raw_output.startswith("```"):
            raw_output = raw_output[3:]
        if raw_output.endswith("```"):
            raw_output = raw_output[:-3]
        
        raw_output = raw_output.strip()
        
        # Validar JSON
        parsed_json = json.loads(raw_output)
        print(f"¡Éxito! Se extrajeron {len(parsed_json)} cuentas.")
        
        # Guardar resultados
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(parsed_json, f, indent=2, ensure_ascii=False)
            
        print(f"Resultados guardados en: {output_path}")
        print(f"Estadísticas IA: Proveedor: {result['provider']}, Tokens: {result['tokens_used']}, Latencia: {result['latency']:.2f}s")
        
    except json.JSONDecodeError as e:
        print("La respuesta de la IA no fue un JSON válido.")
        print(f"Error: {e}")
        print("Respuesta cruda:")
        print(raw_output)
    except Exception as e:
        print(f"Error en el proceso de extracción: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extraer catálogos de cuentas de países.")
    parser.add_argument("--country", required=True, choices=["mx", "co", "pa"], help="Código del país (ej. mx)")
    parser.add_argument("--source", required=True, help="Ruta al archivo de texto o CSV fuente")
    parser.add_argument("--output", help="Ruta de salida (por defecto: research/standards/{country}/extracted_accounts.json)")
    
    args = parser.parse_args()
    
    output_path = args.output
    if not output_path:
        output_path = f"research/standards/{args.country}/extracted_accounts.json"
        
    extract_accounts(args.country, args.source, output_path)
