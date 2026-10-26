---
name: MUJ Campus AI Navigator
colors:
  surface: '#f7f9fb'
  surface-dim: '#d8dadc'
  surface-bright: '#f7f9fb'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#f2f4f6'
  surface-container: '#eceef0'
  surface-container-high: '#e6e8ea'
  surface-container-highest: '#e0e3e5'
  on-surface: '#191c1e'
  on-surface-variant: '#494454'
  inverse-surface: '#2d3133'
  inverse-on-surface: '#eff1f3'
  outline: '#7b7486'
  outline-variant: '#cbc3d7'
  surface-tint: '#6d3bd7'
  primary: '#6b38d4'
  on-primary: '#ffffff'
  primary-container: '#8455ef'
  on-primary-container: '#fffbff'
  inverse-primary: '#d0bcff'
  secondary: '#4648d4'
  on-secondary: '#ffffff'
  secondary-container: '#6063ee'
  on-secondary-container: '#fffbff'
  tertiary: '#006947'
  on-tertiary: '#ffffff'
  tertiary-container: '#00855b'
  on-tertiary-container: '#f5fff6'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#e9ddff'
  primary-fixed-dim: '#d0bcff'
  on-primary-fixed: '#23005c'
  on-primary-fixed-variant: '#5516be'
  secondary-fixed: '#e1e0ff'
  secondary-fixed-dim: '#c0c1ff'
  on-secondary-fixed: '#07006c'
  on-secondary-fixed-variant: '#2f2ebe'
  tertiary-fixed: '#6ffbbe'
  tertiary-fixed-dim: '#4edea3'
  on-tertiary-fixed: '#002113'
  on-tertiary-fixed-variant: '#005236'
  background: '#f7f9fb'
  on-background: '#191c1e'
  surface-variant: '#e0e3e5'
typography:
  headline-xl:
    fontFamily: Plus Jakarta Sans
    fontSize: 40px
    fontWeight: '700'
    lineHeight: 48px
    letterSpacing: -0.02em
  headline-xl-mobile:
    fontFamily: Plus Jakarta Sans
    fontSize: 30px
    fontWeight: '700'
    lineHeight: 38px
    letterSpacing: -0.02em
  headline-lg:
    fontFamily: Plus Jakarta Sans
    fontSize: 28px
    fontWeight: '700'
    lineHeight: 36px
    letterSpacing: -0.02em
  headline-md:
    fontFamily: Plus Jakarta Sans
    fontSize: 22px
    fontWeight: '600'
    lineHeight: 30px
    letterSpacing: -0.015em
  headline-sm:
    fontFamily: Plus Jakarta Sans
    fontSize: 18px
    fontWeight: '600'
    lineHeight: 26px
    letterSpacing: -0.01em
  body-lg:
    fontFamily: Plus Jakarta Sans
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 24px
  body-md:
    fontFamily: Plus Jakarta Sans
    fontSize: 14px
    fontWeight: '400'
    lineHeight: 20px
  body-sm:
    fontFamily: Plus Jakarta Sans
    fontSize: 12px
    fontWeight: '400'
    lineHeight: 18px
  label-lg:
    fontFamily: Outfit
    fontSize: 14px
    fontWeight: '600'
    lineHeight: 20px
    letterSpacing: 0.01em
  label-md:
    fontFamily: Outfit
    fontSize: 12px
    fontWeight: '600'
    lineHeight: 16px
    letterSpacing: 0.02em
  label-sm:
    fontFamily: Outfit
    fontSize: 11px
    fontWeight: '500'
    lineHeight: 14px
    letterSpacing: 0.04em
rounded:
  sm: 0.5rem
  DEFAULT: 1rem
  md: 1.5rem
  lg: 2rem
  xl: 3rem
  full: 9999px
spacing:
  gutter: 1rem
  gutter-mobile: 0.75rem
  margin: 1.5rem
  margin-mobile: 1rem
  space-xs: 0.25rem
  space-sm: 0.5rem
  space-md: 0.875rem
  space-lg: 1.25rem
  space-xl: 1.75rem
---

## Brand & Style

