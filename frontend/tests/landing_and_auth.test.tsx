import React from "react";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { vi, describe, it, expect, beforeEach } from "vitest";
import LandingPage from "../src/pages/LandingPage";
import AuthModal from "../src/components/auth/AuthModal";
import { AuthProvider } from "../src/context/AuthContext";

const mockFetch = vi.fn();
global.fetch = mockFetch;

describe("Landing Page & Auth Flow", () => {
  beforeEach(() => {
    mockFetch.mockReset();
    localStorage.clear();
  });

  it("renders Landing Page with hero, start scanning CTA, and top right auth buttons", () => {
    render(
      <AuthProvider>
        <MemoryRouter>
          <LandingPage />
        </MemoryRouter>
      </AuthProvider>
    );

    // Brand and Hero
    expect(screen.getByText("Start Scanning")).toBeInTheDocument();
    expect(screen.getByText("Autonomous Web Recon &")).toBeInTheDocument();
    expect(screen.getByText("Sign In")).toBeInTheDocument();
    expect(screen.getByText("Create Account")).toBeInTheDocument();

    // Pipeline phases
    expect(screen.getByText("Target Ingestion & Headless SPA Recon")).toBeInTheDocument();
    expect(screen.getByText("Autonomous Orchestrator Dispatching")).toBeInTheDocument();
    expect(screen.getByText("Structural Feature Classification")).toBeInTheDocument();
    expect(screen.getByText("Semantic Vector Memory & RAG Retrieval")).toBeInTheDocument();
    expect(screen.getByText("Security Analysis & Groq LLM Reasoning")).toBeInTheDocument();
    expect(screen.getByText("Executive Security Audit & OWASP Scoring")).toBeInTheDocument();

    // OWASP Top 10
    expect(screen.getByText("OWASP Top 10 Security Matrix")).toBeInTheDocument();
    expect(screen.getAllByText("Broken Access Control").length).toBeGreaterThanOrEqual(1);
    expect(screen.getAllByText("Cryptographic Failures").length).toBeGreaterThanOrEqual(1);
  });

  it("opens AuthModal when clicking Start Scanning while unauthenticated", async () => {
    render(
      <AuthProvider>
        <MemoryRouter>
          <AuthModal />
          <LandingPage />
        </MemoryRouter>
      </AuthProvider>
    );

    const startScanBtns = screen.getAllByRole("button", { name: /start scanning/i });
    fireEvent.click(startScanBtns[0]);

    // AuthModal should pop up
    await waitFor(() => {
      expect(screen.getByText("Create Security Account")).toBeInTheDocument();
      expect(screen.getByPlaceholderText(/Choose a username/i)).toBeInTheDocument();
      expect(screen.getByPlaceholderText(/analyst@domain.com/i)).toBeInTheDocument();
    });
  });

  it("allows switching between Sign In and Create Account in AuthModal", async () => {
    render(
      <AuthProvider>
        <MemoryRouter>
          <AuthModal />
          <LandingPage />
        </MemoryRouter>
      </AuthProvider>
    );

    const signInBtn = screen.getByRole("button", { name: "Sign In" });
    fireEvent.click(signInBtn);

    await waitFor(() => {
      expect(screen.getByText("Sign In to Sniff")).toBeInTheDocument();
      expect(screen.getByPlaceholderText(/e\.g\. security_lead/i)).toBeInTheDocument();
    });
  });
});
