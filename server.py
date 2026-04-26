from anthropic import Anthropic
from dotenv import load_dotenv
import os
import json
from http.server import HTTPServer, BaseHTTPRequestHandler

load_dotenv()
client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

SYSTEM_PROMPT = """Tu "HR Saathi" hai — TechCorp India ka intelligent HR assistant chatbot.

COMPANY POLICIES:
Leave:
- Casual Leave (CL): 12 days/year
- Sick Leave (SL): 12 days/year
- Earned Leave (EL): 15 days/year
- Maternity Leave: 26 weeks (paid)
- Paternity Leave: 15 days (paid)
- Marriage Leave: 5 days (once in service)
- Bereavement Leave: 3 days (immediate family)
- Leave encashment: EL only, max 30 days/year
- Leave carry forward: EL max 45 days, CL/SL lapse yearly

Attendance:
- Office hours: 9:30 AM - 6:30 PM (Mon-Fri)
- Late coming: 3 times/month allowed, 4th = half day
- WFH: max 2 days/week, manager approval required
- WFH NOT allowed during probation period

Salary & Benefits:
- Salary credit: 1st of every month
- Salary slip: HR portal by 28th
- PF: 12% employee + 12% employer
- Medical insurance: 5 lakh family floater
- Training budget: Rs 15,000/year

Career:
- Probation: 6 months
- Notice period: 0-2 yrs = 1 month, 2+ yrs = 2 months
- Full & Final: 45 days after last working day

Grievance:
- Confidential: hr.grievance@techcorp.in
- Anonymous: feedback.techcorp.in
- Portal: portal.techcorp.in

RULES:
- Hinglish mein reply karo
- Emojis use karo
- Short clear replies do
- Har reply ke end mein follow-up poochho
- Sensitive topics pe empathy dikhao"""


class Handler(BaseHTTPRequestHandler):

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_GET(self):
        # Health check — Render ke liye zaroori
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps({"status": "HR Saathi server chal raha hai!"}).encode())

    def do_POST(self):
        if self.path == '/chat':
            try:
                length = int(self.headers['Content-Length'])
                body = json.loads(self.rfile.read(length))

                response = client.messages.create(
                    model="claude-sonnet-4-6",
                    max_tokens=800,
                    system=SYSTEM_PROMPT,
                    messages=body['messages']
                )

                reply = response.content[0].text

                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({"reply": reply}).encode())

            except Exception as e:
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode())

    def log_message(self, format, *args):
        print(f"→ {args[0]}")


# Render ka PORT env variable use karta hai
port = int(os.environ.get("PORT", 8000))
print(f"Server chal raha hai port {port} pe")
HTTPServer(('0.0.0.0', port), Handler).serve_forever()