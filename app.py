from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup
from collections import Counter
import re

app = Flask(__name__)

def extract_keywords(text):
    stop_words = set([
        "the", "is", "at", "which", "on", "and", "a", "in", "to", "for", "of", "with", "by", "from"
    ])
    words = re.findall(r'\b[a-z]{3,}\b', text.lower())
    words = [word for word in words if word not in stop_words]
    return Counter(words).most_common(5)

@app.route("/extract_main_keyword", methods=["POST"])
def extract_main_keyword():
    data = request.json
    url = data.get("url")

    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')

        title = soup.title.string if soup.title else ""
        meta = soup.find("meta", attrs={"name": "description"})
        description = meta["content"] if meta else ""
        h1 = soup.find("h1")
        heading = h1.get_text() if h1 else ""

        combined = f"{title} {description} {heading}"
        keywords = extract_keywords(combined)

        return jsonify({
            "url": url,
            "extracted_keywords": keywords,
            "main_keyword": keywords[0][0] if keywords else None
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500