This design system expresses a friendly, hyper-refined, and luminous campus companion. The brand personality blends academic clarity with an approachable, contemporary softness—delivering wayfinding that feels intuitive, calm, and delightful rather than clinical or complex. Designed primarily for university students, faculty, and campus visitors navigating a sprawling campus, the UI evokes feelings of ease, discovery, safety, and modern precision.

The visual style merges soft-pastel minimalism with delicate glassmorphism. It takes inspiration from the spatial depth and crispness of Apple Maps, the typographically balanced restraint of Notion, and the micro-engineered polish of Linear. Translucent floating surfaces, pastel-tinted atmospheric blurs, and organic rounded contours produce a tactile, weightless interface that hovers effortlessly above cartographic backgrounds.

## Colors

The palette relies on luminous pastel accents anchored by soft neutral canvases:

- **Primary Accent (`#8b5cf6` - Soft Lavender):** Used for key interactive drivers, active states, glowing path polyline segments, and primary brand touchpoints.
- **Secondary Accent (`#6366f1` - Pastel Indigo):** Complements the lavender for multi-stop nodes, analytical indicators, and subtle gradient shifts.
- **Origin Waypoint (`#10b981` - Pastel Emerald):** Dedicated exclusively to origin markers, active starting points, and optimistic status metrics (e.g., optimal path found).
- **Destination Waypoint (`#f43f5e` - Pastel Rose / Coral):** Reserved strictly for destination markers, terminal breadcrumbs, and urgent campus alerts.
- **Neutrals & Surfaces:** Built on a layered foundation of `rgba(255, 255, 255, 0.88)` to `rgba(255, 255, 255, 0.96)` for frosted glass cards, paired with slate neutral scales for typography: `#0f172a` for primary copy, `#475569` for secondary text, and `#94a3b8` for muted metadata.
- **Borders:** Translucent strokes using `rgba(255, 255, 255, 0.7)` on light map regions and `rgba(139, 92, 246, 0.12)` for focused containers.

## Typography

The typographic hierarchy uses **Plus Jakarta Sans** for headlines and general body text, giving the app an open, welcoming, and ultra-contemporary voice. **Outfit** serves as the label and metadata face, delivering geometric precision and legible compactness across badges, algorithm stats, distance markers, and segmented navigation tabs.

- **Weight Discipline:** Headlines range from 600 (SemiBold) to 700 (Bold). Body copy sits strictly at 400 (Regular) and 500 (Medium) to maintain lightness without cluttering frosted surfaces.
- **Kerning and Scaling:** Display titles feature subtle negative tracking (`-0.02em`) to keep words tight and modern, while micro labels and stats leverage positive tracking (`+0.02em` to `+0.04em`) to ensure legibility on dynamic map tiles.

## Layout & Spacing

The interface employs a contextual viewport-overlay architecture. The base layer is a full-bleed, warm-toned pastel vector map canvas. UI panels, routing sheets, search bars, and floating controls exist as floating spatial components.

- **Mobile Viewports (<768px):** Navigation search and status bars float pinned to the top safe area with `margin-mobile` padding. Route discovery sheets dock at the bottom as collapsible bottom drawers with full horizontal bleed or `margin-mobile` floating edges.
- **Tablet / Desktop Viewports (≥768px):** The UI transitions to floating modal cards anchored to the top-left or side-docked left column (max width 420px), leaving unobstructed canvas visibility for the campus map.
- **Internal Component Spacing:** Follows a strict base-4 rhythm. Padding scales cleanly from `space-xs` (4px) for pill tags, to `space-md` (14px) for interactive inputs, up to `space-xl` (28px) for expanded route overview cards.

## Elevation & Depth

Visual hierarchy is communicated through translucent glassmorphic layering, subtle ambient color glow, and multi-tier drop shadows:

