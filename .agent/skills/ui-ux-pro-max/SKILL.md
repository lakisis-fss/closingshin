---
name: ui-ux-pro-max
description: Master design system generator with 50+ styles, 21+ palettes, and 50+ fonts. Use when designing premium UI, creating design tokens, exploring aesthetics, or generating complete design system recommendations for any web/mobile app. Includes intelligent reasoning for different product categories.
allowed-tools: Read, Write, Edit, Glob, Grep, Bash, python
---

# UI/UX Pro Max

> **Ultimate Design Intelligence** - Modular design systems, curated palettes, and intelligent reasoning.
> **Philosophy:** High-contrast, premium-first, conversion-optimized, and accessibility-aware.

---

## 🎯 When to Use This Skill

- Creating a new design system from scratch
- Restyling an existing application to a specific aesthetic (e.g., Luxury, Minimalist, Cyberpunk)
- Generating design tokens (colors, typography, spacing, shadows)
- Planning page layouts and conversion patterns
- Audit and optimization of UI/UX for specific industries

---

## 🚀 Key Modules

### 1. Design System Generator (`scripts/design_system.py`)
Intelligent engine that combines:
- **Search**: Scans `data/` for matching products, styles, colors, and layouts.
- **Reasoning**: Applies logic based on the product category (SaaS, E-commerce, Lifestyle, etc.).
- **Persistence**: Generates `MASTER.md` and page-specific overrides in `design-system/` folder.

### 2. Assets & Data (`data/`)
- `products.csv`: Industry-specific design patterns.
- `styles.csv`: Detailed aesthetic definitions.
- `colors.csv`: Curated hex palettes.
- `typography.csv`: Font pairings and mood mapping.

---

## 🛠️ Usage Patterns

### Generate a complete Design System
Use the `design_system.py` script to get a comprehensive recommendation.

```bash
python .agent/skills/ui-ux-pro-max/scripts/design_system.py "SaaS Dashboard" "My Project"
```

### Apply a specific Style
Load the corresponding style from `data/styles.csv` and apply its attributes:
- **Spacing**: Use tokens like `--space-md` (16px), `--space-lg` (24px).
- **Shadows**: Use `--shadow-md`, `--shadow-lg` for depth.
- **Transitions**: Standard 150-300ms ease-in-out.

---

## ✅ Design Checklist (MANDATORY)

- [ ] **No Emojis as Icons**: Use SVG (Heroicons, Lucide, etc.).
- [ ] **Interactive States**: Every clickable element MUST have `cursor-pointer` and a hover transition.
- [ ] **Contrast**: Maintain minimum 4.5:1 ratio for readability.
- [ ] **Responsive**: Test at 375px, 768px, 1024px, and 1440px.
- [ ] **Accessibility**: Focus states must be visible; respect `prefers-reduced-motion`.

---

## 🔗 How to Invoke (Slash Command)

You can trigger this skill via the `/ui-ux-pro-max` workflow.

```
/ui-ux-pro-max "Luxury Perfume Landing Page"
```

---
**Version:** 2.0.0
**Coverage:** 50 Styles | 21 Palettes | 50 Fonts
