async function sendMessage(){
  const input = document.getElementById('user-input');
  const name = document.getElementById('user-name').value || 'Guest';
  const email = document.getElementById('user-email').value || 'N/A';
  const text = input.value.trim();
  if(!text) return;
  addMessage(text,'user');
  input.value='';
  try{
    const res = await fetch('/ask', {
      method:'POST',
      headers:{'Content-Type':'application/json'},
      body: JSON.stringify({question: text, name: name, email: email})
    });
    const data = await res.json();
    addMessage(data.answer || 'No answer','bot');
    if(data.escalated){
      addMessage('Your request was escalated and logged.','bot');
    }
  }catch(e){
    addMessage('Error contacting server','bot');
  }
}
function addMessage(t,cls){
  const box = document.getElementById('chat-box');
  const d = document.createElement('div');
  d.className = 'message ' + cls;
  d.innerText = t;
  box.appendChild(d);
  box.scrollTop = box.scrollHeight;
}
document.getElementById('user-input').addEventListener('keypress', function(e){ if(e.key==='Enter') sendMessage(); });

// const escalationKeywords = [
//   "not satisfied",
//   "talk to human",
//   "human support",
//   "escalate"
// ];

// async function sendMessage(){
//   const input = document.getElementById('user-input');
//   const name = document.getElementById('user-name').value || 'Guest';
//   const email = document.getElementById('user-email').value || 'N/A';
//   const text = input.value.trim();
//   if(!text) return;

//   addMessage(text,'user');
//   input.value='';

//   // Check escalation
//   if (escalationKeywords.some(k => text.toLowerCase().includes(k))) {
//     document.getElementById("escalationModal").style.display = "flex";
//     return;
//   }

//   try{
//     const res = await fetch('/ask', {
//       method:'POST',
//       headers:{'Content-Type':'application/json'},
//       body: JSON.stringify({question: text, name: name, email: email})
//     });
//     const data = await res.json();
//     addMessage(data.answer || 'No answer','bot');
//     if(data.escalated){
//       addMessage('Your request was escalated and logged.','bot');
//     }
//   }catch(e){
//     addMessage('Error contacting server','bot');
//   }
// }

// function addMessage(t,cls){
//   const box = document.getElementById('chat-box');
//   const d = document.createElement('div');
//   d.className = 'message ' + cls;
//   d.innerText = t;
//   box.appendChild(d);
//   box.scrollTop = box.scrollHeight;
// }

// // Enter key listener
// document.getElementById('user-input').addEventListener('keypress', function(e){
//   if(e.key==='Enter') sendMessage();
// });

// // Modal handling
// document.getElementById("closeModal").onclick = function() {
//   document.getElementById("escalationModal").style.display = "none";
// };

// document.getElementById("escalationForm").addEventListener("submit", async (e) => {
//   e.preventDefault();
//   const name = document.getElementById("esc-name").value;
//   const email = document.getElementById("esc-email").value;
//   const question = document.getElementById("user-input").value || "Escalation request";

//   await fetch("/log_escalation", {
//     method: "POST",
//     headers: { "Content-Type": "application/json" },
//     body: JSON.stringify({ name, email, question })
//   });

//   alert("✅ Your request has been submitted. Our team will contact you.");
//   document.getElementById("escalationModal").style.display = "none";
// });
