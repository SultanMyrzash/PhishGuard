import os
from email.message import EmailMessage

def create_eml(filename, subject, sender, to, body):
    msg = EmailMessage()
    msg.set_content(body)
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = to
    
    with open(filename, 'wb') as f:
        f.write(msg.as_bytes())
    print(f"Created: {filename}")

# 1. OBVIOUS PHISHING (The Nigerian Prince / Lottery Style)
body_phish = """
URGENT ATTENTION BENEFICIARY,

We have identified an unclaimed sum of $5,500,000.00 USD in your name deposited by the United Nations Compensation Commission. 

To claim your fund, you must reply immediately with your Full Name, Bank Account, and Phone Number. 

If you do not reply within 24 hours, the funds will be cancelled.

Sincerely,
Mr. John Smith
Central Bank Director
"""
create_eml("sample1_obvious_phish.eml", "URGENT: FINAL NOTIFICATION OF FUNDS", "director@central-bank-office-link.net", "victim@gmail.com", body_phish)

# 2. SPEAR PHISHING (CEO Fraud / Business Email Compromise)
# This is harder to detect. It uses authority and fear.
body_spear = """
Hi,

I am in a meeting right now and can't talk, but I need you to process a wire transfer for a new vendor immediately. It must go out before the cut-off time (1 hour from now).

I have attached the invoice details. Please process this to the account ending in 9921. 

Do not delay, this is for a priority client.

Thanks,
Elon Musk
CEO
"""
create_eml("sample2_ceo_fraud.eml", "Urgent Wire Transfer Request", "e.musk@tesIa-motors.co", "finance@tesla.com", body_spear)
# Note: The domain tesIa-motors.co has a capital 'i' instead of 'l' and wrong domain.

# 3. LEGITIMATE EMAIL (Safe)
body_safe = """
Hi Team,

Just a reminder that the weekly standup meeting is rescheduled to Friday at 10:00 AM.
Please make sure to update your Jira tickets before then.

See you there,
Sarah
"""
create_eml("sample3_safe_email.eml", "Meeting Reschedule", "sarah@company.com", "team@company.com", body_safe)