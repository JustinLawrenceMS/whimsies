#!/usr/bin/env python3
import os
import ssl
import smtplib
import logging
import logging.handlers
import argparse

#!/usr/bin/env python3
import os
import ssl
import smtplib
import logging
import logging.handlers
import argparse
import time
import sys
import traceback
from email.message import EmailMessage

try:
		from dotenv import load_dotenv
		load_dotenv()
except Exception:
		pass

import schedule


PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_DIR = os.path.join(PROJECT_DIR, "logs")
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOG_DIR, "whimsy.log")

# Basic logging config: console + rotating file
logger = logging.getLogger()
logger.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s %(levelname)s [%(name)s] %(message)s")

ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
ch.setFormatter(formatter)
logger.addHandler(ch)

fh = logging.handlers.RotatingFileHandler(LOG_FILE, maxBytes=5 * 1024 * 1024, backupCount=3)
fh.setLevel(logging.INFO)
fh.setFormatter(formatter)
logger.addHandler(fh)

# Optional Sentry integration (set SENTRY_DSN env var to enable)
SENTRY_ENABLED = False
SENTRY_DSN = os.getenv("SENTRY_DSN")
if SENTRY_DSN:
		try:
				import sentry_sdk

				sentry_sdk.init(dsn=SENTRY_DSN)
				SENTRY_ENABLED = True
				logging.info("Sentry initialized")
		except Exception:
				logging.exception("Failed to initialize Sentry SDK; continuing without it")


def report_exception(exc: BaseException):
		"""Log and optionally report an exception to Sentry."""
		logging.exception("Unhandled exception: %s", exc)
		if SENTRY_ENABLED:
				try:
						sentry_sdk.capture_exception(exc)
				except Exception:
						logging.exception("Failed to send exception to Sentry")


def _excepthook(exc_type, exc_value, exc_tb):
		# Format traceback and log
		tb = ''.join(traceback.format_exception(exc_type, exc_value, exc_tb))
		logging.critical("Uncaught exception:\n%s", tb)
		try:
				if SENTRY_ENABLED:
						sentry_sdk.capture_exception(exc_value)
		except Exception:
				logging.exception("Failed to notify Sentry about uncaught exception")


sys.excepthook = _excepthook


def send_email():
		smtp_server = os.getenv("SMTP_SERVER")
		smtp_port = int(os.getenv("SMTP_PORT", "465"))
		smtp_username = os.getenv("SMTP_USERNAME")
		smtp_password = os.getenv("SMTP_PASSWORD")
		from_addr = os.getenv("FROM_EMAIL")
		to_addr = os.getenv("TO_EMAIL")

		if not all([smtp_server, smtp_port, smtp_username, smtp_password, from_addr, to_addr]):
				logging.error("Missing one or more required SMTP environment variables. See .env.example for names.")
				return

		to_name = os.getenv("TO_NAME", "Queen of Whimsies")
		subject = os.getenv("EMAIL_SUBJECT", f"A Morning Note for my {to_name}")

		default_plain = os.getenv("EMAIL_PLAIN" + "❤️❤️❤️❤️❤️❤️❤️❤️❤️❤️❤️❤️❤️❤️❤️", f"Good morning, {to_name} " + "❤️\n\n")

		# A prettier, mobile-friendly HTML template with inline CSS.
		default_html = f"""<!doctype html>
<html lang="en">
	<head>
		<meta charset="utf-8">
		<meta name="viewport" content="width=device-width,initial-scale=1" />
		<style>
			body {{ background:#f7f6fb; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial; margin:0; padding:0; }}
			.card {{ max-width:600px; margin:28px auto; background:#fff; border-radius:12px; box-shadow:0 6px 20px rgba(32,33,36,0.08); overflow:hidden; }}
			.hero {{ background:linear-gradient(135deg,#ff9a9e 0%,#fecfef 100%); padding:28px; text-align:center; color:#3b2a2a; }}
			h1 {{ margin:0; font-size:22px; }}
			.content {{ padding:24px; color:#333; line-height:1.5; }}
			.heart {{ color:#e74c3c; font-size:20px; margin:0 6px; }}
			.footer {{ padding:16px 24px; font-size:12px; color:#888; text-align:center; background:#fafafa; }}
			@media (max-width:420px) {{ .content {{ padding:16px; }} .hero {{ padding:20px; }} }}
		</style>
	</head>
	<body>
		<div class="card">
			<div class="hero">
				<h1>Good morning, {to_name} <span class="heart">❤️</span></h1>
			</div>
			<div class="content">
				<p>My dearest {to_name},</p>
				<p>Every morning I wake grateful for you. You are radiant, kind, and endlessly beautiful — inside and out.</p>
				<p><strong>I love you.</strong> Have a wonderful day filled with whimsy and joy.</p>
				<p>All my love,<br/>Yours forever</p>
			</div>
			<div class="footer">Sent with love • Whimsy</div>
		</div>
	</body>
</html>"""

		plain = os.getenv("EMAIL_PLAIN", default_plain)
		html = os.getenv("EMAIL_HTML", default_html)

		msg = EmailMessage()
		msg["Subject"] = subject
		msg["From"] = from_addr
		msg["To"] = to_addr
		msg.set_content(plain)
		msg.add_alternative(html, subtype="html")

		try:
				if smtp_port == 465:
						context = ssl.create_default_context()
						with smtplib.SMTP_SSL(smtp_server, smtp_port, context=context) as server:
								server.login(smtp_username, smtp_password)
								server.send_message(msg)
				else:
						# try STARTTLS
						with smtplib.SMTP(smtp_server, smtp_port) as server:
								server.ehlo()
								try:
										server.starttls(context=ssl.create_default_context())
										server.ehlo()
								except Exception:
										pass
								server.login(smtp_username, smtp_password)
								server.send_message(msg)
				logging.info("Email sent to %s", to_addr)
		except Exception as e:
				logging.exception("Failed to send email to %s: %s", to_addr, e)
				try:
						report_exception(e)
				except Exception:
						logging.exception("Error while reporting exception")


def schedule_daily(at_time="08:00"):
		schedule.clear()
		schedule.every().day.at(at_time).do(send_email)
		logging.info("Scheduled daily email at %s", at_time)
		try:
				while True:
						schedule.run_pending()
						time.sleep(30)
		except KeyboardInterrupt:
				logging.info("Scheduler stopped by user")


def main():
		parser = argparse.ArgumentParser(description="Send a daily loving email to your Queen of Whimsies")
		parser.add_argument("--send-now", action="store_true", help="Send the email immediately and exit")
		parser.add_argument("--run", action="store_true", help="Run scheduler to send every morning at 08:00 local time")
		parser.add_argument("--time", type=str, default="08:00", help="Time of day to send in HH:MM (24h) when using --run")
		args = parser.parse_args()

		if args.send_now:
				send_email()
				return

		if args.run:
				schedule_daily(at_time=args.time)
				return

		parser.print_help()


if __name__ == "__main__":
		main()
