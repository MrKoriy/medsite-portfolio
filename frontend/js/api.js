(function () {
  "use strict";

  class ApiError extends Error {
    constructor(message, status, code) {
      super(message);
      this.name = "ApiError";
      this.status = status;
      this.code = code;
    }
  }

  function notify(message) {
    document.querySelectorAll("[data-api-error]").forEach((node) => {
      node.textContent = message;
      node.hidden = false;
    });
  }

  function token() {
    return sessionStorage.getItem("medsite_admin_token");
  }

  async function request(path, options = {}) {
    const headers = { Accept: "application/json", ...(options.headers || {}) };
    if (options.body && typeof options.body !== "string") {
      headers["Content-Type"] = "application/json";
      options.body = JSON.stringify(options.body);
    }
    const authToken = token();
    if (options.auth && authToken) headers.Authorization = `Bearer ${authToken}`;
    let response;
    try {
      response = await fetch(`${API_BASE_URL}${path}`, { ...options, headers });
    } catch (error) {
      const apiError = new ApiError("Не удалось подключиться к серверу. Проверьте, запущен ли API.", 0, "NETWORK_ERROR");
      notify(apiError.message);
      throw apiError;
    }
    let payload = null;
    if (response.status !== 204) {
      try { payload = await response.json(); } catch (_) { payload = null; }
    }
    if (!response.ok) {
      const error = payload && payload.error ? payload.error : {};
      const apiError = new ApiError(error.message || `Ошибка запроса (${response.status})`, response.status, error.code || "HTTP_ERROR");
      if (response.status === 401 && token()) {
        sessionStorage.removeItem("medsite_admin_token");
        window.dispatchEvent(new CustomEvent("admin:unauthorized"));
      }
      notify(apiError.message);
      throw apiError;
    }
    return payload;
  }

  const query = (params) => {
    const search = new URLSearchParams();
    Object.entries(params || {}).forEach(([key, value]) => {
      if (value !== undefined && value !== null && value !== "") search.set(key, value);
    });
    const result = search.toString();
    return result ? `?${result}` : "";
  };

  window.api = {
    ApiError,
    health: () => request("/api/health"),
    services: (params) => request(`/api/services${query(params)}`),
    service: (id) => request(`/api/services/${id}`),
    createService: (body) => request("/api/services", { method: "POST", body, auth: true }),
    updateService: (id, body) => request(`/api/services/${id}`, { method: "PUT", body, auth: true }),
    deleteService: (id) => request(`/api/services/${id}`, { method: "DELETE", auth: true }),
    doctors: (params) => request(`/api/doctors${query(params)}`),
    doctor: (id) => request(`/api/doctors/${id}`),
    createDoctor: (body) => request("/api/doctors", { method: "POST", body, auth: true }),
    updateDoctor: (id, body) => request(`/api/doctors/${id}`, { method: "PUT", body, auth: true }),
    deleteDoctor: (id) => request(`/api/doctors/${id}`, { method: "DELETE", auth: true }),
    slots: (id, date) => request(`/api/doctors/${id}/slots${query({ date })}`),
    faq: (params) => request(`/api/faq${query(params)}`),
    faqItem: (id) => request(`/api/faq/${id}`),
    createFaq: (body) => request("/api/faq", { method: "POST", body, auth: true }),
    updateFaq: (id, body) => request(`/api/faq/${id}`, { method: "PUT", body, auth: true }),
    deleteFaq: (id) => request(`/api/faq/${id}`, { method: "DELETE", auth: true }),
    createAppointment: (body) => request("/api/appointments", { method: "POST", body }),
    login: (body) => request("/api/admin/login", { method: "POST", body }),
    appointments: (params) => request(`/api/admin/appointments${query(params)}`, { auth: true }),
    updateAppointment: (id, body) => request(`/api/admin/appointments/${id}`, { method: "PATCH", body, auth: true }),
    seo: (page) => request(`/api/admin/seo/${encodeURIComponent(page)}`, { auth: true }),
    updateSeo: (page, body) => request(`/api/admin/seo/${encodeURIComponent(page)}`, { method: "PUT", body, auth: true })
  };
  window.showApiError = notify;
}());
