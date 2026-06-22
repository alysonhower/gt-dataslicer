# DataSlicer UI Design Contract

This is the source of truth for all DataSlicer desktop UI work. Future UI workers must use this contract before editing `src/gt_dataslicer/ui/web/*`. Do not re-read the source PDF for ordinary implementation decisions; the applicable product identity, visual tokens, component primitives, and guardrails are captured here.

## 1. Product Identity

- Visible product name: `DataSlicer`.
- Required descriptor: `Powered by Grant Thornton Brasil`.
- The header must preserve the product-name plus descriptor structure currently shown in `src/gt_dataslicer/ui/web/index.html`.
- The language switch remains a first-class header control with `pt-BR` and `en-US` options.
- DataSlicer is an IT product/app under Grant Thornton identity. Use the descriptor form `Powered by Grant Thornton (country name)`; for this repository the country name is `Brasil`.
- The product name may use Grant Thornton visual identity, but the UI must not invent or embed Grant Thornton logo assets.

## 2. Grant Thornton Identity Rules From PDF 1

- Corporate/sub-brand architecture allows an own product or sub-brand name with Grant Thornton identity when the product name is written in a GT Walsheim Black style and brand purple, in the Pantone 268 direction.
- For IT products/apps, the descriptor line option is `Powered by Grant Thornton (country name)` and must include the country name.
- Product wordmark treatment: text-only `DataSlicer`, visually comparable to GT Walsheim Black, core purple, bold, and simple. Do not add symbols around it.
- Descriptor treatment: GT Walsheim Regular style, black or corporate purple, visually subordinate but never tiny; keep it at least 25% of the product-name height when both appear together.
- Use generous white space, large purple headings, thin purple rules, teal outline or connector accents for structure and flow, and structured cards/tables with purple headers and pale rows.
- The Mobius symbol cannot be used standalone with this product/sub-brand treatment.
- The GT acronym should never be used externally in public-domain UI copy, product names, badges, iconography, screenshots, or assets. It may appear in this document only as a forbidden brand reference or as part of the font name `GT Walsheim`.
- Optional unique icon-style symbols are allowed by the brand architecture only when they are aligned and unique; this project has no approved icon asset, so implement none.

## 3. Implementation Tokens

Use the existing CSS variables as the palette. Do not introduce a new palette for UI work.

| Token | Value | Use |
| --- | --- | --- |
| `--purple` | `#4f2d7f` | Primary brand actions, active states, section rules, selected cards. |
| `--purple-dark` | `#32144f` | Main headings, strong card titles, high-emphasis text. |
| `--teal` | `#007f89` | Supporting accent for flow, drag state, running status, connectors, outlines. |
| `--red` | `#b3263a` | Errors, destructive states, validation failures. |
| `--ink` | `#1f1f22` | Primary body text. |
| `--muted` | `#5f6368` | Secondary text, helper copy, metadata. |
| `--line` | `#d7d2dd` | Borders, dividers, quiet card outlines. |
| `--surface` | `#ffffff` | Main panels and control surfaces. |
| `--surface-soft` | `#f6f4f8` | Page background, inset cards, secondary panels. |
| `--focus` | `#009ca6` | Visible keyboard focus rings only. |

Allowed contextual fills already present in CSS may continue only for their current roles: near-white card fill `#fbfafc`, pale teal drag fill `#eef9fa`, pale purple segmented fill `#f7f5fa`, pale red error fill `#fff4f5`, and technical-details fill `#f7f7f8`. New hardcoded colors are forbidden unless first added to `:root` and this table with a named semantic role.

Typography stack is fixed:

```css
font-family: "GT Walsheim", "Segoe UI", Arial, sans-serif;
font-size: 16px;
line-height: 1.45;
```

- Do not download, bundle, or reference proprietary font files.
- If GT Walsheim is unavailable, the app must fall back to `Segoe UI`, then `Arial`, then `sans-serif`.
- Headings use `--purple-dark`, compact line-height, and bold weight. Eyebrows, labels, active nav markers, and disclosure summaries use `--purple`.

