import sentry_sdk
import os
from dotenv import load_dotenv

# Load from b/.env
load_dotenv("b/.env")
dsn = os.getenv("SENTRY_DSN")
print(f"Testing DSN: {dsn}")

if not dsn:
    print("❌ SENTRY_DSN not found in b/.env")
    exit(1)

try:
    sentry_sdk.init(
        dsn=dsn,
        traces_sample_rate=1.0,
        debug=True 
    )
    print("🚀 Sentry initialized. Sending message...")
    event_id = sentry_sdk.capture_message("Hello from Antigravity direct test!")
    if event_id:
        print(f"✅ Event sent! ID: {event_id}")
    else:
        print("❌ Event not sent (event_id is None)")
    
    sentry_sdk.flush()
    print("Done.")
except Exception as e:
    print(f"❌ Error: {e}")
