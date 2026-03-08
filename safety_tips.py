def get_safety_tips(final_risk_score):
    tips = []

    if final_risk_score >= 70:
        tips.append("Do NOT pay any registration or processing fee.")
        tips.append("Do NOT share OTP, Aadhaar, PAN, or bank details.")
        tips.append("Verify the company website and official contact.")
        tips.append("Avoid jobs that ask you to contact only via WhatsApp or Telegram.")
        tips.append("Search the company name online before applying.")

    elif final_risk_score >= 40:
        tips.append("Verify the job details carefully before applying.")
        tips.append("Check the official company website.")
        tips.append("Avoid sharing personal information too early.")
        tips.append("Confirm the job offer through official HR channels.")

    else:
        tips.append("Job seems relatively safe, but always apply through official websites.")
        tips.append("Keep records of communication with recruiters.")
        tips.append("Do not share sensitive personal information unnecessarily.")

    return tips