Spacing, radius, and shadow primitives:

- Page shell: `--surface-soft` background with white topbar and a 4px purple bottom rule.
- Main workspace: centered, max-width approximately 1240px, two-column desktop layout with a sticky step rail; single-column layout below 900px.
- Standard panel: `padding: 22px`, `border: 1px solid var(--line)`, `border-radius: 8px`, `background: var(--surface)`.
- Standard card: `padding: 12px` to `16px`, `border: 1px solid var(--line)`, `border-radius: 8px`, `background: var(--surface-soft)` unless it is an interactive selected card.
- Compact controls use 6px radius; cards and panels use 8px radius; segmented controls may use 7px to preserve the current fit.
- Shadows are restrained. Use the existing selected-card shadow `0 1px 4px rgba(79, 45, 127, 0.18)` only for active/selected cards, not as decoration.
- Use the existing spacing rhythm: 4px, 6px, 8px, 10px, 12px, 14px, 16px, 18px, 20px, 22px, 24px, 32px, and 40px. Do not invent arbitrary visual spacing.

## 4. Layout And Composition Rules

- Keep the UI non-technical-first, bilingual, and practical. Use short task-oriented copy.
- Preserve the pipeline boundary: JavaScript may collect choices and render status, but Python/DuckDB remains the source of truth for filtering, query assembly, derived columns, summarization, CSV export, XLSX export, and Parquet export.
- Use white surfaces over a pale background, purple hierarchy, and teal only as a supporting flow/focus/accent color.
- Use cards to reduce cognitive load: each card has a label or heading, optional meta/help text, a body/control area, and optional action row.
- Details intended for support/debugging must stay behind collapsed `details` disclosure controls.
- Warnings and errors must be visible, specific, and friendly. Errors use `--red`, pale red fill, and no hidden-only treatment.
- ZIP passwords and secret-like values must never appear in visible progress, report cards, evidence examples, screenshots, logs, or persisted UI records.

## 5. Component Primitives

All future UI work must compose from these primitives or extend this contract first.

### Panels

- Use panels for each workflow step.
- Panel background is `--surface`; border is `--line`; radius is 8px; padding is 22px.
- Panel headings contain a purple eyebrow and `--purple-dark` title.
- Section actions align at the right on desktop and stack on narrow screens.

### Step Navigation

- Step rail uses white cards with a 4px transparent left rule by default.
- Active step uses `border-left-color: var(--purple)`, `--purple-dark` text, and bold weight.
- Step labels must be dynamically consistent with visible order when route mode changes.

### Route Cards

- Route cards are interactive label cards with hidden radio inputs, white surface, `--line` border, 8px radius, and at least 112px height.
- The selected route card uses `--purple` border and the restrained selected-card shadow.
- Titles use `--purple-dark`; supporting text uses `--muted`.
- Route cards must support keyboard focus through `:focus-within`.

### File Drop Zone

- The drop zone is the primary file selector surface.
- Use dashed `--purple` border, 8px radius, centered text, and `--purple-dark` copy.
- Drag state uses `--teal` border and pale teal fill.
- It must be clickable and keyboard operable with Enter and Space when it becomes the picker control.

### Summary Cards And File Summary Items

- File summary items, queue items, and small metric cards use `--surface-soft`, `--line` border, compact spacing, and overflow-safe text.
- Labels use `--purple`; values use `--ink` or `--purple-dark` for emphasis.
- Long paths and file names must wrap safely.

### Format Cards

- Format cards live inside a segmented pale-purple container.
- Inactive cards are transparent with `--ink` text and `--purple-dark` title.
- Active format cards use `--purple` fill, white title text, and selected-card shadow.
- Preserve radiogroup semantics and `aria-pressed` or equivalent state.

### Output Name Cards And Rows

- Output-name rows use the standard card border, 6px to 8px radius, soft surface, and grid alignment.
- Generated names should be visually calm, editable, and clearly tied to the input display name.
- Invalid names use red border or left rule plus pale red fill, with direct explanatory text.

### Derived-Column Cards

