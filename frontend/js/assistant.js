/* AI-ассистент «МедСферы»: плавающий виджет чата. */
(function () {
  "use strict";

  var config = window.MEDSITE_CONFIG || { apiBaseUrl: window.API_BASE_URL || "http://127.0.0.1:8000" };
  var BASE = config.apiBaseUrl;
  var STORAGE_KEY = "medsite_chat_history";
  var MAX_HISTORY = 12;

  var state = {
    open: false,
    busy: false,
    history: loadHistory(),
  };

  function loadHistory() {
    try {
      var raw = sessionStorage.getItem(STORAGE_KEY);
      var parsed = raw ? JSON.parse(raw) : [];
      return Array.isArray(parsed) ? parsed.slice(-MAX_HISTORY) : [];
    } catch (_) {
      return [];
    }
  }

  function saveHistory() {
    try {
      sessionStorage.setItem(STORAGE_KEY, JSON.stringify(state.history.slice(-MAX_HISTORY)));
    } catch (_) { /* приватный режим — не страшно */ }
  }

  function clientId() {
    var match = document.cookie.split("; ").find(function (item) { return item.startsWith("clientID="); });
    return match ? decodeURIComponent(match.slice("clientID=".length)) : "anon";
  }

  function el(tag, className, text) {
    var node = document.createElement(tag);
    if (className) node.className = className;
    if (text !== undefined) node.textContent = text;
    return node;
  }

  function buildWidget() {
    var root = el("div", "ai-chat");
    root.setAttribute("data-ai-chat", "");

    var panel = el("div", "ai-chat__panel");
    panel.hidden = true;

    var header = el("div", "ai-chat__header");
    header.appendChild(el("strong", "", "Ассистент МедСферы"));
    header.appendChild(el("span", "ai-chat__hint", "услуги · врачи · запись"));
    var closeBtn = el("button", "ai-chat__close", "×");
    closeBtn.type = "button";
    closeBtn.setAttribute("aria-label", "Закрыть чат");
    header.appendChild(closeBtn);

    var log = el("div", "ai-chat__log");
    log.setAttribute("data-ai-log", "");
    log.setAttribute("aria-live", "polite");

    var form = el("form", "ai-chat__form");
    form.setAttribute("data-ai-form", "");
    var input = el("input", "ai-chat__input");
    input.type = "text";
    input.name = "question";
    input.placeholder = "Спросите про услуги или запись…";
    input.maxLength = 800;
    input.autocomplete = "off";
    input.required = true;
    var sendBtn = el("button", "ai-chat__send", "➤");
    sendBtn.type = "submit";
    sendBtn.setAttribute("aria-label", "Отправить");
    form.appendChild(input);
    form.appendChild(sendBtn);

    var statusLine = el("p", "ai-chat__status");
    statusLine.setAttribute("data-ai-status", "");
    statusLine.hidden = true;

    panel.appendChild(header);
    panel.appendChild(log);
    panel.appendChild(statusLine);
    panel.appendChild(form);

    var fab = el("button", "ai-chat__fab", "💬");
    fab.type = "button";
    fab.setAttribute("aria-label", "Открыть чат с ассистентом");

    root.appendChild(panel);
    root.appendChild(fab);
    document.body.appendChild(root);

    fab.addEventListener("click", function () { toggle(root, panel, fab, log, input); });
    closeBtn.addEventListener("click", function () { toggle(root, panel, fab, log, input); });
    form.addEventListener("submit", function (event) { submit(event, form, input, log, statusLine, sendBtn); });

    if (state.history.length) renderHistory(log);
  }

  function toggle(root, panel, fab, log, input) {
    state.open = !state.open;
    panel.hidden = !state.open;
    fab.classList.toggle("is-open", state.open);
    if (state.open) {
      log.scrollTop = log.scrollHeight;
      input.focus();
    }
  }

  function bubble(log, role, text) {
    var item = el("div", "ai-chat__msg ai-chat__msg--" + role, text);
    log.appendChild(item);
    log.scrollTop = log.scrollHeight;
    return item;
  }

  function renderHistory(log) {
    state.history.forEach(function (m) { bubble(log, m.role, m.content); });
  }

  function submit(event, form, input, log, statusLine, sendBtn) {
    event.preventDefault();
    if (state.busy) return;
    var question = input.value.trim();
    if (!question) return;

    state.busy = true;
    sendBtn.disabled = true;
    input.disabled = true;
    statusLine.hidden = false;
    statusLine.textContent = "Ассистент печатает…";

    bubble(log, "user", question);
    input.value = "";

    var body = JSON.stringify({
      question: question,
      history: state.history.slice(-MAX_HISTORY),
    });

    fetch(BASE + "/api/assistant/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json", "X-Client-ID": clientId() },
      body: body,
    })
      .then(function (resp) {
        return resp.json().then(function (data) { return { ok: resp.ok, data: data }; });
      })
      .then(function (result) {
        if (!result.ok) {
          var code = result.data && result.data.error ? result.data.error.code : "ERROR";
          var friendly = {
            AI_ASSISTANT_DISABLED: "Ассистент временно отключён, но вы всегда можете оставить заявку в форме записи.",
            RATE_LIMITED: "Слишком много вопросов подряд — чуть-чуть помедленнее 🙂",
            AI_RATE_LIMITED: "Ассистент перегружен, попробуйте через минуту.",
          };
          bubble(log, "assistant", friendly[code] || "Что-то пошло не так. Попробуйте ещё раз или оставьте заявку в форме записи.");
        } else {
          var answer = (result.data && result.data.answer) || "Пустой ответ, попробуйте ещё раз.";
          bubble(log, "assistant", answer);
          state.history.push({ role: "user", content: question });
          state.history.push({ role: "assistant", content: answer });
          saveHistory();
        }
      })
      .catch(function () {
        bubble(log, "assistant", "Нет связи с сервером. Проверьте соединение или оставьте заявку в форме записи.");
      })
      .finally(function () {
        state.busy = false;
        sendBtn.disabled = false;
        input.disabled = false;
        statusLine.hidden = true;
        input.focus();
      });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", buildWidget);
  } else {
    buildWidget();
  }
})();
