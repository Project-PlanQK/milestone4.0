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
        "https://docs.planqk.de/implementations/create-a-service.html"
    ]

    for url in urls:
        process_url(url)