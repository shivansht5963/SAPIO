# 🎨 Frontend Developer Guide — Field Force Management System

> **For**: Frontend Developer  
> **Scope**: UI Design, Pages, Components, UX Patterns — **No API integration yet**  
> **Stack**: React (Vite) · Vanilla CSS / CSS Modules · React Router  
> **Priority**: Clean, modern, role-aware UI that feels professional and production-ready

---

## Table of Contents
1. [Design Philosophy & Principles](#1-design-philosophy--principles)
2. [Design System & Tokens](#2-design-system--tokens)
3. [Typography & Iconography](#3-typography--iconography)
4. [Layout Architecture](#4-layout-architecture)
5. [Pages & Screens](#5-pages--screens)
6. [Component Library](#6-component-library)
7. [Role-Based UI Behavior](#7-role-based-ui-behavior)
8. [User Flows](#8-user-flows)
9. [Responsive & Accessibility Guidelines](#9-responsive--accessibility-guidelines)
10. [Micro-Interactions & Animations](#10-micro-interactions--animations)
11. [Empty, Loading & Error States](#11-empty-loading--error-states)
12. [Folder Structure](#12-folder-structure)

---

## 1. Design Philosophy & Principles

### The Look & Feel
This is a **field operations management tool** — it should feel like a **modern SaaS dashboard** (think Linear, Notion, or Vercel Dashboard). Not a toy. Not a bootstrap template. Clean, confident, minimal but information-rich.

### Core Principles
| Principle | What It Means |
|---|---|
| **Clarity over decoration** | Every element must serve a purpose. No gratuitous gradients or shadows. |
| **Information density done right** | Dashboards show a lot of data — use whitespace, grouping, and hierarchy to keep it scannable. |
| **Role-aware experience** | The UI adapts to who is logged in. Agents see a simple, focused view. Admins see the full control panel. |
| **Feedback everywhere** | Every click, hover, and action gives visual feedback. No silent failures. |
| **Dark mode first** | Design with a sleek dark theme as the primary. Light mode is optional/secondary. |

---

## 2. Design System & Tokens

### Color Palette

> ⚠️ **Colors TBD** — Color scheme will be provided separately. Use the token names below as placeholders in your CSS variables.

```
/* ── Background Layers ── */
--bg-primary:       /* TODO */     /* Main background */
--bg-secondary:     /* TODO */     /* Cards, sidebar */
--bg-tertiary:      /* TODO */     /* Hover states, elevated surfaces */
--bg-elevated:      /* TODO */     /* Modals, dropdowns */

/* ── Accent / Brand ── */
--accent-primary:   /* TODO */     /* Primary actions, links, CTA buttons */
--accent-hover:     /* TODO */     /* Lighter accent on hover */
--accent-muted:     /* TODO */     /* Accent background tint (low opacity) */

/* ── Text ── */
--text-primary:     /* TODO */     /* Headings, primary text */
--text-secondary:   /* TODO */     /* Descriptions, secondary info */
--text-muted:       /* TODO */     /* Timestamps, metadata */
--text-inverse:     /* TODO */     /* Text on accent buttons */

/* ── Status Colors ── */
--status-pending:   /* TODO */     /* Amber-ish */
--status-assigned:  /* TODO */     /* Blue-ish */
--status-progress:  /* TODO */     /* Purple-ish */
--status-completed: /* TODO */     /* Green-ish */
--status-cancelled: /* TODO */     /* Red-ish */

/* ── Risk Flags ── */
--risk-low:         /* TODO */     /* Positive / safe */
--risk-medium:      /* TODO */     /* Warning / caution */
--risk-high:        /* TODO */     /* Danger / urgent */

/* ── Borders & Dividers ── */
--border-subtle:    /* TODO */     /* Very faint dividers */
--border-default:   /* TODO */     /* Normal borders */
--border-strong:    /* TODO */     /* Emphasized borders */

/* ── Shadows ── */
--shadow-sm:        /* TODO */     /* Subtle elevation */
--shadow-md:        /* TODO */     /* Medium elevation (cards) */
--shadow-lg:        /* TODO */     /* High elevation (modals) */

/* ── Spacing Scale ── */
--space-xs:   4px;
--space-sm:   8px;
--space-md:   16px;
--space-lg:   24px;
--space-xl:   32px;
--space-2xl:  48px;
--space-3xl:  64px;

/* ── Border Radius ── */
--radius-sm:  6px;
--radius-md:  10px;
--radius-lg:  16px;
--radius-full: 9999px;
```

### Surfaces & Cards
- Cards use `--bg-secondary` with `1px solid var(--border-subtle)`
- On hover: border transitions to `--border-default`, subtle `translateY(-1px)`
- Active/selected cards: left border accent `3px solid var(--accent-primary)`

---

## 3. Typography & Iconography

### Font
Use **Inter** from Google Fonts — it's the industry standard for dashboard UIs.

```
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

--font-family:    'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
```

### Type Scale

| Token | Size | Weight | Use Case |
|---|---|---|---|
| `--text-h1` | 28px | 700 | Page titles |
| `--text-h2` | 22px | 600 | Section titles |
| `--text-h3` | 18px | 600 | Card titles |
| `--text-body` | 14px | 400 | General text |
| `--text-body-medium` | 14px | 500 | Emphasized body text |
| `--text-small` | 12px | 400 | Timestamps, metadata, badges |
| `--text-caption` | 11px | 500 | Labels, overlines (uppercase, tracked) |

### Icons
Use **Lucide React** (`lucide-react` npm package):
- Consistent, clean, 24px default stroke icons
- Stroke width: 1.5px for sidebar, 2px for buttons
- Icons always paired with labels in navigation (never icon-only in sidebar)

---

## 4. Layout Architecture

### App Shell

```
┌──────────────────────────────────────────────────────┐
│  Top Bar (64px)                                      │
│  ┌──────┬───────────────────────────────────────────┐ │
│  │ Logo │ Page Title         User Avatar · Role Tag │ │
│  └──────┴───────────────────────────────────────────┘ │
├────────┬─────────────────────────────────────────────┤
│        │                                             │
│  Side  │           Main Content Area                 │
│  bar   │                                             │
│  240px │    ┌─────────────────────────────────────┐   │
│        │    │  Page content, cards, tables, etc.  │   │
│        │    └─────────────────────────────────────┘   │
│        │                                             │
│  Nav   │                                             │
│  Links │                                             │
│        │                                             │
│────────│                                             │
│  User  │                                             │
│  Info  │                                             │
└────────┴─────────────────────────────────────────────┘
```

### Top Bar (64px)
- **Left**: App logo/icon + app name "FFMS"
- **Center**: Current page title (breadcrumb style if nested, e.g., `Tasks / Task #42`)
- **Right**: 
  - Notification bell icon (badge count)
  - User avatar (initials circle if no photo)
  - User name + Role badge (e.g., `Shivansh · Admin`)
  - Dropdown on click: Profile, Settings, Logout

### Sidebar (240px, collapsible to 64px icon-only)
- Background: `--bg-secondary`
- Subtle left border or separator
- Links: icon + label, 44px height, rounded hover background
- Active link: `--accent-muted` background + `--accent-primary` text + left accent bar
- Collapse toggle button at bottom of sidebar
- Grouped with subtle section labels (overline text): "MAIN", "OPERATIONS", "INSIGHTS"

### Main Content Area
- Max width: `1200px`, centered with auto margins
- Padding: `var(--space-xl)` on all sides
- Page header area: title + subtitle + action buttons (right-aligned)

---

## 5. Pages & Screens

### 5.1 — Login Page

**Layout**: Centered card on a full-screen dark background with subtle gradient or mesh pattern.

**Elements**:
- App logo at top (centered, larger)
- "Welcome back" heading
- "Sign in to your account" subtext
- Username input field
- Password input field (with show/hide toggle)
- "Sign In" button (full width, accent color, large)
- Error message area (red border + text, animated slide-in)
- Footer: "Field Force Management System" subtle text

**Design Notes**:
- Background: subtle radial gradient from `--bg-tertiary` center to `--bg-primary` edges
- Card: `--bg-secondary`, rounded-lg, shadow-lg, `max-width: 400px`
- Inputs: dark backgrounds (`--bg-tertiary`), subtle borders, focus ring in accent color
- Button: solid `--accent-primary`, rounded, smooth hover darken transition

---

### 5.2 — Dashboard

**Layout**: Grid of stat cards at top + charts/tables below.

**Top Row — Stat Cards** (4 cards in a row):
| Card | Value | Icon | Color |
|---|---|---|---|
| Total Tasks | `142` | ClipboardList | accent |
| Pending | `38` | Clock | amber |
| Completed | `89` | CheckCircle | emerald |
| High Risk Visits | `7` | AlertTriangle | red |

Each stat card:
- Large number (28px, bold)
- Label below (12px, muted text)
- Small icon top-right, tinted with the card's accent
- Subtle accent-tinted left border or top border

**Middle Section — Two-Column Layout**:
- **Left (60%)**: "Recent Tasks" — mini table showing last 5-8 tasks (title, status badge, assignee, date)
- **Right (40%)**: "Task Status Distribution" — simple donut/pie chart or stacked horizontal bar

**Bottom Section**:
- "Recent Activity" — timeline-style list showing last 10 activity logs
  - Each item: avatar, action text, timestamp (relative: "2 hours ago")
  - Subtle connecting line between items

---

### 5.3 — Task List Page

**Page Header**:
- Title: "Tasks"
- Subtitle: "Manage and track all field operations tasks"
- Action button (top-right): "+ Create Task" (visible only for Admin/Manager/Lead)

**Filters Bar** (below header):
- Status dropdown: All, Pending, Assigned, In Progress, Completed, Cancelled
- Team dropdown: All Teams, Team Alpha, Team Beta...
- Region dropdown: All Regions, North, South, West
- Search input: "Search tasks..." with magnifying glass icon
- All filters in a single row, compact, with rounded pill-style dropdowns

**Task Table**:
| Column | Width | Notes |
|---|---|---|
| Title | 35% | Clickable → navigates to detail |
| Status | 12% | Color-coded badge/pill |
| Assigned To | 18% | Avatar circle + name |
| Due Date | 12% | Relative or formatted date, red if overdue |
| Team | 12% | Text |
| Priority/Risk | 11% | Color dot or flag (if visit has AI risk) |

**Table Design**:
- Rows: alternating `--bg-secondary` / `--bg-primary` backgrounds (very subtle)
- Hover: row background `--bg-tertiary`, cursor pointer
- Borders: only horizontal dividers (`--border-subtle`), no vertical borders
- Pagination at bottom: "Showing 1-10 of 142" + Prev / page numbers / Next

**Empty State** (if no tasks):
- Centered illustration or icon (ClipboardX)
- "No tasks found" heading
- "Try adjusting your filters or create a new task" subtext
- "+ Create Task" button

---

### 5.4 — Task Detail Page

**Layout**: Two-column on desktop, single column on mobile.

**Left Column (65%)** — Task Info Card:
- **Header**: Task title (h2) + Status badge + created date
- **Info Grid** (2×3 grid of label-value pairs):
  - Created By: avatar + name
  - Assigned To: avatar + name (or "Unassigned" in muted text)
  - Due Date: date (red if overdue)
  - Team: team name
  - Region: region name
  - Status: full lifecycle stepper (Pending → Assigned → In Progress → Completed)
- **Description**: full description text block
- **Actions bar** (bottom of card):
  - "Assign" button (if unassigned + user is Lead/Manager)
  - "Start Visit" button (if Agent + task is assigned to them + no active visit)
  - "Change Status" dropdown (if permitted)

**Right Column (35%)** — Visit & AI Panel:

**If no visit exists**:
- Empty card: "No visit recorded yet"
- "Start Visit" button (for Agent)

**If visit exists**:
- **Visit Status Card**:
  - Status badge (Started / Completed)
  - Start time
  - End time (if completed)
  - Duration (calculated)

- **Visit Notes Card** (if completed):
  - Raw notes text in a bordered text area (read-only look, monospace optional)

- **🤖 AI Insights Card** (if completed — this is the **showcase feature**):
  - Card title: "AI Analysis" with a sparkle/brain icon
  - Subtle accent gradient border or glow effect to make it stand out
  - **Summary**: AI-generated summary text
  - **Recommendation**: recommendation text with a lightbulb icon
  - **Risk Flag**: large color-coded badge
    - `Low` → green badge with check icon
    - `Medium` → amber badge with alert icon  
    - `High` → red badge with warning icon, pulsing subtle animation
  - Footer: "Generated by AI · Mock Analysis" in muted text

---

### 5.5 — Create Task Modal / Page

**Approach**: Full-page form or a slide-over panel from the right.

**Form Fields**:
| Field | Type | Required | Notes |
|---|---|---|---|
| Title | Text input | ✅ | Max 200 chars, char counter shown |
| Description | Textarea | ✅ | 4-5 rows, resizable |
| Assign To | Searchable dropdown | ❌ | Shows agents in scope (avatar + name + team) |
| Due Date | Date picker | ✅ | Cannot be in the past |
| Team | Dropdown | Auto | Auto-set if Lead, selectable if Manager/Admin |
| Region | Dropdown | Auto | Auto-set based on team or user scope |

**Actions**:
- "Create Task" primary button (accent)
- "Cancel" secondary button (ghost/outline)
- Success: toast notification + redirect to task list
- Validation errors: inline red text below each field

---

### 5.6 — Visit Update Form (Agent View)

**Start Visit**:
- Confirmation dialog/modal: "Start visit for Task: {title}?"
- "Confirm" button → creates visit record → page updates to show active visit timer

**Active Visit State** (on Task Detail page):
- A running timer showing elapsed time since visit start
- Pulsing green dot indicator: "Visit in progress"
- "Complete Visit" button

**Complete Visit Form** (modal or inline expansion):
- Large textarea: "Enter your visit notes..." (min 6 rows)
- Helper text: "Describe what happened during the visit. Be detailed — AI will analyze your notes."
- Character/word count shown
- "Submit & Complete" primary button
- After submission → AI Insights card renders with the results

---

### 5.7 — Activity Logs Page (Admin / Auditor)

**Page Header**:
- Title: "Activity Logs"
- Subtitle: "Complete audit trail of system actions"

**Filters**:
- Entity type dropdown: All, Task, Visit
- Action dropdown: All, Created, Assigned, Started, Completed, Status Changed
- Date range picker: From / To

**Log Table**:
| Column | Notes |
|---|---|
| Timestamp | Formatted: "May 20, 2026 · 2:34 PM" |
| User | Avatar + name |
| Action | Color-coded badge (created=blue, completed=green, etc.) |
| Entity | "Task #42" or "Visit #18" — clickable link |
| Description | Full human-readable description |

**Design**: 
- Timeline-style left border accent on each row
- Alternating row backgrounds
- Pagination: 20 per page

---

### 5.8 — Reports Page (Manager / Admin / Auditor)

**Layout**: 2×2 grid of report cards. Each card is a mini-report with a table.

**Report Card 1 — Pending Tasks by Region/Team**:
- Title: "Pending Tasks Overview"
- Table: Region | Team | Count
- Sorted by count descending
- Highlight rows with count > 10 (amber background tint)

**Report Card 2 — Avg Completion Time**:
- Title: "Agent Performance"
- Table: Agent | Avg Duration (mins) | Total Visits
- Sort by duration
- Color code: fast = green, slow = red

**Report Card 3 — Recent Visits (Last 7 Days)**:
- Title: "Visit Activity (Last 7 Days)"
- Daily breakdown: Date | Visits Completed
- Optionally a small sparkline or bar chart

**Report Card 4 — Task Status Distribution**:
- Title: "Task Distribution by Region"
- Table: Region | Pending | Assigned | In Progress | Completed | Cancelled
- Each status cell color-coded with the status color (subtle background)

---

## 6. Component Library

Build these as reusable components. Each should be self-contained and accept props.

### Core UI Components

| Component | Props | Notes |
|---|---|---|
| `Button` | variant (primary, secondary, ghost, danger), size (sm, md, lg), icon, loading, disabled | Accent bg for primary, border-only for secondary |
| `Badge` | color (green, amber, red, blue, purple, gray), text, size | Pill-shaped, used for statuses and risk flags |
| `Input` | type, label, placeholder, error, helperText, icon | Dark bg, focus ring, inline error |
| `Textarea` | label, rows, placeholder, charCount, error | Resizable, char counter |
| `Select` | label, options, placeholder, searchable | Dark bg dropdown, arrow icon |
| `Card` | title, subtitle, headerAction, children | Standard card wrapper with header bar |
| `Modal` | title, isOpen, onClose, children, actions | Centered overlay, backdrop blur |
| `Avatar` | name, size (sm, md, lg), src | Initials circle if no src, color generated from name |
| `Table` | columns, data, onRowClick, emptyState | Sortable headers, hover rows |
| `Pagination` | page, totalPages, onPageChange | Prev / numbered / Next |
| `Toast` | message, type (success, error, info, warning) | Auto-dismiss, slide-in from top-right |
| `Tooltip` | text, position | Dark tooltip with arrow |
| `Spinner` | size (sm, md, lg) | CSS-only loading spinner |
| `EmptyState` | icon, title, description, action | Centered empty state block |
| `StatCard` | label, value, icon, color, trend | Dashboard stat card |

### Domain-Specific Components

| Component | Description |
|---|---|
| `StatusBadge` | Renders task/visit status as a colored pill badge |
| `RiskFlag` | Renders risk level (Low/Medium/High) with icon + color |
| `TaskRow` | A single row in the task table with all columns |
| `ActivityItem` | A single log entry in timeline format |
| `AiInsightsCard` | The AI summary/recommendation/risk panel — the hero component |
| `VisitTimeline` | Shows visit lifecycle: started → in progress → completed with times |
| `UserInfo` | Avatar + name + role badge inline |
| `StatusStepper` | Horizontal step indicator showing task lifecycle progress |
| `SidebarLink` | Icon + label, active state, collapsible |
| `PageHeader` | Title + subtitle + action buttons layout |
| `FilterBar` | Row of filter dropdowns + search |

---

## 7. Role-Based UI Behavior

The UI must dynamically adapt based on the logged-in user's role. For now, use a **mock role variable** (hardcoded or from a context/state) to simulate this.

### Sidebar Navigation per Role

| Menu Item | Admin | Regional Mgr | Team Lead | Field Agent | Auditor |
|---|---|---|---|---|---|
| Dashboard | ✅ | ✅ | ✅ | ✅ | ✅ |
| Tasks | ✅ | ✅ | ✅ | ✅ (My Tasks) | ❌ |
| Visits | ✅ | ✅ | ✅ | ✅ (My Visits) | ❌ |
| Reports | ✅ | ✅ | ❌ | ❌ | ✅ |
| Activity Logs | ✅ | ❌ | ❌ | ❌ | ✅ |
| User Management | ✅ | ❌ | ❌ | ❌ | ❌ |

### Button / Action Visibility

| Action | Admin | Regional Mgr | Team Lead | Field Agent | Auditor |
|---|---|---|---|---|---|
| Create Task | ✅ | ✅ | ✅ | ❌ | ❌ |
| Assign Task | ✅ | ✅ | ✅ | ❌ | ❌ |
| Start Visit | ❌ | ❌ | ❌ | ✅ | ❌ |
| Complete Visit | ❌ | ❌ | ❌ | ✅ | ❌ |
| View AI Insights | ✅ | ✅ | ✅ | ✅ | ✅ |
| View Logs | ✅ | ❌ | ❌ | ❌ | ✅ |

### Dashboard Stat Differences

| Role | What They See |
|---|---|
| Admin | System-wide totals: all tasks, all visits, all risk flags |
| Regional Manager | Only their region's stats |
| Team Lead | Only their team's stats |
| Field Agent | Only their own: my tasks, my visits, my completions |
| Auditor | System-wide read-only stats + log summary |

---

## 8. User Flows

### Flow 1: Agent Completes a Visit
```
Login → Dashboard (sees "My Tasks: 5 pending")
  → Click task from dashboard or navigate to "My Tasks"
  → Task List (filtered to self)
  → Click task row → Task Detail Page
  → Click "Start Visit" → confirmation dialog → visit starts (timer shown)
  → Click "Complete Visit" → notes form appears
  → Type notes → "Submit & Complete"
  → AI Insights card appears with summary, recommendation, risk flag
  → Toast: "Visit completed successfully"
```

### Flow 2: Team Lead Creates & Assigns a Task
```
Login → Dashboard (sees team stats)
  → Click "Tasks" in sidebar
  → Task List Page → Click "+ Create Task"
  → Fill form: title, description, due date
  → Select agent from "Assign To" dropdown (only team members shown)
  → "Create Task" → toast: "Task created"
  → Redirected to Task List → new task appears at top
```

### Flow 3: Admin Reviews Logs
```
Login → Dashboard (system-wide stats)
  → Click "Activity Logs" in sidebar
  → Logs Page → filter by "Visit" + "Completed"
  → See all visit completion events with timestamps
  → Click entity link "Visit #18" → navigates to visit detail
```

### Flow 4: Auditor Views Reports
```
Login → Dashboard (read-only system stats)
  → Click "Reports" in sidebar
  → Reports Page → 4 report cards visible
  → Review "Agent Performance" report for avg completion times
  → Review "Pending Tasks Overview" for bottlenecks
```

---

## 9. Responsive & Accessibility Guidelines

### Breakpoints
| Name | Width | Layout Changes |
|---|---|---|
| Desktop | ≥ 1024px | Full sidebar + multi-column content |
| Tablet | 768–1023px | Sidebar collapses to icons, 2-column content |
| Mobile | < 768px | Sidebar becomes hamburger menu, single column, stacked cards |

### Responsive Rules
- **Sidebar**: Collapsible. On tablet: icon-only (64px). On mobile: hidden, accessible via hamburger icon in top bar.
- **Dashboard stat cards**: 4-column → 2-column (tablet) → 1-column (mobile)
- **Tables**: Horizontal scroll on mobile, with sticky first column
- **Task Detail**: 2-column → stacked single column on mobile (info card on top, visit/AI below)
- **Modals**: Full-screen on mobile, centered on desktop

### Accessibility (a11y)
- All interactive elements must be keyboard navigable (Tab, Enter, Escape)
- Focus rings visible on all focusable elements (accent color, 2px offset)
- Inputs have associated `<label>` elements (or `aria-label`)
- Color is never the sole indicator — always pair with text/icons (e.g., risk badge has icon + text + color)
- Buttons have descriptive text or `aria-label` (no icon-only buttons without labels)
- Modals trap focus and close on Escape
- Minimum contrast ratio: 4.5:1 for body text, 3:1 for large text
- All images/icons have `alt` or `aria-hidden`

---

## 10. Micro-Interactions & Animations

### Transition Defaults
```css
--transition-fast:   150ms ease;
--transition-base:   200ms ease;
--transition-slow:   300ms ease;
```

### Animation Catalog

| Element | Interaction | Animation |
|---|---|---|
| **Buttons** | Hover | Background lightens, subtle scale(1.02), 150ms |
| **Buttons** | Click | scale(0.97) press effect, 100ms |
| **Buttons** | Loading | Spinner replaces text, width preserved |
| **Cards** | Hover | translateY(-2px), shadow elevation increases, 200ms |
| **Sidebar links** | Hover | Background slides in from left, 150ms |
| **Sidebar links** | Active | Left accent bar slides in, 200ms |
| **Table rows** | Hover | Background tint, 100ms |
| **Modals** | Open | Backdrop fade-in (200ms) + modal scale(0.95→1) + opacity(0→1) (250ms) |
| **Modals** | Close | Reverse of open, 150ms |
| **Toast** | Appear | Slide down from top-right + fade in, 300ms |
| **Toast** | Dismiss | Slide up + fade out, 200ms, auto-dismiss after 4s |
| **Badges** | Appear | Scale pop: scale(0→1), 200ms with slight overshoot |
| **Risk: High** | Idle | Subtle pulse animation (opacity 1→0.7→1, 2s loop) |
| **Status stepper** | Progress | Filled bar width animates to new step, 400ms ease |
| **Page transitions** | Navigate | Content fades in (opacity 0→1, 200ms) + slight translateY(8→0) |
| **Sidebar** | Collapse/Expand | Width animates (240px ↔ 64px), labels fade, 250ms |
| **Filter dropdowns** | Open | Dropdown slides down + fades in, 150ms |
| **Visit timer** | Active | Pulsing green dot (CSS animation, 1.5s loop) |

### Loading Skeleton
When data is loading, show animated skeleton placeholders (shimmer effect):
- Rectangles for text lines
- Circles for avatars
- Rounded rectangles for badges
- Use CSS `@keyframes shimmer` with a gradient sweep

---

## 11. Empty, Loading & Error States

Every page and component that displays data must handle three states:

### Loading State
- Show skeleton loaders that match the layout of the actual content
- Skeleton colors: `--bg-tertiary` with shimmer from `--bg-secondary`
- Duration: show for minimum 300ms to avoid flash

### Empty State
| Page | Icon | Title | Description | Action |
|---|---|---|---|---|
| Task List | ClipboardX | No tasks found | Try adjusting your filters or create a new task | + Create Task |
| My Tasks (Agent) | CheckCircle | All caught up! | You have no pending tasks right now | — |
| Visits | MapPin | No visits recorded | Visit records will appear here when agents start visits | — |
| Logs | FileText | No activity yet | System activity will be logged here | — |
| Reports | BarChart3 | No data available | Reports will populate once tasks and visits are created | — |

### Error State
- Show a card with:
  - Red-tinted AlertTriangle icon
  - "Something went wrong" heading
  - Error detail text (if available)
  - "Try Again" button
- Network errors: "Unable to connect. Check your internet connection."
- 403: "You don't have permission to view this page."
- 404: "Page not found" with a "Go to Dashboard" button

---

## 12. Folder Structure

```
frontend/
├── public/
│   └── favicon.svg
├── src/
│   ├── assets/                    # Static assets (logos, illustrations)
│   │
│   ├── components/                # Reusable components
│   │   ├── ui/                    # Core UI primitives
│   │   │   ├── Button.jsx
│   │   │   ├── Button.css
│   │   │   ├── Badge.jsx
│   │   │   ├── Card.jsx
│   │   │   ├── Input.jsx
│   │   │   ├── Select.jsx
│   │   │   ├── Modal.jsx
│   │   │   ├── Table.jsx
│   │   │   ├── Pagination.jsx
│   │   │   ├── Toast.jsx
│   │   │   ├── Spinner.jsx
│   │   │   ├── EmptyState.jsx
│   │   │   ├── Skeleton.jsx
│   │   │   └── Tooltip.jsx
│   │   │
│   │   ├── domain/                # Domain-specific components
│   │   │   ├── StatusBadge.jsx
│   │   │   ├── RiskFlag.jsx
│   │   │   ├── AiInsightsCard.jsx
│   │   │   ├── TaskRow.jsx
│   │   │   ├── ActivityItem.jsx
│   │   │   ├── VisitTimeline.jsx
│   │   │   ├── UserInfo.jsx
│   │   │   ├── StatusStepper.jsx
│   │   │   └── StatCard.jsx
│   │   │
│   │   └── layout/                # Layout components
│   │       ├── AppShell.jsx       # Sidebar + TopBar + Content wrapper
│   │       ├── Sidebar.jsx
│   │       ├── TopBar.jsx
│   │       ├── PageHeader.jsx
│   │       └── FilterBar.jsx
│   │
│   ├── pages/                     # Page-level components
│   │   ├── Login.jsx
│   │   ├── Dashboard.jsx
│   │   ├── TaskList.jsx
│   │   ├── TaskDetail.jsx
│   │   ├── CreateTask.jsx
│   │   ├── Visits.jsx
│   │   ├── Reports.jsx
│   │   └── ActivityLogs.jsx
│   │
│   ├── context/                   # React context providers
│   │   ├── AuthContext.jsx        # User role, token, permissions (mock for now)
│   │   └── ToastContext.jsx       # Global toast notifications
│   │
│   ├── hooks/                     # Custom hooks
│   │   ├── useAuth.js
│   │   └── useToast.js
│   │
│   ├── data/                      # Mock data (until API integration)
│   │   ├── mockTasks.js
│   │   ├── mockVisits.js
│   │   ├── mockUsers.js
│   │   ├── mockLogs.js
│   │   └── mockDashboard.js
│   │
│   ├── utils/                     # Utility functions
│   │   ├── formatDate.js
│   │   ├── roleConfig.js          # Sidebar links, permissions per role
│   │   └── constants.js           # Status values, risk levels, etc.
│   │
│   ├── styles/                    # Global styles
│   │   ├── variables.css          # All design tokens
│   │   ├── reset.css              # CSS reset / normalize
│   │   ├── global.css             # Global element styles
│   │   └── animations.css         # Keyframe animations
│   │
│   ├── App.jsx                    # Router + context providers
│   ├── main.jsx                   # Entry point
│   └── index.css                  # Import all style files
│
├── index.html
├── package.json
└── vite.config.js
```

---

## Quick Reference: What to Build First

**Recommended build order** (UI-only, no API calls):

1. **Design tokens** → `variables.css`, `reset.css`, `global.css`, `animations.css`
2. **Core UI components** → Button, Badge, Card, Input, Select, Modal, Table, Spinner, EmptyState
3. **Layout** → AppShell, Sidebar, TopBar, PageHeader
4. **Mock data** → Fill `data/` folder with realistic fake data
5. **Auth context** → Mock auth with role switching (dropdown in header to simulate different roles)
6. **Login page** → Hardcoded auth, stores mock role
7. **Dashboard** → StatCards + Recent Tasks table + Activity timeline
8. **Task List** → FilterBar + Table + Pagination + Empty state
9. **Task Detail** → Info card + Visit panel + **AI Insights Card**
10. **Create Task** → Form with validation
11. **Activity Logs** → Table with filters
12. **Reports** → 4 report cards with tables

> **Tip for the frontend dev**: Add a hidden "Role Switcher" dropdown in the top bar during development. This lets you quickly switch between Admin/Manager/Lead/Agent/Auditor to verify that the UI adapts correctly for each role, without needing to log in and out.
