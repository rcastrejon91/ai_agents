import os
import smtplib
from email.mime.text import MIMEText
import requests
from bs4 import BeautifulSoup
import openai

# Settings
SMTP_HOST = os.getenv("SMTP_HOST")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASS = os.getenv("SMTP_PASS")
EMAIL_TO = os.getenv("EMAIL_TO")
EMAIL_FROM = os.getenv("EMAIL_FROM")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

openai.api_key = OPENAI_API_KEY

# Step 1 — Fetch new info from the web
def gather_info():
    urls = [
        "https://www.bbc.com/news",
        "https://www.scientificamerican.com/",
        "https://techcrunch.com/"
    ]
    content = ""
    for url in urls:
        try:
            r = requests.get(url, timeout=10)
            soup = BeautifulSoup(r.text, "html.parser")
            text = " ".join([p.get_text() for p in soup.find_all("p")[:5]])
            content += f"\nFrom {url}:\n{text}\n"
        except Exception as e:
            content += f"\n[Error fetching {url}: {e}]\n"
    return content

# Step 2 — Summarize with OpenAI
def summarize_with_ai(text):
    prompt = f"Summarize the following info and suggest what Lyra should learn next:\n{text}"
    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[{"role": "system", "content": "You are Lyra, an AI assistant who emails daily learning updates."},
                  {"role": "user", "content": prompt}]
    )
    return response.choices[0].message["content"]

# Step 3 — Send email
def send_email(subject, body):
    msg = MIMEText(body, "plain", "utf-8")
    msg["Subject"] = subject
    msg["From"] = EMAIL_FROM
    msg["To"] = EMAIL_TO

    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
        server.starttls()
        server.login(SMTP_USER, SMTP_PASS)
        server.send_message(msg)

if __name__ == "__main__":
    info = gather_info()
    summary = summarize_with_ai(info)
    send_email("Lyra Daily Learning Update", summary)
    print("Email sent successfully.")
