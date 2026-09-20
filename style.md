ndigo Workspace

Overview

A calm, compact application UI built from white panels, a pale grey sidebar, fine borders and clear typography. Indigo identifies primary actions and selected tabs. Use the same design system across the whole project; choose each page layout according to its task.

Composition

Desktop: 250px sidebar beside a flexible white workspace with softly rounded top corners.

Header: title left, relevant actions right, thin bottom divider.

Content: 24px padding, 16px panel gaps and 24px section gaps.

Use tables for records, focused columns for forms, split panels for review, and grids for dashboards.

Keep account controls at the sidebar bottom. Add filters and tabs only where useful.

Mobile: navigation drawer, stacked panels, 16px padding and locally scrollable tables.

Colours and typography

Keep surfaces neutral. Reserve indigo for actions, links, focus and selection. Use green, amber and red only for meaningful status. Pair status colours with labels.

Use Inter throughout, falling back to system sans-serif. Load Inter explicitly if available; declaring it does not download the font. Titles are 24px semibold, section headings 16px semibold, body text 14px and metadata 12px. Use sentence case, subdued supporting text and tabular numerals for data.

Components

Navigation: 36–40px rows, 16px outline icons, light grey active background and a short dark left marker. Active tabs use indigo text and a 2px underline.

Buttons: compact rectangular controls with 9px corners. Primary: solid indigo/white. Secondary: white/neutral border. Ghost: transparent. Prefer one primary action per task area.

Forms: persistent labels, 40px outlined fields and helper text below. Keep related fields grouped and forms around 720px wide. Preserve input after errors.

Cards: white, 1px border, 12px corners and 16px padding. Separate inner sections with dividers rather than nested cards.

Tables: lightly tinted headers, thin row separators, 44px single-line or 56px two-line rows. Left-align text, right-align numbers. Use subtle hover backgrounds.

Dialogs and drawers: same white surface and borders, 16px corners, 24px padding, soft shadow and a subdued backdrop. Keep actions together in the footer.

Uploads and reviews: compact file rows with progress and errors. Place source documents beside editable values on desktop and stack on mobile. Highlight only fields needing attention.

Charts: thin charcoal and teal lines, faint gridlines, small labels and white tooltips. Keep metrics compact. Use actual data and clear units.

Effects and states

Keep ordinary panels flat. Use shadows only for floating elements. Hover changes colour or background, without movement. Use 150ms transitions and respect reduced-motion preferences. Show local loading, empty, error and disabled states. Errors include a recovery action. All controls need keyboard access and visible focus; dialogs manage focus and return it when closed. Use 44px touch targets on mobile and accessible text contrast.

Tailwind CSS

The following setup targets Tailwind CSS v4. Add it to the project's global stylesheet after Tailwind is installed for the chosen framework. The YAML above is documentation; Tailwind does not read it automatically. Keep these theme values synchronized with it. For an existing v3 project, map the same tokens into theme.extend instead of using @theme.

@import "tailwindcss";

@theme {
  --font-sans: "Inter", system-ui, sans-serif;
  --color-canvas: #f7f7f8;
  --color-surface: #ffffff;
  --color-subtle: #fafafa;
  --color-selected: #eeeeef;
  --color-ink: #111113;
  --color-muted: #68686f;
  --color-line: #e6e6e8;
  --color-brand: #3528f5;
  --color-brand-hover: #2b20d7;
  --color-brand-soft: #eeecff;
  --color-success: #16803c;
  --color-warning: #95620a;
  --color-danger: #c33434;
  --color-teal: #138e96;
  --radius-control: 9px;
  --radius-card: 12px;
  --radius-dialog: 16px;
  --radius-shell: 22px;
  --shadow-floating: 0 6px 20px rgb(0 0 0 / 8%);
}

@layer base {
  body {
    @apply bg-canvas font-sans text-sm text-ink antialiased;
    line-height: 1.45;
  }
}

Reusable class recipes

Apply these recipes in shared components. Combine button variants with the common button classes.

Component

Tailwind classes

App shell

min-h-dvh bg-canvas lg:grid lg:grid-cols-[250px_minmax(0,1fr)]

Desktop sidebar

hidden flex-col gap-1 p-4 lg:flex lg:sticky lg:top-0 lg:h-dvh

Workspace

min-w-0 border border-line bg-surface lg:rounded-t-shell

Page header

flex min-h-[68px] flex-wrap items-center justify-between gap-3 border-b border-line px-4 py-3 lg:px-6

Page body

space-y-6 p-4 lg:p-6

Page title

text-2xl font-semibold leading-tight tracking-tight

Section title

text-base font-semibold

Supporting text

text-xs text-muted

Card

rounded-card border border-line bg-surface p-4

Button base

inline-flex min-h-11 items-center justify-center gap-2 rounded-control px-3 text-sm font-medium transition-colors duration-150 motion-reduce:transition-none focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-brand disabled:pointer-events-none disabled:opacity-50 md:min-h-[34px]

Primary variant

bg-brand text-white hover:bg-brand-hover

Secondary variant

border border-line bg-surface text-ink hover:bg-subtle

Input

h-11 w-full rounded-control border border-line bg-surface px-3 text-sm placeholder:text-muted focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-brand md:h-10

Active navigation

flex min-h-10 items-center gap-2 rounded-lg border-l-2 border-ink bg-selected px-3 text-sm font-medium

Active tab

border-b-2 border-brand px-3 py-3 text-sm font-medium text-brand

Table wrapper

overflow-x-auto rounded-card border border-line bg-surface

Table row

border-b border-line hover:bg-subtle

Numeric cell

px-4 py-3 text-right tabular-nums

Dialog panel

w-full max-w-lg rounded-dialog border border-line bg-surface p-6 shadow-floating

Guardrails

Reuse shared tokens and components across all routes.

Adapt page structure to the workflow; do not repeat one dashboard everywhere.

No gradients, glass effects, heavy shadows, decorative hero sections or oversized headings.

Keep secondary controls neutral and reserve saturated colour for meaning.

Avoid excessive pills, nested cards, emoji icons and inconsistent spacing.

Keep narrow screens usable without shrinking desktop text or causing page-wide overflow.

Do not treat class recipes as complete behaviour: implement labels, focus management, mobile navigation and component states.

Tailwind reference: Theme variables.