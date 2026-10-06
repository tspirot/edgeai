/* ==========================================================================
   КВО ТЕ — ПИРОТСКИ AI МОЗАК (FRONTEND LOGIKA)
   ========================================================================== */

document.addEventListener("DOMContentLoaded", () => {
  // DOM елементи
  const chatForm = document.getElementById("chatForm");
  const userInput = document.getElementById("userInput");
  const aiResponseText = document.getElementById("aiResponseText");
  const lastQuestionBadge = document.getElementById("lastQuestionBadge");
  const chatFeed = document.getElementById("chatFeed");
  const avatarWrapper = document.querySelector(".avatar-wrapper");
  const btnToggleSound = document.getElementById("btnToggleSound");
  const lblSoundStatus = document.getElementById("lblSoundStatus");
  const btnReplayAudio = document.getElementById("btnReplayAudio");
  const btnCopyAnswer = document.getElementById("btnCopyAnswer");
  const btnClearChat = document.getElementById("btnClearChat");

  // Модал елементи
  const dictModal = document.getElementById("dictModal");
  const btnOpenDictionary = document.getElementById("btnOpenDictionary");
  const btnCloseModal = document.getElementById("btnCloseModal");
  const dictSearchInput = document.getElementById("dictSearchInput");
  const dictResults = document.getElementById("dictResults");
  const dictStats = document.getElementById("dictStats");
  const btnRandomInDict = document.getElementById("btnRandomInDict");

  // Стање апликације
  let soundEnabled = true;
  let isTyping = false;
  let currentAnswer = aiResponseText.textContent.trim();
  let typingTimer = null;
  let searchDebounceTimer = null;

  // Иницијализација синтезе говора (Web Speech API)
  const synth = window.speechSynthesis;
  let serbianVoice = null;

  function loadVoices() {
    if (!synth) return;
    const voices = synth.getVoices();
    // Потражи српски, хрватски, босански или fallback јужнословенски глас
    serbianVoice = voices.find(v => v.lang.startsWith("sr") || v.lang.startsWith("hr") || v.lang.startsWith("bs")) || null;
  }

  if (synth) {
    loadVoices();
    if (synth.onvoiceschanged !== undefined) {
      synth.onvoiceschanged = loadVoices;
    }
  }

  // Говор функција
  function speak(text) {
    if (!soundEnabled || !text) return;

    // Активирај визуелне таласе око аватара
    avatarWrapper.classList.add("speaking");

    // Прво покушај Web Speech API у прегледачу
    if (synth) {
      try {
        synth.cancel(); // Заустави претходни говор
        const clean = text.replace(/[\*\#\_\"\'•]/g, "");
        const utter = new SpeechSynthesisUtterance(clean);
        if (serbianVoice) {
          utter.voice = serbianVoice;
        }
        utter.rate = 0.95; // Мало спорији пиротски тон
        utter.pitch = 0.9;
        
        utter.onend = () => {
          avatarWrapper.classList.remove("speaking");
        };
        utter.onerror = () => {
          avatarWrapper.classList.remove("speaking");
        };

        synth.speak(utter);
        return;
      } catch (e) {
        console.warn("Web Speech API неуспешан, користим серверски SAPI...", e);
      }
    }

    // Fallback: Пошаљи захтев серверу да говори (Windows SAPI / Linux espeak)
    fetch("/api/govori", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ tekst: text })
    }).finally(() => {
      setTimeout(() => {
        avatarWrapper.classList.remove("speaking");
      }, 3000);
    });
  }

  // Ефекат куцаће машине (Typewriter)
  function typeWriter(text, element, callback) {
    if (typingTimer) clearInterval(typingTimer);
    isTyping = true;
    element.classList.add("typing");
    element.textContent = "";
    let i = 0;
    const speed = 20; // ms по слову

    typingTimer = setInterval(() => {
      if (i < text.length) {
        element.textContent += text.charAt(i);
        i++;
      } else {
        clearInterval(typingTimer);
        typingTimer = null;
        isTyping = false;
        element.classList.remove("typing");
        if (callback) callback();
      }
    }, speed);
  }

  // Додавање поруке у историју разговора
  function appendChatMessage(role, text) {
    const row = document.createElement("div");
    row.className = `msg-row msg-${role}`;

    const bubble = document.createElement("div");
    bubble.className = "msg-bubble";

    if (role === "ai") {
      const author = document.createElement("div");
      author.className = "msg-author";
      author.textContent = "🤖 Пироћанец:";
      bubble.appendChild(author);
    }

    const content = document.createElement("div");
    content.textContent = text;
    bubble.appendChild(content);

    row.appendChild(bubble);
    chatFeed.appendChild(row);
    chatFeed.scrollTop = chatFeed.scrollHeight;
  }

  // Слање питања AI мозгу
  async function askQuestion(questionText) {
    if (!questionText || !questionText.trim()) return;
    const q = questionText.trim();

    // Додај корисничко питање у историју
    appendChatMessage("user", q);
    lastQuestionBadge.innerHTML = `👉 <em>„${escapeHtml(q)}”</em>`;

    // Индикација да размишља
    aiResponseText.textContent = "Чекај мало да претумачим...";
    aiResponseText.classList.add("typing");

    try {
      const res = await fetch("/api/pitaj", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ pitanje: q })
      });

      if (!res.ok) throw new Error("Сервер није одговорио");
      const data = await res.json();
      const answer = data.odgovor || "Ич те не разумем комшија!";
      currentAnswer = answer;

      // Прикажи одговор кроз куцаћу машину
      typeWriter(answer, aiResponseText, () => {
        appendChatMessage("ai", answer);
      });

      // Изговори одговор
      speak(answer);

    } catch (err) {
      console.error(err);
      const errMsg = "Бре комшија, прекиде се жица од интернет или сервер не ради!";
      currentAnswer = errMsg;
      aiResponseText.textContent = errMsg;
      aiResponseText.classList.remove("typing");
    }
  }

  // Преузимање насумичне пиротске речи
  async function fetchRandomWord() {
    try {
      const res = await fetch("/api/random_rec");
      const data = await res.json();
      
      const pitanje = `Шта значи реч '${data.rec}'?`;
      let odgovor = `• '${data.rec.toUpperCase()}' значи: ${data.znacenje}`;
      if (data.primeri && data.primeri.length > 0) {
        odgovor += ` | Пример: "${data.primeri[0]}"`;
      }

      appendChatMessage("user", pitanje);
      lastQuestionBadge.innerHTML = `👉 <em>${pitanje}</em>`;
      currentAnswer = odgovor;

      typeWriter(odgovor, aiResponseText, () => {
        appendChatMessage("ai", odgovor);
      });
      speak(odgovor);

    } catch (e) {
      console.error(e);
    }
  }

  // Руковање слањем формулара
  chatForm.addEventListener("submit", (e) => {
    e.preventDefault();
    const val = userInput.value;
    if (val.trim()) {
      askQuestion(val);
      userInput.value = "";
    }
  });

  // Брза дугмад (Chips)
  document.querySelectorAll(".chip-btn").forEach(btn => {
    btn.addEventListener("click", () => {
      const action = btn.dataset.action;
      const query = btn.dataset.query;

      if (action === "random-rec") {
        fetchRandomWord();
      } else if (query) {
        askQuestion(query);
      }
    });
  });

  // Звук Toggle
  btnToggleSound.addEventListener("click", () => {
    soundEnabled = !soundEnabled;
    btnToggleSound.classList.toggle("active", soundEnabled);
    lblSoundStatus.textContent = soundEnabled ? "Укључен" : "Искључен";
    btnToggleSound.querySelector(".btn-icon").textContent = soundEnabled ? "🔊" : "🔇";
    if (!soundEnabled && synth) {
      synth.cancel();
      avatarWrapper.classList.remove("speaking");
    }
  });

  // Поновни говор
  btnReplayAudio.addEventListener("click", () => {
    if (currentAnswer) {
      speak(currentAnswer);
    }
  });

  // Копирање одговора
  btnCopyAnswer.addEventListener("click", async () => {
    if (!currentAnswer) return;
    try {
      await navigator.clipboard.writeText(currentAnswer);
      const orig = btnCopyAnswer.textContent;
      btnCopyAnswer.textContent = "✅";
      setTimeout(() => btnCopyAnswer.textContent = orig, 1200);
    } catch (e) {
      console.warn("Није могуће копирати", e);
    }
  });

  // Брисање ћаскања
  btnClearChat.addEventListener("click", () => {
    chatFeed.innerHTML = "";
  });

  // =========================================================================
  // РЕЧНИК МОДАЛ
  // =========================================================================
  function openDictionaryModal() {
    dictModal.classList.add("open");
    dictModal.setAttribute("aria-hidden", "false");
    dictSearchInput.focus();
    loadDictionaryResults("");
  }

  function closeDictionaryModal() {
    dictModal.classList.remove("open");
    dictModal.setAttribute("aria-hidden", "true");
  }

  btnOpenDictionary.addEventListener("click", openDictionaryModal);
  btnCloseModal.addEventListener("click", closeDictionaryModal);
  dictModal.addEventListener("click", (e) => {
    if (e.target === dictModal) closeDictionaryModal();
  });

  async function loadDictionaryResults(query) {
    dictStats.textContent = "Претражујем 2.726 одредница САНУ речника...";
    try {
      const res = await fetch(`/api/recnik?q=${encodeURIComponent(query)}`);
      const data = await res.json();
      
      dictResults.innerHTML = "";
      dictStats.textContent = `Пронађено: ${data.ukupno} одредница (приказано до 50)`;

      if (!data.rezultati || data.rezultati.length === 0) {
        dictResults.innerHTML = `<div style="text-align:center; padding: 2rem; color: var(--text-dim);">
          Нема поклапања за „${escapeHtml(query)}”. Пробај други израз или српски појам.
        </div>`;
        return;
      }

      data.rezultati.forEach(item => {
        const card = document.createElement("div");
        card.className = "dict-card";
        card.title = "Кликни да питаш комшију за ову реч";

        let primeriHtml = "";
        if (item.primeri && item.primeri.length > 0) {
          primeriHtml = `<div class="dict-examples">📍 ${escapeHtml(item.primeri.slice(0, 2).join(" | "))}</div>`;
        }

        card.innerHTML = `
          <div class="dict-card-head">
            <span class="dict-word">${escapeHtml(item.rec || "")}</span>
            <span class="dict-kind">${escapeHtml(item.vrsta || "")}</span>
          </div>
          <div class="dict-meaning">${escapeHtml(item.znacenje || "")}</div>
          ${primeriHtml}
        `;

        card.addEventListener("click", () => {
          closeDictionaryModal();
          askQuestion(`шта значи ${item.rec}`);
        });

        dictResults.appendChild(card);
      });
    } catch (e) {
      dictStats.textContent = "Грешка при учитавању речника.";
    }
  }

  dictSearchInput.addEventListener("input", (e) => {
    clearTimeout(searchDebounceTimer);
    searchDebounceTimer = setTimeout(() => {
      loadDictionaryResults(e.target.value.trim());
    }, 280);
  });

  btnRandomInDict.addEventListener("click", () => {
    fetchRandomWord();
    closeDictionaryModal();
  });

  // Тастатурне пречице (1-6, R, M, ESC)
  window.addEventListener("keydown", (e) => {
    // Ако је отворен модал, ESC га затвара
    if (e.key === "Escape") {
      closeDictionaryModal();
      return;
    }

    // Ако корисник куца у пољу за унос, не пресрећи 1-6
    if (document.activeElement === userInput || document.activeElement === dictSearchInput) {
      return;
    }

    if (e.key >= "1" && e.key <= "6") {
      const btn = document.querySelector(`.chip-btn[data-key="${e.key}"]`);
      if (btn) {
        e.preventDefault();
        btn.click();
      }
    } else if (e.key.toLowerCase() === "r") {
      e.preventDefault();
      fetchRandomWord();
    } else if (e.key.toLowerCase() === "m") {
      e.preventDefault();
      btnToggleSound.click();
    }
  });

  function escapeHtml(text) {
    if (!text) return "";
    return String(text)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#039;");
  }
});
