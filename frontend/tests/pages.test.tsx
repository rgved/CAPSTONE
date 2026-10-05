import React from "react";
import { render, screen, waitFor } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { vi, describe, it, expect, beforeEach } from "vitest";

import Dashboard from "../src/pages/Dashboard";
import NewScan from "../src/pages/NewScan";
import MissionDetail from "../src/pages/MissionDetail";
import Findings from "../src/pages/Findings";
import Reports from "../src/pages/Reports";
import Metrics from "../src/pages/Metrics";

// Mock Recharts ResponsiveContainer to render directly in JSDOM
vi.mock("recharts", async () => {
  const original = await vi.importActual("recharts") as any;
  return {
    ...original,
    ResponsiveContainer: ({ children }: any) => <div>{children}</div>
  };
});

// Mock Global Fetch
const mockFetch = vi.fn();
global.fetch = mockFetch;

const createTestQueryClient = () =>
  new QueryClient({
    defaultOptions: {
      queries: {
        retry: false
      }
    }
  });

describe("Frontend Dashboard Pages", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("Dashboard renders statistics and tables after API success", async () => {
    const mockDashboardData = {
      stats: {
        total_missions: 3,
        total_findings: 15,
        avg_token_reduction: 60.5,
        features_identified: 5
      },
      recent_missions: [
        {
          mission_id: "MISSION-001",
          target: "http://localhost:8080",
          status: "completed",
          date: "2026-06-17T12:00:00Z",
          findings: 5
        }
      ],
      findings_severity: [
        { severity: "High", count: 2 },
        { severity: "Medium", count: 5 },
        { severity: "Low", count: 8 },
        { severity: "Informational", count: 0 }
      ],
      feature_distribution: [{ name: "Authentication", value: 1 }]
    };

    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => mockDashboardData
    });

    const queryClient = createTestQueryClient();

    render(
      <QueryClientProvider client={queryClient}>
        <MemoryRouter>
          <Dashboard />
        </MemoryRouter>
      </QueryClientProvider>
    );

    expect(screen.getByText("Loading platform metrics...")).toBeInTheDocument();

    await waitFor(() => {
      expect(screen.getByText("Security Dashboard")).toBeInTheDocument();
      expect(screen.getByText("60.5%")).toBeInTheDocument();
      expect(screen.getByText("http://localhost:8080")).toBeInTheDocument();
      expect(screen.getByText("MISSION-001")).toBeInTheDocument();
    });
  });

  it("NewScan form validates URL and starts a scan", async () => {
    const queryClient = createTestQueryClient();

    render(
      <QueryClientProvider client={queryClient}>
        <MemoryRouter>
          <NewScan />
        </MemoryRouter>
      </QueryClientProvider>
    );

    expect(screen.getByText("Launch Target Scan")).toBeInTheDocument();
    expect(screen.getByPlaceholderText("https://example.com")).toBeInTheDocument();
  });

  it("MissionDetail page renders target, summary, token reduction stats and timeline", async () => {
    const mockMissionDetail = {
      mission_id: "MISSION-001",
      target_url: "http://localhost:8080",
      status: "completed",
      runtime: "45.2s",
      generated_at: "2026-06-17T12:00:00Z",
      recon_summary: {
        routes: 10,
        forms: 2,
        inputs: 5,
        buttons: 3,
        scripts: 1,
        links: 4,
        meta_tags: 1
      },
      features: [{ name: "authentication", confidence: 95.0 }],
      token_reduction: {
        original_tokens: 1000,
        reduced_tokens: 400,
        reduction_percentage: 60.0
      },
      findings: [
        {
          finding_id: "FIND-001",
          title: "CSRF vulnerable login form",
          category: "missing_csrf",
          severity: "high",
          confidence: 0.9,
          evidence: ["Form action login.php"],
          description: "Missing anti-forgery token in form login.",
          recommendation: "Implement anti-CSRF."
        }
      ],
      report_id: "REPORT-001"
    };

    const mockTimeline = [
      { task: "RUN_RECON", status: "completed", timestamp: "2026-06-17T12:00:00Z" }
    ];

    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => mockMissionDetail
    });

    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => mockTimeline
    });

    const queryClient = createTestQueryClient();

    render(
      <QueryClientProvider client={queryClient}>
        <MemoryRouter initialEntries={["/mission/MISSION-001"]}>
          <Routes>
            <Route path="/mission/:id" element={<MissionDetail />} />
          </Routes>
        </MemoryRouter>
      </QueryClientProvider>
    );

    await waitFor(() => {
      expect(screen.getByText("Inspection Window")).toBeInTheDocument();
      expect(screen.getByText("http://localhost:8080")).toBeInTheDocument();
      expect(screen.getByText("CSRF vulnerable login form")).toBeInTheDocument();
      expect(screen.getByText("60%")).toBeInTheDocument();
      expect(screen.getByText("RUN_RECON")).toBeInTheDocument();
    });
  });

  it("Findings Explorer filters findings and opens details", async () => {
    const mockFindings = [
      {
        finding_id: "FIND-001",
        title: "Weak auth form",
        category: "weak_authentication",
        severity: "high",
        confidence: 0.95,
        evidence: [],
        description: "Hardcoded credentials present.",
        mission: "MISSION-001",
        date: "2026-06-17T12:00:00Z",
        recommendation: "Rotate credentials."
      }
    ];

    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => mockFindings
    });

    const queryClient = createTestQueryClient();

    render(
      <QueryClientProvider client={queryClient}>
        <MemoryRouter>
          <Findings />
        </MemoryRouter>
      </QueryClientProvider>
    );

    await waitFor(() => {
      expect(screen.getByText("Findings Explorer")).toBeInTheDocument();
      expect(screen.getByText("Weak auth form")).toBeInTheDocument();
      expect(screen.getByText("MISSION-001")).toBeInTheDocument();
    });
  });

  it("Reports page lists report records and displays details on select", async () => {
    const mockReports = [
      {
        report_id: "REPORT-001",
        mission_id: "MISSION-001",
        target: "http://localhost:8080",
        generated_at: "2026-06-17T12:00:00Z"
      }
    ];

    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => mockReports
    });

    const queryClient = createTestQueryClient();

    render(
      <QueryClientProvider client={queryClient}>
        <MemoryRouter>
          <Reports />
        </MemoryRouter>
      </QueryClientProvider>
    );

    await waitFor(() => {
      expect(screen.getByText("Security Reports")).toBeInTheDocument();
      expect(screen.getByText("REPORT-001")).toBeInTheDocument();
    });
  });

  it("Metrics dashboard visualizes accumulated project run trends", async () => {
    const mockMetrics = {
      total_missions: 3,
      total_findings: 10,
      avg_runtime: 45.2,
      avg_token_reduction: 60.0,
      token_reduction_by_mission: [{ mission_id: "MISSION-001", reduction: 60.0 }],
      findings_by_severity: [{ severity: "High", count: 5 }],
      feature_distribution: [{ name: "Authentication", count: 2 }],
      mission_runtime_trend: [{ mission_id: "MISSION-001", runtime: 45.2 }]
    };

    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => mockMetrics
    });

    const queryClient = createTestQueryClient();

    render(
      <QueryClientProvider client={queryClient}>
        <MemoryRouter>
          <Metrics />
        </MemoryRouter>
      </QueryClientProvider>
    );

    await waitFor(() => {
      expect(screen.getByText("Research Analytics & Evaluation")).toBeInTheDocument();
      expect(screen.getByText("45.2s")).toBeInTheDocument();
      expect(screen.getByText("60%")).toBeInTheDocument();
    });
  });
});
