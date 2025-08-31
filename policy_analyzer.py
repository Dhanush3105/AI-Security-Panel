# If running locally or in Colab, uncomment these lines:
!pip install googletrans==4.0.0-rc1 spacy requests beautifulsoup4 textblob
!python -m spacy download en_core_web_sm
!python -m textblob.download_corpora

import spacy
import requests
from bs4 import BeautifulSoup
from textblob import TextBlob
import os
from googletrans import Translator

nlp_spacy = spacy.load("en_core_web_sm")
translator = Translator()

# Define risky patterns in various categories
security_risk_phrases = {
    "Data Sharing & Selling": [
        "share your data", "sell your data", "third-party partners", "affiliates may access",
        "data brokers", "marketing partners"
    ],
    "Weak User Control": [
        "consent automatically", "opt-out required", "mandatory consent", "you agree by default",
        "without your knowledge"
    ],
    "Policy Changes": [
        "subject to change", "may update at any time", "without prior notice"
    ],
    "Liability Disclaimers": [
        "we are not responsible", "we disclaim all liability", "use at your own risk"
    ],
    "Surveillance & Tracking": [
        "track your behavior", "collect location data", "monitor your activity",
        "session recording", "key logging"
    ],
    "Account & Access Risks": [
        "you are responsible for safeguarding", "we may disable your account without notice"
    ],
    "Retention & Deletion": [
        "retain your information", "data may be stored indefinitely", "we may keep your data"
    ],
    "International Data Transfer": [
        "transfer your data internationally", "outside your jurisdiction"
    ]
}

def translate_to_indian_langs(text: str) -> dict:
    targets = {"te": "Telugu", "hi": "Hindi", "ta": "Tamil"}
    out = {}
    for code, name in targets.items():
        try:
            translated = translator.translate(text, src="en", dest=code).text
            out[code] = translated
        except Exception as e:
            out[code] = f"⚠️ translation failed: {e}"
    return out

def fetch_policy_text(url):
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        paragraphs = soup.find_all('p')
        text = ' '.join([p.get_text() for p in paragraphs])
        return text
    except Exception as e:
        print(f"Error fetching page: {e}")
        return ""

def simplify_sentence(sentence):
    doc = nlp_spacy(sentence)
    simplified = []
    for token in doc:
        if token.dep_ in ('nsubj', 'dobj', 'ROOT', 'pobj', 'attr', 'nmod'):
            simplified.append(token.text)
    return ' '.join(simplified)

def detect_security_issues(sentence_text):
    lower_text = sentence_text.lower()
    issues_found = []
    for category, phrases in security_risk_phrases.items():
        for phrase in phrases:
            if phrase in lower_text:
                issues_found.append((category, phrase))
    return issues_found

def analyze_text_sentiment(text):
    blob = TextBlob(text)
    sentences = blob.sentences
    flagged_sentences = []
    dark_pattern_reported = False

    for sentence in sentences:
        issues = detect_security_issues(sentence.raw)
        if issues:
            simplified = simplify_sentence(sentence.raw)
            flagged_sentences.append({
                "original": sentence.raw.strip(),
                "simplified": simplified,
                "issues": issues
            })
            dark_pattern_reported = True

    return flagged_sentences, dark_pattern_reported

def main():
    url = input("🔗 Enter the URL of the Privacy Policy or Terms & Conditions page: ").strip()
    print("\n⏳ Fetching and analyzing...")
    text = fetch_policy_text(url)

    if not text:
        print("❌ Failed to fetch the webpage.")
        return

    flagged_sentences, dark_flag = analyze_text_sentiment(text)

    if flagged_sentences:
        print("\n⚡ SECURITY RISKS / DARK PATTERNS DETECTED:")
        for item in flagged_sentences:
            print(f"\n🔸 Sentence: {item['original']}")
            print(f"   ➤ Simplified: {item['simplified']}")
            print("   🚨 Issues:")
            for cat, phrase in item['issues']:
                print(f"      • {phrase} ({cat})")

            translations = translate_to_indian_langs(item["simplified"])
            print("   🌐 Translations:")
            for lang_code, translated in translations.items():
                print(f"      {lang_code.upper()}: {translated}")
    else:
        print("\n✅ No risky or dark pattern content detected. Document appears user-friendly.")

    if dark_flag:
        print("\n🚨 WARNING: Security-related issues detected! 🚨")
    else:
        print("\n✅ No major risks detected.")

if __name__ == "__main__":
    main()
