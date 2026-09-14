/* Клинический ассистент «МедСферы»: минималистичный виджет консультации. */
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
    } catch (_) { /* приватный режим — пропускаем */ }
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
    var headerInfo = el("div", "ai-chat__header-info");
    headerInfo.appendChild(el("strong", "", "Клинический консультант"));
    headerInfo.appendChild(el("span", "ai-chat__hint", "онлайн"));
    header.appendChild(headerInfo);

    var closeBtn = el("button", "ai-chat__close");
    closeBtn.type = "button";
    closeBtn.setAttribute("aria-label", "Закрыть диалог");
    closeBtn.innerHTML = '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>';
    header.appendChild(closeBtn);

    var log = el("div", "ai-chat__log");
    log.setAttribute("data-ai-log", "");
    log.setAttribute("aria-live", "polite");

    var form = el("form", "ai-chat__form");
    form.setAttribute("data-ai-form", "");
    var input = el("input", "ai-chat__input");
    input.type = "text";
    input.name = "question";
    input.placeholder = "Спросите о приёме, услугах или врачах…";
    input.maxLength = 800;
    input.autocomplete = "off";
    input.required = true;

    var sendBtn = el("button", "ai-chat__send");
    sendBtn.type = "submit";
    sendBtn.setAttribute("aria-label", "Отправить вопрос");
    sendBtn.innerHTML = '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><line x1="22" y1="2" x2="11" y2="13"></line><polygon points="22 2 15 22 11 13 2 9 22 2"></polygon></svg>';

    form.appendChild(input);
    form.appendChild(sendBtn);

    var statusLine = el("p", "ai-chat__status");
    statusLine.setAttribute("data-ai-status", "");
    statusLine.hidden = true;

    panel.appendChild(header);
    panel.appendChild(log);
    panel.appendChild(statusLine);
    panel.appendChild(form);

    var fab = el("button", "ai-chat__fab");
    fab.type = "button";
    fab.setAttribute("aria-label", "Открыть консультант клиники");
    fab.innerHTML = '<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path></svg><span>Консультант</span>';

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
    statusLine.textContent = "Консультант формирует ответ…";

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
            AI_ASSISTANT_DISABLED: "Консультант временно недоступен. Вы можете оформить запись напрямую через регистратуру на сайте.",
            RATE_LIMITED: "Слишком частые запросы. Пожалуйста, подождите минуту перед следующим вопросом.",
            AI_RATE_LIMITED: "Высокая нагрузка на сервис. Попробуйте повторить запрос через минуту.",
          };
          bubble(log, "assistant", friendly[code] || "Не удалось получить ответ. Пожалуйста, оформите заявку на приём на сайте.");
        } else {
          var answer = (result.data && result.data.answer) || "Ответ не сформирован. Повторите запрос.";
          bubble(log, "assistant", answer);
          state.history.push({ role: "user", content: question });
          state.history.push({ role: "assistant", content: answer });
          saveHistory();
        }
      })
      .catch(function () {
        bubble(log, "assistant", "Нет связи с клиническим сервером. Проверьте сеть или воспользуйтесь формой записи.");
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
