import re

def check_company_credibility(text):
    text = text.lower()
    score = 0
    reasons = []

    # 1. Company structure or company-like words
    if re.search(r"\b(pvt\.?\s*ltd|private limited|ltd|limited|inc|llc|corp|company|solutions|technologies|systems)\b", text):
        score += 2
        reasons.append("Company name or structure detected")
    else:
        reasons.append("No clear company structure found")

    # 2. Website check
    if re.search(r"(www\.|http://|https://)", text):
        score += 2
        reasons.append("Website link found")
    else:
        reasons.append("No official website mentioned")

    # 3. Email check
    email_match = re.search(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", text)
    if email_match:
        email = email_match.group()
        if not ("gmail.com" in email or "yahoo.com" in email or "outlook.com" in email):
            score += 2
            reasons.append("Official company email found")
        else:
            score -= 1
            reasons.append("Free email provider used")
    else:
        reasons.append("No email contact provided")

    # 4. WhatsApp / Telegram
    if "whatsapp" in text or "telegram" in text:
        score -= 2
        reasons.append("Only messaging app contact used")

    # 5. Location
    if re.search(r"\b(chennai|bangalore|hyderabad|mumbai|delhi|pune|india)\b", text):
        score += 1
        reasons.append("Office location mentioned")
    else:
        reasons.append("No office location mentioned")

    # 6. Scam language penalty
    scam_phrases = ["no experience", "earn fast", "work from home", "urgent hiring", "registration fee", "pay fee"]
    for phrase in scam_phrases:
        if phrase in text:
            score -= 1
            reasons.append(f"Suspicious phrase detected: '{phrase}'")

    # Final credibility
    if score >= 4:
        credibility = "HIGH"
    elif score >= 2:
        credibility = "MEDIUM"
    else:
        credibility = "LOW"

    return credibility, score, reasons


if __name__ == "__main__":
    job_text = input("Enter job description:\n")
    credibility, score, reasons = check_company_credibility(job_text)

    print("\nCompany Credibility:", credibility)
    print("Credibility Score:", score)
    print("Reasons:")
    for r in reasons:
        print("-", r)