import { useState } from "react";
import { useParams, Link } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { api } from "../services/api";
import type { MissionDetail as MissionDetailType, TimelineTask } from "../types";
import {
  Clock,
  Calendar,
  Layers,
  Compass,
  FileText,
  Percent,
  ChevronDown,
  ChevronUp,
  ShieldAlert,
  ArrowLeft,
  ChevronRight,
  TrendingDown,
  Sparkles,
  Target
} from "lucide-react";

export default function MissionDetail() {
  const { id } = useParams<{ id: string }>();
  const [collapsedFindings, setCollapsedFindings] = useState<Record<string, boolean>>({});

  // 1. Fetch Mission Details
  const { data: mission, isLoading: isDetailLoading, error } = useQuery<MissionDetailType>({
    queryKey: ["mission", id],
    queryFn: () => api.getMissionDetail(id!),
    enabled: !!id,
    refetchInterval: (query) => {
      // Poll every 3 seconds if the mission status is "running"
      return query.state.data?.status === "running" ? 3000 : false;
    }
  });

  // 2. Fetch Timeline
  const { data: timeline } = useQuery<TimelineTask[]>({
    queryKey: ["mission-timeline", id],
    queryFn: () => api.getMissionTimeline(id!),
    enabled: !!id,
    refetchInterval: (_query) => {
      // Poll timeline as well while running
      return mission?.status === "running" ? 3000 : false;
    }
  });

  const toggleFinding = (fid: string) => {
    setCollapsedFindings(prev => ({
      ...prev,
      [fid]: !prev[fid]
    }));
  };

  const expandAll = () => {
    setCollapsedFindings({});
  };

  const collapseAll = () => {
    if (mission?.findings) {
      const allCollapsed: Record<string, boolean> = {};
      mission.findings.forEach(f => {
        allCollapsed[f.finding_id] = true;
      });
      setCollapsedFindings(allCollapsed);
    }
  };

  if (isDetailLoading) {
    return (
      <div className="flex-1 flex items-center justify-center bg-[#0B1220] min-h-[500px]">
        <div className="flex flex-col items-center gap-4">
          <div className="w-12 h-12 rounded-full border-4 border-t-transparent border-[#3B82F6] animate-spin"></div>
          <span className="text-[#94A3B8] text-sm font-medium">Loading mission details...</span>
        </div>
      </div>
    );
  }

  if (error || !mission) {
    return (
      <div className="bg-[#111827] border border-[#1F2937] p-8 rounded-xl text-center max-w-xl mx-auto mt-12 space-y-4">
        <ShieldAlert className="w-12 h-12 text-[#EF4444] mx-auto animate-bounce" />
        <h3 className="text-lg font-bold text-[#F8FAFC]">Mission Loading Failed</h3>
        <p className="text-sm text-[#94A3B8]">The requested mission ({id}) could not be retrieved or does not exist.</p>
        <Link to="/" className="inline-flex items-center gap-2 text-xs font-bold text-[#3B82F6] hover:underline mt-4">
          <ArrowLeft className="w-4 h-4" /> Back to Dashboard
        </Link>
      </div>
    );
  }

  const getSeverityStyle = (sev: string) => {
    switch (sev.toLowerCase()) {
      case "high":
        return { bg: "bg-[#EF4444]/10", border: "border-[#EF4444]/20", text: "text-[#EF4444]" };
      case "medium":
        return { bg: "bg-[#F59E0B]/10", border: "border-[#F59E0B]/20", text: "text-[#F59E0B]" };
      case "low":
        return { bg: "bg-[#EAB308]/10", border: "border-[#EAB308]/20", text: "text-[#EAB308]" };
      default:
        return { bg: "bg-[#3B82F6]/10", border: "border-[#3B82F6]/20", text: "text-[#3B82F6]" };
    }
  };

  return (
    <div className="space-y-8 animate-fadeIn">
      {/* Header breadcrumb */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <Link to="/" className="p-2 bg-[#111827] border border-[#1F2937] rounded-lg text-[#94A3B8] hover:text-[#F8FAFC] transition-colors">
            <ArrowLeft className="w-4 h-4" />
          </Link>
          <div>
            <div className="flex items-center gap-2 text-xs text-[#94A3B8]">
              <span>Missions</span>
              <ChevronRight className="w-3 h-3" />
              <span className="font-mono">{mission.mission_id}</span>
            </div>
            <h1 className="text-xl font-bold text-[#F8FAFC] mt-1">Inspection Window</h1>
          </div>
        </div>

        {mission.report_id && (
          <Link
            to={`/reports?id=${mission.report_id}`}
            className="px-4 py-2.5 bg-[#3B82F6] hover:bg-[#2563EB] text-white text-xs font-bold rounded-lg transition-all flex items-center gap-1.5 shadow-lg shadow-blue-500/20"
          >
            <FileText className="w-4 h-4" /> Read Security Report
          </Link>
        )}
      </div>

      {/* Section 1 — Mission Summary */}
      <div className="bg-[#111827] border border-[#1F2937] p-6 rounded-xl grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-6">
        <div>
          <p className="text-[10px] font-bold text-[#94A3B8] uppercase tracking-wider">Mission ID</p>
          <p className="text-sm font-mono font-bold text-[#3B82F6] mt-1.5">{mission.mission_id}</p>
        </div>
        <div>
          <p className="text-[10px] font-bold text-[#94A3B8] uppercase tracking-wider">Target URL</p>
          <a
            href={mission.target_url}
            target="_blank"
            rel="noopener noreferrer"
            className="text-sm font-medium text-[#3B82F6] hover:underline mt-1.5 truncate max-w-xs md:max-w-md block"
            title={mission.target_url}
          >
            {mission.target_url || "https://example.com"}
          </a>
        </div>
        <div>
          <p className="text-[10px] font-bold text-[#94A3B8] uppercase tracking-wider">Status</p>
          <div className="mt-1.5">
            <span className={`px-2.5 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-wider ${
              mission.status === "completed" ? "bg-[#22C55E]/10 text-[#22C55E]" :
              mission.status === "failed" ? "bg-[#EF4444]/10 text-[#EF4444]" :
              "bg-[#F59E0B]/10 text-[#F59E0B] animate-pulse"
            }`}>
              {mission.status}
            </span>
          </div>
        </div>
        <div>
          <p className="text-[10px] font-bold text-[#94A3B8] uppercase tracking-wider">Runtime</p>
          <p className="text-sm font-semibold text-[#F8FAFC] mt-1.5 flex items-center gap-1.5">
            <Clock className="w-4 h-4 text-[#94A3B8]" /> {mission.runtime}
          </p>
        </div>
        <div>
          <p className="text-[10px] font-bold text-[#94A3B8] uppercase tracking-wider">Timestamp</p>
          <p className="text-sm font-semibold text-[#F8FAFC] mt-1.5 flex items-center gap-1.5">
            <Calendar className="w-4 h-4 text-[#94A3B8]" /> {mission.generated_at ? new Date(mission.generated_at).toLocaleString() : "Unknown"}
          </p>
        </div>
      </div>

      {/* Grid: Recon and Features */}
      <div className="grid grid-cols-1 xl:grid-cols-3 gap-8">
        {/* Section 2 — Recon Summary */}
        <div className="bg-[#111827] border border-[#1F2937] p-6 rounded-xl xl:col-span-2 space-y-6">
          <h3 className="text-sm font-bold text-[#F8FAFC] border-b border-[#1F2937] pb-3 flex items-center gap-2">
            <Compass className="w-4 h-4 text-[#3B82F6]" /> Recon Discovery Summary
          </h3>
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
            <div className="bg-[#0B1220] border border-[#1F2937] p-4 rounded-lg">
              <span className="text-[10px] font-bold text-[#94A3B8] uppercase tracking-wider">Routes</span>
              <p className="text-2xl font-bold text-[#F8FAFC] mt-1">{mission.recon_summary.routes}</p>
            </div>
            <div className="bg-[#0B1220] border border-[#1F2937] p-4 rounded-lg">
              <span className="text-[10px] font-bold text-[#94A3B8] uppercase tracking-wider">Forms</span>
              <p className="text-2xl font-bold text-[#F8FAFC] mt-1">{mission.recon_summary.forms}</p>
            </div>
            <div className="bg-[#0B1220] border border-[#1F2937] p-4 rounded-lg">
              <span className="text-[10px] font-bold text-[#94A3B8] uppercase tracking-wider">Inputs</span>
              <p className="text-2xl font-bold text-[#F8FAFC] mt-1">{mission.recon_summary.inputs}</p>
            </div>
            <div className="bg-[#0B1220] border border-[#1F2937] p-4 rounded-lg">
              <span className="text-[10px] font-bold text-[#94A3B8] uppercase tracking-wider">Buttons</span>
              <p className="text-2xl font-bold text-[#F8FAFC] mt-1">{mission.recon_summary.buttons}</p>
            </div>
            <div className="bg-[#0B1220] border border-[#1F2937] p-4 rounded-lg">
              <span className="text-[10px] font-bold text-[#94A3B8] uppercase tracking-wider">Scripts</span>
              <p className="text-2xl font-bold text-[#F8FAFC] mt-1">{mission.recon_summary.scripts}</p>
            </div>
            <div className="bg-[#0B1220] border border-[#1F2937] p-4 rounded-lg">
              <span className="text-[10px] font-bold text-[#94A3B8] uppercase tracking-wider">Links</span>
              <p className="text-2xl font-bold text-[#F8FAFC] mt-1">{mission.recon_summary.links}</p>
            </div>
            <div className="bg-[#0B1220] border border-[#1F2937] p-4 rounded-lg">
              <span className="text-[10px] font-bold text-[#94A3B8] uppercase tracking-wider">Meta Tags</span>
              <p className="text-2xl font-bold text-[#F8FAFC] mt-1">{mission.recon_summary.meta_tags}</p>
            </div>
          </div>
        </div>

        {/* Section 3 — Feature Summary */}
        <div className="bg-[#111827] border border-[#1F2937] p-6 rounded-xl space-y-6">
          <h3 className="text-sm font-bold text-[#F8FAFC] border-b border-[#1F2937] pb-3 flex items-center gap-2">
            <Layers className="w-4 h-4 text-[#8B5CF6]" /> Capabilities Identified
          </h3>
          <div className="space-y-3 max-h-[200px] overflow-y-auto pr-2">
            {mission.features.length === 0 ? (
              <p className="text-xs text-[#94A3B8] italic py-4">No classified features detected yet.</p>
            ) : (
              mission.features.map((f, idx) => {
                const isUnknown = f.name.toLowerCase() === "unknown";
                const displayName = isUnknown ? "General Web Surface" : f.name.replace(/_/g, " ");
                return (
                  <div key={idx} className="flex justify-between items-center p-3 rounded-lg bg-[#0B1220] border border-[#1F2937]">
                    <div className="flex items-center gap-2">
                      <div className={`w-2 h-2 rounded-full ${isUnknown ? "bg-[#94A3B8]" : "bg-[#8B5CF6]"}`}></div>
                      <span className="text-xs font-bold text-[#F8FAFC] uppercase">{displayName}</span>
                    </div>
                    <span className={`text-[11px] font-mono font-bold px-2 py-0.5 rounded border ${
                      isUnknown 
                        ? "text-[#94A3B8] border-[#94A3B8]/20 bg-[#94A3B8]/10" 
                        : "text-[#8B5CF6] border-[#8B5CF6]/20 bg-[#8B5CF6]/10"
                    }`}>
                      {f.confidence.toFixed(0)}% confidence
                    </span>
                  </div>
                );
              })
            )}
          </div>
        </div>
      </div>

      {/* Grid: Research Token Metrics and Timeline */}
      <div className="grid grid-cols-1 xl:grid-cols-3 gap-8">
        {/* Section 4 — Token Reduction Metrics */}
        <div className="bg-[#111827] border-[#3B82F6] border-2 p-6 rounded-xl space-y-6 flex flex-col justify-between shadow-xl shadow-blue-500/5">
          <div>
            <h3 className="text-sm font-bold text-[#F8FAFC] pb-3 border-b border-[#1F2937] flex items-center gap-2">
              <Percent className="w-4 h-4 text-[#3B82F6]" /> Token Reduction Stats
            </h3>
            <p className="text-xs text-[#94A3B8] mt-4 leading-relaxed">
              This card highlights the efficiency of our <strong>Selective Fetch Service</strong> compared to submitting raw, unfiltered HTML payloads.
            </p>
            
            <div className="grid grid-cols-2 gap-4 mt-6">
              <div className="p-3 bg-[#0B1220] border border-[#1F2937] rounded-lg">
                <span className="text-[10px] font-bold text-[#94A3B8] uppercase">Original Tokens</span>
                <p className="text-xl font-bold text-[#EF4444] mt-1">{mission.token_reduction.original_tokens || "—"}</p>
              </div>
              <div className="p-3 bg-[#0B1220] border border-[#1F2937] rounded-lg">
                <span className="text-[10px] font-bold text-[#94A3B8] uppercase">Reduced Tokens</span>
                <p className="text-xl font-bold text-[#22C55E] mt-1">{mission.token_reduction.reduced_tokens || "—"}</p>
              </div>
            </div>
          </div>

          <div className="mt-6 pt-4 border-t border-[#1F2937] flex items-center justify-between">
            <span className="text-xs text-[#94A3B8] font-medium">Reduction Achieved:</span>
            <span className="text-xl font-extrabold text-[#22C55E] flex items-center gap-1">
              <TrendingDown className="w-5 h-5" /> {mission.token_reduction.reduction_percentage}%
            </span>
          </div>
        </div>

        {/* Section 5 — Mission Timeline */}
        <div className="bg-[#111827] border border-[#1F2937] p-6 rounded-xl xl:col-span-2 space-y-6">
          <h3 className="text-sm font-bold text-[#F8FAFC] border-b border-[#1F2937] pb-3 flex items-center gap-2">
            <Clock className="w-4 h-4 text-[#F59E0B]" /> Execution Timeline
          </h3>
          <div className="space-y-4 max-h-[250px] overflow-y-auto pr-2">
            {!timeline || timeline.length === 0 ? (
              <p className="text-xs text-[#94A3B8] italic py-4">No task logs available for this mission.</p>
            ) : (
              timeline.map((t, idx) => (
                <div key={idx} className="flex items-center justify-between p-3 bg-[#0B1220] border border-[#1F2937] rounded-lg">
                  <div className="flex items-center gap-3">
                    <div className={`w-2 h-2 rounded-full ${
                      t.status === "completed" ? "bg-[#22C55E]" :
                      t.status === "failed" ? "bg-[#EF4444]" : "bg-[#F59E0B] animate-pulse"
                    }`}></div>
                    <span className="text-xs font-mono font-bold text-[#F8FAFC]">{t.task}</span>
                  </div>
                  <div className="flex items-center gap-4">
                    <span className={`text-[10px] font-bold uppercase tracking-wider ${
                      t.status === "completed" ? "text-[#22C55E]" :
                      t.status === "failed" ? "text-[#EF4444]" : "text-[#F59E0B]"
                    }`}>{t.status}</span>
                    <span className="text-[10px] font-mono text-[#94A3B8]">
                      {new Date(t.timestamp).toLocaleTimeString()}
                    </span>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      </div>

      {/* Section 6 — Findings list */}
      <div className="space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-[#1F2937] pb-3">
          <div className="flex items-center gap-3">
            <h3 className="text-base font-bold text-[#F8FAFC]">
              Mission Findings ({mission.findings.length})
            </h3>
            <span className="text-xs font-medium text-[#A855F7] flex items-center gap-1.5 bg-[#A855F7]/10 px-3 py-1 rounded-full border border-[#A855F7]/20">
              <Sparkles className="w-3.5 h-3.5" /> Explainable AI Reasoning Active
            </span>
          </div>
          {mission.findings.length > 0 && (
            <div className="flex items-center gap-2">
              <button
                onClick={expandAll}
                className="px-2.5 py-1 text-[11px] font-semibold text-[#94A3B8] hover:text-[#F8FAFC] bg-[#1F2937]/50 hover:bg-[#1F2937] rounded border border-[#1F2937] transition-all"
              >
                Expand All
              </button>
              <button
                onClick={collapseAll}
                className="px-2.5 py-1 text-[11px] font-semibold text-[#94A3B8] hover:text-[#F8FAFC] bg-[#1F2937]/50 hover:bg-[#1F2937] rounded border border-[#1F2937] transition-all"
              >
                Collapse All
              </button>
            </div>
          )}
        </div>
        
        {mission.findings.length === 0 ? (
          <div className="bg-[#111827] border border-[#1F2937] p-8 rounded-xl text-center text-[#94A3B8] italic">
            No findings generated yet.
          </div>
        ) : (
          <div className="space-y-4">
            {mission.findings.map((finding) => {
              const isExpanded = !collapsedFindings[finding.finding_id];
              const sev = getSeverityStyle(finding.severity);
              return (
                <div key={finding.finding_id} className="bg-[#111827] border border-[#1F2937] rounded-xl overflow-hidden transition-all duration-300">
                  {/* Header */}
                  <div
                    onClick={() => toggleFinding(finding.finding_id)}
                    className="p-5 flex items-center justify-between cursor-pointer hover:bg-[#1F2937]/20 transition-all select-none"
                  >
                    <div className="flex items-center gap-3">
                      <span className={`px-2.5 py-0.5 rounded text-[9px] font-extrabold uppercase tracking-wider border ${sev.bg} ${sev.text} ${sev.border}`}>
                        {finding.severity}
                      </span>
                      <span className="font-semibold text-sm text-[#F8FAFC]">{finding.title}</span>
                      {finding.reasoning && (
                        <span className="hidden md:inline-flex items-center gap-1 text-[10px] font-semibold text-[#A855F7] bg-[#A855F7]/10 px-2 py-0.5 rounded border border-[#A855F7]/20">
                          <Sparkles className="w-2.5 h-2.5" /> AI Explained
                        </span>
                      )}
                    </div>
                    <div className="flex items-center gap-4">
                      <span className="text-xs font-mono font-bold text-[#94A3B8]">{finding.finding_id}</span>
                      {isExpanded ? <ChevronUp className="w-5 h-5 text-[#94A3B8]" /> : <ChevronDown className="w-5 h-5 text-[#94A3B8]" />}
                    </div>
                  </div>

                  {/* Expanded Body */}
                  {isExpanded && (
                    <div className="p-6 border-t border-[#1F2937] bg-[#0B1220]/40 space-y-6">
                      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                        <div>
                          <h4 className="text-[10px] font-bold text-[#94A3B8] uppercase tracking-wider">Category</h4>
                          <p className="text-xs font-mono font-bold text-[#F8FAFC] mt-1.5">{finding.category}</p>
                        </div>
                        <div>
                          <h4 className="text-[10px] font-bold text-[#94A3B8] uppercase tracking-wider">Security Confidence</h4>
                          <p className="text-xs font-semibold text-[#8B5CF6] mt-1.5">{(finding.confidence * 100).toFixed(0)}%</p>
                        </div>
                        <div>
                          <h4 className="text-[10px] font-bold text-[#94A3B8] uppercase tracking-wider">Finding Key</h4>
                          <p className="text-xs font-mono text-[#94A3B8] mt-1.5">{finding.finding_id}</p>
                        </div>
                      </div>

                      {/* Description */}
                      <div className="space-y-1.5">
                        <h4 className="text-[10px] font-bold text-[#94A3B8] uppercase tracking-wider">Description</h4>
                        <p className="text-xs text-[#94A3B8] leading-relaxed">{finding.description}</p>
                      </div>

                      {/* Explainable AI Reasoning */}
                      {finding.reasoning && (
                        <div className="space-y-1.5">
                          <h4 className="text-[10px] font-bold text-[#94A3B8] uppercase tracking-wider flex items-center gap-1.5">
                            <Sparkles className="w-3.5 h-3.5 text-[#A855F7]" /> Explainable Security Reasoning (AI Narrative & Evidence Analysis)
                          </h4>
                          <div className="p-4 rounded-lg bg-[#A855F7]/5 border border-[#A855F7]/20 text-[#E9D5FF] space-y-2">
                            <p className="text-xs leading-relaxed italic">{finding.reasoning}</p>
                            <div className="text-[10px] text-[#A855F7]/80 font-medium">
                              ✓ Evidence-backed deductive reasoning • Calibrated risk calculation • False-positive pruned
                            </div>
                          </div>
                        </div>
                      )}

                      {/* Recommendations */}
                      {finding.recommendation && (
                        <div className="space-y-1.5">
                          <h4 className="text-[10px] font-bold text-[#94A3B8] uppercase tracking-wider">Recommendation</h4>
                          <p className="text-xs text-[#22C55E] font-medium leading-relaxed">{finding.recommendation}</p>
                        </div>
                      )}

                      {/* Evidence */}
                      {finding.evidence && finding.evidence.length > 0 && (
                        <div className="space-y-2">
                          <h4 className="text-[10px] font-bold text-[#94A3B8] uppercase tracking-wider">Evidence Logs</h4>
                          <div className="bg-[#0B1220] border border-[#1F2937] p-4 rounded-lg space-y-2 overflow-x-auto max-h-[150px]">
                            {finding.evidence.map((log, idx) => (
                              <pre key={idx} className="text-[10px] text-[#94A3B8] whitespace-pre-wrap font-mono">{log}</pre>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* Section 7 — Prioritized Attack Surface (Risk Engine) */}
      <div className="space-y-4 pt-4 border-t border-[#1F2937]">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
          <div>
            <h3 className="text-base font-bold text-[#F8FAFC] flex items-center gap-2">
              <Target className="w-4 h-4 text-[#3B82F6]" />
              Prioritized Attack Surface (Risk Engine)
            </h3>
            <p className="text-xs text-[#94A3B8] mt-0.5">
              Calculated via <span className="font-mono text-[#3B82F6]">Risk = Exposure × Sensitivity × Reachability</span> to prioritize high-value scan targets.
            </p>
          </div>
          <span className="text-xs font-mono font-bold text-[#94A3B8] bg-[#111827] border border-[#1F2937] px-3 py-1 rounded-lg self-start">
            {mission.prioritized_attack_surface?.length || 0} Endpoints Scored
          </span>
        </div>

        {mission.prioritized_attack_surface && mission.prioritized_attack_surface.length > 0 ? (
          <div className="bg-[#111827] border border-[#1F2937] rounded-xl overflow-hidden shadow-lg">
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead className="bg-[#0B1220] text-[#94A3B8] uppercase tracking-wider font-semibold border-b border-[#1F2937]">
                  <tr>
                    <th className="p-4">Rank / URL</th>
                    <th className="p-4">Risk Score</th>
                    <th className="p-4">Priority</th>
                    <th className="p-4">Sensitivity</th>
                    <th className="p-4">Exposure</th>
                    <th className="p-4">Reachability</th>
                    <th className="p-4">Classification</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-[#1F2937]/50 text-[#F8FAFC]">
                  {mission.prioritized_attack_surface.map((ep, idx) => {
                    const getRiskBadge = (score: number) => {
                      if (score >= 8.5) return "bg-[#EF4444]/10 text-[#EF4444] border-[#EF4444]/30";
                      if (score >= 6.5) return "bg-[#F59E0B]/10 text-[#F59E0B] border-[#F59E0B]/30";
                      if (score >= 3.5) return "bg-[#EAB308]/10 text-[#EAB308] border-[#EAB308]/30";
                      return "bg-[#3B82F6]/10 text-[#3B82F6] border-[#3B82F6]/30";
                    };

                    return (
                      <tr key={idx} className="hover:bg-[#1F2937]/30 transition-colors">
                        <td className="p-4 font-mono">
                          <div className="flex items-center gap-2">
                            <span className="w-5 h-5 rounded-full bg-[#0B1220] border border-[#1F2937] text-[10px] font-bold text-[#94A3B8] flex items-center justify-center">
                              {idx + 1}
                            </span>
                            <span className="truncate max-w-xs md:max-w-md" title={ep.url}>{ep.url}</span>
                          </div>
                        </td>
                        <td className="p-4">
                          <span className={`px-2.5 py-0.5 rounded text-xs font-mono font-extrabold border ${getRiskBadge(ep.risk_score)}`}>
                            {ep.risk_score.toFixed(1)} / 10
                          </span>
                        </td>
                        <td className="p-4">
                          <span className="text-[10px] uppercase font-extrabold tracking-wider text-[#94A3B8]">
                            {ep.priority}
                          </span>
                        </td>
                        <td className="p-4 font-mono text-[#F8FAFC]">
                          {ep.sensitivity.toFixed(1)}
                        </td>
                        <td className="p-4 font-mono text-[#F8FAFC]">
                          {ep.exposure.toFixed(1)}
                        </td>
                        <td className="p-4 font-mono text-[#F8FAFC]">
                          {ep.reachability.toFixed(2)}
                        </td>
                        <td className="p-4 text-[#94A3B8] italic text-xs">
                          {ep.reason}
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>
        ) : (
          <div className="bg-[#111827] border border-[#1F2937] p-8 rounded-xl text-center text-[#94A3B8] italic">
            No endpoints discovered for prioritization in this scan.
          </div>
        )}
      </div>
    </div>
  );
}
