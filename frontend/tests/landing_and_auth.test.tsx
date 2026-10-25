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

  it("displays Google Sign In option and allows signing in with Google", async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ google_client_id: "" }),
    });

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

    await waitFor(() => {
      expect(screen.getByText("Sign up with Google")).toBeInTheDocument();
    });

    // Click Google Auth
    const googleBtn = screen.getByText("Sign up with Google");
    fireEvent.click(googleBtn);

    await waitFor(() => {
      expect(screen.getByText("Sign in with Google")).toBeInTheDocument();
      expect(screen.getByPlaceholderText("your.name@gmail.com")).toBeInTheDocument();
      expect(screen.getByText("Continue with Google")).toBeInTheDocument();
    });

    // Mock the backend Google auth response
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        token: "fake-google-jwt-token",
        user: { id: 10, username: "google_user", email: "google_user@gmail.com", auth_provider: "google" }
      }),
    });

    fireEvent.change(screen.getByPlaceholderText("your.name@gmail.com"), {
      target: { value: "google_user@gmail.com" }
    });
    fireEvent.click(screen.getByText("Continue with Google"));

    await waitFor(() => {
      expect(localStorage.getItem("sniff_token")).toBe("fake-google-jwt-token");
    });
  });

  it("navigates back to the landing page when signing out", async () => {
    // Pre-seed an authenticated user
    localStorage.setItem("sniff_token", "test-token");
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        user: { id: 1, username: "auditor", email: "auditor@recon.io" }
      }),
    });

    render(
      <AuthProvider>
        <MemoryRouter initialEntries={["/dashboard"]}>
          <LandingPage />
        </MemoryRouter>
      </AuthProvider>
    );

    await waitFor(() => {
      expect(screen.getByTitle("Sign Out")).toBeInTheDocument();
    });

    const signOutBtn = screen.getByTitle("Sign Out");
    fireEvent.click(signOutBtn);

    await waitFor(() => {
      expect(localStorage.getItem("sniff_token")).toBeNull();
      expect(screen.getByText("Start Scanning")).toBeInTheDocument();
    });
  });
});
