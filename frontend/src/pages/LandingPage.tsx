import React, { useState, useEffect, useRef } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import {
  Shield,
  ArrowRight,
  Terminal,
  Cpu,
  Layers,
  Database,
  Search,
  FileCheck2,
  Lock,
  AlertTriangle,
  ChevronRight,
  Activity,
  LogOut,
  Sliders,
  CheckCircle2,
  Radar
} from "lucide-react";

interface TimelinePhase {
  id: number;
  phase: string;
  name: string;
  icon: React.ComponentType<{ className?: string }>;
  agent: string;
  color: string;
  badge: string;
  description: string;
  inputs: string;
  outputs: string;
  techniques: string[];
}

const TIMELINE_PHASES: TimelinePhase[] = [
  {
    id: 1,
    phase: "Phase 1",
    name: "Target Ingestion & Headless SPA Recon",
    icon: Radar,
    agent: "Recon Worker Agent",
    color: "#38BDF8",
    badge: "DOM Discovery",
    description: "Cores through multi-page websites and modern Single-Page Applications (React, Vue, Next.js). Discovers clickable links, parses interactive forms, input elements, buttons, and extracts external scripts and CDNs.",
    inputs: "Seed Target URL + Crawl Depth / Page Budget Limit",
    outputs: "Structured Routes, Forms, Input Types, Buttons, Script Hashes",
    techniques: ["SPA Client-side Route Discovery", "Recursive Same-Domain Crawling", "Form & Input Extraction", "Subresource Integrity Verification"]
  },
  {
    id: 2,
    phase: "Phase 2",
    name: "Autonomous Orchestrator Dispatching",
    icon: Cpu,
    agent: "Smart Orchestrator",
    color: "#818CF8",
    badge: "Task FSM Engine",
    description: "Operates as the central deterministic mission controller. Decouples exploration from deep analysis, instantiates task states, bounds token and execution budgets, and guarantees mission isolation.",
    inputs: "Discovered URL Topology + Security Mission Objective",
    outputs: "Isolated Task Work Orders with Execution Deadlines",
    techniques: ["Finite State Machine (PENDING → RUNNING → COMPLETED)", "Domain & Session Isolation", "Runtime Throttling & Fallback Recovery"]
  },
  {
    id: 3,
    phase: "Phase 3",
    name: "Structural Feature Classification",
    icon: Layers,
    agent: "Feature Extraction Agent",
    color: "#34D399",
    badge: "Capability Mapping",
    description: "Scrutinizes HTML structures, form actions, authentication tokens, file inputs, and API endpoints to categorize web capabilities with mathematically normalized confidence scores.",
    inputs: "Raw Recon DOM Metadata and Form Topologies",
    outputs: "Feature Matrix: Auth, API, File Upload, Admin Panels, Input Fields",
    techniques: ["Heuristic Attribute Weighting", "Action URL & Name Attribute Profiling", "Normalized 0-100% Confidence Scoring"]
  },
  {
    id: 4,
    phase: "Phase 4",
    name: "Semantic Vector Memory & RAG Retrieval",
    icon: Database,
    agent: "ChromaDB Vector Store",
    color: "#FBBF24",
    badge: "Cosine RAG Search",
    description: "Embeds discovered routes, technical attributes, and past finding contexts into localized SQLite and ChromaDB vector collections for lightning-fast similarity lookup across reconnaissance missions.",
    inputs: "Classified Capabilities & Endpoint Text Payloads",
    outputs: "Contextual RAG Augmentation for LLM Reasoning",
    techniques: ["Domain-Isolated Collections", "Cosine Proximity Search", "Reconnaissance Deduplication", "Cross-Mission Attack Path Memory"]
  },
  {
    id: 5,
    phase: "Phase 5",
    name: "Security Analysis & Groq LLM Reasoning",
    icon: Search,
    agent: "Security Analysis Agent",
    color: "#FB7185",
    badge: "AI Threat Reasoning",
    description: "Leverages high-speed Groq Llama 3 models to perform deep vulnerability reasoning over verified attack vectors—pinpointing CSRF omissions, insecure file uploads, exposed endpoints, and header misconfigurations.",
    inputs: "Augmented Attack Surface Vectors + DOM Evidence Extracts",
    outputs: "Verified Security Findings with Reasoning Chains & Code Evidence",
    techniques: ["Zero Token Bloat Prompting", "Ground-Truth Evidence Verification", "Anti-Hallucination Schema Enforcement", "Vulnerability Risk Triage"]
  },
  {
    id: 6,
    phase: "Phase 6",
    name: "Executive Security Audit & OWASP Scoring",
    icon: FileCheck2,
    agent: "Report Agent & Risk Scorer",
    color: "#A78BFA",
    badge: "Audit & Mitigation",
    description: "Aggregates verified findings, ranks the prioritized attack surface according to exploitability, assigns CVSS 3.1 severity metrics (Critical, High, Medium, Low), and generates remediation advisories.",
    inputs: "Ranked Findings + Capability Confidence Scores",
    outputs: "Comprehensive Security Report, CVSS Metrics, Mitigation Checklist",
    techniques: ["CVSS 3.1 Severity Scoring", "Attack Surface Ranking (Depth & Query Weights)", "Actionable Developer Remediation Steps"]
  }
];

