import json
import pandas as pd
from llama_index.llms.openai import OpenAI
from llama_index.core.evaluation import CorrectnessEvaluator
import os
from dotenv import load_dotenv


# Lade die .env-Datei
load_dotenv()

# === HIER DEINE DIREKTEN CREDENTIALS EINFÜGEN ===
openai_api_key = os.getenv("OPENAI_API_KEY")  # <-- OpenAI API-Key eintragen
eval_model = "gpt-4o"                       # oder "gpt-4", "gpt-3.5-turbo"

# GPT-Modell initialisieren
llm = OpenAI(
    api_key=openai_api_key,
    model=eval_model,
)

# Evaluator definieren (hier: Correctness)
evaluator = CorrectnessEvaluator(llm=llm)

# Deine Daten mit responses laden
with open("V1_RAG_Eval_with_responses.json", "r", encoding="utf-8") as f:
    data = json.load(f)["examples"]

results = []

for idx, ex in enumerate(data):
    query = ex["query"]
    response = ex.get("response", "")
    reference = ex.get("reference_answer", "")
    print(f"{idx+1}/{len(data)}: Evaluating...")
    try:
        eval_result = evaluator.evaluate(
            query=query,
            response=response,
            reference=reference
        )
    except Exception as e:
        print(f"Fehler bei Frage {idx+1}: {e}")
        eval_result = {"score": None, "reason": str(e)}

    results.append({
        "question": query,
        "response": response,
        "reference_answer": reference,
        "evaluation": eval_result
    })

# Ergebnisse als CSV speichern
df = pd.DataFrame(results)
df.to_csv("evaluation_results.csv", index=False)
print("Evaluation abgeschlossen und als evaluation_results.csv gespeichert.")

