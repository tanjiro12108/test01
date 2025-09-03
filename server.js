<script>
const input = document.getElementById('chatInput');
const btn = document.getElementById('sendBtn');
const messages = document.getElementById('messages');

function appendBubble(text, who='user'){
  const el = document.createElement('div');
  el.className = 'msg ' + (who==='user' ? 'user' : 'bot');
  el.innerHTML = (who==='bot' ? '<small>Knowlege Bot</small>' + text : text);
  messages.appendChild(el);
  messages.scrollTop = messages.scrollHeight;
}

btn.addEventListener('click', async () => {
  const userMessage = input.value.trim();
  if(!userMessage) return;

  appendBubble(userMessage, 'user');
  input.value = '';

  // Show "typing…" placeholder
  const thinking = document.createElement('div');
  thinking.className = 'msg bot';
  thinking.innerHTML = '<small>Knowlege Bot</small> ⌛ Thinking...';
  messages.appendChild(thinking);
  messages.scrollTop = messages.scrollHeight;

  // Fetch from OpenAI
  try {
    const res = await fetch("https://api.openai.com/v1/chat/completions", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": "Bearer YOUR_OPENAI_API_KEY"
      },
      body: JSON.stringify({
        model: "gpt-4o-mini",   // cheaper, faster model for hackathons
        messages: [
          { role: "system", content: "You are Knowlege Bot, a student assistant for Department of Technical Education, Rajasthan. Answer in simple, helpful language." },
          { role: "user", content: userMessage }
        ]
      })
    });
    const data = await res.json();
    const botReply = data.choices[0].message.content;

    thinking.remove();
    appendBubble(botReply, 'bot');
  } catch (err) {
    thinking.remove();
    appendBubble("⚠️ Error: " + err.message, 'bot');
  }
});

input.addEventListener('keydown', e => { if(e.key === 'Enter') btn.click(); });
</script>
