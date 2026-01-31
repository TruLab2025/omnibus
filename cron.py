import json
import time
import os
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from parser import parse_price

# Try to load .env file if it exists (requires python-dotenv)
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

DATA_FILE = "tracked.json"

def send_alert(email, url, old_price, new_price, title="Produkt", image_url=None):
    """
    Sends a real email alert using SMTP with HTML styling.
    """
    smtp_host = os.getenv("SMTP_HOST")
    smtp_port = os.getenv("SMTP_PORT", "587")
    smtp_user = os.getenv("SMTP_USER")
    smtp_pass = os.getenv("SMTP_PASS")
    smtp_from = os.getenv("SMTP_FROM", f"Price Tracker <{smtp_user}>")

    print(f"\n--- 🔔 SENDING HTML ALERT EMAIL TO: {email} ---")
    
    if not all([smtp_host, smtp_user, smtp_pass]):
        print("⚠️  SMTP configuration missing! Set SMTP_HOST, SMTP_USER, and SMTP_PASS in .env")
        return

    savings = round(old_price - new_price, 2)
    subject = f"🔔 Kupuj! Cena spadła o {savings} PLN"
    img_tag = f'<img src="{image_url}" alt="Produkt" style="width: 150px; height: 150px; object-fit: contain; background: #fff; border-radius: 12px; padding: 5px;">' if image_url else ""

    # Plain text version (fallback)
    body_text = f"🔔 Kupuj! Cena produktu {title} spadła o {savings} PLN! Sprawdź ofertę: {url}"

    # HTML Version (styled like the app)
    body_html = f"""
    <html>
    <body style="margin: 0; padding: 0; font-family: 'Inter', Helvetica, Arial, sans-serif; background-color: #0f172a; color: #f8fafc;">
        <table align="center" border="0" cellpadding="0" cellspacing="0" width="100%" style="max-width: 600px; margin: 20px auto; background-color: #1e293b; border-radius: 24px; border: 1px solid #334155; overflow: hidden; border-collapse: separate;">
            <tr>
                <td style="padding: 40px; text-align: center;">
                    <h1 style="margin: 0 0 10px 0; font-size: 28px; font-weight: 700; color: #818cf8;">Kupuj! Cena spadła</h1>
                    <p style="margin: 0; color: #94a3b8; font-size: 16px;">Twój produkt właśnie staniał. Sprawdź szczegóły poniżej.</p>
                </td>
            </tr>
            <tr>
                <td style="padding: 0 40px 30px 40px;">
                    <table border="0" cellpadding="0" cellspacing="0" width="100%" style="background: rgba(15, 23, 42, 0.5); border: 1px solid #334155; border-radius: 16px; padding: 20px;">
                        <tr>
                            <td style="width: 160px; vertical-align: top;">
                                {img_tag}
                            </td>
                            <td style="padding-left: 20px; vertical-align: top;">
                                <h2 style="margin: 0 0 10px 0; font-size: 18px; font-weight: 700; color: #ffffff;">{title}</h2>
                                <div style="margin-bottom: 20px;">
                                    <div style="font-size: 12px; color: #94a3b8; margin-bottom: 5px;">Aktualna Cena</div>
                                    <div style="font-size: 24px; font-weight: 800; color: #22c55e;">{new_price} PLN</div>
                                    <div style="font-size: 14px; color: #94a3b8; text-decoration: line-through;">Było: {old_price} PLN</div>
                                </div>
                                <div style="display: inline-block; padding: 10px 15px; background: rgba(34, 197, 94, 0.1); border-radius: 8px; color: #22c55e; font-weight: 700; font-size: 14px;">
                                    Oszczędzasz: {savings} PLN
                                </div>
                            </td>
                        </tr>
                    </table>
                </td>
            </tr>
            <tr>
                <td style="padding: 0 40px 40px 40px; text-align: center;">
                    <a href="{url}" style="display: inline-block; padding: 16px 32px; background-color: #6366f1; color: #ffffff; text-decoration: none; border-radius: 12px; font-weight: 700; font-size: 16px;">Sprawdź ofertę w sklepie</a>
                </td>
            </tr>
            <tr>
                <td style="padding: 20px; background-color: #0f172a; text-align: center; color: #64748b; font-size: 12px;">
                    Wiadomość wysłana przez Omnibus PoC. Dziękujemy za korzystanie z naszej apki!
                </td>
            </tr>
        </table>
    </body>
    </html>
    """

    message = MIMEMultipart("alternative")
    message["From"] = smtp_from
    message["To"] = email
    message["Subject"] = subject
    
    message.attach(MIMEText(body_text, "plain"))
    message.attach(MIMEText(body_html, "html"))

    try:
        context = ssl.create_default_context()
        if smtp_port == "465":
            with smtplib.SMTP_SSL(smtp_host, int(smtp_port), context=context) as server:
                server.login(smtp_user, smtp_pass)
                server.sendmail(smtp_user, email, message.as_string())
        else:
            with smtplib.SMTP(smtp_host, int(smtp_port)) as server:
                server.starttls(context=context)
                server.login(smtp_user, smtp_pass)
                server.sendmail(smtp_user, email, message.as_string())
        
        print("✅ HTML Alert email sent successfully!")
    except Exception as e:
        print(f"❌ Failed to send email: {e}")

def run_cron():
    print(f"[{datetime.now()}] Starting price check...")
    
    try:
        with open(DATA_FILE, "r") as f:
            items = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        print("No items to check.")
        return

    updated_items = []
    
    for item in items:
        print(f"Checking: {item['url']}")
        result = parse_price(item['url'])
        
        if result:
            new_price = result["current_price"]
            last_known = item["last_known_price"]
            
            if new_price < last_known:
                send_alert(
                    item["email"], 
                    item["url"], 
                    last_known, 
                    new_price, 
                    title=result.get("title", "Produkt"),
                    image_url=result.get("image_url")
                )
                item["last_known_price"] = new_price
            
            item["last_checked"] = datetime.now().isoformat()
        
        updated_items.append(item)

    with open(DATA_FILE, "w") as f:
        json.dump(updated_items, f, indent=2)
    
    print(f"[{datetime.now()}] Price check completed.")

if __name__ == "__main__":
    run_cron()
