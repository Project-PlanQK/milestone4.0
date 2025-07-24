import json
import pandas as pd
import os
from llama_index.llms.openai import OpenAI
from dotenv import load_dotenv
from llama_index.core.evaluation import (
    CorrectnessEvaluator,
    FaithfulnessEvaluator,
)
# Lade die .env-Datei
load_dotenv()

openai_api_key = os.getenv("OPENAI_API_KEY")
eval_model = "gpt-4o"  # or your chosen model

llm = OpenAI(
    api_key=openai_api_key,
    model=eval_model,
)

# Initialize evaluators for each metric
evaluator = CorrectnessEvaluator(llm=llm)
#faithfulness_evaluator = FaithfulnessEvaluator(llm=llm)

with open("V2_RAG_Eval_with_responses.json", "r", encoding="utf-8") as f:
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

df = pd.DataFrame(results)
df.to_csv("evaluation_results.csv", index=False)
print("Evaluation finished and saved as evaluation_results.csv")