- **Level 1 (Inline Elements & Controls):** Badges, step counters, and segmented switches. Background is `rgba(255, 255, 255, 0.7)` with `backdrop-filter: blur(8px)`. Border is `1px solid rgba(255, 255, 255, 0.6)`. Shadow: `0 2px 6px -1px rgba(15, 23, 42, 0.04)`.
- **Level 2 (Floating Action Pills & Floating Buttons):** Zoom toggles, layer switchers, and quick-filter pills. Background is `rgba(255, 255, 255, 0.9)` with `backdrop-filter: blur(16px)`. Border is `1px solid rgba(255, 255, 255, 0.8)`. Shadow: `0 8px 24px -4px rgba(99, 102, 241, 0.08), 0 2px 6px -1px rgba(15, 23, 42, 0.04)`.
- **Level 3 (Modal Sheets & Route Summary Panels):** Primary floating sheets and routing directions. Background is `rgba(255, 255, 255, 0.92)` with `backdrop-filter: blur(24px)`. Border is `1px solid rgba(255, 255, 255, 0.9)`. Shadow: `0 20px 40px -8px rgba(139, 92, 246, 0.12), 0 4px 12px -2px rgba(15, 23, 42, 0.03)`.
- **Interactive Waypoint Glow:** Waypoint pins and navigation polyline pulses use soft-colored drop shadows (`box-shadow: 0 0 16px rgba(139, 92, 246, 0.35)` for path guides; `0 0 12px rgba(16, 185, 129, 0.4)` for Start; `0 0 12px rgba(244, 63, 94, 0.4)` for Destination).

## Shapes

The design uses an ultra-soft, rounded shape language (`roundedness: 3`).

- **Pill Geometry:** Search inputs, action buttons, filter tags, and floating controls utilize complete pill radiuses (`9999px`) to maintain a friendly, soft-touch hand feel.
- **Cards & Bottom Sheets:** Primary cards, sheet containers, and route preview modals feature `rounded-3xl` (24px to 28px on mobile, 32px on desktop), eliminating sharp architectural corners and reinforcing the cute, modern look.
- **Nested Inner Surfaces:** Nested list items, input fields inside cards, and algorithm stats panels scale proportionately to `rounded-2xl` (16px) to maintain harmonious concentric border curves.

## Components

### Buttons
- **Primary Action (Navigate / Start Route):** Lavender gradient background (`linear-gradient(135deg, #8b5cf6 0%, #6366f1 100%)`), text color pure white, pill-shaped, height 48px, subtle glow shadow `0 6px 16px rgba(99, 102, 241, 0.3)`. Active press downscales slightly (`scale(0.98)`).
- **Secondary Action:** Frosted glass pill (`bg-white/80`), subtle stroke `border border-purple-100/60`, text color slate-700, with a hover transition to `bg-white/95`.

### Chips & Filter Pills
- Floating horizontal list with 8px gaps.
- Inactive: Frosted translucent surface (`bg-white/70`, `border-white/50`), slate-600 text.
- Active: Soft lavender fill (`#f5f3ff`), lavender stroke (`border-violet-300`), text color `#7c3aed`, with a soft pastel dot indicator.

### Segmented Controls (Routing Modes: Walking / Shuttle / Accessible)
- Contained within an ultra-rounded track (`bg-slate-100/70` with `p-1`).
- Active segment: Pure white pill card with `shadow-sm`, sliding animated transition, and bold Outfit label styling.

### Input Fields (Origin & Destination Inputs)
- Floating grouped pill cards with frosted backdrops (`bg-white/90`).
- Left adornment displays a green dot (`#10b981`) for Start and a rose dot (`#f43f5e`) for Destination, linked visually by a vertical pastel dashed line.
- Text input: `font-size: 14px`, borderless with focus ring transitioning to a soft lavender halo. Includes a clear button (`✕`) in muted slate.

### Step-by-Step Route Breadcrumbs
- Vertical breadcrumb stepper with smooth connector lines.
- Completed and upcoming turns marked with soft lavender badges (`28px` diameter) housing directional arrow pictograms.
- Active instruction highlighted with an elevated glass card showing remaining distance in bold Outfit numericals.

### Interactive Glowing Path Markers & Polylines
- **Map Polyline:** Soft violet line with a semi-transparent lilac halo blur.
- **Start Node:** Emerald circular marker with a concentric pulsing radar ring.
- **Destination Node:** Coral pin with a gentle floating bounce animation and glowing shadow.

### Algorithm Performance Stats Panel
- Compact micro-card nested in route preview (`bg-violet-50/60`, `border border-violet-100/40`, `rounded-2xl`).
- Displays path calculation details (e.g., Dijkstra/A* path compute time, walking ETA, elevation gain, accessibility score).
- Labels styled in `label-sm` Outfit uppercase, and values displayed in high-contrast `headline-sm` with tabular numerals.