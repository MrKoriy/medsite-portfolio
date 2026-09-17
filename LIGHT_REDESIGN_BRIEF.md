# Light clinic redesign
User: redesign ALL pages around supplied warm light clinic videos. Change font and heavy panels/cards/tables. Keep two scroll videos and chapter title.

UI UX Pro Max used: medical clinic warm minimal -> accessible healthcare layout, readable 16px type, visible focus and 44px targets. Its teal palette does NOT fit user videos, so override with warm ivory #F7F5F0, white #FFFEFB, stone #EAE5DC, sage #48614F, ink #29332C, muted #62685F. Typography search verified Golos Text Cyrillic. Use self-hosted Golos Text variable font, fallback sans-serif.

Scope: all six frontend HTML pages including admin, shared CSS, video copy styling, assistant widget styling. Preserve API/data attributes, forms, navigation and backend. No new framework. Light editorial look with thin rules, generous whitespace, low-radius cards, no heavy glass or dark panels. Warm opaque chapter interlude. Keep title text. Desktop portrait videos un-stretched. Mobile compact editorial copy not a large dark card.

Fix malformed CSS tokens at beginning of existing style.css (variables outside :root). Replace old styles instead of accumulating overrides. Modular CSS files <=350 lines when practical. Existing media-review is untracked and must remain untouched. No git commits by agents.

Acceptance: all pages 375/390 and1440 no horizontal viewport overflow; readable loaded Cyrillic font; site/video colors coherent; scroll times advance/reverse and transition opaque; forms/nav selectors intact; JS syntax; backend tests. First make plan, then implement, review 4 lenses, parent independently browser-verifies.
