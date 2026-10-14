# PROPESA — User Settings Panel (iOS Settings-Inspired)

## Objective

Add a **Settings button in the upper-right area of the application header**. Clicking it should open a dedicated settings panel that feels organized like iOS Settings: a clean, focused panel with grouped settings, clear labels, and simple controls.

The first settings must be:
1. **Appearance:** switch between Dark mode and Light mode.
2. **Text size:** a horizontal slider that adjusts the application font size, with a visible current value/label.

The existing platform is already functional. Implement this as a focused feature addition, not a redesign.

## 1. Preserve the existing product

- Inspect the existing project and identify the header, global styles/theme system, and current component architecture before editing.
- Keep the current page layout, sidebar, navigation, operational cards, tables, workflows, and business logic unchanged.
- Do not replace or rebuild the dashboard.
- Do not introduce a new framework or dependency for a settings panel.
- Follow the project's existing styling conventions and use its current icon library if one is already installed.
- Make the smallest maintainable change that fits the existing application.

## 2. Settings button placement and behavior

- Add a clearly recognizable **Settings** control at the upper-right of the main application header, near the existing user/account controls.
- Use a gear/settings icon and a short label if the header has enough room. If space is limited, use an icon button with an accessible name and tooltip.
- Keep the button aligned with existing header controls; do not cover or displace important content.
- Clicking the control opens a settings panel. Clicking again, the close icon, or pressing Escape closes it.
- Clicking outside the panel should close it if consistent with the app's existing interaction patterns.
- Keep keyboard focus usable and visible. Return focus to the settings button when the panel closes.
- The panel must not cause the underlying page to navigate or lose unsaved operational work.

## 3. Panel design — inspired by iOS Settings

Create a polished, restrained settings surface with:
- A clear header titled **Configuración**, matching the application's Spanish UI.
- A close button in the top-right.
- Grouped sections with headings and short descriptions.
- Rounded setting rows/cards, subtle separators, comfortable spacing, and clear selected states.
- The existing PROPESA visual identity: deep navy, ocean blue, and restrained cyan accents. Do not make the entire panel bright blue.
- A layout that works on desktop and smaller screens. On desktop, use a right-side drawer or compact floating panel that feels native to the app. On mobile/narrow layouts, it can expand to nearly full width or full screen.
- Keep the settings panel visually separate from, but consistent with, the current dashboard.

Suggested grouping:
1. **Apariencia**
   - Theme selector: `Oscuro` / `Claro`
2. **Accesibilidad**
   - Text size slider
   - Current size label/value

Do not add unrelated settings or fake controls that do nothing.

## 4. Dark mode / Light mode

Provide a clear two-option selector, segmented control, or equivalent:
- `Oscuro`
- `Claro`

Requirements:
- Switching modes must immediately update the **entire application**, not just the settings panel.
- Dark mode should preserve the existing dark PROPESA look, using the existing navy/charcoal palette and brand accents.
- Light mode should be a complete, intentional theme with light neutral backgrounds, readable dark text, subtle borders, and the same PROPESA navy/ocean-blue/cyan accents.
- Do not implement light mode by merely turning the main background white while leaving white text, dark overlays, or dark-only borders in place.
- Update all major UI surfaces and states, including header, sidebar, cards, tables, forms, inputs, dropdowns, modal/drawer, hover/selected states, and status messages.
- Keep semantic status colors (success, warning, danger) meaningful in both themes.
- Ensure text and controls have accessible contrast in both modes.
- If the project already has a theme provider or CSS variables, use it. Otherwise, implement a centralized theme mechanism (for example, CSS custom properties and a theme attribute on the app root) rather than scattered per-component overrides.

## 5. Text-size slider

Add a horizontal slider with:
- Minimum: **12 px**
- Default: **14 px** (or the application's measured current base size if different; preserve the current default appearance)
- Maximum: **20 px**
- Step: **1 px**

Show a visible label such as `Tamaño del texto` and a current value such as `14 px`. Include useful endpoints or labels like `Pequeño` and `Grande` if they fit the design.

Requirements:
- Moving the slider updates text size immediately, so the user can preview the change without closing settings.
- Apply the setting consistently to the application, including navigation labels, card labels, tables, form controls, and body copy.
- Use a centralized CSS variable or equivalent scalable typography mechanism. Avoid applying a font-size to the entire root in a way that unintentionally breaks icon sizes, fixed-width controls, line heights, or layout.
- Use `rem`-based sizing or a root typography token where suitable; check that key headings and supporting labels scale proportionally.
- Allow the interface to reflow naturally at larger sizes. Prevent clipping, overlapping, and inaccessible controls.
- Do not scale logos or icons as if they were body text unless that is how the existing design system works.
- The slider must be keyboard accessible and display its current value to assistive technology.

## 6. Persistence and safe defaults

- Save the selected theme and text-size preference so they remain after refresh and when navigating between pages.
- Use the project's existing preference/settings storage if available. Otherwise, use `localStorage` for non-sensitive UI preferences.
- On first use, preserve the current default visual experience rather than unexpectedly switching themes or changing the current text size.
- Load stored preferences early enough to avoid a noticeable flash of the wrong theme where practical.
- If storage is unavailable, the settings should still work for the current session without crashing.

## 7. Suggested implementation pattern

Adapt this to the existing codebase rather than copying blindly.

- Define a single source of truth for theme and text-size preferences.
- Centralize theme colors using CSS variables/design tokens.
- Expose a theme setting at the app root, for example `data-theme="dark"` or `data-theme="light"`.
- Expose the chosen base text size as a CSS custom property, for example `--app-font-size`.
- Keep settings state synchronized with the actual UI and persisted preference.
- Avoid duplicate theme state in individual components.
- Avoid global CSS overrides that unintentionally affect third-party widgets.

## 8. Spanish UI copy

Use consistent Spanish labels:
- Button: `Ajustes`
- Panel title: `Configuración`
- Group: `Apariencia`
- Theme: `Tema`
- Options: `Oscuro`, `Claro`
- Group: `Accesibilidad`
- Slider: `Tamaño del texto`
- Slider endpoints: `Pequeño`, `Grande`
- Close button accessible label: `Cerrar configuración`

## 9. Acceptance checklist

Before finishing, verify:

- [ ] Settings button is visible and correctly aligned in the upper-right header.
- [ ] Clicking it opens and closes the settings panel.
- [ ] Escape closes the panel; keyboard focus remains usable.
- [ ] Dark/light switching updates the whole application immediately.
- [ ] Both themes have readable contrast across tables, forms, cards, navigation, and menus.
- [ ] Text-size slider works from 12 px to 20 px in 1 px increments.
- [ ] Current text-size value is visible.
- [ ] Text size changes throughout the app without breaking icons, logos, controls, or layout.
- [ ] Theme and text-size choices persist after refresh.
- [ ] Existing operational workflows and business logic still work.
- [ ] No unrelated layout redesign or dependency was introduced.

## Final instruction

Build a real, functional settings feature — not a static mockup. Preserve the current PROPESA interface and behavior, use the existing architecture, and implement the settings panel with careful responsive behavior, persistence, accessibility, and proportional text scaling. At the end, report the files changed, how preferences are stored, and which checks were performed.