interface OwaspItem {
  id: string;
  code: string;
  name: string;
  severity: "Critical" | "High" | "Medium";
  description: string;
  howSniffDetects: string;
  evidenceTriggers: string[];
  remediation: string;
}

const OWASP_TOP_10: OwaspItem[] = [
  {
    id: "a01",
    code: "A01:2021",
    name: "Broken Access Control",
    severity: "Critical",
    description: "Failures that allow unauthorized information disclosure, modification, or destruction of data outside the user's intended permissions.",
    howSniffDetects: "Discovers unauthenticated administrative endpoints, shadow API routes, and parameter-based role tampering opportunities across crawled routes.",
    evidenceTriggers: ["/admin or /dashboard exposed without auth wall", "Sensitive endpoints reachable via direct GET requests", "Insecure role parameters in forms"],
    remediation: "Enforce strict server-side access control checks; deny by default; disable web server directory listing."
  },
  {
    id: "a02",
    code: "A02:2021",
    name: "Cryptographic Failures",
    severity: "High",
    description: "Flaws related to cryptography (or lack thereof), which frequently lead to exposure of sensitive user credentials and confidential data in transit.",
    howSniffDetects: "Flags plaintext HTTP form submission targets, sensitive password fields without TLS enforcement, and missing HSTS security headers.",
    evidenceTriggers: ["Form action using http:// instead of https://", "Password and token fields transmitted unencrypted", "Missing Strict-Transport-Security header"],
    remediation: "Enforce HTTPS with HSTS; apply modern TLS 1.3 encryption; store passwords using salted hashing (SHA-256 or bcrypt)."
  },
  {
    id: "a03",
    code: "A03:2021",
    name: "Injection (SQLi / XSS / Command)",
    severity: "Critical",
    description: "Hostile data sent to an interpreter as part of a command or query, tricking the interpreter into executing unintended commands or accessing data.",
    howSniffDetects: "Extracts all user input surfaces, URL search parameters, search bars, and textarea inputs that accept unsanitized dynamic user inputs.",
    evidenceTriggers: ["Unvalidated query parameters reflected in DOM", "Input forms lacking input type constraints", "Dynamic script execution without sanitization"],
    remediation: "Use parameterized queries, modern ORMs, and context-aware HTML output encoding; apply strict Content-Security-Policy (CSP)."
  },
  {
    id: "a04",
    code: "A04:2021",
    name: "Insecure Design",
    severity: "High",
    description: "Risks related to design flaws and architectural weaknesses that cannot be fixed by a simple implementation patch alone.",
    howSniffDetects: "Evaluates business logic flaws such as unrestricted file upload inputs with no MIME validation or rate-limiting parameters on sensitive forms.",
    evidenceTriggers: ["File upload forms without accept attribute or size constraints", "Login forms lacking brute-force throttling or CAPTCHA"],
    remediation: "Establish secure development lifecycles, threat modeling, and robust architectural defense-in-depth patterns."
  },
  {
    id: "a05",
    code: "A05:2021",
    name: "Security Misconfiguration",
    severity: "High",
    description: "Missing security hardening, default credentials, verbose error stack traces, and unconfigured or missing HTTP security response headers.",
    howSniffDetects: "Scans response headers for missing Content-Security-Policy, X-Frame-Options, X-Content-Type-Options, and inspects responses for stack trace leaks.",
    evidenceTriggers: ["Missing Content-Security-Policy (CSP)", "Missing X-Frame-Options (Clickjacking vulnerability)", "Detailed stack traces revealed in error pages"],
    remediation: "Harden server configurations, remove unused features, strip debug headers, and deploy automated header audits."
  },
  {
    id: "a06",
    code: "A06:2021",
    name: "Vulnerable & Outdated Components",
    severity: "Medium",
    description: "Operating with client-side or server-side libraries whose dependencies contain publicly known CVEs and exploit vectors.",
    howSniffDetects: "Extracts third-party script tags, jQuery, Lodash, and frontend library version banners and correlates with known vulnerability feeds.",
    evidenceTriggers: ["Outdated library versions detected in script URLs", "Vendor CDN bundles with published Common Vulnerabilities (CVEs)"],
    remediation: "Continuously audit dependencies with npm audit, Snyk, or Dependabot; retire obsolete client-side components."
  },
  {
    id: "a07",
    code: "A07:2021",
    name: "Identification & Authentication Failures",
    severity: "Critical",
    description: "Weaknesses in confirmation of the user's identity, authentication mechanisms, session management, or CSRF token handling.",
    howSniffDetects: "Audits authentication and state-changing POST forms for the complete omission of Cross-Site Request Forgery (CSRF) tokens.",
    evidenceTriggers: ["POST forms lacking hidden csrf_token or anti-forgery headers", "Session cookies lacking HttpOnly and SameSite flags"],
    remediation: "Implement synchronized anti-CSRF tokens, SameSite=Strict cookie flags, and multi-factor authentication (MFA)."
  },
  {
    id: "a08",
    code: "A08:2021",
    name: "Software & Data Integrity Failures",
    severity: "Medium",
    description: "Code and infrastructure that do not protect against integrity violations, such as loading scripts from CDNs without cryptographic validation.",
    howSniffDetects: "Inspects all external CDN <script> and <link> tags for the absence of cryptographic Subresource Integrity (SRI) integrity hashes.",
    evidenceTriggers: ["External CDN script loaded without integrity='sha384-...' attribute", "Insecure third-party widget ingestion"],
    remediation: "Always declare Subresource Integrity (SRI) attributes with SHA-384 or SHA-512 hashes on all external assets."
  },
  {
    id: "a09",
    code: "A09:2021",
    name: "Security Logging & Monitoring Failures",
    severity: "Medium",
    description: "Insufficient logging, detection, monitoring, and active response that allow attackers to sustain attacks without being noticed.",
    howSniffDetects: "Profiles verbose error responses, silent failures, and probe-sensitive routes that leak system state without structured audit events.",
    evidenceTriggers: ["Server internal 500 errors revealing database schema info", "Unmonitored administrative and debug endpoints"],
    remediation: "Centralize structured logging, monitor authentication events and input validation failures, and implement alerts."
  },
  {
    id: "a10",
    code: "A10:2021",
    name: "Server-Side Request Forgery (SSRF)",
    severity: "Critical",
    description: "Flaws occurring when a web application fetches a remote resource without validating the user-supplied URL.",
    howSniffDetects: "Identifies webhook endpoints, URL preview inputs, and proxy redirect parameters susceptible to internal intranet traversal.",
    evidenceTriggers: ["Input forms asking for external URL or webhook destinations", "Proxy or fetch parameters accessible via GET/POST requests"],
    remediation: "Sanitize and restrict destination addresses; maintain an allowlist of permitted IP ranges; block private IP schemas (RFC 1918)."
  }
];

