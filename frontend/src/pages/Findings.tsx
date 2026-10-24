import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import { api } from "../services/api";
import type { Finding } from "../types";
import {
  ShieldAlert,
  Search,
  SlidersHorizontal,
  X,
  ExternalLink,
  ClipboardCheck,
  Sparkles
} from "lucide-react";

export default function Findings() {
  const [severity, setSeverity] = useState("all");
  const [category, setCategory] = useState("all");
  const [search, setSearch] = useState("");
  const [selectedFinding, setSelectedFinding] = useState<Finding | null>(null);

  // Fetch findings
  const { data: findings, isLoading } = useQuery<Finding[]>({
    queryKey: ["findings", severity, category, search],
    queryFn: () => api.getFindings(severity, category, search),
    refetchInterval: 5000 // Keep findings list updated
  });

  const getSeverityStyle = (sev: string) => {
    switch (sev.toLowerCase()) {
      case "high":
        return "bg-[#EF4444]/10 text-[#EF4444] border-[#EF4444]/20";
      case "medium":
        return "bg-[#F59E0B]/10 text-[#F59E0B] border-[#F59E0B]/20";
      case "low":
        return "bg-[#EAB308]/10 text-[#EAB308] border-[#EAB308]/20";
      default:
        return "bg-[#3B82F6]/10 text-[#3B82F6] border-[#3B82F6]/20";
    }
  };

  const categories = [
    { label: "All Categories", value: "all" },
    { label: "CSRF Risks", value: "missing_csrf" },
    { label: "Weak Authentication", value: "weak_authentication" },
    { label: "Exposed Endpoints", value: "exposed_endpoint" },
    { label: "File Upload Risks", value: "file_upload_risk" },
    { label: "Security Headers", value: "missing_security_headers" },
    { label: "Admin Panels", value: "admin_surface" },
    { label: "Sensitive Inputs", value: "sensitive_input" },
    { label: "Vulnerable Dependencies", value: "vulnerable_dependency" },
    { label: "Subresource Integrity", value: "missing_subresource_integrity" },
    { label: "Verbose Error Leaks", value: "verbose_error_leak" },
  ];

  return (
    <div className="space-y-8 animate-fadeIn relative min-h-screen">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-[#F8FAFC]">Findings Explorer</h1>
          <p className="text-sm text-[#94A3B8] mt-1">Cross-mission registry of all security findings discovered across target domains.</p>
        </div>
        <div className="flex items-center gap-2 bg-[#A855F7]/10 border border-[#A855F7]/20 px-3.5 py-2 rounded-xl text-xs text-[#E9D5FF] w-fit">
          <Sparkles className="w-4 h-4 text-[#A855F7] shrink-0" />
          <span><strong>Explainable AI Active:</strong> Every finding includes reasoning & evidence breakdown.</span>
        </div>
      </div>

      {/* Filters Panel */}
      <div className="bg-[#111827] border border-[#1F2937] p-6 rounded-xl space-y-4 md:space-y-0 md:flex md:items-center md:justify-between gap-4">
        {/* Search */}
        <div className="relative flex-1 max-w-md">
          <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-[#94A3B8]" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search findings by title, description, ID..."
            className="w-full bg-[#0B1220] border border-[#1F2937] rounded-lg pl-10 pr-4 py-2 text-xs text-[#F8FAFC] placeholder-[#94A3B8] focus:border-[#3B82F6] outline-none transition-all"
          />
        </div>

        {/* Dropdowns */}
        <div className="flex flex-wrap items-center gap-3">
          {/* Severity */}
          <div className="flex items-center gap-2 bg-[#0B1220] border border-[#1F2937] px-3 py-1.5 rounded-lg focus-within:border-[#3B82F6] transition-all">
            <SlidersHorizontal className="w-3.5 h-3.5 text-[#94A3B8]" />
            <select
              value={severity}
              onChange={(e) => setSeverity(e.target.value)}
              className="bg-[#0B1220] text-xs text-[#F8FAFC] font-semibold outline-none border-none cursor-pointer pr-1"
            >
              <option value="all" className="bg-[#111827] text-[#F8FAFC]">All Severities</option>
              <option value="high" className="bg-[#111827] text-[#EF4444] font-semibold">High</option>
              <option value="medium" className="bg-[#111827] text-[#F59E0B] font-semibold">Medium</option>
              <option value="low" className="bg-[#111827] text-[#EAB308] font-semibold">Low</option>
            </select>
          </div>

          {/* Category */}
          <div className="flex items-center gap-2 bg-[#0B1220] border border-[#1F2937] px-3 py-1.5 rounded-lg focus-within:border-[#3B82F6] transition-all">
            <SlidersHorizontal className="w-3.5 h-3.5 text-[#94A3B8]" />
            <select
              value={category}
              onChange={(e) => setCategory(e.target.value)}
              className="bg-[#0B1220] text-xs text-[#F8FAFC] font-semibold outline-none border-none cursor-pointer pr-1"
            >
              {categories.map((c) => (
                <option key={c.value} value={c.value} className="bg-[#111827] text-[#F8FAFC]">
                  {c.label}
                </option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {/* Findings Table */}
      <div className="bg-[#111827] border border-[#1F2937] rounded-xl overflow-hidden">
        {isLoading ? (
          <div className="flex flex-col items-center justify-center py-24 text-center">
            <div className="w-10 h-10 rounded-full border-4 border-t-transparent border-[#3B82F6] animate-spin"></div>
            <span className="text-[#94A3B8] text-xs font-semibold mt-4">Filtering observations...</span>
          </div>
        ) : !findings || findings.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-20 text-center space-y-2">
            <ShieldAlert className="w-12 h-12 text-[#94A3B8] stroke-1 animate-pulse" />
            <p className="text-sm font-semibold text-[#F8FAFC]">No findings generated yet.</p>
            <p className="text-xs text-[#94A3B8]">Try tweaking your filter options or run a new scan.</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead>
                <tr className="bg-[#1F2937]/25 border-b border-[#1F2937] text-[#94A3B8] font-bold uppercase tracking-wider">
                  <th className="p-4">Finding ID</th>
                  <th className="p-4">Title & Explainable Reasoning</th>
                  <th className="p-4">Severity</th>
                  <th className="p-4">Mission</th>
                  <th className="p-4">Date</th>
                  <th className="p-4 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[#1F2937]">
                {[...findings]
                  .sort((a, b) => {
                    const severityOrder: Record<string, number> = { high: 3, medium: 2, low: 1, informational: 0 };
                    const weightA = severityOrder[a.severity?.toLowerCase()] ?? 0;
                    const weightB = severityOrder[b.severity?.toLowerCase()] ?? 0;
                    return weightB - weightA;
                  })
                  .map((f) => (
                  <tr
                    key={f.finding_id}
                    className="hover:bg-[#1F2937]/20 transition-all cursor-pointer group"
                    onClick={() => setSelectedFinding(f)}
                  >
                    <td className="p-4 font-mono font-bold text-[#3B82F6] whitespace-nowrap">{f.finding_id}</td>
                    <td className="p-4">
                      <div className="font-semibold text-[#F8FAFC]">{f.title}</div>
                      {f.reasoning && (
                        <div className="text-[11px] text-[#A855F7] line-clamp-1 italic mt-1 flex items-center gap-1.5">
                          <Sparkles className="w-3 mx-0 shrink-0" />
                          <span className="truncate">{f.reasoning}</span>
                        </div>
                      )}
                    </td>
                    <td className="p-4 whitespace-nowrap">
                      <span className={`px-2.5 py-0.5 rounded text-[9px] font-extrabold uppercase tracking-wide border ${getSeverityStyle(f.severity)}`}>
                        {f.severity}
                      </span>
                    </td>
                    <td className="p-4 font-mono text-[#94A3B8] whitespace-nowrap" onClick={(e) => e.stopPropagation()}>
                      <Link to={`/mission/${f.mission}`} className="hover:text-[#3B82F6] hover:underline inline-flex items-center gap-1">
                        {f.mission} <ExternalLink className="w-3 h-3" />
                      </Link>
                    </td>
                    <td className="p-4 text-[#94A3B8] whitespace-nowrap">
                      {f.date ? new Date(f.date).toLocaleDateString() : "—"}
                    </td>
                    <td className="p-4 text-right whitespace-nowrap">
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          setSelectedFinding(f);
                        }}
                        className="px-3 py-1 bg-[#1F2937] group-hover:bg-[#3B82F6] group-hover:text-white rounded text-xs font-semibold transition-all"
                      >
                        Inspect
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Side Sliding Drawer Overlay */}
      {selectedFinding && (
        <div className="fixed inset-0 bg-black/60 z-50 flex justify-end animate-fadeIn">
          {/* Backdrop closer */}
          <div className="absolute inset-0" onClick={() => setSelectedFinding(null)}></div>
          
          {/* Drawer Body */}
          <div className="w-full max-w-xl bg-[#111827] border-l border-[#1F2937] p-8 z-10 overflow-y-auto space-y-6 flex flex-col justify-between shadow-2xl relative animate-slideLeft">
            <button
              onClick={() => setSelectedFinding(null)}
              className="absolute top-6 right-6 p-2 rounded-lg bg-[#0B1220] border border-[#1F2937] text-[#94A3B8] hover:text-[#F8FAFC] transition-colors"
            >
              <X className="w-4 h-4" />
            </button>

            <div className="space-y-6">
              {/* Drawer Title */}
              <div>
                <span className={`px-2.5 py-0.5 rounded text-[9px] font-extrabold uppercase tracking-wide border ${getSeverityStyle(selectedFinding.severity)}`}>
                  {selectedFinding.severity}
                </span>
                <h2 className="text-lg font-bold text-[#F8FAFC] mt-3">{selectedFinding.title}</h2>
                <div className="flex items-center gap-2 mt-1.5 text-xs text-[#94A3B8]">
                  <span className="font-mono text-[#3B82F6] font-bold">{selectedFinding.finding_id}</span>
                  <span>•</span>
                  <span>Mission:</span>
                  <Link to={`/mission/${selectedFinding.mission}`} className="font-mono text-[#3B82F6] hover:underline inline-flex items-center gap-0.5">
                    {selectedFinding.mission} <ExternalLink className="w-2.5 h-2.5" />
                  </Link>
                </div>
              </div>

              {/* Categorization & Status */}
              <div className="grid grid-cols-2 gap-4 border-t border-b border-[#1F2937] py-4">
                <div>
                  <span className="text-[10px] font-bold text-[#94A3B8] uppercase">Category</span>
                  <p className="text-xs font-mono font-bold text-[#F8FAFC] mt-1">{selectedFinding.category}</p>
                </div>
                <div>
                  <span className="text-[10px] font-bold text-[#94A3B8] uppercase">Classification</span>
                  <p className="text-xs font-bold text-[#3B82F6] mt-1">Verified Finding</p>
                </div>
              </div>

              {/* Description */}
              <div className="space-y-2">
                <span className="text-[10px] font-bold text-[#94A3B8] uppercase">Description</span>
                <p className="text-xs text-[#94A3B8] leading-relaxed">{selectedFinding.description}</p>
              </div>

              {/* Explainable AI Reasoning */}
              {selectedFinding.reasoning && (
                <div className="space-y-2">
                  <span className="text-[10px] font-bold text-[#94A3B8] uppercase flex items-center gap-1.5">
                    <Sparkles className="w-3.5 h-3.5 text-[#A855F7]" /> Explainable Security Reasoning (AI Narrative & Evidence Analysis)
                  </span>
                  <div className="p-4 rounded-lg bg-[#A855F7]/5 border border-[#A855F7]/20 text-[#E9D5FF] space-y-2">
                    <p className="text-xs leading-relaxed italic">{selectedFinding.reasoning}</p>
                    <div className="text-[10px] text-[#A855F7]/80 font-medium">
                      ✓ Evidence-backed deductive reasoning • Calibrated risk calculation • False-positive pruned
                    </div>
                  </div>
                </div>
              )}

              {/* Recommendations */}
              {selectedFinding.recommendation && (
                <div className="space-y-2">
                  <span className="text-[10px] font-bold text-[#94A3B8] uppercase">Remediation Guidance</span>
                  <div className="p-4 rounded-lg bg-[#22C55E]/5 border border-[#22C55E]/20 text-[#22C55E] flex items-start gap-2.5">
                    <ClipboardCheck className="w-5 h-5 shrink-0 mt-0.5" />
                    <p className="text-xs font-medium leading-relaxed">{selectedFinding.recommendation}</p>
                  </div>
                </div>
              )}

              {/* Evidence */}
              {selectedFinding.evidence && selectedFinding.evidence.length > 0 && (
                <div className="space-y-2">
                  <span className="text-[10px] font-bold text-[#94A3B8] uppercase">Evidence Log</span>
                  <div className="bg-[#0B1220] border border-[#1F2937] p-4 rounded-lg space-y-2 max-h-[200px] overflow-y-auto">
                    {selectedFinding.evidence.map((log, idx) => (
                      <pre key={idx} className="text-[10px] text-[#94A3B8] whitespace-pre-wrap font-mono">{log}</pre>
                    ))}
                  </div>
                </div>
              )}
            </div>

            {/* Close action */}
            <div className="pt-6 border-t border-[#1F2937] flex justify-end">
              <button
                onClick={() => setSelectedFinding(null)}
                className="px-4 py-2 bg-[#1F2937] hover:bg-[#111827] text-[#F8FAFC] text-xs font-bold rounded-lg border border-[#1F2937] transition-all"
              >
                Close Details
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
