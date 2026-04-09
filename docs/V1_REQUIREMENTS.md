# Personal Consistency Tracker — Version 1 Requirements Document

> **Document Version:** 1.0
> **Last Updated:** 2026-04-09
> **Status:** Draft

---

## Table of Contents

1. [Introduction](#1-introduction)
2. [Scope — What V1 Includes](#2-scope--what-v1-includes)
3. [A — Tracking System](#3-a--tracking-system)
4. [B — Data Management & Views](#4-b--data-management--views)
5. [C — Upgrade / Progression Logic](#5-c--upgrade--progression-logic)
6. [D — LLM Integration](#6-d--llm-integration)
7. [E — Web UI / Dashboard](#7-e--web-ui--dashboard)
8. [F — API Endpoints](#8-f--api-endpoints)
9. [Non-Functional Requirements](#9-non-functional-requirements)
10. [Out of Scope for V1](#10-out-of-scope-for-v1)
11. [Glossary](#11-glossary)

---

## 1. Introduction

### 1.1 Purpose

This document defines the **Version 1** requirements for the **Personal Consistency Tracker with AI Suggestions**. The application helps users build and maintain daily habits by tracking completion of duties tied to personal goals, computing consistency metrics, managing progressive difficulty upgrades, and providing AI-powered suggestions to help users improve.

### 1.2 Target Users

- Individuals who want to build and track daily habits.
- Self-improvement practitioners who follow progressive overload principles.
- Users who want AI-assisted coaching for habit formation.

### 1.3 Key Objectives

| # | Objective |
|---|-----------|
| O1 | Allow users to define personal goals and assign daily duties to each goal. |
| O2 | Provide daily logging of duty completion with a simple ✓/✗ interface. |
| O3 | Calculate and visualise consistency at daily, weekly, and monthly levels. |
| O4 | Implement an automatic upgrade/progression system based on sustained high consistency. |
| O5 | Integrate with LLM providers to generate personalised suggestions. |
| O6 | Deliver a responsive web UI that works on desktop and mobile. |

---

## 2. Scope — What V1 Includes

| Area | Included in V1 |
|------|----------------|
| Tracking System | ✅ Full daily logging, multiple goals, consistency calculation |
| Data Views | ✅ All 7 views (Goals & Duties, Daily Log, Weekly Analytics, Upgrade History, Monthly Growth, Progression Insights, Dashboard) |
| Upgrade Logic | ✅ Rule-based progression engine |
| LLM Integration | ✅ Multi-provider support (OpenAI, Anthropic, Google, Ollama) |
| Web UI | ✅ Responsive dashboard with charts, dark/light theme |
| API | ✅ RESTful endpoints for all core operations |
| Authentication | ❌ Deferred — single-user mode in V1 |
| Multi-user / Teams | ❌ Deferred to V2 |
| Mobile Native App | ❌ Deferred — responsive web only |
| Push Notifications | ❌ Deferred to V2 |

---

## 3. A — Tracking System

### 3.1 Goals

| Req ID | Requirement | Priority |
|--------|-------------|----------|
| TS-01 | Users can create, read, update, and delete **Goals**. | High |
| TS-02 | Each Goal has: Goal ID, Name, Purpose/Why, Current Duty, Difficulty, Priority, Status. | High |
| TS-03 | **Difficulty** levels: `Easy`, `Medium`, `Hard`, `Hard+`, `Elite`. | High |
| TS-04 | **Priority** levels: `High`, `Medium`, `Low`. | High |
| TS-05 | **Status** values: `Active`, `Paused`, `Completed`. | High |
| TS-06 | Only goals with status `Active` appear in the daily log by default. | Medium |

### 3.2 Duties

| Req ID | Requirement | Priority |
|--------|-------------|----------|
| TS-07 | Each Goal has exactly one **Current Duty** at any time. | High |
| TS-08 | A Duty is a free-text description of the daily action (e.g. "Read 30 min", "Run 5 km"). | High |
| TS-09 | When a duty is upgraded, the previous duty is archived in the Upgrade History. | High |

### 3.3 Daily Logging

| Req ID | Requirement | Priority |
|--------|-------------|----------|
| TS-10 | Users log each active goal as **✓ (done)** or **✗ (not done)** for a given date. | High |
| TS-11 | Users can optionally attach a **text note** to any daily log entry. | Medium |
| TS-12 | Only one log entry per goal per date is allowed (upsert behaviour). | High |
| TS-13 | The system tracks the date of each log entry. | High |

### 3.4 Consistency Calculation

| Req ID | Requirement | Priority |
|--------|-------------|----------|
| TS-14 | **Daily consistency %** = (goals completed / total active goals) × 100 for that day. | High |
| TS-15 | **Weekly consistency %** per goal = (days completed / 7) × 100 for a given ISO week. | High |
| TS-16 | **Monthly consistency %** per goal = (days completed / days in month) × 100. | High |
| TS-17 | **Overall consistency %** = average of daily consistency across the selected period. | High |

---

## 4. B — Data Management & Views

The application provides **seven logical views** (corresponding to "sheets" in the original specification). Each view is both an API resource and a UI page.

### 4.1 Goals & Duties View

Master reference of all goals.

| Field | Type | Description |
|-------|------|-------------|
| Goal ID | Auto-generated UUID | Unique identifier |
| Name | String (required) | Short goal name |
| Purpose / Why | Text | Motivation behind the goal |
| Current Duty | Text (required) | The active daily duty |
| Difficulty | Enum | `Easy` / `Medium` / `Hard` / `Hard+` / `Elite` |
| Priority | Enum | `High` / `Medium` / `Low` |
| Status | Enum | `Active` / `Paused` / `Completed` |
| Created At | Timestamp | When the goal was created |
| Updated At | Timestamp | Last modification time |

### 4.2 Daily Log View

Day-to-day tracking entries.

| Field | Type | Description |
|-------|------|-------------|
| Date | Date | The calendar date |
| Goal columns | Boolean per goal | ✓ (true) or ✗ (false) per active goal |
| Notes | Text (optional) | Free-form daily notes |
| Overall % | Computed | Daily consistency percentage |

**Acceptance Criteria:**
- AC-1: When all active goals are marked ✓, overall % = 100%.
- AC-2: Editing a past date's log recalculates that day's overall %.
- AC-3: Goals added mid-week do not penalise earlier days.

### 4.3 Weekly Analytics View

Analysis and AI-generated suggestions per week.

| Field | Type | Description |
|-------|------|-------------|
| Week | ISO Week identifier | e.g. "2026-W15" |
| Goal Name | String | The goal being analysed |
| Weekly Consistency % | Computed | Completion rate for the week |
| Status Indicator | Derived | ✅ (≥ 90%) / ⚠️ (70–89%) / ❌ (< 70%) |
| LLM Suggestion | Text | AI-generated suggestion for struggling goals |

**Rules for Status Indicators:**
- ✅ **On Track**: Weekly consistency ≥ 90%
- ⚠️ **Needs Attention**: Weekly consistency 70%–89%
- ❌ **Struggling**: Weekly consistency < 70%

### 4.4 Upgrade History View

Full record of every duty progression event.

| Field | Type | Description |
|-------|------|-------------|
| Upgrade # | Auto-increment | Sequential upgrade number per goal |
| Date | Timestamp | When the upgrade occurred |
| Goal Name | String | Associated goal |
| Previous Duty | Text | The duty before upgrade |
| New Duty | Text | The duty after upgrade |
| Previous Difficulty | Enum | Difficulty before upgrade |
| New Difficulty | Enum | Difficulty after upgrade |
| Consistency Before | Percentage | Consistency % at time of upgrade |
| Consistency After | Percentage | Consistency % after 1 week post-upgrade |
| Status | Derived | ✅ Good / ⚠️ Watch / ❌ Failed |
| Notes | Text (optional) | User or system notes |

**Post-Upgrade Status Rules:**
- ✅ **Good**: Post-upgrade consistency ≥ 80%
- ⚠️ **Watch**: Post-upgrade consistency 60%–79%
- ❌ **Failed**: Post-upgrade consistency < 60%

### 4.5 Monthly Growth View

Monthly upgrade readiness tracking.

| Field | Type | Description |
|-------|------|-------------|
| Month | String | e.g. "2026-04" |
| Goal Name | String | The goal |
| Previous Duty | Text | Duty at start of month |
| Current Consistency | Percentage | Consistency for the month so far |
| Weeks at ≥ 95% | Integer | Count of consecutive weeks ≥ 95% |
| Ready for Upgrade? | Boolean | true if ≥ 95% for ≥ 4 weeks |
| Proposed New Duty | Text (LLM-generated) | AI-suggested next duty |

### 4.6 Progression Insights View

Smart analysis combining historical data and AI.

| Section | Description |
|---------|-------------|
| Upgrade Performance Matrix | Success rate per goal, average consistency drop post-upgrade |
| Difficulty Progression Paths | Visualise the sequence of difficulty levels traversed per goal |
| Upgrade Safety Indicators | Risk assessment for proposed upgrades based on past patterns |
| Compounding Effect Analysis | How small, consistent improvements compound over time |
| Next Upgrade Recommendations | AI-generated prioritised list of goals ready for upgrade |

### 4.7 Dashboard View

At-a-glance summary.

| Widget | Description |
|--------|-------------|
| Overall Consistency % | Single number for the current period |
| Perfect Days | Count of days where all goals = ✓ |
| Current Goals Performance | Mini table of each active goal with its weekly % |
| Last 4 Weeks Trend | Sparkline or small line chart |
| Upgrade Readiness | List of goals approaching upgrade threshold |
| Progression Journey | Timeline of upgrades completed |

---

## 5. C — Upgrade / Progression Logic

### 5.1 Core Rules

```
IF weekly_consistency >= 95% AND consecutive_weeks_at_95 >= 4 THEN
    → Mark goal as "Ready for Upgrade"
    → Propose new duty with difficulty increased by 1 level
    → Examples:
        30 min → 45 min
        Basic → Advanced
        Daily → 2× Daily
        Easy → Medium, Medium → Hard, Hard → Hard+, Hard+ → Elite

ELSE IF weekly_consistency < 70% THEN
    → Flag goal as "Struggling"
    → Trigger LLM suggestion to modify current duty
        (reduce scope, restructure, change timing)

ELSE (70% – 94%)
    → Maintain current duty
    → Suggest small improvements via LLM
```

### 5.2 Upgrade Execution Flow

1. System detects upgrade readiness (rule above).
2. System (or LLM) proposes a new duty and new difficulty level.
3. User reviews and **confirms** or **modifies** the proposal.
4. Upon confirmation:
   - Current duty is archived in Upgrade History.
   - New duty becomes the active duty.
   - Consistency tracking resets for the new duty period.
5. After 1 week, the system evaluates post-upgrade consistency and assigns a status (✅/⚠️/❌).

### 5.3 Downgrade / Rollback

| Req ID | Requirement | Priority |
|--------|-------------|----------|
| UL-01 | If post-upgrade consistency is ❌ (< 60%) for 2 consecutive weeks, the system suggests reverting to the previous duty. | Medium |
| UL-02 | User can manually revert an upgrade at any time. | Medium |

---

## 6. D — LLM Integration

### 6.1 Supported Providers

| Provider | Models | Notes |
|----------|--------|-------|
| **OpenAI** | GPT-4, GPT-3.5-turbo | Cloud-based, requires API key |
| **Anthropic** | Claude 3 Opus, Sonnet, Haiku | Cloud-based, requires API key |
| **Google** | Gemini | Cloud-based, requires API key |
| **Ollama** | Any locally hosted model | Local/private, no API key needed |

### 6.2 Configuration

| Req ID | Requirement | Priority |
|--------|-------------|----------|
| LLM-01 | User can select the active LLM provider and model from a settings page. | High |
| LLM-02 | API keys are stored securely (environment variables or encrypted storage). | High |
| LLM-03 | Ollama endpoint URL is configurable (default: `http://localhost:11434`). | Medium |
| LLM-04 | The system gracefully falls back to rule-based suggestions if no LLM is configured or the LLM call fails. | High |

### 6.3 LLM-Powered Features

| Feature | Trigger | Output |
|---------|---------|--------|
| **Analyse Consistency Patterns** | Weekly analytics generation | Text summary of trends per goal |
| **Suggest Duty Modifications** | Goal flagged as ⚠️ or ❌ | Concrete suggestions to adjust the duty |
| **Assess Upgrade Readiness** | Goal reaches ≥ 95% for 4 weeks | Risk analysis and proposed new duty |
| **Identify Compounding Effects** | Monthly growth view | Narrative on cumulative improvements |
| **Personalised Motivation** | Dashboard load | Short motivational message based on recent performance |
| **Structured Recommendations** | Progression Insights view | Prioritised list of next actions |

### 6.4 Prompt Design (Internal)

- All LLM calls include the user's goal context: goal name, purpose, current duty, difficulty, and recent consistency data.
- Prompts follow a structured template to ensure deterministic, actionable output.
- Temperature is set low (0.3–0.5) for analytical tasks and moderate (0.7) for motivational content.

---

## 7. E — Web UI / Dashboard

### 7.1 General Requirements

| Req ID | Requirement | Priority |
|--------|-------------|----------|
| UI-01 | The UI must be **responsive** — fully functional on desktop (≥ 1024 px) and mobile (≥ 320 px). | High |
| UI-02 | Support **Dark** and **Light** themes, user-selectable, with preference persisted. | Medium |
| UI-03 | Touch-friendly navigation for mobile (hamburger menu, swipe gestures where appropriate). | Medium |
| UI-04 | All pages load within **2 seconds** on a standard broadband connection. | High |

### 7.2 Pages / Views

| Page | Route | Description |
|------|-------|-------------|
| Home / Dashboard | `/` | Overview with key metrics (Section 4.7) |
| Daily Log | `/log` | Interface to log today's duties; calendar to view past dates |
| Weekly Analytics | `/analytics/weekly` | Charts and AI suggestions per week |
| Monthly Growth | `/analytics/monthly` | Monthly upgrade readiness view |
| Upgrade History | `/upgrades` | Timeline and table of all upgrades |
| Progression Insights | `/insights` | AI-powered analysis dashboards |
| Goals Management | `/goals` | CRUD interface for goals and duties |
| Settings | `/settings` | LLM provider configuration, theme, data export |

### 7.3 Charts & Visualisation

| Chart Type | Used In | Purpose |
|------------|---------|---------|
| **Line Chart** | Dashboard, Weekly Analytics | Consistency trend over time |
| **Bar Chart** | Weekly Analytics, Monthly Growth | Per-goal weekly/monthly comparison |
| **Pie / Donut Chart** | Dashboard | Distribution of goal statuses |
| **Sparkline** | Dashboard (Last 4 Weeks Trend) | Compact trend indicator |
| **Timeline** | Upgrade History | Visual progression journey |

### 7.4 Data Export

| Req ID | Requirement | Priority |
|--------|-------------|----------|
| UI-05 | Export all data as **CSV**. | High |
| UI-06 | Export all data as **JSON**. | Medium |
| UI-07 | Export is available from the Settings page and covers all views. | Medium |

---

## 8. F — API Endpoints

All endpoints return JSON. Base path: `/api`.

### 8.1 Goals

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/goals/` | List all goals |
| POST | `/api/goals/` | Create a new goal |
| GET | `/api/goals/:id` | Get a single goal |
| PUT | `/api/goals/:id` | Update a goal |
| DELETE | `/api/goals/:id` | Delete a goal |

### 8.2 Duties

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/duties/` | List all duties (current and archived) |
| POST | `/api/duties/` | Create / assign a new duty to a goal |
| GET | `/api/duties/:id` | Get a single duty |
| PUT | `/api/duties/:id` | Update a duty |
| DELETE | `/api/duties/:id` | Delete a duty |

### 8.3 Daily Logs

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/logs/` | List log entries (supports `?date=YYYY-MM-DD` and `?goal_id=` filters) |
| POST | `/api/logs/` | Create or update (upsert) a daily log entry |
| GET | `/api/logs/:id` | Get a single log entry |
| DELETE | `/api/logs/:id` | Delete a log entry |

### 8.4 Analytics

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/analytics/weekly` | Weekly consistency data; supports `?week=2026-W15` and `?goal_id=` |
| GET | `/api/analytics/monthly` | Monthly growth data; supports `?month=2026-04` and `?goal_id=` |

### 8.5 Upgrades

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/upgrades/` | List all upgrade history records |
| POST | `/api/upgrades/` | Record a new upgrade event |
| GET | `/api/upgrades/readiness` | Get current upgrade readiness status for all active goals |
| GET | `/api/upgrades/:id` | Get a single upgrade record |

### 8.6 AI Suggestions

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/suggestions/` | Get AI suggestions for all struggling goals |
| GET | `/api/suggestions/:goal_id` | Get AI suggestion for a specific goal |
| POST | `/api/suggestions/generate` | Force-generate fresh suggestions |

### 8.7 Configuration

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/config/` | Get current LLM configuration (keys redacted) |
| PUT | `/api/config/` | Update LLM provider/model settings |

### 8.8 Data Export

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/export/?format=csv` | Export all data as CSV |
| GET | `/api/export/?format=json` | Export all data as JSON |

---

## 9. Non-Functional Requirements

| Category | Requirement |
|----------|-------------|
| **Performance** | API responses ≤ 500 ms (excluding LLM calls). LLM calls show a loading indicator. |
| **Availability** | The app runs as a self-hosted service; uptime depends on user infrastructure. |
| **Security** | API keys stored in environment variables or encrypted config. No secrets in source code. |
| **Data Persistence** | All data stored in PostgreSQL. Database migrations managed via an ORM. |
| **Containerisation** | Full Docker Compose setup for one-command deployment. |
| **Browser Support** | Latest 2 versions of Chrome, Firefox, Safari, Edge. |
| **Accessibility** | WCAG 2.1 AA compliance for core workflows (logging, viewing dashboard). |

---

## 10. Out of Scope for V1

The following features are explicitly **not** included in Version 1 but may be considered for future releases:

- Multi-user accounts and authentication/authorization
- Team/group goals and shared dashboards
- Native mobile applications (iOS/Android)
- Push notifications and reminders
- Social features (sharing, leaderboards)
- Offline-first / PWA mode
- Calendar integrations (Google Calendar, Outlook)
- Habit streaks and gamification badges
- Custom reporting and query builder

---

## 11. Glossary

| Term | Definition |
|------|------------|
| **Goal** | A personal objective the user wants to achieve (e.g. "Get fit", "Read more"). |
| **Duty** | The specific daily action tied to a goal (e.g. "Run 5 km", "Read 30 min"). |
| **Consistency %** | The percentage of days a duty was completed over a given period. |
| **Upgrade** | Increasing the difficulty or scope of a duty after sustained high consistency. |
| **LLM** | Large Language Model — an AI system used to generate suggestions and analysis. |
| **Progression** | The overall journey of moving through difficulty levels over time. |
| **ISO Week** | A week as defined by ISO 8601 (Monday–Sunday). |
