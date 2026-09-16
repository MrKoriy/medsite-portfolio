(function () {
  "use strict";

  const worldEl = document.getElementById("world");
  if (!worldEl || typeof window.mountScrollWorld !== "function") return;

  window.mountScrollWorld(worldEl, {
    brand: null,
    cta: null,
    hint: "прокрутите для обзора клиники",
    diveScroll: 1.1,
    connScroll: 0.7,
    atmosphere: true,
    sections: [
      {
        id: "triage",
        label: "Приёмное отделение",
        still: "assets/world/triage.webp",
        clip: "assets/world/triage.mp4",
        accent: "#11382d",
        scroll: 1.3,
        linger: 0.35,
        eyebrow: "ЛИЦЕНЗИЯ № ЛО-77-01-021480 · ДОКАЗАТЕЛЬНАЯ МЕДИЦИНА",
        title: "Приёмное отделение и маршрутизация",
        body: "Оценка состояния за 3 минуты. Персональный медицинский координатор организует приём без очередей и задержек.",
        tags: ["Экспресс-триаж", "Электронная регистрация", "Приём Пн–Сб 08:30–20:30"]
      },
      {
        id: "diagnostics",
        label: "Лаборатория и МРТ",
        still: "assets/world/diagnostics.webp",
        clip: "assets/world/diagnostics.mp4",
        accent: "#0e4a42",
        scroll: 1.3,
        linger: 0.35,
        eyebrow: "ВЫСОКОТОЧНЫЙ СКРИНИНГ",
        title: "Лабораторный комплекс и томография",
        body: "Цифровой МРТ-томограф 1.5 Тесла с пониженным уровнем акустического шума. Анализы крови и C-реактивные тесты день в день.",
        tags: ["МРТ Siemens Magnetom", "Срочные экспресс-панели", "Цифровой архив DICOM"]
      },
      {
        id: "consulting",
        label: "Консультативное крыло",
        still: "assets/world/consulting.webp",
        clip: "assets/world/consulting.mp4",
        accent: "#1a4731",
        scroll: 1.3,
        linger: 0.35,
        eyebrow: "МЕЖДУНАРОДНЫЕ КЛИНИЧЕСКИЕ ПРОТОКОЛЫ",
        title: "Врачи доказательной практики",
        body: "Длительность консультаций от 30 до 60 минут. Никаких гомеопатических средств, БАДов и лишних анализов — только верифицированные методы.",
        tags: ["Приём 30–60 минут", "Терапия и Неврология", "Второе экспертное мнение"]
      },
      {
        id: "day_hospital",
        label: "Дневной стационар",
        still: "assets/world/day_hospital.webp",
        clip: "assets/world/day_hospital.mp4",
        accent: "#1e3d36",
        scroll: 1.3,
        linger: 0.35,
        eyebrow: "МАЛОИНВАЗИВНЫЕ МЕТОДИКИ",
        title: "Дневной стационар и реабилитация",
        body: "Светлые индивидуальные палаты с постоянным кардиомониторингом. Восстановительная терапия под непрерывным контролем ведущего врача.",
        tags: ["Персональный бокс", "Инфузионная терапия", "Контроль гемодинамики"]
      },
      {
        id: "digital_care",
        label: "Запись на приём",
        still: "assets/world/digital_care.webp",
        clip: "assets/world/digital_care.mp4",
        accent: "#11382d",
        scroll: 1.4,
        linger: 0.45,
        eyebrow: "ОНЛАЙН-РАСПИСАНИЕ",
        title: "Выберите специалиста и удобное время",
        body: "Мгновенное подтверждение без телефонных звонков. Электронная медкарта и доступ к протоколам осмотра сразу после приёма.",
        tags: ["Запись 24/7", "Связь с врачом", "Электронная карта"],
        cta: {
          primary: { label: "Выбрать врача и время", href: "#appointment" },
          secondary: { label: "Прейскурант услуг", href: "#services" }
        }
      }
    ],
    connectors: []
  });
})();
