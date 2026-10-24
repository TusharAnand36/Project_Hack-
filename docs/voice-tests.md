# Voice input tests (website plan Phase 7)

Voice is an optional way to fill the "Describe in words" box. It never submits anything: the transcript goes into the editable text box, "Fill the form" fills the form, and the user presses Analyse.

## Automated (run on every `npm test` / `npm run e2e`)

| Check | Result |
|---|---|
| States idle → requesting → listening (live interim text) → processing → ready, `hi-IN` locale, transcript handed over for editing (mocked `SpeechRecognition`) | pass |
| Errors: `not-allowed` → "microphone blocked" (denied); silence → "no speech heard"; each offers Try again / Type instead | pass |
| No speech API (Firefox) → mic hidden, typing still works | pass |
| Chromium (headless) → mic offered | pass |
| Read-aloud offered only when a voice for the language exists | pass |

## Manual (needs real devices and a microphone, not possible from the build container)

Status: **not run yet**. Fill this table during rehearsal. Demo voice only if it worked in rehearsal (risk register: noisy hall).

Phrase A (en-IN): "Groundnut cake from Rajkot, about 48% protein, for a protein drink, no solvents"
Phrase B (hi-IN): "राजकोट की मूंगफली की खली, लगभग 48% प्रोटीन, प्रोटीन ड्रिंक के लिए"

| Browser / device | Lang | Quiet room: transcript usable without edits? | With background noise | Form filled correctly? | Notes |
|---|---|---|---|---|---|
| Chrome desktop | en-IN | | | | |
| Chrome desktop | hi-IN | | | | |
| Chrome Android | en-IN | | | | |
| Chrome Android | hi-IN | | | | |
| Safari iOS (14.5+) | en-IN | | | | |
| Safari iOS (14.5+) | hi-IN | | | | |
| Firefox desktop | — | mic hidden (expected) | — | text path works? | |

Privacy note shown next to the mic: the browser's speech service processes the audio (Chrome sends it to Google, Safari to Apple); do not say personal details.
