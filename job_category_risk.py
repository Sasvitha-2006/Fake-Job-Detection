def job_category_risk(text):
    text = text.lower()

    high_risk = [
        "data entry", "part time", "work from home", "typing job",
        "online job", "captcha", "form filling"
    ]

    medium_risk = [
        "marketing", "sales", "telecalling", "customer support",
        "business development", "call center"
    ]

    low_risk = [
        "software", "developer", "engineer", "programmer",
        "analyst", "teacher", "nurse", "accountant",
        "designer", "researcher", "manager"
    ]

    detected_category = "Other / Unknown"
    risk_level = "Refer ML & Rule-based result"

    for word in high_risk:
        if word in text:
            detected_category = word
            risk_level = "HIGH"
            return detected_category, risk_level

    for word in medium_risk:
        if word in text:
            detected_category = word
            risk_level = "MEDIUM"
            return detected_category, risk_level

    for word in low_risk:
        if word in text:
            detected_category = word
            risk_level = "LOW"
            return detected_category, risk_level

    # If no category matched
    return detected_category, risk_level


if __name__ == "__main__":
    job_text = input("Enter job description:\n")

    category, risk = job_category_risk(job_text)

    print("\nDetected Job Category:", category)
    print("Category Risk Level:", risk)