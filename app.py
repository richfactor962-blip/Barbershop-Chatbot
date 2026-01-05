import os
from flask import Flask, request, jsonify, render_template_string
from openai import OpenAI

app = Flask(__name__)

# Use the API key from Render environment variables
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

SYSTEM_PROMPT = """
You are a helpful assistant for a barbershop.
Answer questions about services, prices, hours, location, walk-ins, and booking.
If asked something outside that scope, say you can help with hours, prices, or booking.
Be friendly and concise.
"""

HTML = """
<!doctype html>
<html>
<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width,initial-scale=1"/>
  <title>Barbershop AI</title>
  <style>
    body { font-family: system-ui, Arial; margin: 20px; }
    #chat { border: 1px solid #ddd; padding: 12px; border-radius: 10px; height: 55vh; overflow: auto; }
    .msg { margin: 8px 0; }
    .me { font-weight: 600; }
    .bot { font-weight: 600; }
    form { display: flex; gap: 8px; margin-top: 10px; }
    input { flex: 1; padding: 10px; border-radius: 10px; border: 1px solid #ccc; }
    button { padding: 10px 14px; border-radius: 10px; border: 1px solid #ccc; }
  </style>
</head>
<body>
  <h2>Barbershop AI (Demo)</h2>
  <div id="chat"></div>
  <form id="f">
    <input id="t" placeholder="Ask about hours, prices, booking..." autocomplete="off"/>
    <button type="submit">Send</button>
  </form>

<script>
const chat = document.getElementById("chat");
const f = document.getElementById("f");
const t = document.getElementById("t");

function add(who, text){
  const d = document.createElement("div");
  d.className = "msg";
  d.innerHTML = `<span class="${who}">${who==="me"?"You":"Bot"}:</span> ${text}`;
  chat.appendChild(d);
  chat.scrollTop = chat.scrollHeight;
}

f.addEventListener("submit", async (e)=>{
  e.preventDefault();
  const text = t.value.trim();
  if(!text) return;
  t.value = "";
  add("me", text);
  add("bot", "<em>typing…</em>");
  const typing = chat.lastChild;

  const r = await fetch("/chat", {
    method: "POST",
    headers: {"Content-Type":"application/json"},
    body: JSON.stringify({text})
  });

  typing.remove();
  if(!r.ok){ add("bot","Error. Try again."); return; }
  const data = await r.json();
  add("bot", data.reply);
});

add("bot","Hi! Ask me about hours, prices, services, walk-ins, or booking.");
</script>
</body>
</html>
"""

@app.get("/")
def home():
    return render_template_string(HTML)

@app.post("/chat")
def chat():
    user_text = (request.json or {}).get("text","").strip()
    if not user_text:
        return jsonify({"reply":"Ask me about hours, prices, or booking."})

    resp = client.responses.create(
        model="gpt-4.1-mini",
        input=[
            {"role":"system","content": SYSTEM_PROMPT},
            {"role":"user","content": user_text}
        ]
    )
    return jsonify({"reply": resp.output_text})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 3000)))
