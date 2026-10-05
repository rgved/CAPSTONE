import React, { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { api } from "../services/api";
import type { TimelineTask, MissionDetail } from "../types";
import {
  Play,
  CheckCircle2,
  XCircle,
  Loader2,
  Globe,
  ArrowRight,
  ShieldCheck,
  Compass,
  Cpu,
  Zap,
  Layers,
  FileText,
  RotateCcw,
  Sparkles
} from "lucide-react";

type StepKey = "recon" | "feature_extraction" | "efficient_fetch" | "analysis" | "report_generation";

interface StepConfig {
  key: StepKey;
  label: string;
  taskName: string;
  description: string;
  activeStatusText: string;
  icon: React.ReactNode;
}

function normalizeTargetUrl(input: string) {
  const value = input.trim();
  if (!value) {
    return value;
  }

  if (value.startsWith("http://") || value.startsWith("https://")) {
    return value;
  }

  return `https://${value}`;
}

const STEPS: StepConfig[] = [
  {
    key: "recon",
    label: "Reconnaissance & Route Crawl",
    taskName: "RUN_RECON",
    description: "Discover endpoints, HTTP headers, inputs, forms, and interactive buttons",
    activeStatusText: "Crawling web routes, extracting DOM structures & security headers...",
    icon: <Compass className="w-4 h-4" />
  },
  {
    key: "feature_extraction",
    label: "Feature Extraction",
    taskName: "EXTRACT_FEATURES",
    description: "Categorize page structures into security features using AI",
    activeStatusText: "Classifying attack surface and security features with LLM reasoning...",
    icon: <Layers className="w-4 h-4" />
  },
  {
    key: "efficient_fetch",
    label: "Efficient Fetch & Compression",
    taskName: "RUN_EFFICIENT_FETCH",
    description: "Compress token payload and optimize selective context retrieval",
    activeStatusText: "Performing semantic chunking & token reduction optimization...",
    icon: <Zap className="w-4 h-4" />
  },
  {
    key: "analysis",
    label: "Security Analysis",
    taskName: "RUN_ANALYSIS",
    description: "Inspect targeted structures for vulnerabilities and misconfigurations",
    activeStatusText: "Analyzing security evidence, headers, CSRF & authentication surfaces...",
    icon: <Cpu className="w-4 h-4" />
  },
  {
    key: "report_generation",
    label: "Report Generation",
    taskName: "GENERATE_REPORT",
    description: "Synthesize findings into executive summary, risk score & remediation advice",
    activeStatusText: "Compiling executive security reconnaissance report & recommendations...",
    icon: <FileText className="w-4 h-4" />
  }
];

const SAMPLE_TARGETS = [
  "https://www.hariomlightings.com/",
  "https://vynoa.in",
  "https://example.com"
];

export default function NewScan() {
  const [url, setUrl] = useState("");
  const [error, setError] = useState("");
  const [scanning, setScanning] = useState(false);
  const [missionId, setMissionId] = useState<string | null>(null);
  const [timeline, setTimeline] = useState<Record<StepKey, "pending" | "running" | "completed" | "failed">>({
    recon: "pending",
    feature_extraction: "pending",
    efficient_fetch: "pending",
    analysis: "pending",
    report_generation: "pending"
  });

  const [overallStatus, setOverallStatus] = useState<"running" | "completed" | "failed" | null>(null);
  const [missionDetail, setMissionDetail] = useState<MissionDetail | null>(null);

  // Validate URL and start scan
  const handleStartScan = async (e?: React.FormEvent, customUrl?: string) => {
    if (e) e.preventDefault();
    setError("");

    const targetUrl = normalizeTargetUrl(customUrl || url);
    if (!targetUrl) {
      setError("Please enter a valid target URL");
      return;
    }

    try {
      setScanning(true);
      setOverallStatus("running");
      setMissionDetail(null);
      
      // Step 1 starts in running state immediately
      setTimeline({
        recon: "running",
        feature_extraction: "pending",
        efficient_fetch: "pending",
        analysis: "pending",
        report_generation: "pending"
      });

      const res = await api.startScan(targetUrl);
      setMissionId(res.mission_id);
      if (customUrl) setUrl(customUrl);
    } catch (err: any) {
      setError(err.message || "Failed to initiate scan");
      setScanning(false);
      setOverallStatus(null);
    }
  };

  // Fast polling (500ms) for real-time stepper updates
  useEffect(() => {
    if (!missionId) return;

    let isMounted = true;

    const poll = async () => {
      try {
        const [tasks, detail] = await Promise.all([
          api.getMissionTimeline(missionId) as Promise<TimelineTask[]>,
          api.getMissionDetail(missionId) as Promise<MissionDetail>
        ]);

        if (!isMounted) return;

        setOverallStatus(detail.status);
        if (detail.status === "completed" || detail.status === "failed") {
          setMissionDetail(detail);
        }

        const newTimeline = { ...timeline };

        if (detail.status === "completed") {
          // All steps completed
          STEPS.forEach(s => {
            newTimeline[s.key] = "completed";
          });
        } else if (detail.status === "failed") {
          // Mark completed ones, and mark the failed one
          let foundFailed = false;
          STEPS.forEach(step => {
            const matchedTask = tasks.find(t => t.task === step.taskName);
            if (matchedTask?.status === "completed") {
              newTimeline[step.key] = "completed";
            } else if (matchedTask?.status === "failed" || !foundFailed) {
              newTimeline[step.key] = "failed";
              foundFailed = true;
            } else {
              newTimeline[step.key] = "pending";
            }
          });
        } else {
          // Running status: evaluate steps dynamically
          let firstPendingFound = false;

          STEPS.forEach((step) => {
            const matchedTask = tasks.find(t => t.task === step.taskName);
            if (matchedTask?.status === "completed") {
              newTimeline[step.key] = "completed";
            } else if (matchedTask?.status === "failed") {
              newTimeline[step.key] = "failed";
            } else if (matchedTask?.status === "running" || matchedTask?.status === "pending") {
              newTimeline[step.key] = "running";
              firstPendingFound = true;
            } else if (!firstPendingFound) {
              // This is the active next step in progress
              newTimeline[step.key] = "running";
              firstPendingFound = true;
            } else {
              newTimeline[step.key] = "pending";
            }
          });
        }

        setTimeline(newTimeline);
      } catch (err) {
        console.error("Error polling scan timeline", err);
      }
    };

    const pollInterval = setInterval(poll, 500);
    // Execute immediately on mount/missionId set
    poll();

    return () => {
      isMounted = false;
      clearInterval(pollInterval);
    };
  }, [missionId]);

  // Compute completed percentage
  const completedCount = STEPS.filter(s => timeline[s.key] === "completed").length;
  const progressPercent = overallStatus === "completed" ? 100 : Math.round((completedCount / STEPS.length) * 100);

  return (
    <div className="max-w-4xl mx-auto space-y-8 animate-fadeIn">
      {/* Header */}
      <div>
        <div className="flex items-center gap-3">
          <div className="p-2.5 bg-[#3B82F6]/10 border border-[#3B82F6]/20 rounded-xl text-[#3B82F6]">
            <Play className="w-5 h-5 fill-[#3B82F6]" />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-[#F8FAFC]">Launch Target Scan</h1>
            <p className="text-sm text-[#94A3B8] mt-0.5">
              Initiate an automated agentic security reconnaissance mission using the smart orchestrator pipeline.
            </p>
          </div>
        </div>
      </div>

      {/* Input panel (When not scanning) */}
      {!scanning ? (
        <div className="bg-[#111827]/90 backdrop-blur border border-[#1F2937] p-8 rounded-2xl shadow-xl space-y-6">
          <form onSubmit={handleStartScan} className="space-y-6">
            <div className="space-y-2.5">
              <label htmlFor="url" className="text-sm font-semibold text-[#F8FAFC] flex items-center justify-between">
                <span>Target URL</span>
                <span className="text-xs font-normal text-[#94A3B8]">Supports HTTP / HTTPS web applications</span>
              </label>
              <div className="relative group">
                <Globe className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-[#94A3B8] group-focus-within:text-[#3B82F6] transition-colors" />
                <input
                  id="url"
                  type="text"
                  value={url}
                  onChange={(e) => setUrl(e.target.value)}
                  placeholder="https://example.com"
                  className="w-full bg-[#0B1220] border border-[#1F2937] rounded-xl pl-12 pr-4 py-3.5 text-sm text-[#F8FAFC] placeholder-[#64748B] focus:border-[#3B82F6] focus:ring-2 focus:ring-[#3B82F6]/20 outline-none transition-all"
                />
              </div>
              {error && <p className="text-xs text-[#EF4444] font-medium mt-1 flex items-center gap-1.5"><XCircle className="w-3.5 h-3.5" /> {error}</p>}
            </div>

            {/* Quick Sample Targets */}
            <div className="space-y-2">
              <span className="text-xs font-medium text-[#94A3B8]">Quick Select Sample Targets:</span>
              <div className="flex flex-wrap gap-2">
                {SAMPLE_TARGETS.map(sample => (
                  <button
                    key={sample}
                    type="button"
                    onClick={() => {
                      setUrl(sample);
                      handleStartScan(undefined, sample);
                    }}
                    className="px-3 py-1.5 bg-[#0B1220] hover:bg-[#1E293B] border border-[#1F2937] hover:border-[#3B82F6]/50 rounded-lg text-xs font-mono text-[#94A3B8] hover:text-[#38BDF8] transition-all flex items-center gap-1.5"
                  >
                    <Globe className="w-3 h-3 text-[#3B82F6]" />
                    {sample}
                  </button>
                ))}
              </div>
            </div>

            <button
              type="submit"
              className="w-full bg-gradient-to-r from-[#3B82F6] to-[#2563EB] hover:from-[#2563EB] hover:to-[#1D4ED8] text-white py-3.5 rounded-xl text-sm font-bold shadow-lg shadow-blue-500/25 hover:shadow-blue-500/40 transition-all flex items-center justify-center gap-2 transform active:scale-[0.99]"
            >
              <Play className="w-4 h-4 fill-white" /> Launch Security Reconnaissance
            </button>
          </form>

          {/* Pipeline overview info */}
          <div className="pt-6 border-t border-[#1F2937] grid grid-cols-1 md:grid-cols-3 gap-4 text-xs text-[#94A3B8]">
            <div className="flex items-start gap-2.5 p-3 rounded-xl bg-[#0B1220]/50 border border-[#1F2937]/50">
              <Compass className="w-4 h-4 text-[#38BDF8] shrink-0 mt-0.5" />
              <div>
                <strong className="text-[#F8FAFC] block mb-0.5">Recursive Crawling</strong>
                Discovers forms, input fields, scripts, and endpoints.
              </div>
            </div>
            <div className="flex items-start gap-2.5 p-3 rounded-xl bg-[#0B1220]/50 border border-[#1F2937]/50">
              <Cpu className="w-4 h-4 text-[#A855F7] shrink-0 mt-0.5" />
              <div>
                <strong className="text-[#F8FAFC] block mb-0.5">AI Security Reasoning</strong>
                Categorizes attack surface and identifies vulnerability evidence.
              </div>
            </div>
            <div className="flex items-start gap-2.5 p-3 rounded-xl bg-[#0B1220]/50 border border-[#1F2937]/50">
              <Zap className="w-4 h-4 text-[#22C55E] shrink-0 mt-0.5" />
              <div>
                <strong className="text-[#F8FAFC] block mb-0.5">Efficient Fetch</strong>
                Reduces LLM tokens by ~50%+ via selective chunking.
              </div>
            </div>
          </div>
        </div>
      ) : (
        /* Progress Timeline panel */
        <div className="bg-[#111827]/90 backdrop-blur border border-[#1F2937] p-8 rounded-2xl shadow-2xl space-y-8 animate-fadeIn">
          {/* Top Status Header */}
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-6 border-b border-[#1F2937]">
            <div>
              <div className="flex items-center gap-2.5 flex-wrap">
                <span className="font-mono text-xs font-bold text-white bg-[#3B82F6] px-2.5 py-1 rounded-md shadow-sm">
                  {missionId || "INITIALIZING..."}
                </span>
                <span className="text-xs text-[#94A3B8]">•</span>
                <span className="text-sm font-medium text-[#F8FAFC] truncate max-w-md" title={url}>
                  {url}
                </span>
              </div>
              <div className="flex items-center gap-2 mt-2">
                <span className="text-xs text-[#94A3B8]">Mission Status:</span>
                {overallStatus === "running" && (
                  <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-bold bg-[#3B82F6]/10 border border-[#3B82F6]/30 text-[#3B82F6] animate-pulse">
                    <Loader2 className="w-3 h-3 animate-spin" /> SCAN IN PROGRESS ({progressPercent}%)
                  </span>
                )}
                {overallStatus === "completed" && (
                  <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-bold bg-[#22C55E]/10 border border-[#22C55E]/30 text-[#22C55E]">
                    <CheckCircle2 className="w-3.5 h-3.5" /> COMPLETED (100%)
                  </span>
                )}
                {overallStatus === "failed" && (
                  <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-bold bg-[#EF4444]/10 border border-[#EF4444]/30 text-[#EF4444]">
                    <XCircle className="w-3.5 h-3.5" /> SCAN ABORTED
                  </span>
                )}
              </div>
            </div>

            {/* Top Quick Reset Action */}
            <button
              onClick={() => {
                setScanning(false);
                setUrl("");
                setMissionId(null);
                setOverallStatus(null);
                setMissionDetail(null);
              }}
              className="self-start sm:self-auto px-3 py-1.5 text-xs text-[#94A3B8] hover:text-[#F8FAFC] hover:bg-[#1F2937] border border-[#1F2937] rounded-lg transition-all flex items-center gap-1.5"
              title="Reset and start a new scan"
            >
              <RotateCcw className="w-3 h-3" /> New Target
            </button>
          </div>

          {/* Progress Bar */}
          <div className="space-y-1.5">
            <div className="flex justify-between text-xs text-[#94A3B8]">
              <span>Orchestrator Pipeline Progress</span>
              <span className="font-semibold text-[#F8FAFC]">{completedCount} of 5 Workers Finished</span>
            </div>
            <div className="w-full h-2 bg-[#0B1220] rounded-full overflow-hidden border border-[#1F2937]">
              <div
                className={`h-full transition-all duration-500 ${
                  overallStatus === "failed"
                    ? "bg-[#EF4444]"
                    : overallStatus === "completed"
                    ? "bg-gradient-to-r from-[#3B82F6] to-[#22C55E]"
                    : "bg-gradient-to-r from-[#3B82F6] to-[#60A5FA] animate-pulse"
                }`}
                style={{ width: `${Math.max(8, progressPercent)}%` }}
              ></div>
            </div>
          </div>

          {/* Timeline Stepper */}
          <div className="space-y-5">
            {STEPS.map((step, idx) => {
              const status = timeline[step.key];
              const isLast = idx === STEPS.length - 1;
              
              return (
                <div key={step.key} className="flex gap-4 relative group">
                  {/* Connector Line */}
                  {!isLast && (
                    <div
                      className={`absolute left-[20px] top-10 w-[2px] h-[calc(100%-10px)] transition-colors duration-300 ${
                        status === "completed"
                          ? "bg-[#22C55E]/60"
                          : status === "running"
                          ? "bg-gradient-to-b from-[#3B82F6] to-[#1F2937]"
                          : "bg-[#1F2937]"
                      }`}
                    ></div>
                  )}

                  {/* Step status indicator */}
                  <div className="z-10 shrink-0">
                    {status === "completed" ? (
                      <div className="w-10 h-10 rounded-full bg-[#22C55E]/10 border-2 border-[#22C55E] flex items-center justify-center text-[#22C55E] shadow-lg shadow-green-500/20">
                        <CheckCircle2 className="w-6 h-6" />
                      </div>
                    ) : status === "failed" ? (
                      <div className="w-10 h-10 rounded-full bg-[#EF4444]/10 border-2 border-[#EF4444] flex items-center justify-center text-[#EF4444] shadow-lg shadow-red-500/20">
                        <XCircle className="w-6 h-6" />
                      </div>
                    ) : status === "running" ? (
                      <div className="w-10 h-10 rounded-full bg-[#3B82F6]/15 border-2 border-[#3B82F6] flex items-center justify-center text-[#3B82F6] shadow-lg shadow-blue-500/30 animate-pulse">
                        <Loader2 className="w-5 h-5 animate-spin" />
                      </div>
                    ) : (
                      <div className="w-10 h-10 rounded-full bg-[#0B1220] border border-[#1F2937] flex items-center justify-center text-[#64748B]">
                        <span className="text-xs font-bold">{idx + 1}</span>
                      </div>
                    )}
                  </div>

                  {/* Step Info */}
                  <div className={`flex-1 p-3.5 rounded-xl border transition-all ${
                    status === "running"
                      ? "bg-[#0B1220]/80 border-[#3B82F6]/40 shadow-md shadow-blue-500/5"
                      : status === "completed"
                      ? "bg-[#0B1220]/40 border-[#1F2937]"
                      : "bg-transparent border-transparent"
                  }`}>
                    <div className="flex items-center justify-between gap-2 flex-wrap">
                      <div className="flex items-center gap-2">
                        <span className={`p-1 rounded ${
                          status === "completed" ? "text-[#22C55E]" : status === "running" ? "text-[#3B82F6]" : "text-[#64748B]"
                        }`}>
                          {step.icon}
                        </span>
                        <h4 className={`text-sm font-bold ${
                          status === "running"
                            ? "text-[#38BDF8]"
                            : status === "completed"
                            ? "text-[#F8FAFC]"
                            : status === "failed"
                            ? "text-[#EF4444]"
                            : "text-[#64748B]"
                        }`}>
                          {step.label}
                        </h4>
                      </div>

                      {/* Status Badges */}
                      {status === "running" && (
                        <span className="text-[11px] bg-[#3B82F6]/20 border border-[#3B82F6]/40 text-[#38BDF8] px-2.5 py-0.5 rounded-full font-bold flex items-center gap-1.5 animate-pulse">
                          <Loader2 className="w-3 h-3 animate-spin" /> In Progress
                        </span>
                      )}
                      {status === "completed" && (
                        <span className="text-[11px] bg-[#22C55E]/10 border border-[#22C55E]/30 text-[#22C55E] px-2 py-0.5 rounded-full font-semibold flex items-center gap-1">
                          Done
                        </span>
                      )}
                      {status === "failed" && (
                        <span className="text-[11px] bg-[#EF4444]/10 border border-[#EF4444]/30 text-[#EF4444] px-2 py-0.5 rounded-full font-semibold">
                          Failed
                        </span>
                      )}
                    </div>

                    <p className="text-xs text-[#94A3B8] mt-1 pl-7">
                      {status === "running" ? (
                        <span className="text-[#38BDF8] font-medium flex items-center gap-1.5 animate-pulse">
                          {step.activeStatusText}
                        </span>
                      ) : (
                        step.description
                      )}
                    </p>
                  </div>
                </div>
              );
            })}
          </div>

          {/* Quick Stats Summary when Completed */}
          {overallStatus === "completed" && missionDetail && (
            <div className="p-5 rounded-xl bg-[#0B1220] border border-[#1F2937] space-y-4 animate-fadeIn">
              <div className="flex items-center gap-2 text-xs font-bold uppercase tracking-wider text-[#22C55E]">
                <Sparkles className="w-4 h-4" /> Scan Summary & Findings Ready
              </div>
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-center">
                <div className="p-3 bg-[#111827] border border-[#1F2937] rounded-lg">
                  <div className="text-lg font-bold text-[#38BDF8]">
                    {missionDetail.recon_summary?.routes || 1}
                  </div>
                  <div className="text-[11px] text-[#94A3B8] mt-0.5">Routes Crawled</div>
                </div>
                <div className="p-3 bg-[#111827] border border-[#1F2937] rounded-lg">
                  <div className="text-lg font-bold text-[#A855F7]">
                    {missionDetail.features?.length || 1}
                  </div>
                  <div className="text-[11px] text-[#94A3B8] mt-0.5">Features Extracted</div>
                </div>
                <div className="p-3 bg-[#111827] border border-[#1F2937] rounded-lg">
                  <div className="text-lg font-bold text-[#EF4444]">
                    {missionDetail.findings?.length || 0}
                  </div>
                  <div className="text-[11px] text-[#94A3B8] mt-0.5">Findings Identified</div>
                </div>
                <div className="p-3 bg-[#111827] border border-[#1F2937] rounded-lg">
                  <div className="text-lg font-bold text-[#22C55E]">
                    {missionDetail.token_reduction?.reduction_percentage || 0}%
                  </div>
                  <div className="text-[11px] text-[#94A3B8] mt-0.5">Token Reduction</div>
                </div>
              </div>
            </div>
          )}

          {/* Bottom Actions Bar */}
          {overallStatus !== "running" && (
            <div className="pt-6 border-t border-[#1F2937] flex flex-col-reverse sm:flex-row items-center justify-between gap-3">
              <button
                onClick={() => {
                  setScanning(false);
                  setUrl("");
                  setMissionId(null);
                  setOverallStatus(null);
                  setMissionDetail(null);
                }}
                className="w-full sm:w-auto px-5 py-2.5 bg-[#1F2937] hover:bg-[#374151] text-[#F8FAFC] text-sm font-semibold rounded-xl border border-[#374151] transition-all flex items-center justify-center gap-2"
              >
                <RotateCcw className="w-4 h-4" /> Scan Another URL
              </button>

              {overallStatus === "completed" && missionId && (
                <Link
                  to={`/mission/${missionId}`}
                  className="w-full sm:w-auto px-7 py-3 bg-gradient-to-r from-[#22C55E] to-[#16A34A] hover:from-[#16A34A] hover:to-[#15803D] text-white text-sm font-bold rounded-xl transition-all flex items-center justify-center gap-2 shadow-xl shadow-green-500/25 transform hover:scale-[1.02] active:scale-[0.98]"
                >
                  <ShieldCheck className="w-4 h-4" /> Inspect Report <ArrowRight className="w-4 h-4" />
                </Link>
              )}

              {overallStatus === "failed" && (
                <button
                  onClick={() => handleStartScan(undefined, url)}
                  className="w-full sm:w-auto px-6 py-2.5 bg-[#EF4444] hover:bg-[#DC2626] text-white text-sm font-bold rounded-xl transition-all flex items-center justify-center gap-2 shadow-lg shadow-red-500/20"
                >
                  <RotateCcw className="w-4 h-4" /> Retry Scan
                </button>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
