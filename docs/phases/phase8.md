# Phase 8 — Frontend Dashboard (React + Vite + TypeScript)

Status: Active

---

# Objective

Build a professional frontend dashboard for the Agentic Web Application Security Reconnaissance Platform.

The dashboard will become the primary interface for the platform.

Users should be able to:

* Launch scans
* Monitor scan progress
* View findings
* Read reports
* Explore missions
* View research metrics

The dashboard must consume data from the existing backend.

The dashboard must not:

* Perform security analysis
* Generate findings
* Run LLMs
* Access SQLite directly

All business logic remains inside the backend.

---

# Technology Stack

Frontend:

```text
React 19
Vite
TypeScript
```

UI Components:

```text
shadcn/ui
```

Icons:

```text
lucide-react
```

Charts:

```text
recharts
```

Routing:

```text
react-router-dom
```

Data Fetching:

```text
TanStack Query
```

Styling:

```text
TailwindCSS
```

Backend:

```text
Existing Python Backend
```

Database:

```text
SQLite
```

Memory:

```text
ChromaDB
```

---

# Design Inspiration

The UI should resemble:

```text
GitHub
Linear
Vercel
Burp Suite
Datadog
```

Avoid:

```text
Bootstrap style
AdminLTE
Corporate templates
Consumer landing pages
```

---

# Theme

Dark mode only.

---

Background

```css
#0B1220
```

---

Cards

```css
#111827
```

---

Borders

```css
#1F2937
```

---

Primary

```css
#3B82F6
```

---

Success

```css
#22C55E
```

---

Warning

```css
#F59E0B
```

---

Danger

```css
#EF4444
```

---

Text

```css
#F8FAFC
```

---

Muted Text

```css
#94A3B8
```

---

Typography

Font:

```text
Inter
```

Only.

---

# Project Structure

```text
frontend/

├── src/
│
├── pages/
│   ├── Dashboard.tsx
│   ├── NewScan.tsx
│   ├── MissionDetail.tsx
│   ├── Reports.tsx
│   ├── Findings.tsx
│   └── Metrics.tsx
│
├── components/
│   ├── layout/
│   │   ├── Sidebar.tsx
│   │   ├── Header.tsx
│   │   └── PageContainer.tsx
│   │
│   ├── cards/
│   │   ├── StatCard.tsx
│   │   ├── FindingCard.tsx
│   │   └── MissionCard.tsx
│   │
│   ├── charts/
│   │   ├── FindingsChart.tsx
│   │   ├── RuntimeChart.tsx
│   │   ├── FeatureChart.tsx
│   │   └── TokenReductionChart.tsx
│   │
│   └── tables/
│       ├── FindingsTable.tsx
│       ├── ReportsTable.tsx
│       └── MissionsTable.tsx
│
├── services/
│   ├── api.ts
│   ├── missions.ts
│   ├── findings.ts
│   ├── reports.ts
│   └── metrics.ts
│
├── hooks/
│
├── types/
│
└── App.tsx
```

---

# Layout

Global Layout:

```text
+------------------------------------------------------+
| Header                                               |
+------------------+-----------------------------------+
| Sidebar          | Main Content                      |
|                  |                                   |
| Dashboard        |                                   |
| New Scan         |                                   |
| Findings         |                                   |
| Reports          |                                   |
| Metrics          |                                   |
|                  |                                   |
+------------------+-----------------------------------+
```

Sidebar Width:

```text
280px
```

---

# Header

Left:

```text
Agentic Security Recon Platform
```

Right:

```text
Current Mission Count
Current Findings Count
```

---

# Navigation

Sidebar Entries:

```text
Dashboard
New Scan
Findings
Reports
Metrics
```

Use lucide-react icons.

---

# Page 1 — Dashboard

Purpose:

Platform overview.

---

## Top Statistics

Display four cards:

```text
Total Missions
Total Findings
Average Token Reduction
Features Identified
```

Each card:

```text
Value
Label
Small Trend Indicator
```

---

## Recent Missions

Table:

```text
Mission ID
Target
Status
Date
Findings
```

Latest first.

---

## Findings Overview

Chart:

```text
Findings By Severity
```

Use Bar Chart.

---

## Feature Distribution

Chart:

```text
Authentication
File Upload
Dashboard
Admin
Search
API
```

Use Pie Chart.

---

# Page 2 — New Scan

Purpose:

Launch a scan.

---

## URL Input

Placeholder:

```text
https://example.com
```

---

## Scan Button

Large primary button.

Text:

```text
Start Scan
```

---

## Validation

Must start with:

```text
http://
or
https://
```

Show error otherwise.

