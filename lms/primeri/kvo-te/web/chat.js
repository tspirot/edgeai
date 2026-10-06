/* ==========================================================================
   ПИРОТ-GPT — FRONTEND LOGIKA (CHATGPT-STYLE)
   ========================================================================== */

document.addEventListener("DOMContentLoaded", () => {
  // DOM елементи
  const sidebar = document.getElementById("sidebar");
  const btnToggleSidebar = document.getElementById("btnToggleSidebar");
  const btnSidebarCloseMobile = document.getElementById("btnSidebarCloseMobile");
  const btnNewChat = document.getElementById("btnNewChat");
  const historyList = document.getElementById("historyList");
  const personaButtons = document.querySelectorAll(".persona-btn");
  const lblActivePersona = document.getElementById("lblActivePersona");
  const chkAutoSpeak = document.getElementById("chkAutoSpeak");
  const btnClearCurrentChat = document.getElementById("btnClearCurrentChat");
  const btnOpenSettings = document.getElementById("btnOpenSettings");
  const settingsModal = document.getElementById("settingsModal");
  const btnCloseSettings = document.getElementById("btnCloseSettings");
  const selAiProvider = document.getElementById("selAiProvider");
  const groupApiKey = document.getElementById("groupApiKey");
  const txtApiKey = document.getElementById("txtApiKey");
  const btnToggleKeyVisibility = document.getElementById("btnToggleKeyVisibility");
  const apiKeyHint = document.getElementById("apiKeyHint");
  const txtAiModel = document.getElementById("txtAiModel");
  const settingsStatusBox = document.getElementById("settingsStatusBox");
  const btnTestConnection = document.getElementById("btnTestConnection");
  const btnSaveSettings = document.getElementById("btnSaveSettings");

  const messagesViewport = document.getElementById("messagesViewport");
  const welcomeHero = document.getElementById("welcomeHero");
  const messagesThread = document.getElementById("messagesThread");
  const composerForm = document.getElementById("composerForm");
  const chatPromptInput = document.getElementById("chatPromptInput");
  const btnSend = document.getElementById("btnSend");
  const starterCards = document.querySelectorAll(".starter-card");

  // Стање апликације
  const STORAGE_KEY = "pirot_gpt_sessions_v1";
  let activePersona = "stedisa";
  let isGenerating = false;
  let sessions = loadSessions();
  let currentSessionId = sessions.length > 0 ? sessions[0].id : createNewSession().id;

  // Иницијализација говора (Web Speech API)
  const synth = window.speechSynthesis;
  let serbianVoice = null;
  function initVoice() {
    if (!synth) return;
    const voices = synth.getVoices();
    serbianVoice = voices.find(v => v.lang.startsWith("sr") || v.lang.startsWith("hr") || v.lang.startsWith("bs")) || null;
  }
  if (synth) {
    initVoice();
    if (synth.onvoiceschanged !== undefined) synth.onvoiceschanged = initVoice;
  }

  function speakText(text) {
    if (!text || !chkAutoSpeak.checked) return;
    if (synth) {
      try {
        synth.cancel();
        const clean = text.replace(/[\*\#\_\"\'•]/g, "");
        const utter = new SpeechSynthesisUtterance(clean);
        if (serbianVoice) utter.voice = serbianVoice;
        utter.rate = 0.95;
        utter.pitch = 0.9;
        synth.speak(utter);
        return;
      } catch (e) {
        console.warn("Web Speech није успео, покушавам серверски говор...", e);
      }
    }

    // Серверски fallback
    fetch("/api/govori", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ tekst: text })
    }).catch(() => {});
  }

  // =========================================================================
  // РУКОВАЊЕ СЕСИЈАМА (STORAGE & HISTORY)
  // =========================================================================
  function loadSessions() {
    try {
      const raw = localStorage.getItem(STORAGE_KEY);
      return raw ? JSON.parse(raw) : [];
    } catch {
      return [];
    }
  }

  function saveSessions() {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(sessions));
    } catch (e) {
      console.warn("Storage пун", e);
    }
  }

  function createNewSession() {
    const newSess = {
      id: "sess_" + Date.now(),
      title: "Нов муабет",
      persona: activePersona,
      messages: [],
      updatedAt: Date.now()
    };
    sessions.unshift(newSess);
    saveSessions();
    return newSess;
  }

  function getCurrentSession() {
    let s = sessions.find(x => x.id === currentSessionId);
    if (!s) {
      s = createNewSession();
      currentSessionId = s.id;
    }
    return s;
  }

  function renderHistorySidebar() {
    historyList.innerHTML = "";
    if (sessions.length === 0) {
      historyList.innerHTML = `<div style="padding: 0.8rem; font-size: 0.8rem; color: var(--text-muted); text-align: center;">Нема претходних муабета</div>`;
      return;
    }

    sessions.forEach(sess => {
      const item = document.createElement("div");
      item.className = `history-item ${sess.id === currentSessionId ? "active" : ""}`;
      
      const titleSpan = document.createElement("span");
      titleSpan.className = "history-title";
      titleSpan.textContent = sess.title || "Муабет";
      titleSpan.title = sess.title;

      const delBtn = document.createElement("button");
      delBtn.className = "history-delete-btn";
      delBtn.innerHTML = "&times;";
      delBtn.title = "Обриши муабет";
      delBtn.addEventListener("click", (e) => {
        e.stopPropagation();
        deleteSession(sess.id);
      });

      item.appendChild(titleSpan);
      item.appendChild(delBtn);

      item.addEventListener("click", () => {
        switchSession(sess.id);
      });

      historyList.appendChild(item);
    });
  }

  function switchSession(sessId) {
    if (synth) synth.cancel();
    currentSessionId = sessId;
    const sess = getCurrentSession();
    setPersona(sess.persona || "stedisa", false);
    renderMessages();
    renderHistorySidebar();
    if (window.innerWidth <= 768) {
      sidebar.classList.remove("mobile-open");
    }
  }

  function deleteSession(sessId) {
    sessions = sessions.filter(s => s.id !== sessId);
    if (currentSessionId === sessId) {
      if (sessions.length > 0) {
        currentSessionId = sessions[0].id;
      } else {
        const fresh = createNewSession();
        currentSessionId = fresh.id;
      }
    }
    saveSessions();
    renderHistorySidebar();
    renderMessages();
  }

  // =========================================================================
  // ПЕРСОНЕ (ШТЕДИША / МЕРАКЛИЈА / ПРОФЕСОР)
  // =========================================================================
  const PERSONA_NAMES = {
    stedisa: "Бајица Станко (Штедиша)",
    meraklija: "Чика Добри (Мераклија)",
    profesor: "Проф. Златковић (САНУ)"
  };

  function setPersona(personaKey, updateSession = true) {
    activePersona = personaKey;
    personaButtons.forEach(btn => {
      btn.classList.toggle("active", btn.dataset.persona === personaKey);
    });
    lblActivePersona.textContent = PERSONA_NAMES[personaKey] || "ПиротGPT";

    if (updateSession) {
      const sess = getCurrentSession();
      sess.persona = personaKey;
      saveSessions();
    }
  }

  personaButtons.forEach(btn => {
    btn.addEventListener("click", () => {
      setPersona(btn.dataset.persona, true);
    });
  });

  // =========================================================================
  // ПРИКАЗ ПОРУКА
  // =========================================================================
  function renderMessages() {
    const sess = getCurrentSession();
    messagesThread.innerHTML = "";

    if (!sess.messages || sess.messages.length === 0) {
      welcomeHero.style.display = "flex";
      messagesThread.style.display = "none";
      return;
    }

    welcomeHero.style.display = "none";
    messagesThread.style.display = "flex";

    sess.messages.forEach(msg => {
      appendMessageToThread(msg.role, msg.content, false);
    });

    scrollToBottom();
  }

  function appendMessageToThread(role, content, animate = false) {
    welcomeHero.style.display = "none";
    messagesThread.style.display = "flex";

    const row = document.createElement("div");
    row.className = `message-row ${role}`;

    const avatar = document.createElement("div");
    avatar.className = "msg-avatar";
    avatar.textContent = role === "user" ? "👤" : (activePersona === "meraklija" ? "🥓" : (activePersona === "profesor" ? "📜" : "👴"));

    const bodyWrapper = document.createElement("div");
    bodyWrapper.className = "msg-body-wrapper";

    if (role === "ai") {
      const meta = document.createElement("div");
      meta.className = "msg-meta-author";
      meta.textContent = PERSONA_NAMES[activePersona] || "ПиротGPT";
      bodyWrapper.appendChild(meta);
    }

    const contentBox = document.createElement("div");
    contentBox.className = "msg-content";

    if (animate) {
      contentBox.classList.add("typing-cursor");
      bodyWrapper.appendChild(contentBox);
      row.appendChild(avatar);
      row.appendChild(bodyWrapper);
      messagesThread.appendChild(row);
      scrollToBottom();

      // Стримовање текста
      let i = 0;
      const speed = 14;
      const timer = setInterval(() => {
        if (i < content.length) {
          contentBox.innerHTML = formatMarkdown(content.substring(0, i + 1));
          i++;
          scrollToBottom();
        } else {
          clearInterval(timer);
          contentBox.classList.remove("typing-cursor");
          contentBox.innerHTML = formatMarkdown(content);
          addMessageActions(bodyWrapper, content);
          scrollToBottom();
        }
      }, speed);

    } else {
      contentBox.innerHTML = formatMarkdown(content);
      bodyWrapper.appendChild(contentBox);
      if (role === "ai") {
        addMessageActions(bodyWrapper, content);
      }
      row.appendChild(avatar);
      row.appendChild(bodyWrapper);
      messagesThread.appendChild(row);
    }
  }

  function addMessageActions(container, text) {
    const actions = document.createElement("div");
    actions.className = "msg-actions";

    const btnCopy = document.createElement("button");
    btnCopy.className = "msg-action-btn";
    btnCopy.innerHTML = "📋 Копирај";
    btnCopy.addEventListener("click", async () => {
      try {
        await navigator.clipboard.writeText(text);
        btnCopy.innerHTML = "✅ Копирано!";
        setTimeout(() => btnCopy.innerHTML = "📋 Копирај", 1500);
      } catch {}
    });

    const btnSpeak = document.createElement("button");
    btnSpeak.className = "msg-action-btn";
    btnSpeak.innerHTML = "🔊 Чуј";
    btnSpeak.addEventListener("click", () => {
      speakText(text);
    });

    actions.appendChild(btnCopy);
    actions.appendChild(btnSpeak);
    container.appendChild(actions);
  }

  function formatMarkdown(txt) {
    if (!txt) return "";
    let safe = txt
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;");

    // Bold **text**
    safe = safe.replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>");
    // Italic *text*
    safe = safe.replace(/\*(.*?)\*/g, "<em>$1</em>");
    // Листе
    safe = safe.replace(/^[•\-\*]\s+(.*)$/gm, "<li>$1</li>");
    safe = safe.replace(/(<li>.*<\/li>)/s, "<ul>$1</ul>");
    // Нови редови у параграфе
    const lines = safe.split(/\n\n+/);
    return lines.map(p => `<p>${p.replace(/\n/g, "<br>")}</p>`).join("");
  }

  function scrollToBottom() {
    messagesViewport.scrollTop = messagesViewport.scrollHeight;
  }

  // =========================================================================
  // СЛАЊЕ ПИТАЊА
  // =========================================================================
  async function sendMessage(userText) {
    if (!userText || !userText.trim() || isGenerating) return;
    const text = userText.trim();
    chatPromptInput.value = "";
    resizeInput();

    const sess = getCurrentSession();

    // Додај корисничку поруку
    sess.messages.push({ role: "user", content: text, timestamp: Date.now() });
    if (sess.title === "Нов муабет") {
      sess.title = text.length > 28 ? text.substring(0, 28) + "..." : text;
    }
    sess.updatedAt = Date.now();
    saveSessions();
    renderHistorySidebar();

    appendMessageToThread("user", text, false);
    scrollToBottom();

    // Припреми историју за сервер
    const historyPayload = sess.messages.slice(-8).map(m => ({
      role: m.role,
      content: m.content
    }));

    isGenerating = true;
    btnSend.disabled = true;

    try {
      const res = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          messages: historyPayload,
          persona: activePersona,
          govori_na_serveru: false
        })
      });

      if (!res.ok) throw new Error("Сервер грешка");
      const data = await res.json();
      const answer = data.odgovor || "Ич те не разумем комшија!";

      // Сачувај у сесију
      sess.messages.push({ role: "ai", content: answer, timestamp: Date.now() });
      sess.updatedAt = Date.now();
      saveSessions();

      // Прикажи са анимацијом
      appendMessageToThread("ai", answer, true);

      // Говори одговор ако је штиклирано
      speakText(answer);

    } catch (err) {
      console.error(err);
      const errMsg = "Бре комшија, прекиде се веза са сервером! Провери дал' ради сервер у позадини.";
      appendMessageToThread("ai", errMsg, false);
    } finally {
      isGenerating = false;
      btnSend.disabled = false;
      chatPromptInput.focus();
    }
  }

  // =========================================================================
  // ДОГАЂАЈИ И УНОС ТЕКСТА
  // =========================================================================
  function resizeInput() {
    chatPromptInput.style.height = "auto";
    chatPromptInput.style.height = Math.min(chatPromptInput.scrollHeight, 160) + "px";
  }

  chatPromptInput.addEventListener("input", resizeInput);

  function handleUserSubmit() {
    const text = chatPromptInput.value.trim();
    if (!text || isGenerating) return;
    sendMessage(text);
  }

  // Слање поруке на притисак тастера ENTER (Shift+Enter за нови ред)
  chatPromptInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleUserSubmit();
    }
  });

  composerForm.addEventListener("submit", (e) => {
    e.preventDefault();
    handleUserSubmit();
  });

  btnSend.addEventListener("click", (e) => {
    e.preventDefault();
    handleUserSubmit();
  });

  // Стартер картице
  starterCards.forEach(card => {
    card.addEventListener("click", () => {
      const prompt = card.dataset.prompt;
      if (prompt) sendMessage(prompt);
    });
  });

  // Дугме за нов муабет
  btnNewChat.addEventListener("click", () => {
    if (synth) synth.cancel();
    const fresh = createNewSession();
    currentSessionId = fresh.id;
    renderHistorySidebar();
    renderMessages();
    chatPromptInput.focus();
  });

  // Очисти тренутни разговор
  btnClearCurrentChat.addEventListener("click", () => {
    if (synth) synth.cancel();
    const sess = getCurrentSession();
    sess.messages = [];
    sess.title = "Нов муабет";
    saveSessions();
    renderHistorySidebar();
    renderMessages();
  });

  // Бочна трака Toggle
  btnToggleSidebar.addEventListener("click", () => {
    if (window.innerWidth <= 768) {
      sidebar.classList.toggle("mobile-open");
    } else {
      sidebar.classList.toggle("collapsed");
    }
  });

  btnSidebarCloseMobile.addEventListener("click", () => {
    sidebar.classList.remove("mobile-open");
  });

  // =========================================================================
  // ПОДЕШАВАЊА AI МОДЕЛА (SETTINGS MODAL)
  // =========================================================================
  function showSettingsStatus(msg, type = "info") {
    if (!settingsStatusBox) return;
    settingsStatusBox.style.display = "block";
    settingsStatusBox.className = `settings-status-box ${type}`;
    settingsStatusBox.textContent = msg;
  }

  function hideSettingsStatus() {
    if (!settingsStatusBox) return;
    settingsStatusBox.style.display = "none";
    settingsStatusBox.textContent = "";
  }

  function updateApiKeyVisibility() {
    if (!selAiProvider || !groupApiKey) return;
    const prov = selAiProvider.value;
    if (prov === "oflajn" || prov === "ollama") {
      groupApiKey.style.display = "none";
    } else {
      groupApiKey.style.display = "flex";
      if (prov === "groq") {
        apiKeyHint.textContent = "Кључ са console.groq.com (бесплатан и тренутно најбржи)";
      } else if (prov === "gemini") {
        apiKeyHint.textContent = "Google AI Studio кључ (aistudio.google.com)";
      } else if (prov === "openrouter") {
        apiKeyHint.textContent = "OpenRouter кључ (openrouter.ai/keys)";
      } else if (prov === "openai") {
        apiKeyHint.textContent = "OpenAI API кључ (platform.openai.com)";
      }
    }
  }

  if (selAiProvider) {
    selAiProvider.addEventListener("change", updateApiKeyVisibility);
  }

  if (btnToggleKeyVisibility && txtApiKey) {
    btnToggleKeyVisibility.addEventListener("click", () => {
      if (txtApiKey.type === "password") {
        txtApiKey.type = "text";
        btnToggleKeyVisibility.textContent = "🔒";
      } else {
        txtApiKey.type = "password";
        btnToggleKeyVisibility.textContent = "👁️";
      }
    });
  }

  async function loadServerConfig() {
    try {
      const res = await fetch("/api/config");
      if (!res.ok) return;
      const cfg = await res.json();
      if (cfg.provider && selAiProvider) selAiProvider.value = cfg.provider;
      if (cfg.model && txtAiModel) txtAiModel.value = cfg.model;
      if (txtApiKey) {
        if (cfg.has_api_key) {
          txtApiKey.placeholder = `Сачуван кључ: ${cfg.masked_key} (остави празно да задржиш)`;
        } else {
          txtApiKey.placeholder = "Унесите ваш API кључ...";
        }
      }
      updateApiKeyVisibility();
    } catch (e) {
      console.warn("Грешка при учитавању конфигурације", e);
    }
  }

  if (btnOpenSettings && settingsModal) {
    btnOpenSettings.addEventListener("click", () => {
      hideSettingsStatus();
      loadServerConfig();
      settingsModal.style.display = "flex";
    });
  }

  if (btnCloseSettings && settingsModal) {
    btnCloseSettings.addEventListener("click", () => {
      settingsModal.style.display = "none";
    });
  }

  if (settingsModal) {
    settingsModal.addEventListener("click", (e) => {
      if (e.target === settingsModal) {
        settingsModal.style.display = "none";
      }
    });
  }

  if (btnTestConnection) {
    btnTestConnection.addEventListener("click", async () => {
      showSettingsStatus("Тестирам везу са моделом...", "info");
      btnTestConnection.disabled = true;
      try {
        const prov = selAiProvider ? selAiProvider.value : "oflajn";
        const key = txtApiKey ? txtApiKey.value.trim() : "";
        const model = txtAiModel ? txtAiModel.value.trim() : "";

        // Прво сачувај ако је корисник унео нове податке
        await fetch("/api/config", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            provider: prov,
            api_key: key,
            model: model,
            keep_existing_key: true
          })
        });

        const res = await fetch("/api/test_llm", { method: "POST" });
        const rez = await res.json();
        if (rez.uspeh) {
          showSettingsStatus(`✅ Веза успешна! (${rez.provider})\nОдговор: "${rez.poruka}"`, "success");
        } else {
          showSettingsStatus(`❌ Грешка: ${rez.poruka || "Неуспешно повезивање"}`, "error");
        }
      } catch (err) {
        showSettingsStatus(`❌ Грешка при тестирању: ${err.message}`, "error");
      } finally {
        btnTestConnection.disabled = false;
      }
    });
  }

  if (btnSaveSettings) {
    btnSaveSettings.addEventListener("click", async () => {
      btnSaveSettings.disabled = true;
      showSettingsStatus("Чувам подешавања...", "info");
      try {
        const prov = selAiProvider ? selAiProvider.value : "oflajn";
        const key = txtApiKey ? txtApiKey.value.trim() : "";
        const model = txtAiModel ? txtAiModel.value.trim() : "";

        const res = await fetch("/api/config", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            provider: prov,
            api_key: key,
            model: model,
            keep_existing_key: true
          })
        });

        if (res.ok) {
          showSettingsStatus("✅ Подешавања успешно сачувана у config.yaml!", "success");
          setTimeout(() => {
            if (settingsModal) settingsModal.style.display = "none";
          }, 1200);
        } else {
          showSettingsStatus("❌ Грешка приликом чувања на серверу.", "error");
        }
      } catch (err) {
        showSettingsStatus(`❌ Грешка: ${err.message}`, "error");
      } finally {
        btnSaveSettings.disabled = false;
      }
    });
  }

  // Иницијални приказ и учитавање конфигурације
  loadServerConfig();
  renderHistorySidebar();
  renderMessages();
  chatPromptInput.focus();
});
