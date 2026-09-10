(function () {
  "use strict";

  const page = document.body.dataset.page;
  const state = { services: [], doctors: [], faq: [], utm: {} };
  const $ = (selector, root = document) => root.querySelector(selector);
  const escapeText = (value) => String(value ?? "");
  const rubles = (value) => `${new Intl.NumberFormat("ru-RU").format(value)} ₽`;

  function setupNavigation() {
    const menuButton = $("[data-menu-button]");
    const nav = $("[data-nav]");
    menuButton?.addEventListener("click", () => {
      const expanded = menuButton.getAttribute("aria-expanded") === "true";
      menuButton.setAttribute("aria-expanded", String(!expanded));
      nav.classList.toggle("is-open", !expanded);
    });
    $("[data-year]").textContent = new Date().getFullYear();
  }

  function captureAnalytics() {
    const params = new URLSearchParams(window.location.search);
    ["utm_source", "utm_medium", "utm_campaign", "utm_content", "utm_term", "source"].forEach((key) => {
      if (params.get(key)) state.utm[key] = params.get(key);
    });
    const cookie = document.cookie.split("; ").find((item) => item.startsWith("clientID="));
    let clientId = "";
    try { clientId = cookie ? decodeURIComponent(cookie.slice("clientID=".length)) : ""; } catch (_) { clientId = ""; }
    if (!clientId) {
      clientId = window.crypto?.randomUUID?.() || `cid-${Date.now()}-${Math.random().toString(16).slice(2)}`;
      document.cookie = `clientID=${encodeURIComponent(clientId)}; max-age=31536000; path=/; SameSite=Lax`;
    }
    state.utm.client_id = clientId;
    if (!state.utm.source) state.utm.source = "website";
  }

  function setLoading(target, loading) {
    if (!target) return;
    target.classList.toggle("is-loading", loading);
    target.setAttribute("aria-busy", String(loading));
  }

  function renderServices(items, target = $("[data-services-list]")) {
    if (!target) return;
    target.replaceChildren();
    if (!items.length) { target.innerHTML = '<p class="empty-state">Услуги пока не добавлены.</p>'; return; }
    items.forEach((service) => {
      const card = document.createElement("article");
      card.className = "card service-card";
      const title = document.createElement("h3"); title.textContent = escapeText(service.name);
      const description = document.createElement("p"); description.textContent = escapeText(service.description) || "Подберём комфортный план лечения.";
      const meta = document.createElement("div"); meta.className = "card-meta"; meta.textContent = `${rubles(service.price)} · ${service.duration_minutes} мин.`;
      card.append(title, description, meta); target.append(card);
    });
  }

  function renderDoctors(items, target = $("[data-doctors-list]")) {
    if (!target) return;
    target.replaceChildren();
    if (!items.length) { target.innerHTML = '<p class="empty-state">Врачи пока не добавлены.</p>'; return; }
    items.forEach((doctor) => {
      const card = document.createElement("article"); card.className = "card doctor-card";
      const media = document.createElement("div"); media.className = "doctor-photo";
      if (doctor.photo_url) { const image = document.createElement("img"); image.src = doctor.photo_url; image.alt = doctor.full_name; media.append(image); } else media.textContent = doctor.full_name.split(" ").map((part) => part[0]).slice(0, 2).join("");
      const content = document.createElement("div");
      const name = document.createElement("h3"); name.textContent = doctor.full_name;
      const specialty = document.createElement("p"); specialty.className = "eyebrow"; specialty.textContent = doctor.specialty;
      const bio = document.createElement("p"); bio.textContent = doctor.bio || `${doctor.experience_years} лет практики`;
      content.append(name, specialty, bio); card.append(media, content); target.append(card);
    });
  }

  function renderFaq(items, target = $("[data-faq-list]")) {
    if (!target) return;
    target.replaceChildren();
    if (!items.length) { target.innerHTML = '<p class="empty-state">Вопросы пока не добавлены.</p>'; return; }
    items.forEach((item) => {
      const details = document.createElement("details"); details.className = "faq-item";
      const summary = document.createElement("summary"); summary.textContent = item.question;
      const answer = document.createElement("p"); answer.textContent = item.answer;
      details.append(summary, answer); target.append(details);
    });
  }

  async function loadPublicData() {
    const results = await Promise.allSettled([api.services(), api.doctors(), api.faq()]);
    const [services, doctors, faq] = results;
    if (services.status === "fulfilled") { state.services = services.value.items || []; renderServices(state.services); }
    if (doctors.status === "fulfilled") { state.doctors = doctors.value.items || []; renderDoctors(state.doctors); }
    if (faq.status === "fulfilled") { state.faq = faq.value.items || []; renderFaq(state.faq); }
    setupAppointment();
  }

  function setupAppointment() {
    const form = $("[data-appointment-form]");
    if (!form || !state.services.length || !state.doctors.length) return;
    const doctorSelect = $("[name=doctor_id]", form); const serviceSelect = $("[name=service_id]", form);
    const dateInput = $("[name=date]", form); const slotSelect = $("[name=slot_start]", form);
    const slotsHint = $("[data-slots-hint]"); const submit = $("[type=submit]", form);
    serviceSelect.replaceChildren(new Option("Выберите услугу", ""));
    state.services.forEach((service) => serviceSelect.add(new Option(`${service.name} · ${rubles(service.price)}`, service.id)));
    function populateDoctors() {
      const selected = doctorSelect.value;
      doctorSelect.replaceChildren(new Option(serviceSelect.value ? "Выберите врача" : "Сначала выберите услугу", ""));
      state.doctors.filter((doctor) => doctor.service_ids.includes(Number(serviceSelect.value))).forEach((doctor) => doctorSelect.add(new Option(`${doctor.full_name} · ${doctor.specialty}`, doctor.id)));
      if ([...doctorSelect.options].some((option) => option.value === selected)) doctorSelect.value = selected;
      loadSlots();
    }
    async function loadSlots() {
      slotSelect.replaceChildren(new Option("Сначала выберите дату", "")); slotSelect.disabled = true;
      if (!doctorSelect.value || !dateInput.value) return;
      slotsHint.textContent = "Загружаем свободное время…"; setLoading(slotSelect, true);
      try {
        const result = await api.slots(doctorSelect.value, dateInput.value);
        slotSelect.replaceChildren(new Option(result.slots.length ? "Выберите время" : "Свободных слотов нет", ""));
        result.slots.forEach((slot) => slotSelect.add(new Option(new Date(slot).toLocaleTimeString("ru-RU", { hour: "2-digit", minute: "2-digit" }), slot)));
        slotSelect.disabled = !result.slots.length; slotsHint.textContent = result.slots.length ? "Выберите удобное время." : "На эту дату свободных слотов нет.";
      } catch (_) { slotsHint.textContent = "Не удалось загрузить слоты."; }
      finally { setLoading(slotSelect, false); }
    }
    serviceSelect.addEventListener("change", populateDoctors); doctorSelect.addEventListener("change", loadSlots); dateInput.addEventListener("change", loadSlots);
    const today = new Date();
    dateInput.min = `${today.getFullYear()}-${String(today.getMonth() + 1).padStart(2, "0")}-${String(today.getDate()).padStart(2, "0")}`;
    populateDoctors();
    form.addEventListener("submit", async (event) => {
      event.preventDefault();
      const data = new FormData(form); submit.disabled = true; $("[data-form-message]", form).textContent = "";
      const body = { doctor_id: Number(data.get("doctor_id")), service_id: Number(data.get("service_id")), slot_start: data.get("slot_start"), client_name: data.get("client_name").trim(), client_phone: data.get("client_phone").trim(), ...state.utm };
      try {
        const result = await api.createAppointment(body);
        const success = $("[data-appointment-success]");
        form.hidden = true; success.hidden = false; $("[data-lead-id]").textContent = result.lead_id; success.focus();
      } catch (error) { $("[data-form-message]", form).textContent = error.code === "SLOT_UNAVAILABLE" ? "Этот слот уже занят. Выберите другое время." : error.message; submit.disabled = false; }
    });
  }

  setupNavigation(); captureAnalytics();
  if (page !== "admin") loadPublicData().catch(() => {});
}());