---

## Live Progress Tracker

Display:

```text
Recon
Feature Extraction
Efficient Fetch
Analysis
Report Generation
```

Each step:

```text
Pending
Running
Completed
Failed
```

Represent using:

```text
Timeline Component
```

---

# Page 3 — Mission Detail

Purpose:

Complete mission inspection.

Route:

```text
/mission/:id
```

---

## Section 1 — Mission Summary

Display:

```text
Mission ID
Target URL
Status
Runtime
Generated At
```

---

## Section 2 — Recon Summary

Cards:

```text
Routes
Forms
Inputs
Buttons
Scripts
Links
Meta Tags
```

---

## Section 3 — Feature Summary

Display:

```text
Feature Name
Confidence
```

Example:

```text
Authentication
97%
```

---

## Section 4 — Token Reduction Metrics

Display:

```text
Original Tokens
Reduced Tokens
Reduction Percentage
```

Example:

```text
2297

997

56.6%
```

This section must be highlighted because it supports the research contribution.

---

## Section 5 — Findings

Display findings as cards.

Collapsed:

```text
[MEDIUM]
Login Form Missing CSRF Protection
```

Expanded:

```text
Category
Severity
Confidence
Evidence
Description
Recommendation
```

---

## Severity Colors

High:

```css
#EF4444
```

Medium:

```css
#F59E0B
```

Low:

```css
#EAB308
```

Informational:

```css
#3B82F6
```

---

# Page 4 — Findings

Purpose:

Cross-mission finding explorer.

---

## Filters

Severity

```text
All
High
Medium
Low
Informational
```

Category

```text
missing_csrf
authentication
file_upload
dashboard
api
etc
```

Search Box:

```text
Search Findings...
```

---

## Findings Table

Columns:

```text
Finding ID
Title
Severity
Confidence
Mission
Date
```

---

## Finding Detail Drawer

Opens on click.

Displays:

```text
Title
Severity
Category
Confidence
Evidence
Description
Recommendation
```

---

# Page 5 — Reports

Purpose:

Read generated reports.

---

## Reports Table

Columns:

```text
Report ID
Mission ID
Target
Generated At
```

---

## Report Viewer

Display:

```text
Executive Summary

Coverage Summary

Severity Breakdown

Findings

Recommendations
```

Read-only.

---

## Findings Rendering

Render findings exactly as report agent produced them.

Do not regenerate.

Do not modify.

---

# Page 6 — Metrics

Purpose:

Research and evaluation dashboard.

---

## Metric Cards

Display:

```text
Total Missions

Total Findings

Average Runtime

Average Token Reduction
```

---

## Chart 1

```text
Token Reduction by Mission
```

Line Chart.

---

## Chart 2

```text
Findings by Severity
```

Bar Chart.

---

## Chart 3

```text
Feature Distribution
```

Pie Chart.

---

## Chart 4

```text
Mission Runtime Trend
```

Line Chart.

---

# Required Backend APIs

The frontend must consume APIs.

Do not access SQLite directly.

Required endpoints:

```text
GET  /api/dashboard

GET  /api/missions

GET  /api/missions/{id}

POST /api/scan

GET  /api/findings

GET  /api/reports

GET  /api/reports/{id}

GET  /api/metrics
```

---

# Empty States

If no scans exist:

```text
No missions found.

Start your first scan.
```

If no findings exist:

```text
No findings generated yet.
```

If no reports exist:

```text
No reports available.
```

---

# Performance Requirements

Initial load:

```text
< 2 seconds
```

Mission page:

```text
< 2 seconds
```

Reports page:

```text
< 1 second
```

---

# Testing Requirements

Create:

```text
frontend/tests/
```

Verify:

```text
Dashboard renders

Mission page loads

Findings page loads

Reports page loads

Metrics page loads

API calls succeed
```

---

# Out Of Scope

Do NOT implement:

```text
Authentication

User Accounts

RBAC

PDF Export

Notifications

Email

Multi-Tenant Support

Cloud Deployment
```

---

# Definition Of Done

Phase 8 is complete when:

✓ Dashboard loads

✓ User can launch scans

✓ Mission details are visible

✓ Findings are searchable

✓ Reports are readable

✓ Metrics are visualized

✓ Existing backend remains unchanged

✓ All frontend tests pass

✓ UI follows design specification

✓ Dashboard becomes primary interface

---

# Success Criteria

A user can:

1. Enter a URL
2. Start a scan
3. Watch progress
4. Review findings
5. Read reports
6. Analyze metrics

without opening SQLite, ChromaDB, or console logs.

The dashboard becomes the official interface for the platform.
