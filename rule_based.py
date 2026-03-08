# rule_based.py

scam_words = [
    # money related
    "pay fee", "registration fee", "processing fee", "deposit", "charges",
    "investment required", "upfront payment", "join fee",

    # urgency
    "urgent hiring", "immediate joining", "limited seats", "act fast",
    "hurry up", "apply now", "last chance",

    # no qualification
    "no experience", "no interview", "no qualification",
    "anyone can apply", "no skills required",

    # contact outside platform
    "whatsapp", "telegram", "direct message", "dm me",
    "call now", "contact immediately",

    # salary traps
    "earn fast", "quick money", "guaranteed income",
    "high income", "huge salary", "easy money",

    # remote work scams
    "work from home", "part time job", "online job",
    "home based job", "typing job",

    # pressure language
    "limited offer", "only today", "don’t miss",
    "apply immediately",

    # fake trust words
    "100% genuine", "trusted job", "safe job",
    "no risk", "assured job",

    # suspicious instructions
    "send otp", "share otp", "bank details",
    "aadhar", "pan card", "kyc",

    # suspicious roles
    "data entry", "form filling", "captcha work"
]

def rule_based_score(text):
    text = text.lower()
    score = 0
    found_words = []

    for word in scam_words:
        if word in text:
            score += 1
            found_words.append(word)

    return score, found_words


# Test the rule-based system
if __name__ == "__main__":
    sample_text = "Urgent hiring! No experience needed. Work from home and earn fast. Contact on WhatsApp and pay registration fee."
    score, words = rule_based_score(sample_text)

    print("Rule-based score:", score)
    print("Suspicious words found:", words)