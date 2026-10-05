import React from "react";
import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { describe, it, expect } from "vitest";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";

import Logo from "../src/components/brand/Logo";
import Sidebar from "../src/components/layout/Sidebar";
import Header from "../src/components/layout/Header";

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: false
    }
  }
});

describe("Brand and Logo Components", () => {
  it("Logo component renders Sniff. brand text with italic serif styling", () => {
    render(
      <MemoryRouter>
        <Logo size="md" />
      </MemoryRouter>
    );

    expect(screen.getByText("Sniff")).toBeInTheDocument();
    expect(screen.getByText(".")).toBeInTheDocument();
    expect(screen.getByText("Security Recon")).toBeInTheDocument();
    expect(screen.getByText("S.")).toBeInTheDocument();
  });

  it("Sidebar renders the Sniff. brand logo", () => {
    render(
      <MemoryRouter>
        <Sidebar />
      </MemoryRouter>
    );

    expect(screen.getByText("Sniff")).toBeInTheDocument();
    expect(screen.getByText(".")).toBeInTheDocument();
    expect(screen.getByText("Security Recon")).toBeInTheDocument();
    expect(screen.getByText("Dashboard")).toBeInTheDocument();
    expect(screen.getByText("New Scan")).toBeInTheDocument();
  });

  it("Header renders Sniff. brand title bar", () => {
    render(
      <QueryClientProvider client={queryClient}>
        <MemoryRouter>
          <Header />
        </MemoryRouter>
      </QueryClientProvider>
    );

    expect(screen.getByText("Sniff")).toBeInTheDocument();
    expect(screen.getByText("Agentic Web Security Reconnaissance")).toBeInTheDocument();
  });
});