- Derived-column cards use `--surface-soft`, `--line` border, 8px radius, and 14px padding.
- Header includes derived title/preview and action controls.
- Preview text uses `--purple-dark`; summaries use `--ink`.
- Derived columns are post-filter projections. They must be validated and compiled in Python/DuckDB, never implemented as JavaScript-only data transforms.

### Progress Bars And Timeline

- Progress status cards use the standard card shell with clear phase title, current input/artifact, and a bounded timeline.
- Running state uses `--teal`; done state uses `--purple`; error state uses `--red`.
- Determinate progress bars are allowed only when the app knows a reliable percentage. DuckDB scan/export phases are indeterminate unless exact progress exists.
- Progress bars require accessible names and current values when determinate. Indeterminate bars require an accessible status description.
- Progress must never expose ZIP passwords, sensitive filters, or hidden full paths unless those paths are already explicitly visible elsewhere.

### Operator Tokens, Tooltips, And Focus States

- Visual filter operators use these display-only tokens: `=`, `≠`, `>`, `≥`, `<`, `≤`, `∈`, `∉`, `≤ x ≤`, `…x…`, `x…`, `…x`, `.*`, `∅`, and `≠ ∅`. Map them to stable operator IDs in JavaScript and backend payloads.
- Symbols must never become persisted backend DSL by accident.
- Every symbolic operator must expose localized plain-language meaning on mouse hover, keyboard focus, and screen-reader-accessible labels/descriptions.
- Hover-only explanations are forbidden.
- Focus states use a 3px solid `--focus` outline and 2px outline offset for buttons, selects, inputs, textareas, drop zone, format cards, route cards, step links, and column suggestions.

### Result Cards, Warnings, Errors, And Technical Details

- Result cards use a five-column desktop grid that collapses to one column below 900px.
- Result labels use muted text; result numbers and key values use `--purple-dark`.
- Warning and error cards must retain visible severity styling. Error states use `--red` and pale red fill.
- Technical details stay in collapsed disclosure, with bordered preformatted content for support/debugging only.

## 6. Accessibility Rules

- Every interactive control must be reachable and usable by keyboard.
- Visible focus states are mandatory and must use `--focus`; do not remove outlines.
- Symbolic operators need accessible labels or descriptions that include their plain-language meaning in the active language.
- Progress bars need accessible labels, determinate values when known, and clear indeterminate status text when values are unknown.
- Drag/drop must have a non-pointer path: click, Enter, and Space must trigger the same picker flow when the drop zone is the primary selector.
- Use `aria-live` for file summaries, warnings, queue changes, job status, and result updates where users need confirmation.
- Do not rely on color alone to communicate active, warning, error, or completion states.

## 7. Explicit Forbidden Items

- No external downloads for UI work.
- No bundled proprietary fonts, including no bundled GT Walsheim font files.
- No Grant Thornton logo asset, invented logo asset, standalone Mobius symbol, or product icon pretending to be an approved brand mark.
- No external-facing GT acronym in UI copy, product naming, assets, badges, or screenshots.
- No arbitrary new color palette, gradients, decorative illustrations, emojis-as-icons, or unrelated brand styles.
- No JavaScript-only data transforms, filtering, query assembly, summarization, CSV export, XLSX export, or Parquet export.
- No persisted, logged, or displayed ZIP passwords.
- No fake progress percentages.
- No tooltip-only operator explanations.
- No raw JSON or technical output as the default user-facing result state; keep it behind disclosure.

## 8. Implementation Checklist For Future UI Tasks

- Confirm every new color comes from a token in this file.
- Confirm every spacing value follows the existing rhythm or is added here first.
- Confirm every new card or control maps to a primitive above.
- Confirm product identity remains `DataSlicer` plus `Powered by Grant Thornton Brasil`.
- Confirm no Mobius, no external-facing GT acronym, no invented Grant Thornton assets, and no external downloads.
- Confirm keyboard, focus, accessible labels, warnings/errors, and progress semantics are implemented before claiming done.
- Confirm the Python/DuckDB pipeline remains the source of truth for data behavior.
