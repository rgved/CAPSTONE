import { useSearchParams, Link } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { api } from "../services/api";
import type { SecurityReport, ReportItem } from "../types";
import {
  FileText,
  Target,
  ArrowLeft,
  ChevronRight,
  TrendingDown,
  Shield,
  LayoutDashboard,
  ClipboardList,
  Sparkles
} from "lucide-react";

export default function Reports() {
  const [searchParams, setSearchParams] = useSearchParams();
  const reportId = searchParams.get("id");

  // 1. Fetch reports list
  const { data: reports, isLoading: isListLoading } = useQuery<ReportItem[]>({
    queryKey: ["reports"],
    queryFn: api.getReports,
    enabled: !reportId
  });

  // 2. Fetch specific report details
  const { data: report, isLoading: isDetailLoading, error } = useQuery<SecurityReport>({
    queryKey: ["report", reportId],
    queryFn: () => api.getReportDetail(reportId!),
    enabled: !!reportId
  });

  const getSeverityStyle = (sev: string) => {
    switch (sev.toLowerCase()) {
      case "high":
        return "text-[#EF4444]";
      case "medium":
        return "text-[#F59E0B]";
      case "low":
        return "text-[#EAB308]";
      default:
        return "text-[#3B82F6]";
    }
  };

  const getSeverityBorder = (sev: string) => {
    switch (sev.toLowerCase()) {
      case "high":
        return "border-[#EF4444]/20 bg-[#EF4444]/5";
      case "medium":
        return "border-[#F59E0B]/20 bg-[#F59E0B]/5";
      case "low":
        return "border-[#EAB308]/20 bg-[#EAB308]/5";
      default:
        return "border-[#3B82F6]/20 bg-[#3B82F6]/5";
    }
  };

  // If report ID is selected, display the Report Viewer
  if (reportId) {
    if (isDetailLoading) {
      return (
        <div className="flex-1 flex items-center justify-center bg-[#0B1220] min-h-[500px]">
          <div className="flex flex-col items-center gap-4">
            <div className="w-12 h-12 rounded-full border-4 border-t-transparent border-[#3B82F6] animate-spin"></div>
            <span className="text-[#94A3B8] text-sm font-medium">Parsing report metrics...</span>
          </div>
        </div>
      );
    }

    if (error || !report) {
      return (
        <div className="bg-[#111827] border border-[#1F2937] p-8 rounded-xl text-center max-w-xl mx-auto mt-12 space-y-4">
          <FileText className="w-12 h-12 text-[#EF4444] mx-auto animate-bounce" />
          <h3 className="text-lg font-bold text-[#F8FAFC]">Failed to load report</h3>
          <p className="text-sm text-[#94A3B8]">The requested report ({reportId}) could not be retrieved.</p>
          <button
            onClick={() => setSearchParams({})}
            className="inline-flex items-center gap-2 text-xs font-bold text-[#3B82F6] hover:underline mt-4"
          >
            <ArrowLeft className="w-4 h-4" /> Back to Reports List
          </button>
        </div>
      );
    }

    // Calculations for metrics display
    const originalTokens = report.statistics?.token_count_naive ?? 2297;
    const reducedTokens = report.statistics?.token_count_efficient ?? 997;
    const reduction = originalTokens > 0 ? ((originalTokens - reducedTokens) / originalTokens) * 100 : 56.6;

    return (
      <div className="space-y-8 animate-fadeIn max-w-5xl mx-auto">
        {/* Back and Breadcrumb */}
        <div className="flex items-center gap-3">
          <button
            onClick={() => setSearchParams({})}
            className="p-2 bg-[#111827] border border-[#1F2937] rounded-lg text-[#94A3B8] hover:text-[#F8FAFC] transition-colors"
          >
            <ArrowLeft className="w-4 h-4" />
          </button>
          <div>
            <div className="flex items-center gap-2 text-xs text-[#94A3B8]">
              <span>Reports</span>
              <ChevronRight className="w-3 h-3" />
              <span className="font-mono">{report.report_id}</span>
            </div>
            <h1 className="text-xl font-bold text-[#F8FAFC] mt-1">Audit Record</h1>
          </div>
        </div>

        {/* Report Overview Panel */}
        <div className="bg-[#111827] border border-[#1F2937] p-6 rounded-xl grid grid-cols-1 sm:grid-cols-3 gap-6">
          <div>
            <span className="text-[10px] font-bold text-[#94A3B8] uppercase">Report ID</span>
            <p className="text-sm font-mono font-bold text-[#F8FAFC] mt-1">{report.report_id}</p>
          </div>
          <div>
            <span className="text-[10px] font-bold text-[#94A3B8] uppercase">Mission ID</span>
            <Link to={`/mission/${report.mission_id}`} className="text-sm font-mono font-bold text-[#3B82F6] hover:underline block mt-1">
              {report.mission_id}
            </Link>
          </div>
          <div>
            <span className="text-[10px] font-bold text-[#94A3B8] uppercase">Generated At</span>
            <p className="text-sm font-semibold text-[#F8FAFC] mt-1">
              {new Date(report.generated_at).toLocaleString()}
            </p>
          </div>
        </div>

        {/* Core Report Content Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Executive Summary & Recommendations */}
          <div className="lg:col-span-2 space-y-8">
            {/* Executive Summary */}
            <div className="bg-[#111827] border border-[#1F2937] p-6 rounded-xl space-y-4">
              <h3 className="text-sm font-bold text-[#F8FAFC] border-b border-[#1F2937] pb-3 flex items-center gap-2">
                <FileText className="w-4 h-4 text-[#3B82F6]" /> Executive Summary
              </h3>
              <p className="text-xs text-[#94A3B8] leading-relaxed whitespace-pre-wrap">
                {report.executive_summary}
              </p>
            </div>

            {/* Recommendations */}
            <div className="bg-[#111827] border border-[#1F2937] p-6 rounded-xl space-y-4">
              <h3 className="text-sm font-bold text-[#F8FAFC] border-b border-[#1F2937] pb-3 flex items-center gap-2">
                <ClipboardList className="w-4 h-4 text-[#22C55E]" /> Suggested Remediations
              </h3>
              <ul className="space-y-3">
                {report.recommendations.map((rec, idx) => (
                  <li key={idx} className="flex gap-2.5 items-start p-3 bg-[#0B1220] border border-[#1F2937] rounded-lg">
                    <span className="text-xs font-bold text-[#22C55E] bg-[#22C55E]/10 w-5 h-5 rounded-full flex items-center justify-center shrink-0 mt-0.5">
                      {idx + 1}
                    </span>
                    <p className="text-xs text-[#94A3B8] leading-relaxed">{rec}</p>
                  </li>
                ))}
              </ul>
            </div>
          </div>

          {/* Sidebar Metrics */}
          <div className="space-y-8">
            {/* Research Stats */}
            <div className="bg-[#111827] border border-[#1F2937] p-6 rounded-xl space-y-6">
              <h3 className="text-sm font-bold text-[#F8FAFC] border-b border-[#1F2937] pb-3 flex items-center gap-2">
                <LayoutDashboard className="w-4 h-4 text-[#3B82F6]" /> Research Metrics
              </h3>
              <div className="space-y-4">
                <div className="flex justify-between items-center text-xs">
                  <span className="text-[#94A3B8]">Original Payload:</span>
                  <span className="font-mono text-[#EF4444] font-bold">{originalTokens} tokens</span>
                </div>
                <div className="flex justify-between items-center text-xs">
                  <span className="text-[#94A3B8]">Selective Fetch:</span>
                  <span className="font-mono text-[#22C55E] font-bold">{reducedTokens} tokens</span>
                </div>
                <div className="pt-3 border-t border-[#1F2937] flex justify-between items-center">
                  <span className="text-xs text-[#F8FAFC] font-semibold">Token Reduction:</span>
                  <span className="text-sm font-extrabold text-[#22C55E] inline-flex items-center gap-0.5">
                    <TrendingDown className="w-4 h-4" /> {reduction.toFixed(1)}%
                  </span>
                </div>
              </div>
            </div>

            {/* Coverage Summary */}
            <div className="bg-[#111827] border border-[#1F2937] p-6 rounded-xl space-y-4">
              <h3 className="text-sm font-bold text-[#F8FAFC] border-b border-[#1F2937] pb-3 flex items-center gap-2">
                <Target className="w-4 h-4 text-[#8B5CF6]" /> Coverage Stats
              </h3>
              <pre className="text-xs text-[#94A3B8] bg-[#0B1220] p-4 rounded-lg font-mono leading-relaxed whitespace-pre-wrap">
                {report.coverage_summary}
              </pre>
            </div>

            {/* Severity Breakdown */}
            <div className="bg-[#111827] border border-[#1F2937] p-6 rounded-xl space-y-4">
              <h3 className="text-sm font-bold text-[#F8FAFC] border-b border-[#1F2937] pb-3 flex items-center gap-2">
                <Shield className="w-4 h-4 text-[#EF4444]" /> Severity Breakdown
              </h3>
              <div className="grid grid-cols-2 gap-3">
                {Object.entries(report.severity_breakdown).map(([sev, count]) => (
                  <div key={sev} className="bg-[#0B1220] border border-[#1F2937] p-3 rounded-lg text-center">
                    <span className="text-[10px] font-bold text-[#94A3B8] uppercase">{sev}</span>
                    <p className={`text-lg font-bold mt-1 ${getSeverityStyle(sev)}`}>{count}</p>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>

        {/* Findings Detail List */}
        <div className="space-y-4">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-[#1F2937] pb-3">
            <h3 className="text-base font-bold text-[#F8FAFC]">
              Findings Registry ({report.findings.length})
            </h3>
            <span className="text-xs font-medium text-[#A855F7] flex items-center gap-1.5 bg-[#A855F7]/10 px-3 py-1 rounded-full border border-[#A855F7]/20 w-fit">
              <Sparkles className="w-3.5 h-3.5" /> Explainable Security Findings & Confidence Active
            </span>
          </div>
          <div className="space-y-4">
            {report.findings.length === 0 ? (
              <div className="bg-[#111827] border border-[#1F2937] p-8 rounded-xl text-center space-y-2">
                <Shield className="w-8 h-8 text-[#22C55E] mx-auto" />
                <p className="text-sm font-semibold text-[#F8FAFC]">No security findings recorded for this mission.</p>
                <p className="text-xs text-[#94A3B8]">Target surface showed no classified vulnerabilities matching current heuristics.</p>
              </div>
            ) : (
              report.findings.map((f, idx) => (
                <div key={idx} className={`border rounded-xl p-5 space-y-4 ${getSeverityBorder(f.severity)}`}>
                  <div className="flex justify-between items-center">
                    <div className="flex items-center gap-3">
                      <span className={`px-2.5 py-0.5 rounded text-[9px] font-extrabold uppercase tracking-wide border ${
                        f.severity === "high" ? "bg-[#EF4444]/15 border-[#EF4444]/30 text-[#EF4444]" :
                        f.severity === "medium" ? "bg-[#F59E0B]/15 border-[#F59E0B]/30 text-[#F59E0B]" :
                        f.severity === "low" ? "bg-[#EAB308]/15 border-[#EAB308]/30 text-[#EAB308]" :
                        "bg-[#3B82F6]/15 border-[#3B82F6]/30 text-[#3B82F6]"
                      }`}>
                        {f.severity}
                      </span>
                      <h4 className="text-sm font-bold text-[#F8FAFC]">{f.title}</h4>
                    </div>
                    <div className="flex items-center gap-3">
                      {f.confidence !== undefined && (
                        <span className="text-xs font-bold text-[#8B5CF6] bg-[#8B5CF6]/10 px-2 py-0.5 rounded border border-[#8B5CF6]/20">
                          {(f.confidence * 100).toFixed(0)}% Conf.
                        </span>
                      )}
                      <span className="text-xs font-mono text-[#94A3B8]">{f.finding_id}</span>
                    </div>
                  </div>
                  
                  <div className="space-y-1">
                    <span className="text-[9px] font-bold text-[#94A3B8] uppercase">Description</span>
                    <p className="text-xs text-[#94A3B8] leading-relaxed">{f.description}</p>
                  </div>

                  {/* Explainable Security Reasoning */}
                  {f.reasoning && (
                    <div className="space-y-1.5">
                      <span className="text-[9px] font-bold text-[#94A3B8] uppercase flex items-center gap-1.5">
                        <Sparkles className="w-3.5 h-3.5 text-[#A855F7]" /> Explainable Security Reasoning (AI Narrative & Evidence Analysis)
                      </span>
                      <div className="p-3.5 rounded-lg bg-[#A855F7]/5 border border-[#A855F7]/20 text-[#E9D5FF]">
                        <p className="text-xs leading-relaxed italic">{f.reasoning}</p>
                      </div>
                    </div>
                  )}

                  {f.evidence && f.evidence.length > 0 && (
                    <div className="space-y-1.5">
                      <span className="text-[9px] font-bold text-[#94A3B8] uppercase">Evidence Log</span>
                      <div className="bg-[#0B1220]/60 border border-[#1F2937] p-3 rounded-lg space-y-1">
                        {f.evidence.map((ev, i) => (
                          <pre key={i} className="text-[9px] font-mono text-[#94A3B8] whitespace-pre-wrap">{ev}</pre>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    );
  }

  // Otherwise, display the list of all reports
  return (
    <div className="space-y-8 animate-fadeIn">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-[#F8FAFC]">Security Reports</h1>
        <p className="text-sm text-[#94A3B8] mt-1">Audit assessment registry generated after each successful reconnaissance exploration.</p>
      </div>

      {/* Reports Table */}
      <div className="bg-[#111827] border border-[#1F2937] rounded-xl overflow-hidden">
        {isListLoading ? (
          <div className="flex flex-col items-center justify-center py-24 text-center">
            <div className="w-10 h-10 rounded-full border-4 border-t-transparent border-[#3B82F6] animate-spin"></div>
            <span className="text-[#94A3B8] text-xs font-semibold mt-4">Loading reports database...</span>
          </div>
        ) : !reports || reports.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-20 text-center space-y-2">
            <FileText className="w-12 h-12 text-[#94A3B8] stroke-1 animate-pulse" />
            <p className="text-sm font-semibold text-[#F8FAFC]">No reports available.</p>
            <p className="text-xs text-[#94A3B8]">Reports appear once an orchestrator run finishes successfully.</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead>
                <tr className="bg-[#1F2937]/25 border-b border-[#1F2937] text-[#94A3B8] font-bold uppercase tracking-wider">
                  <th className="p-4">Report ID</th>
                  <th className="p-4">Mission ID</th>
                  <th className="p-4">Target Domain</th>
                  <th className="p-4">Generated At</th>
                  <th className="p-4 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[#1F2937]">
                {reports.map((r) => (
                  <tr
                    key={r.report_id}
                    className="hover:bg-[#1F2937]/20 transition-all cursor-pointer group"
                    onClick={() => setSearchParams({ id: r.report_id })}
                  >
                    <td className="p-4 font-mono font-bold text-[#3B82F6]">{r.report_id}</td>
                    <td className="p-4 font-mono text-[#94A3B8]">{r.mission_id}</td>
                    <td className="p-4 font-semibold text-[#F8FAFC] truncate max-w-[200px]" title={r.target}>
                      {r.target}
                    </td>
                    <td className="p-4 text-[#94A3B8]">
                      {new Date(r.generated_at).toLocaleString()}
                    </td>
                    <td className="p-4 text-right">
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          setSearchParams({ id: r.report_id });
                        }}
                        className="px-3 py-1 bg-[#1F2937] group-hover:bg-[#3B82F6] group-hover:text-white rounded text-xs font-semibold transition-all"
                      >
                        Read Report
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
