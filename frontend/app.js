// Dynamic API endpoint - works for both local development and Vercel deployment
const API = window.location.hostname === 'localhost' ? 
  "http://127.0.0.1:5000/api/chat" : 
  "/api/chat";
const chatEl = document.getElementById("chat");
const typingEl = document.getElementById("typing");
const inputEl = document.getElementById("userInput");
const sendBtn = document.getElementById("sendBtn");

// keep short history for LLM fallback
let history = [];

function addBubble(text, who="bot"){
  const div = document.createElement("div");
  div.className = "bubble " + (who === "user" ? "user" : "bot");
  div.textContent = text;
  chatEl.appendChild(div);
  chatEl.scrollTop = chatEl.scrollHeight;
}

function quickAsk(text){
  inputEl.value = text;
  sendMsg();
}

async function sendMsg(){
  const msg = (inputEl.value || "").trim();
  if(!msg) return;
  addBubble(msg, "user");
  inputEl.value = "";
  sendBtn.disabled = true;
  typingEl.style.display = "block";

  try {
    const res = await fetch(API, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: msg, history })
    });
    const data = await res.json();
    const answer = data.answer || "";
    addBubble(answer, "bot");

    // update history for next turn
    history.push({ role: "user", content: msg });
    history.push({ role: "assistant", content: answer });
  } catch (e) {
    addBubble("Sorry, I couldn't reach the server.", "bot");
  } finally {
    typingEl.style.display = "none";
    sendBtn.disabled = false;
    inputEl.focus();
  }
}
