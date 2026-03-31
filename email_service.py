"""
email_service.py — AI Interview System
========================================
Handles sending interview result emails via Gmail SMTP.

SETUP INSTRUCTIONS (ONE-TIME):
────────────────────────────────
1. Open this file and fill in SENDER_EMAIL and SENDER_PASSWORD below.
2. SENDER_EMAIL  → Your Gmail address  (e.g. yourname@gmail.com)
3. SENDER_PASSWORD → Your Gmail App Password (NOT your normal Gmail password)

HOW TO GET A GMAIL APP PASSWORD:
  a) Go to: https://myaccount.google.com/security
  b) Enable "2-Step Verification" if not already on
  c) Search for "App Passwords" in the Google Account search bar
  d) Create a new app → select "Mail" + "Windows Computer"
  e) Copy the 16-character password (no spaces) and paste below
────────────────────────────────
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# ─────────────────────────────────────────────────────────────
# ✅ CONFIGURE YOUR CREDENTIALS HERE
SENDER_EMAIL    = "YOUR_EMAIL@gmail.com"    # ← Replace with your Gmail
SENDER_PASSWORD = "YOUR_APP_PASSWORD"       # ← Replace with 16-char App Password
# ─────────────────────────────────────────────────────────────


def send_results_email(receiver_email: str, username: str,
                       score: int, feedback: str,
                       transcript: str = "", job_role: str = "General") -> bool:
    """
    Sends a richly formatted HTML email with the candidate's interview results.

    Args:
        receiver_email : Recipient's email address
        username       : Candidate's name (for greeting)
        score          : Numeric score out of 100
        feedback       : Multi-line AI feedback string
        transcript     : Speech-to-text transcript of the interview
        job_role       : The role the candidate was interviewed for

    Returns:
        True if email sent successfully, False otherwise.
    """

    if not receiver_email:
        print("[EMAIL] WARNING: No receiver email - skipping.")
        return False

    # ── Score theming ──────────────────────────────────────────
    if score >= 70:
        score_color = "#22c55e"
        score_label = "Excellent 🌟"
        hero_gradient = "linear-gradient(135deg, #166534, #22c55e)"
    elif score >= 40:
        score_color = "#f59e0b"
        score_label = "Average 👍"
        hero_gradient = "linear-gradient(135deg, #92400e, #f59e0b)"
    else:
        score_color = "#ef4444"
        score_label = "Needs Improvement 📈"
        hero_gradient = "linear-gradient(135deg, #991b1b, #ef4444)"

    # ── Feedback bullets ───────────────────────────────────────
    feedback_lines = [l.strip() for l in feedback.split("\n") if l.strip()]
    feedback_html = "".join(
        f'<li style="padding: 6px 0; color: #cbd5e1; font-size: 15px; line-height: 1.5;">{line}</li>'
        for line in feedback_lines
    )

    # ── Transcript section (shown only if available) ───────────
    transcript_section = ""
    if transcript and transcript != "No meaningful speech detected.":
        transcript_section = f"""
        <div style="background: rgba(0,0,0,0.25); border-left: 4px solid #5D3FD3;
                    border-radius: 0 10px 10px 0; padding: 18px 20px; margin-bottom: 24px;">
          <p style="margin: 0 0 8px; font-size: 12px; color: #a78bfa; font-weight: 700;
                    text-transform: uppercase; letter-spacing: 1px;">📝 Speech Transcript</p>
          <p style="margin: 0; color: #94a3b8; font-size: 14px; line-height: 1.7;
                    font-style: italic;">"{transcript}"</p>
        </div>
        """

    # ── Full HTML email body ───────────────────────────────────
    html_body = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"></head>
    <body style="margin:0; padding:0; background-color:#0B1120; font-family: 'Segoe UI', Arial, sans-serif;">

      <div style="max-width: 620px; margin: 30px auto; background: #111827;
                  border-radius: 20px; overflow: hidden; border: 1px solid rgba(255,255,255,0.08);
                  box-shadow: 0 25px 60px rgba(0,0,0,0.5);">

        <!-- HEADER BANNER -->
        <div style="background: {hero_gradient}; padding: 36px 30px; text-align: center;">
          <p style="margin: 0 0 6px; font-size: 36px; line-height: 1;">🤖</p>
          <h1 style="margin: 0 0 6px; font-size: 24px; font-weight: 800; color: #ffffff;
                     letter-spacing: 0.5px;">AI Interview System</h1>
          <p style="margin: 0; color: rgba(255,255,255,0.8); font-size: 15px;">
            Your Interview Results Are Ready!
          </p>
        </div>

        <!-- BODY -->
        <div style="padding: 36px 32px;">

          <!-- Greeting -->
          <p style="font-size: 18px; color: #e2e8f0; margin: 0 0 6px;">
            Hello, <strong>{username}</strong> 👋
          </p>
          <p style="color: #64748b; font-size: 14px; margin: 0 0 28px; line-height: 1.6;">
            Your AI-powered interview for <strong style="color:#94a3b8;">
            {job_role}</strong> has been analyzed. Here's your full performance breakdown.
          </p>

          <!-- SCORE BOX -->
          <div style="background: rgba(255,255,255,0.04); border: 2px solid {score_color};
                      border-radius: 16px; padding: 28px; text-align: center; margin-bottom: 28px;">
            <p style="margin: 0 0 6px; font-size: 12px; color: #94a3b8;
                      text-transform: uppercase; letter-spacing: 2px; font-weight: 600;">
              Overall Score
            </p>
            <p style="margin: 8px 0; font-size: 60px; font-weight: 900; color: {score_color};
                      line-height: 1;">{score}
              <span style="font-size: 24px; color: #475569;">/100</span>
            </p>
            <span style="background: {score_color}22; color: {score_color}; padding: 5px 20px;
                         border-radius: 20px; font-size: 14px; font-weight: 700;
                         letter-spacing: 0.5px;">{score_label}</span>
          </div>

          <!-- TRANSCRIPT -->
          {transcript_section}

          <!-- AI FEEDBACK -->
          <div style="background: rgba(0,0,0,0.3); border-left: 4px solid #00E8FF;
                      border-radius: 0 12px 12px 0; padding: 20px 22px; margin-bottom: 28px;">
            <p style="margin: 0 0 12px; font-size: 12px; color: #00E8FF; font-weight: 700;
                      text-transform: uppercase; letter-spacing: 1.5px;">🎯 AI Performance Feedback</p>
            <ul style="margin: 0; padding-left: 18px; list-style: disc;">
              {feedback_html}
            </ul>
          </div>

          <!-- TIPS -->
          <div style="background: rgba(93,63,211,0.08); border: 1px solid rgba(93,63,211,0.25);
                      border-radius: 12px; padding: 18px 20px; margin-bottom: 10px;">
            <p style="margin: 0; color: #a78bfa; font-size: 14px; line-height: 1.7;">
              💡 <strong>Tip:</strong> Practice regularly and focus on the feedback points above.
              Every interview session brings you closer to your goal! 🚀
            </p>
          </div>
        </div>

        <!-- FOOTER -->
        <div style="background: rgba(0,0,0,0.3); padding: 20px 30px; text-align: center;
                    border-top: 1px solid rgba(255,255,255,0.06);">
          <p style="margin: 0; color: #334155; font-size: 12px; line-height: 1.8;">
            © 2026 AI Interview System &nbsp;|&nbsp; This is an automated email, please do not reply.<br>
            Role Attempted: <strong style="color:#475569;">{job_role}</strong>
          </p>
        </div>

      </div>
    </body>
    </html>
    """

    # ── Build MIME message ─────────────────────────────────────
    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"🎯 Your AI Interview Result — {score}/100 ({score_label})"
    msg["From"]    = f"AI Interview System <{SENDER_EMAIL}>"
    msg["To"]      = receiver_email
    msg.attach(MIMEText(html_body, "html"))

    # ── Send via Gmail SMTP ────────────────────────────────────
    if SENDER_EMAIL == "YOUR_EMAIL@gmail.com" or SENDER_PASSWORD == "YOUR_APP_PASSWORD":
        print("[EMAIL] DEMO MODE: Credentials not configured.")
        print(f"[EMAIL] Simulating email send to: {receiver_email}")
        print("--- Email Content Preview ---")
        print(f"To: {receiver_email}\nSubject: {msg['Subject']}\nBody: <HTML Content Generated>")
        print("---------------------------")
        return True

    try:
        print(f"[EMAIL] INFO: Sending result to: {receiver_email}")
        with smtplib.SMTP("smtp.gmail.com", 587, timeout=15) as server:
            server.ehlo()
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.sendmail(SENDER_EMAIL, receiver_email, msg.as_string())
        print(f"[EMAIL] SUCCESS: Successfully sent to {receiver_email}")
        return True

    except smtplib.SMTPAuthenticationError:
        print("[EMAIL] ERROR: Authentication failed.")
        print("[EMAIL]    -> Make sure SENDER_EMAIL and SENDER_PASSWORD are correct in email_service.py")
        print("[EMAIL]    -> Use a Gmail App Password, NOT your regular Gmail password.")
        return False

    except smtplib.SMTPException as e:
        print(f"[EMAIL] ERROR: SMTP error: {e}")
        return False

    except Exception as e:
        print(f"[EMAIL] ERROR: Unexpected error: {e}")
        return False
