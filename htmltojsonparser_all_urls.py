import requests
from bs4 import BeautifulSoup
import json
import os

def fetch_webpage(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.text
    except Exception as e:
        print(f"Fehler beim Abrufen von {url}: {e}")
        return None

def extract_text(html):
    soup = BeautifulSoup(html, "html.parser")

    # Entferne Skripte und Styles
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()

    title = soup.title.string.strip() if soup.title else "No Title"
    body = soup.get_text(separator="\n")

    # Aufräumen
    clean_text = "\n".join([line.strip() for line in body.splitlines() if line.strip()])

    return {
        "title": title,
        "content": clean_text
    }

def save_as_json(data, url, output_folder="output"):
    os.makedirs(output_folder, exist_ok=True)
    filename = url.replace("https://", "").replace("http://", "").replace("/", "_")
    filepath = os.path.join(output_folder, f"{filename}.json")

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"✔️  Gespeichert: {filepath}")

def process_url(url):
    html = fetch_webpage(url)
    if html:
        extracted = extract_text(html)
        extracted["url"] = url
        save_as_json(extracted, url)

if __name__ == "__main__":
    # Beispiel-URLs
    urls = [
        "https://docs.planqk.de/quickstart.html",
        "https://platform.planqk.de/quantum-backends",
        "https://docs.planqk.de/sdk-reference.html",
        "https://docs.planqk.de/sdk-reference-service.html",
        "https://docs.planqk.de/cli-reference.html",
        "https://docs.planqk.de/planqk-json-reference.html",
        "https://docs.planqk.de/manage-organizations.html",
        "https://docs.planqk.de/manage-access-tokens.html",
        "https://docs.planqk.de/manage-quantum-jobs.html",
        "https://docs.planqk.de/implementations/introduction.html",
        "https://docs.planqk.de/implementations/getting-started.html",
        "https://docs.planqk.de/implementations/settings.html",
        "https://docs.planqk.de/implementations/create-a-service.html",
        "https://docs.planqk.de/services/managed/introduction.html",
        "https://docs.planqk.de/services/managed/service-configuration.html",
        "https://docs.planqk.de/services/managed/openapi.html",
        "https://docs.planqk.de/services/managed/jobs.html",
        "https://docs.planqk.de/services/managed/custom-containers.html",
        "https://docs.planqk.de/services/managed/runtime-interface.html",
        "https://docs.planqk.de/services/applications.html",
        "https://docs.planqk.de/services/using-a-service.html",
        "https://docs.planqk.de/services/orchestration/introduction.html",
        "https://docs.planqk.de/services/orchestration/workflow-editor.html",
        "https://docs.planqk.de/services/orchestration/example.html",
        "https://docs.planqk.de/services/on-premise/introduction.html",
        "https://docs.planqk.de/services/on-premise/publish-marketplace.html",
        "https://docs.planqk.de/services/on-premise/report-usage.html",
        "https://docs.planqk.de/demos/introduction.html",
        "https://docs.planqk.de/demos/deploy-demo.html",
        "https://docs.planqk.de/demos/environment-variables.html",
        "https://docs.planqk.de/demos/starter-templates.html",
        "https://docs.planqk.de/automation/introduction.html",
        "https://docs.planqk.de/automation/github.html",
        "https://docs.planqk.de/automation/gitlab.html",
        "https://docs.planqk.de/tutorials/tutorial-qiskit-with-planqk-sdk.html",
        "https://docs.planqk.de/tutorials/tutorial-quera-mis.html",
        "https://docs.planqk.de/tutorials/tutorial-local-development.html",
        "https://docs.planqk.de/tutorials/tutorial-meter-on-premise-service.html",
        "https://docs.planqk.de/tutorials/tutorial-dwave.html",
        "https://docs.planqk.de/tutorials/tutorial-ibmq.html",
        "https://docs.planqk.de/tutorials/tutorial-qiskit-runtime.html",
        "https://docs.planqk.de/community/overview.html",
        "https://docs.planqk.de/community/algorithms.html",
        "https://docs.planqk.de/community/data-pools.html",
        "https://docs.planqk.de/community/use-cases.html",
        "https://docs.planqk.de/community/markdown-latex-editor.html",
        "https://docs.planqk.de/community/manage-permissions.html",
        "https://docs.planqk.de/community/publish-content.html",
        "https://docs.planqk.de/community/reviews.html",
        "https://platform.planqk.de/use-cases/bd58ec9f-42ef-4ec7-bd79-86afb85dad97",
        "https://platform.planqk.de/use-cases/9a61aa06-fb8e-4a81-b4eb-e9a54b3e2942",
        "https://platform.planqk.de/use-cases/bd6dfe4d-e4fe-4b44-abd6-2906e58898b8",
        "https://platform.planqk.de/use-cases/7e67a4db-346b-4ab3-9089-0986d36b139d",
        "https://platform.planqk.de/use-cases/07983663-ba5e-4d6b-a4c7-245d3028f121",
        "https://platform.planqk.de/use-cases/cf2281b8-d876-48dd-a103-3b9e9ae11a30",
        "https://platform.planqk.de/use-cases/4635a292-e3c5-4eb5-8939-690326926045",
        "https://platform.planqk.de/use-cases/c0b49ee1-a7e6-419f-a8f3-1fa63d4c2661",
        "https://platform.planqk.de/use-cases/03afca02-9508-4540-ade2-cffbb681e2d8",
        "https://platform.planqk.de/use-cases/bbbd9ae6-7ca9-4285-8b9c-07b9b3465986",
        "https://platform.planqk.de/use-cases/c7314f95-d2f2-4350-9917-0ca6092d8015",
        "https://platform.planqk.de/use-cases/d505a1b5-c5b1-4829-8864-7d46fddd20dd",
        "https://platform.planqk.de/use-cases/bc6305ae-2579-429f-8d4e-11a2b94d1090",
        "https://platform.planqk.de/use-cases/6f627eb8-2e5f-4a39-81af-22c3ecb383a6",
        "https://platform.planqk.de/use-cases/d9a4557d-9cef-4160-a891-9f5c34452788",
        "https://platform.planqk.de/use-cases/13bef5ce-9ca1-4fa1-abe0-7522be1df898",
        "https://platform.planqk.de/use-cases/ac7e5fc5-d166-4473-b1b5-7741ac10b262",
        "https://platform.planqk.de/use-cases/e8664221-933b-4410-9880-80a6900c9f86",
        "https://platform.planqk.de/use-cases/f7abf3a7-9e89-4d27-ab41-456b085fb688",
        "https://platform.planqk.de/use-cases/10494d54-27fe-43e8-99ed-44a44eaead09",
        "https://platform.planqk.de/use-cases/11d21900-69d1-4668-9f67-f0f4309d95c6",
        "https://platform.planqk.de/use-cases/a2ba1c58-d0c7-4808-ac65-a388150b9da0",
        "https://platform.planqk.de/use-cases/cb8fe568-2dcc-4273-9dbc-54b59a1533a2",
        "https://platform.planqk.de/use-cases/6636e69b-097e-40aa-b8d6-6be67d11f62c",
        "https://platform.planqk.de/use-cases/39a14ff7-e2d9-4006-8693-92d164ed9499",
        "https://platform.planqk.de/use-cases/7dcb9984-8ee4-4238-a3e9-a5576693620d",
        "https://platform.planqk.de/use-cases/8d276a89-508a-42c5-a365-ad98ae351bee",
        "https://platform.planqk.de/use-cases/2558e21a-2504-4664-bce3-5f428ef3ecbb",
        "https://platform.planqk.de/use-cases/b37702a6-59ae-44a7-8639-d525cb916dc1",
        "https://platform.planqk.de/use-cases/9fdd35c1-0831-4aa0-b703-821906fcdc2d",
        "https://platform.planqk.de/algorithms/df1244fa-7317-499f-b5d7-3ea70fabbb5f/details",
        "https://platform.planqk.de/algorithms/1e9cce06-44e0-4096-9fbc-957caef9397d/details",
        "https://platform.planqk.de/algorithms/47de067a-d6dc-4ec1-8d8d-4dd2e3b69a23/details",
        "https://platform.planqk.de/algorithms/533c90a5-5fbb-487b-b64d-a8f331aafb10/details",
        "https://platform.planqk.de/algorithms/061f4eb3-d9ee-4f47-befc-9e242bf801ce/details",
        "https://platform.planqk.de/algorithms/86dfd279-db46-4adb-84a7-39bcf1d19d3a/details",
        "https://platform.planqk.de/algorithms/8c6909bd-a258-4702-8356-6ef28321a826/details",
        "https://platform.planqk.de/algorithms/2803f6d4-094e-4aa9-b09d-5847fba03d21/details",
        "https://platform.planqk.de/algorithms/6a564413-4d26-4f5e-a27e-7fdfdb717ad3/details",
        "https://platform.planqk.de/algorithms/786e1ff5-991e-428d-a538-b8b99bc3d175/details",
        "https://platform.planqk.de/algorithms/134cc03c-78d8-4dc1-8204-8ecd1d512ae2/details",
        "https://platform.planqk.de/algorithms/0913a1b9-2562-4b59-ab44-80d59c21a485/details",
        "https://platform.planqk.de/algorithms/fae60bca-d2b6-4aa2-88b7-58caace34179/details",
        "https://platform.planqk.de/algorithms/efc367a5-cc55-438a-995d-9bc6eca63e5e/details",
        "https://platform.planqk.de/algorithms/ae9bac80-672e-432a-983f-a3a7e1a8c92c/details",
        "https://platform.planqk.de/algorithms/9d445a80-6707-4a42-9689-4119c47b7120/details",
        "https://platform.planqk.de/algorithms/e16cc8da-a1c6-4598-b4a2-b1de0061465c/details",
        "https://platform.planqk.de/algorithms/c83040fe-e0a7-42d4-be3c-77e223bfdaeb/details",
        "https://platform.planqk.de/algorithms/b7cbaba1-7fcb-470f-9fd9-45b0972fe10b/details",
        "https://platform.planqk.de/algorithms/ba4c50e3-7429-4471-a250-1762ed4c556a/details",
        "https://platform.planqk.de/algorithms/ac112515-beed-4ec5-9ac7-59e0d8687ecc/details",
        "https://platform.planqk.de/algorithms/0d3ff433-0b08-44e8-97fc-2860c27d351d/details",
        "https://platform.planqk.de/algorithms/f090e078-7804-4e78-b289-b60d7b8ad060/details",
        "https://platform.planqk.de/algorithms/ae45bff7-8f5b-43f8-a39c-1b6e004d8ecd/details",
        "https://platform.planqk.de/algorithms/634a4a5e-b33c-4838-af28-1cf39170be29/details",
        "https://platform.planqk.de/algorithms/fadafc8b-5388-4768-8804-5fc22cf04a20/details",
        "https://platform.planqk.de/algorithms/4ab6ed1f-9f5e-4caf-b0b2-59d1444340d1/details",
        "https://platform.planqk.de/algorithms/31283a02-1d55-4ef8-bccf-3e418ed7ed0d/details",
        "https://platform.planqk.de/algorithms/00ae76fd-e6bf-4e47-93e9-c2f438040add/details",
        "https://platform.planqk.de/algorithms/28fbfa6b-329b-4d99-8c75-f9dbdd365a4f/details"

    ]

    anzahl_url = len(urls)

    for url in urls:
        process_url(url)