export default function LandingPage() {
  const { isAuthenticated, user, openAuthModal, logout } = useAuth();
  const navigate = useNavigate();

  const [activePhase, setActivePhase] = useState<number>(1);
  const [selectedOwasp, setSelectedOwasp] = useState<OwaspItem>(OWASP_TOP_10[0]);
  const phaseRefs = useRef<(HTMLDivElement | null)[]>([]);

  // Smooth scroll spy for the vertical timeline
  useEffect(() => {
    const handleScroll = () => {
      const scrollPos = window.scrollY + 350;
      phaseRefs.current.forEach((el, index) => {
        if (el) {
          const top = el.offsetTop;
          const height = el.offsetHeight;
          if (scrollPos >= top && scrollPos < top + height) {
            setActivePhase(index + 1);
          }
        }
      });
    };

    window.addEventListener("scroll", handleScroll, { passive: true });
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  const handleStartScanning = () => {
    if (isAuthenticated) {
      navigate("/new-scan");
    } else {
      openAuthModal("signup");
    }
  };

  const scrollToSection = (id: string) => {
    const el = document.getElementById(id);
    if (el) {
      el.scrollIntoView({ behavior: "smooth" });
    }
  };

  return (
    <div className="min-h-screen bg-[#0E1217] text-[#F8FAFC] selection:bg-[#E2F952] selection:text-black font-sans">
      {/* ────────────────── TOP NAVBAR ────────────────── */}
      <nav className="sticky top-0 z-40 bg-[#0E1217] border-b-2 border-black px-6 lg:px-12 py-3.5 flex items-center justify-between">
        <div className="flex items-center gap-8">
          <Link to="/" className="flex items-center gap-3 group">
            <span className="font-brand text-2xl text-[#F8FAFC] italic tracking-tight group-hover:text-white transition">
              Sniff<span className="text-[#E2F952]">.</span>
            </span>
            <span className="hidden sm:inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-md text-[10px] font-mono font-bold bg-[#141A23] text-[#E2F952] border-2 border-black shadow-[1.5px_1.5px_0px_#000]">
              Agentic Recon
            </span>
          </Link>

          <div className="hidden md:flex items-center gap-6 text-xs font-bold text-[#94A3B8]">
            <button
              onClick={() => scrollToSection("process")}
              className="hover:text-[#F8FAFC] transition cursor-pointer"
            >
              Recon Process
            </button>
            <button
              onClick={() => scrollToSection("phases")}
              className="hover:text-[#F8FAFC] transition cursor-pointer"
            >
              Agent Pipeline
            </button>
            <button
              onClick={() => scrollToSection("owasp")}
              className="hover:text-[#F8FAFC] transition cursor-pointer"
            >
              OWASP Top 10
            </button>
            {isAuthenticated && (
              <Link
                to="/dashboard"
                className="text-[#E2F952] hover:underline transition flex items-center gap-1 font-mono"
              >
                Dashboard
                <ArrowRight className="w-3 h-3" />
              </Link>
            )}
          </div>
        </div>

        {/* Top-Right Corner Auth / Actions */}
        <div className="flex items-center gap-3">
          {isAuthenticated && user ? (
            <div className="flex items-center gap-3">
              <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-[#141A23] border-2 border-black shadow-[2px_2px_0px_#000]">
                <div className="w-6 h-6 rounded-md bg-[#E2F952] text-black border border-black flex items-center justify-center text-xs font-black font-mono">
                  {user.username.charAt(0).toUpperCase()}
                </div>
                <span className="text-xs font-mono text-[#E2E8F0] font-bold hidden sm:inline">
                  @{user.username}
                </span>
              </div>

              <Link
                to="/dashboard"
                className="px-3.5 py-1.5 rounded-lg bg-[#E2F952] text-black text-xs font-black border-2 border-black shadow-[2.5px_2.5px_0px_#000] hover:-translate-x-0.5 hover:-translate-y-0.5 hover:shadow-[4px_4px_0px_#000] active:translate-x-0.5 active:translate-y-0.5 transition-all flex items-center gap-1.5"
              >
                <span>Console</span>
                <ArrowRight className="w-3.5 h-3.5" />
              </Link>

              <button
                onClick={() => {
                  logout();
                  navigate("/");
                }}
                title="Sign Out"
                className="p-2 rounded-lg bg-[#141A23] border-2 border-black shadow-[2px_2px_0px_#000] text-[#94A3B8] hover:text-black hover:bg-[#EF4444] hover:-translate-x-0.5 hover:-translate-y-0.5 hover:shadow-[3px_3px_0px_#000] active:translate-x-0.5 active:translate-y-0.5 transition-all cursor-pointer"
              >
                <LogOut className="w-4 h-4" />
              </button>
            </div>
          ) : (
            <div className="flex items-center gap-2.5">
              <button
                onClick={() => openAuthModal("login")}
                className="px-4 py-2 rounded-lg text-xs font-bold text-[#CBD5E1] hover:text-white border-2 border-black bg-[#141A23] shadow-[2px_2px_0px_#000] hover:-translate-x-0.5 hover:-translate-y-0.5 hover:shadow-[3.5px_3.5px_0px_#000] transition-all cursor-pointer"
              >
                Sign In
              </button>
              <button
                onClick={() => openAuthModal("signup")}
                className="px-4 py-2 rounded-lg text-xs font-black bg-[#E2F952] text-black border-2 border-black shadow-[2.5px_2.5px_0px_#000] hover:-translate-x-0.5 hover:-translate-y-0.5 hover:shadow-[4px_4px_0px_#000] active:translate-x-0.5 active:translate-y-0.5 transition-all flex items-center gap-1.5 cursor-pointer"
              >
                <Lock className="w-3.5 h-3.5" />
                <span>Create Account</span>
              </button>
            </div>
          )}
        </div>
      </nav>

      {/* ────────────────── HERO SECTION ────────────────── */}
      <section className="relative pt-20 pb-28 px-6 lg:px-12 border-b-2 border-black bg-[#0E1217]">
        <div className="relative max-w-5xl mx-auto text-center">
          {/* Subtle brutalist badge */}
          <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-lg bg-[#141A23] border-2 border-black shadow-[2.5px_2.5px_0px_#000] text-xs font-mono font-bold mb-8">
            <span className="text-[#E2F952]">Phase 8 Ready</span>
            <span className="text-[#475569]">/</span>
            <span className="text-[#CBD5E1]">Autonomous Security Reconnaissance</span>
          </div>

          {/* Headline with editorial italic keyword */}
          <h1 className="text-4xl sm:text-6xl lg:text-7xl font-black tracking-tight text-[#F8FAFC] leading-[1.12] mb-6">
            Autonomous Web Recon &{" "}
            <span className="font-editorial italic font-normal text-[#E2F952] block sm:inline">
              Vulnerability Discovery
            </span>
          </h1>

          {/* Subtitle with mixed italics */}
          <p className="max-w-3xl mx-auto text-base sm:text-lg text-[#94A3B8] leading-relaxed mb-10">
            Powered by a Smart Orchestrator and focused AI worker agents. Crawl <span className="font-editorial italic text-white font-medium">Single-Page Applications</span>, classify functional surfaces, embed topologies with <span className="font-editorial italic text-white font-medium">ChromaDB RAG</span>, and verify <span className="font-editorial italic text-[#E2F952] font-semibold">OWASP Top 10</span> vulnerabilities with Groq LLM reasoning.
          </p>

          {/* Hero CTAs */}
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4 mb-16">
            <button
              onClick={handleStartScanning}
              className="w-full sm:w-auto px-8 py-4 rounded-xl bg-[#E2F952] text-black text-base font-black border-2 border-black shadow-[3.5px_3.5px_0px_#000] hover:-translate-x-0.5 hover:-translate-y-0.5 hover:shadow-[5.5px_5.5px_0px_#000] active:translate-x-0.5 active:translate-y-0.5 active:shadow-[1px_1px_0px_#000] transition-all duration-150 flex items-center justify-center gap-3 cursor-pointer group"
            >
              <Terminal className="w-5 h-5 text-black" />
              <span>Start Scanning</span>
              <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
            </button>

            <button
              onClick={() => scrollToSection("process")}
              className="w-full sm:w-auto px-6 py-4 rounded-xl bg-[#141A23] text-[#F8FAFC] text-sm font-bold border-2 border-black shadow-[3.5px_3.5px_0px_#000] hover:-translate-x-0.5 hover:-translate-y-0.5 hover:shadow-[5.5px_5.5px_0px_#000] active:translate-x-0.5 active:translate-y-0.5 active:shadow-[1px_1px_0px_#000] transition-all duration-150 flex items-center justify-center gap-2 cursor-pointer"
            >
              <Activity className="w-4 h-4 text-[#E2F952]" />
              <span>Explore Agent Pipeline</span>
            </button>
          </div>

          {/* Live Telemetry Bar */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 max-w-4xl mx-auto">
            <div className="p-4 rounded-xl bg-[#141A23] border-2 border-black shadow-[3px_3px_0px_#000] text-left hover:-translate-x-0.5 hover:-translate-y-0.5 hover:shadow-[4.5px_4.5px_0px_#000] transition-all">
              <div className="text-2xl font-black font-mono text-[#F8FAFC]">6 Agents</div>
              <div className="text-xs text-[#94A3B8] font-editorial italic mt-0.5">Specialized Pipeline Stages</div>
            </div>
            <div className="p-4 rounded-xl bg-[#141A23] border-2 border-black shadow-[3px_3px_0px_#000] text-left hover:-translate-x-0.5 hover:-translate-y-0.5 hover:shadow-[4.5px_4.5px_0px_#000] transition-all">
              <div className="text-2xl font-black font-mono text-[#E2F952]">OWASP 2021</div>
              <div className="text-xs text-[#94A3B8] font-editorial italic mt-0.5">Automated Risk Mapping</div>
            </div>
            <div className="p-4 rounded-xl bg-[#141A23] border-2 border-black shadow-[3px_3px_0px_#000] text-left hover:-translate-x-0.5 hover:-translate-y-0.5 hover:shadow-[4.5px_4.5px_0px_#000] transition-all">
              <div className="text-2xl font-black font-mono text-[#38BDF8]">ChromaDB</div>
              <div className="text-xs text-[#94A3B8] font-editorial italic mt-0.5">Vector Memory & RAG</div>
            </div>
            <div className="p-4 rounded-xl bg-[#141A23] border-2 border-black shadow-[3px_3px_0px_#000] text-left hover:-translate-x-0.5 hover:-translate-y-0.5 hover:shadow-[4.5px_4.5px_0px_#000] transition-all">
              <div className="text-2xl font-black font-mono text-[#10B981]">Per-User</div>
              <div className="text-xs text-[#94A3B8] font-editorial italic mt-0.5">Isolated Scan History</div>
            </div>
          </div>
        </div>
      </section>

      {/* ────────────────── ARCHITECTURE FLOW OVERVIEW ────────────────── */}
      <section id="process" className="py-24 px-6 lg:px-12 border-b-2 border-black bg-[#0E1217]">
        <div className="max-w-6xl mx-auto">
          <div className="text-center max-w-3xl mx-auto mb-16">
            <div className="inline-flex items-center gap-2 px-3.5 py-1 bg-[#141A23] border-2 border-black shadow-[2px_2px_0px_#000] text-xs font-mono text-[#E2F952] mb-4">
              <Cpu className="w-3.5 h-3.5" />
              SYSTEM ARCHITECTURE
            </div>
            <h2 className="text-3xl sm:text-4xl font-extrabold text-[#F8FAFC]">
              How Sniff Finds <span className="font-editorial italic font-normal text-[#E2F952]">Web Vulnerabilities</span>
            </h2>
            <p className="text-sm sm:text-base text-[#94A3B8] mt-3">
              Unlike noisy brute-force scanners, Sniff utilizes an autonomous multi-agent pipeline adhering to the <em className="font-editorial text-[#F8FAFC]">"Smart Orchestrator + Focused Workers"</em> paradigm.
            </p>
          </div>

          {/* Flow Cards */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="p-6 bg-[#141A23] border-2 border-black shadow-[4px_4px_0px_#000] hover:-translate-y-1 hover:shadow-[6px_6px_0px_#000] transition-all duration-200 group">
              <div className="w-12 h-12 bg-[#38BDF8] text-black border-2 border-black shadow-[2px_2px_0px_#000] flex items-center justify-center mb-5 font-bold">
                <Radar className="w-6 h-6 text-black" />
              </div>
              <div className="text-xs font-mono text-[#38BDF8] font-bold mb-1">STAGE 1: DISCOVERY</div>
              <h3 className="text-lg font-bold text-[#F8FAFC] mb-2">Deep SPA Reconnaissance</h3>
              <p className="text-xs text-[#94A3B8] leading-relaxed mb-4">
                Headless extraction crawls targets, unmasks client-side SPA routing (<em className="font-editorial text-[#CBD5E1]">React, Angular, Vue</em>), categorizes all forms, buttons, inputs, scripts, and endpoints without tripping rate limiters.
              </p>
              <div className="pt-3 border-t-2 border-black flex items-center justify-between text-[11px] font-mono text-[#94A3B8]">
                <span>Worker: <strong className="text-[#F8FAFC]">Recon Agent</strong></span>
                <span className="px-2 py-0.5 bg-[#10B981]/15 text-[#10B981] border border-black text-[10px] font-bold">Strict HTML Only</span>
              </div>
            </div>

            <div className="p-6 bg-[#141A23] border-2 border-black shadow-[4px_4px_0px_#000] hover:-translate-y-1 hover:shadow-[6px_6px_0px_#000] transition-all duration-200 group">
              <div className="w-12 h-12 bg-[#818CF8] text-black border-2 border-black shadow-[2px_2px_0px_#000] flex items-center justify-center mb-5 font-bold">
                <Database className="w-6 h-6 text-black" />
              </div>
              <div className="text-xs font-mono text-[#818CF8] font-bold mb-1">STAGE 2: VECTOR RAG</div>
              <h3 className="text-lg font-bold text-[#F8FAFC] mb-2">Semantic Feature Memory</h3>
              <p className="text-xs text-[#94A3B8] leading-relaxed mb-4">
                Discovered routes and structures are embedded into <em className="font-editorial text-[#CBD5E1]">ChromaDB</em> with domain-isolated vector spaces. Past vulnerability patterns and attack paths are queried via cosine similarity.
              </p>
              <div className="pt-3 border-t-2 border-black flex items-center justify-between text-[11px] font-mono text-[#94A3B8]">
                <span>Service: <strong className="text-[#F8FAFC]">ChromaDB + SQLite</strong></span>
                <span className="px-2 py-0.5 bg-[#38BDF8]/15 text-[#38BDF8] border border-black text-[10px] font-bold">Cosine RAG</span>
              </div>
            </div>

            <div className="p-6 bg-[#141A23] border-2 border-black shadow-[4px_4px_0px_#000] hover:-translate-y-1 hover:shadow-[6px_6px_0px_#000] transition-all duration-200 group">
              <div className="w-12 h-12 bg-[#FB7185] text-black border-2 border-black shadow-[2px_2px_0px_#000] flex items-center justify-center mb-5 font-bold">
                <Search className="w-6 h-6 text-black" />
              </div>
              <div className="text-xs font-mono text-[#FB7185] font-bold mb-1">STAGE 3: REASONING</div>
              <h3 className="text-lg font-bold text-[#F8FAFC] mb-2">Ground-Truth LLM Triage</h3>
              <p className="text-xs text-[#94A3B8] leading-relaxed mb-4">
                <em className="font-editorial text-[#CBD5E1]">Groq Llama 3</em> evaluates strictly verified DOM evidence. Missing CSRF protections, sensitive input leaks, and risky configurations are triangulated into verified, hallucination-free findings.
              </p>
              <div className="pt-3 border-t-2 border-black flex items-center justify-between text-[11px] font-mono text-[#94A3B8]">
                <span>Engine: <strong className="text-[#F8FAFC]">Groq Llama 3</strong></span>
                <span className="px-2 py-0.5 bg-[#C084FC]/15 text-[#C084FC] border border-black text-[10px] font-bold">CVSS Audited</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ────────────────── VERTICAL TIMELINE / DISCOVERY PROCESS ────────────────── */}
      <section id="phases" className="py-24 px-6 lg:px-12 border-b-2 border-black bg-[#0B0E14] relative">
        <div className="max-w-5xl mx-auto">
          {/* Section Header */}
          <div className="text-center max-w-3xl mx-auto mb-20">
            <div className="inline-flex items-center gap-2 px-3.5 py-1 bg-[#141A23] border-2 border-black shadow-[2px_2px_0px_#000] text-xs font-mono text-[#E2F952] mb-4">
              <Sliders className="w-3.5 h-3.5" />
              DISCOVERY PIPELINE
            </div>
            <h2 className="text-3xl sm:text-5xl font-extrabold text-[#F8FAFC]">
              Agent Pipeline in <span className="font-editorial italic font-normal text-[#E2F952]">Real-Time</span>
            </h2>
            <p className="text-sm sm:text-base text-[#94A3B8] mt-3">
              Scroll down to follow the lifecycle of an autonomous scan as each specialized agent is dispatched along the vertical execution timeline.
            </p>
          </div>

          {/* Vertical Timeline Container */}
          <div className="relative">
            {/* The Solid Vertical Line */}
            <div className="absolute left-6 md:left-1/2 top-0 bottom-0 w-1 bg-black -translate-x-1/2 pointer-events-none" />

            {/* Timeline Phases */}
            <div className="space-y-16">
              {TIMELINE_PHASES.map((phase, idx) => {
                const IconComponent = phase.icon;
                const isEven = idx % 2 === 0;
                const isActive = activePhase === phase.id;

                return (
                  <div
                    key={phase.id}
                    ref={(el) => { phaseRefs.current[idx] = el; }}
                    className={`relative flex flex-col md:flex-row items-start ${
                      isEven ? "md:flex-row-reverse" : ""
                    } gap-8 transition-all duration-300`}
                  >
                    {/* Center Node on the line */}
                    <div
                      onClick={() => setActivePhase(phase.id)}
                      className={`absolute left-6 md:left-1/2 -translate-x-1/2 top-4 w-12 h-12 border-2 border-black flex items-center justify-center z-10 cursor-pointer transition-all duration-200 ${
                        isActive
                          ? "bg-[#E2F952] text-black shadow-[3px_3px_0px_#000] scale-110 font-bold"
                          : "bg-[#141A23] text-[#94A3B8] shadow-[2px_2px_0px_#000] hover:text-[#F8FAFC] hover:bg-[#1C2533]"
                      }`}
                    >
                      <IconComponent className="w-5 h-5" />
                    </div>

                    {/* Content Card (Left or Right depending on isEven) */}
                    <div className="ml-16 md:ml-0 md:w-1/2 pl-0 md:px-8 w-full">
                      <div
                        className={`p-6 bg-[#141A23] border-2 border-black transition-all duration-200 ${
                          isActive
                            ? "shadow-[5px_5px_0px_#000] -translate-y-1 bg-[#171E29]"
                            : "shadow-[3px_3px_0px_#000] hover:shadow-[5px_5px_0px_#000]"
                        }`}
                      >
                        <div className="flex items-center justify-between mb-3">
                          <span
                            className="text-xs font-mono font-bold px-2.5 py-1 border border-black shadow-[1.5px_1.5px_0px_#000]"
                            style={{ backgroundColor: `${phase.color}25`, color: phase.color }}
                          >
                            {phase.phase} • {phase.badge}
                          </span>
                          <span className="text-[11px] font-mono text-[#94A3B8]">
                            {phase.agent}
                          </span>
                        </div>

                        <h3 className="text-xl font-bold text-[#F8FAFC] mb-2">
                          {phase.name}
                        </h3>

                        <p className="text-xs text-[#94A3B8] leading-relaxed mb-4">
                          {phase.description}
                        </p>

                        {/* Techniques tags */}
                        <div className="flex flex-wrap gap-1.5 mb-4">
                          {phase.techniques.map((t, i) => (
                            <span
                              key={i}
                              className="px-2 py-0.5 bg-[#0A0D12] border border-black shadow-[1px_1px_0px_#000] text-[10px] font-mono text-[#CBD5E1]"
                            >
                              ✓ {t}
                            </span>
                          ))}
                        </div>

                        {/* Inputs / Outputs Box */}
                        <div className="p-3 bg-[#0A0D12] border-2 border-black shadow-[2px_2px_0px_#000] text-[11px] font-mono space-y-1.5">
                          <div className="flex items-start gap-2">
                            <span className="text-[#38BDF8] shrink-0 font-bold">IN:</span>
                            <span className="text-[#94A3B8]">{phase.inputs}</span>
                          </div>
                          <div className="flex items-start gap-2">
                            <span className="text-[#10B981] shrink-0 font-bold">OUT:</span>
                            <span className="text-[#E2E8F0]">{phase.outputs}</span>
                          </div>
                        </div>
                      </div>
                    </div>

                    {/* Placeholder space on the opposite side on desktop */}
                    <div className="hidden md:block md:w-1/2" />
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      </section>

      {/* ────────────────── OWASP TOP 10 MATRIX ────────────────── */}
      <section id="owasp" className="py-24 px-6 lg:px-12 border-b-2 border-black bg-[#0E1217]">
        <div className="max-w-6xl mx-auto">
          {/* Header */}
          <div className="text-center max-w-3xl mx-auto mb-16">
            <div className="inline-flex items-center gap-2 px-3.5 py-1 bg-[#141A23] border-2 border-black shadow-[2px_2px_0px_#000] text-xs font-mono text-[#EF4444] mb-4">
              <Shield className="w-3.5 h-3.5" />
              INDUSTRY STANDARD BENCHMARK
            </div>
            <h2 className="text-3xl sm:text-5xl font-extrabold text-[#F8FAFC]">
              OWASP Top 10 Security Matrix
            </h2>
            <p className="text-sm sm:text-base text-[#94A3B8] mt-3">
              Sniff classifies and correlates reconnaissance findings against the latest <span className="font-editorial italic text-[#E2F952]">OWASP Top 10</span> Web Application Security Risks. Click any category below to inspect our automated detection criteria.
            </p>
          </div>

          {/* Interactive OWASP Grid & Detail Panel */}
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
            {/* List of 10 categories (Left Column) */}
            <div className="lg:col-span-5 space-y-2.5">
              {OWASP_TOP_10.map((item) => {
                const isSelected = selectedOwasp.id === item.id;
                return (
                  <button
                    key={item.id}
                    onClick={() => setSelectedOwasp(item)}
                    className={`w-full text-left p-3.5 border-2 border-black transition-all duration-150 flex items-center justify-between cursor-pointer ${
                      isSelected
                        ? "bg-[#1C2533] shadow-[3.5px_3.5px_0px_#000] -translate-y-0.5"
                        : "bg-[#141A23] shadow-[2px_2px_0px_#000] hover:shadow-[3px_3px_0px_#000] hover:bg-[#18202C]"
                    }`}
                  >
                    <div className="flex items-center gap-3">
                      <span className="text-xs font-mono font-bold text-[#E2F952]">
                        {item.code.split(":")[0]}
                      </span>
                      <span className="text-xs font-semibold text-[#F8FAFC]">
                        {item.name}
                      </span>
                    </div>

                    <div className="flex items-center gap-2">
                      <span
                        className={`text-[10px] font-mono font-bold px-2 py-0.5 border border-black shadow-[1px_1px_0px_#000] ${
                          item.severity === "Critical"
                            ? "bg-red-500/20 text-red-400"
                            : item.severity === "High"
                            ? "bg-amber-500/20 text-amber-400"
                            : "bg-blue-500/20 text-blue-400"
                        }`}
                      >
                        {item.severity}
                      </span>
                      <ChevronRight className={`w-4 h-4 text-[#94A3B8] transition-transform ${isSelected ? "text-[#E2F952] translate-x-1" : ""}`} />
                    </div>
                  </button>
                );
              })}
            </div>

            {/* Deep-Dive Inspection Card (Right Column) */}
            <div className="lg:col-span-7 sticky top-24">
              <div className="p-8 bg-[#141A23] border-2 border-black shadow-[6px_6px_0px_#000]">
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center gap-2">
                    <span className="px-3 py-1 bg-[#10141C] text-[#E2F952] border-2 border-black shadow-[2px_2px_0px_#000] font-mono text-xs font-bold">
                      {selectedOwasp.code}
                    </span>
                    <span
                      className={`text-xs font-mono font-bold px-2.5 py-1 border border-black shadow-[1.5px_1.5px_0px_#000] ${
                        selectedOwasp.severity === "Critical"
                          ? "bg-red-500/20 text-red-400"
                          : selectedOwasp.severity === "High"
                          ? "bg-amber-500/20 text-amber-400"
                          : "bg-blue-500/20 text-blue-400"
                      }`}
                    >
                      {selectedOwasp.severity} Severity
                    </span>
                  </div>
                  <span className="text-xs font-mono text-[#94A3B8]">OWASP Top 10 Standard</span>
                </div>

                <h3 className="text-2xl font-bold text-[#F8FAFC] mb-3">
                  {selectedOwasp.name}
                </h3>

                <p className="text-sm text-[#94A3B8] leading-relaxed mb-6 font-sans">
                  {selectedOwasp.description}
                </p>

                {/* How Sniff Detects It */}
                <div className="mb-6">
                  <h4 className="text-xs font-mono uppercase tracking-wider text-[#38BDF8] font-bold mb-2 flex items-center gap-1.5">
                    <Radar className="w-3.5 h-3.5" />
                    How Sniff Discovers & Verifies
                  </h4>
                  <div className="p-4 bg-[#0A0D12] border-2 border-black shadow-[2px_2px_0px_#000] text-xs text-[#CBD5E1] leading-relaxed">
                    {selectedOwasp.howSniffDetects}
                  </div>
                </div>

                {/* Ground Truth Evidence Triggers */}
                <div className="mb-6">
                  <h4 className="text-xs font-mono uppercase tracking-wider text-[#FBBF24] font-bold mb-2 flex items-center gap-1.5">
                    <AlertTriangle className="w-3.5 h-3.5" />
                    Concrete Evidence Triggers Extracted
                  </h4>
                  <div className="space-y-2">
                    {selectedOwasp.evidenceTriggers.map((ev, i) => (
                      <div
                        key={i}
                        className="px-3 py-2 bg-[#0A0D12] border border-black shadow-[1.5px_1.5px_0px_#000] text-xs font-mono text-[#94A3B8] flex items-center gap-2"
                      >
                        <span className="text-[#E2F952] font-bold">»</span>
                        <span>{ev}</span>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Remediation */}
                <div>
                  <h4 className="text-xs font-mono uppercase tracking-wider text-[#10B981] font-bold mb-2 flex items-center gap-1.5">
                    <CheckCircle2 className="w-3.5 h-3.5" />
                    Recommended Developer Remediation
                  </h4>
                  <div className="p-4 bg-[#0A1A14] border-2 border-black shadow-[2px_2px_0px_#000] text-xs text-emerald-300 leading-relaxed font-sans">
                    {selectedOwasp.remediation}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ────────────────── CALL TO ACTION BANNER ────────────────── */}
      <section className="py-20 px-6 lg:px-12 bg-[#0B0E14] border-t-2 border-black relative">
        <div className="max-w-4xl mx-auto text-center p-10 bg-[#141A23] border-2 border-black shadow-[6px_6px_0px_#000]">
          <div className="w-14 h-14 bg-[#E2F952] text-black border-2 border-black shadow-[3px_3px_0px_#000] flex items-center justify-center mx-auto mb-6 font-bold">
            <Terminal className="w-7 h-7" />
          </div>

          <h2 className="text-3xl sm:text-4xl font-extrabold text-[#F8FAFC] tracking-tight mb-4">
            Audit Your Application in <span className="font-editorial italic font-normal text-[#E2F952]">Real-Time</span>
          </h2>

          <p className="text-sm sm:text-base text-[#94A3B8] max-w-2xl mx-auto mb-8">
            Create your analyst credentials or sign in to start scanning target domains. Every mission's routes, capabilities, telemetry, and verified findings are permanently linked to your profile.
          </p>

          <button
            onClick={handleStartScanning}
            className="brutal-btn-primary px-8 py-3.5 text-base inline-flex items-center gap-3 cursor-pointer group"
          >
            <span>Start Scanning Now</span>
            <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
          </button>
        </div>
      </section>

      {/* ────────────────── FOOTER ────────────────── */}
      <footer className="py-8 px-6 lg:px-12 border-t-2 border-black bg-[#0E1217] text-xs text-[#94A3B8] flex flex-col sm:flex-row items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <span className="font-brand text-lg text-[#F8FAFC] italic">
            Sniff<span className="text-[#E2F952]">.</span>
          </span>
          <span className="text-[#475569]">|</span>
          <span>Agentic Web Application Security Reconnaissance</span>
        </div>

        <div className="flex items-center gap-6 font-mono text-[11px]">
          <span className="border-b border-black">Phase 8 Standard</span>
          <span className="border-b border-black">SQLite Ground Truth</span>
          <span className="border-b border-black">Groq Reasoning Engine</span>
        </div>
      </footer>
    </div>
  );
}
