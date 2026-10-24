# Upcycle Compass website

The public website introduces the project before visitors enter the decision tool.
It uses the existing React, CSS/Tailwind, and i18next setup with no added dependencies.

## Pages

- `/#/`: home, what we do, audiences, mission introduction, process, and evidence labels.
- `/#/about`: who we are, the project origin, principles, and transparent modelling.
- `/#/mission`: the mission, commitments, and a roadmap labelled as goals.
- `/#/how-it-works`: a walkthrough of the tool and frequently asked questions.
- `/#/compass`: the existing decision workspace, including its offline preset fallback.

Hash navigation supports direct links on static hosting without extra server routes.
The original decision workflow, engine, data, and API contract are unchanged.

The decision workspace shares the homepage's ivory/forest-green tokens and Arial/serif
typography. Its header, numbered navigation, presets, forms, result cards, tables,
chart palette, evidence popovers, and memo follow the same visual system. The light
brand appearance is consistent even when the operating system uses dark mode.
All six core screens are available in the mobile bottom navigation; desktop navigation
stays available while scrolling. Changing screens returns to the top and moves focus
to the main content. The print memo retains its compact A4 styling.

English and Hindi content live in `web/src/locales/en.json` and `hi.json` under `site`.
Hindi content is a draft and still needs human language review. Existing safety text review rules remain in place.
Team members, credentials, partnerships, and measured environmental impact have not been invented.

## Motion and accessibility

The home-page entrance is staggered; below-the-fold content reveals once with IntersectionObserver.
Only opacity and transforms animate. Button feedback uses short CSS transitions; navigation and
the decision workspace stay immediate. Reduced-motion preferences disable decorative movement,
and content remains visible if IntersectionObserver is unavailable. Hover transforms are limited
to devices with a precise pointer and hover support.

Navigation has active-page states, a mobile disclosure button, keyboard focus indicators,
a skip link, and focus transfer on page changes. The layout adapts to narrow screens.
Real-device touch, screen-reader, and Hindi-reader reviews remain manual checks.

## Hero image

- Project asset: `web/public/images/circular-ingredients.webp`.
- Created using the built-in `image_gen` tool; converted to WebP for delivery.
- It is a conceptual editorial image, not a photograph of a real batch or team facility.

Final generation prompt:

> Use case: photorealistic-natural. Asset type: editorial hero photograph for Upcycle Compass, a science-led circular food website. Primary request: premium, tactile overhead food-material still life, a large shallow rustic ceramic bowl containing finely ground golden groundnut press cake flour, a small dark terracotta dish of rice bran, scattered peanuts in shells and a few whole almonds, with one fresh delicate green stem entering the composition. Arrange the bowls in a sculptural diagonal composition on a warm pale limestone work surface, beautifully lit by strong natural side light with long soft botanical shadows. Close detailed textures, earthy natural colors, olive green, oat beige, caramel, warm orange. Contemporary editorial food photography, sophisticated minimal art direction, crisp lifelike surfaces, no waste-bin imagery. Portrait 4:5 composition with all focal materials centered so it crops well. No text, no typography, no logos, no watermark, no humans.

## Checks

Run `npm test`, `npm run lint`, and `npm run build` from `web/`.
The navigation test covers public pages, the mobile menu, unknown-page fallback,
focus transfer, and entry into the workspace. Existing engine journey scripts now
open `/#/compass`; public navigation is covered separately.
