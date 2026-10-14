# PROPESA Platform — Color System Refinement

## Objective

Refine the existing PROPESA maritime operations platform so its colors match the official company logo while preserving the current interface design.

The platform is already working and its current layout is preferred. This is a **color-system refinement, not a redesign**.

The goal is a professional, marine-inspired, industrial dashboard: deep navy as the anchor, ocean blue for primary actions, and cyan as a restrained accent. Colors must be **proportional and consistent** rather than applied equally across every component.

## 1. Non-negotiable constraints

- Inspect the existing code and styles before editing.
- Preserve the current layout, sidebar structure, navigation, component hierarchy, spacing, sizing, typography, cards, charts, and workflows.
- Do not change JavaScript behavior, business logic, routes, data, or integrations.
- Do not rebuild components or introduce dependencies.
- Avoid broad, speculative redesigns. Make the smallest set of changes needed to establish the palette.
- Preserve existing responsive behavior and interaction states.
- If the project already has CSS variables/design tokens, update and reuse them instead of creating a competing system.
- Keep the official logo asset unchanged.

## 2. Brand palette

Use these colors as the starting point. Inspect the existing logo asset and adjust only if necessary to better match its actual navy and cyan.

| Token | Hex | Intended use |
|---|---|---|
| `--brand-navy` | `#0B1D59` | Sidebar, navigation shell, major brand surfaces |
| `--brand-blue` | `#087DBA` | Primary action buttons, active workflow banners, key links |
| `--brand-cyan` | `#16A6D1` | Small highlights, active indicators, progress fills, focus accents |
| `--bg-main` | `#111827` | Main application background |
| `--bg-surface` | `#1C2638` | Cards, panels, secondary surfaces |
| `--bg-surface-hover` | `#243249` | Hovered card/menu surface where needed |
| `--border-subtle` | `#2D3B50` | Quiet borders and separators |
| `--text-primary` | `#F1F5F9` | Primary text and important figures |
| `--text-secondary` | `#A9B7CA` | Secondary labels and supporting information |
| `--text-muted` | `#8293AA` | Tertiary metadata; do not use for essential information if contrast is too low |
| `--status-success` | `#22C55E` | Completed/success states |
| `--status-warning` | `#F59E0B` | Caution and warnings |
| `--status-danger` | `#EF4444` | Errors, critical problems, genuinely pending/overdue states |

The values are a starting point, not permission to recolor the whole interface indiscriminately. Check contrast and readability in the actual UI.

## 3. Required color proportions

Target this approximate visual balance across the overall application viewport:

- **60% dark neutral surfaces** — main background, cards, panels, inputs, and other large neutral areas.
- **30% deep navy** — sidebar and established navigation/brand surfaces.
- **8% ocean blue** — primary actions and selected operational elements.
- **2% cyan** — high-value accents only.

These are visual-area guidelines, not exact pixel quotas. Evaluate the overall screen at a glance and keep the interface predominantly dark. The cyan should feel intentional and scarce; it must not become a second background color. Ocean blue and cyan should not be used as large fills on every card or menu item.

Status colors (green, amber, red) are semantic and should remain limited to status indicators and relevant data. They are not part of the brand-color percentage calculation.

## 4. Component-level rules

### Sidebar and navigation
- Keep the existing deep navy sidebar.
- Keep the current selected-item shape, spacing, and hierarchy.
- Use a slightly lighter navy/blue surface for the selected item.
- Use a thin cyan left-edge indicator or similarly restrained accent for the active item.
- Use white/very light text for active and important labels; use readable blue-gray for secondary labels.
- Do not add cyan backgrounds to every navigation item.

### Main dashboard
- Use charcoal for the page background and slate for cards/panels.
- Create separation through subtle borders and surface contrast, not bright outlines or glows.
- Avoid pure black unless it is already essential to the design.

### Buttons and actions
- Use ocean blue for primary actions such as “Capturar cajas”.
- Keep button text high-contrast.
- Use cyan for small focus/hover details or selected indicators, not as the default fill for every button.
- Secondary buttons should remain neutral or outlined.

### Metrics, progress, and operational banners
- Keep important numbers easy to scan using primary text.
- Use cyan or ocean blue for progress fills and neutral active states.
- Keep red for errors/critical or genuinely pending states, amber for caution, and green for completed/success states.
- Do not use brand blue to replace meaningful status colors.

### Text, borders, and inputs
- Increase contrast where secondary labels are currently too dim.
- Use primary text for key data and secondary text for supporting labels.
- Use subtle blue-gray borders and clear focus states.
- Verify readable contrast for text on navy, charcoal, blue, and cyan backgrounds.

## 5. Interaction states

Apply the same palette consistently to:
- Default
- Hover
- Active/selected
- Focus-visible
- Disabled
- Loading
- Success, warning, and error states

Do not remove visible keyboard focus indicators. Disabled controls should remain distinguishable without becoming unreadable.

## 6. Implementation approach

1. Inspect the project structure and identify the stylesheet(s), theme tokens, and components responsible for colors.
2. Map existing colors to the new tokens.
3. Centralize colors in existing design tokens or CSS custom properties where practical.
4. Change only color-related declarations and any narrowly necessary contrast adjustments.
5. Remove conflicting hard-coded colors only when they directly undermine the palette.
6. Review the actual page at normal scale and verify the approximate 60/30/8/2 balance.
7. Check that the logo remains accurate and that the UI still looks like the existing product.
8. Test major views and states, including navigation, buttons, cards, progress indicators, warnings, and errors.

## 7. Acceptance criteria

The work is complete only when:

- The platform still has the same layout and behavior.
- Deep navy remains the dominant brand color in the sidebar/navigation.
- Ocean blue is used for a limited set of primary actions.
- Cyan appears as a restrained accent, approximately 2% of the overall visual area.
- The screen remains predominantly dark and easy to read.
- The logo and interface now feel like one cohesive brand.
- Red, amber, and green still communicate status rather than decoration.
- No new dependencies or unrelated changes have been introduced.
- The final response lists the files changed and summarizes the palette and any contrast adjustments.

## Final instruction

**Do not redesign the platform. Do not make every element blue or cyan. Preserve what already works and refine only the colors, with deliberate proportions and strong readability.**
