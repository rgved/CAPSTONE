import { useSearchParams, Link } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { api } from "../services/api";
import type { SecurityReport, ReportItem } from "../types";
import SecurityMetricsStrip from "../components/common/SecurityMetricsStrip";
import {
  FileText,
  ArrowLeft,
  ChevronRight,
  ShieldAlert,
  ClipboardList,
  Activity
} from "lucide-react";

const getOwaspCategory = (category?: string): { code: string; name: string } => {
  switch (category?.toLowerCase()) {
    case "missing_csrf":
    case "admin_surface":
    case "exposed_endpoint":
      return { code: "A01:2025", name: "Broken Access Control" };
    case "missing_security_headers":
    case "verbose_error_leak":
      return { code: "A02:2025", name: "Security Misconfiguration" };
    case "vulnerable_dependency":
      return { code: "A03:2025", name: "Software Supply Chain Failures" };
    case "sensitive_input":
      return { code: "A05:2025", name: "Injection" };
    case "weak_authentication":
      return { code: "A07:2025", name: "Authentication Failures" };
    case "missing_subresource_integrity":
    case "file_upload_risk":
      return { code: "A08:2025", name: "Software or Data Integrity Failures" };
    default:
      return { code: "A02:2025", name: "Security Misconfiguration" };
  }
};

export default function Reports() {
  const [searchParams, setSearchParams] = useSearchParams();
  const reportId = searchParams.get("id");

  // 1. Fetch reports list
  const { data: reports, isLoading: isListLoading } = useQuery<ReportItem[]>({
    queryKey: ["reports"],
    queryFn: api.getReports,
    enabled: !reportId,
    refetchInterval: 5000
  });

  // 2. Fetch specific report details
  const { data: report, isLoading: isDetailLoading, error } = useQuery<SecurityReport>({
    queryKey: ["report", reportId],
    queryFn: () => api.getReportDetail(reportId!),
    enabled: !!reportId
  });

  const getSeverityStyle = (sev: string) => {
    switch (sev.toLowerCase()) {
      case "critical":
        return "bg-[#DC2626]/10 text-[#DC2626] border-[#DC2626]/30";
      case "high":
        return "bg-[#EF4444]/10 text-[#EF4444] border-[#EF4444]/30";
      case "medium":
        return "bg-[#F59E0B]/10 text-[#F59E0B] border-[#F59E0B]/30";
      case "low":
        return "bg-[#EAB308]/10 text-[#EAB308] border-[#EAB308]/30";
      default:
        return "bg-[#38BDF8]/10 text-[#38BDF8] border-[#38BDF8]/30";
    }
  };

  // If report ID is selected, display the Report Viewer
  if (reportId) {
    if (isDetailLoading) {
      return (
        <div className="flex-1 flex items-center justify-center bg-[#090D16] min-h-[500px]">
          <div className="flex flex-col items-center gap-4">
            <div className="w-10 h-10 rounded-full border-2 border-t-transparent border-[#38BDF8] animate-spin"></div>
            <span className="text-[#64748B] text-xs font-mono uppercase tracking-wider">Compiling Executive Audit Record...</span>
          </div>
        </div>
      );
    }

    if (error || !report) {
      return (
        <div className="bg-[#0F172A] border border-[#1E293B] p-8 rounded-xl text-center max-w-xl mx-auto mt-12 space-y-4">
          <FileText className="w-12 h-12 text-[#EF4444] mx-auto animate-bounce" />
          <h3 className="text-base font-bold text-[#F8FAFC]">Report Unavailable</h3>
          <p className="text-xs text-[#64748B]">The requested report ({reportId}) could not be retrieved from the database.</p>
          <button
            onClick={() => setSearchParams({})}
            className="inline-flex items-center gap-2 text-xs font-bold text-[#38BDF8] hover:underline mt-4"
          >
            <ArrowLeft className="w-4 h-4" /> Return to Reports Registry
          </button>
        </div>
      );
    }

    const hasHigh = report.findings.some(f => f.severity?.toLowerCase() === "high" || f.severity?.toLowerCase() === "critical");

    const owaspMap = new Map<string, string>();
    report.findings.forEach(f => {
      const owasp = getOwaspCategory(f.category);
      owaspMap.set(owasp.code, owasp.name);
    });
    const activeOwasp = Array.from(owaspMap.entries()).map(([code, name]) => ({ code, name }));

    return (
      <div className="space-y-8 animate-fadeIn max-w-5xl mx-auto">
        {/* Navigation & Breadcrumb */}
        <div className="flex items-center justify-between border-b-2 border-black pb-5">
          <div className="flex items-center gap-3">
            <button
              onClick={() => setSearchParams({})}
              className="p-2 bg-[#141A23] border-2 border-black shadow-[2px_2px_0px_#000] text-[#94A3B8] hover:text-[#F8FAFC] hover:bg-[#1C2533] active:translate-x-[1px] active:translate-y-[1px] transition-all cursor-pointer"
            >
              <ArrowLeft className="w-4 h-4" />
            </button>
            <div>
              <div className="flex items-center gap-2 text-[11px] text-[#94A3B8] font-mono">
                <span className="cursor-pointer hover:underline" onClick={() => setSearchParams({})}>Reports</span>
                <ChevronRight className="w-3 h-3" />
                <span className="font-mono text-[#E2F952] font-bold">{report.report_id}</span>
              </div>
              <h1 className="text-xl font-extrabold text-[#F8FAFC] mt-0.5">
                Executive Audit <span className="font-editorial italic font-normal text-[#E2F952]">Assessment</span>
              </h1>
            </div>
          </div>

          <span className={`px-3 py-1 text-[10px] font-mono font-bold uppercase tracking-wider border-2 border-black shadow-[1.5px_1.5px_0px_#000] ${
            hasHigh ? "bg-[#EF4444] text-white" : "bg-[#10B981] text-black"
          }`}>
            {hasHigh ? "Remediation Advised" : "Baseline Secured"}
          </span>
        </div>

        {/* Report Overview Panel */}
        <div className="bg-[#141A23] border-2 border-black shadow-[4px_4px_0px_#000] p-6 grid grid-cols-1 sm:grid-cols-4 gap-4">
          <div>
            <span className="text-[10px] font-bold text-[#94A3B8] uppercase tracking-wider font-mono">Report Identifier</span>
            <p className="text-sm font-mono font-bold text-[#38BDF8] mt-1">{report.report_id}</p>
          </div>
          <div>
            <span className="text-[10px] font-bold text-[#94A3B8] uppercase tracking-wider font-mono">Mission Target</span>
            <Link to={`/mission/${report.mission_id}`} className="text-sm font-mono font-bold text-[#F8FAFC] hover:text-[#E2F952] hover:underline block mt-1">
              {report.mission_id}
            </Link>
          </div>
          <div>
            <span className="text-[10px] font-bold text-[#94A3B8] uppercase tracking-wider font-mono">Evaluated URL</span>
            <p className="text-sm font-mono font-medium text-[#F8FAFC] truncate mt-1" title={report.target_url}>
              {report.target_url}
            </p>
          </div>
          <div>
            <span className="text-[10px] font-bold text-[#94A3B8] uppercase tracking-wider font-mono">Generated At</span>
            <p className="text-sm font-medium text-[#94A3B8] mt-1">
              {new Date(report.generated_at).toLocaleString()}
            </p>
          </div>
        </div>

        {/* Unified Platform Metric Strip */}
        <SecurityMetricsStrip variant="full" />

        {/* Core Report Content Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Executive Summary & Recommendations */}
          <div className="lg:col-span-2 space-y-6">
            {/* Executive Summary */}
            <div className="bg-[#141A23] border-2 border-black shadow-[4px_4px_0px_#000] p-6 space-y-3">
              <h3 className="text-sm font-bold text-[#F8FAFC] border-b-2 border-black pb-3 flex items-center gap-2">
                <FileText className="w-4 h-4 text-[#E2F952]" /> Executive Summary
              </h3>
              <p className="text-xs text-[#CBD5E1] leading-relaxed whitespace-pre-wrap font-sans">
                {report.executive_summary}
              </p>
            </div>

            {/* Recommendations */}
            <div className="bg-[#141A23] border-2 border-black shadow-[4px_4px_0px_#000] p-6 space-y-3">
              <h3 className="text-sm font-bold text-[#F8FAFC] border-b-2 border-black pb-3 flex items-center gap-2">
                <ClipboardList className="w-4 h-4 text-[#10B981]" /> Actionable Remediations
              </h3>
              <ul className="space-y-3">
                {report.recommendations.map((rec, idx) => (
                  <li key={idx} className="flex gap-3 items-start p-3.5 bg-[#0E1217] border-2 border-black shadow-[2px_2px_0px_#000]">
                    <span className="text-xs font-mono font-bold text-black bg-[#E2F952] border border-black w-5 h-5 flex items-center justify-center shrink-0 mt-0.5">
                      {idx + 1}
                    </span>
                    <p className="text-xs text-[#CBD5E1] leading-relaxed font-sans">{rec}</p>
                  </li>
                ))}
              </ul>
            </div>
          </div>

          {/* Sidebar Metrics */}
          <div className="space-y-6">
            {/* OWASP Top 10 Risk Alignment */}
            <div className="bg-[#141A23] border-2 border-black shadow-[4px_4px_0px_#000] p-6 space-y-3">
              <h3 className="text-sm font-bold text-[#F8FAFC] border-b-2 border-black pb-3 flex items-center gap-2">
                <ShieldAlert className="w-4 h-4 text-[#EF4444]" /> OWASP Top 10 Alignment
              </h3>
              {activeOwasp.length === 0 ? (
                <p className="text-xs text-[#94A3B8] font-editorial italic py-2">No critical OWASP surface deviations mapped.</p>
              ) : (
                <div className="space-y-2">
                  {activeOwasp.map((item, idx) => (
                    <div key={idx} className="p-3 bg-[#0E1217] border-2 border-black shadow-[1.5px_1.5px_0px_#000]">
                      <span className="text-[10px] font-mono font-bold text-[#EF4444] block">{item.code}</span>
                      <span className="text-xs font-semibold text-[#F8FAFC] mt-0.5 block">{item.name}</span>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Severity Distribution */}
            <div className="bg-[#141A23] border-2 border-black shadow-[4px_4px_0px_#000] p-6 space-y-3">
              <h3 className="text-sm font-bold text-[#F8FAFC] border-b-2 border-black pb-3 flex items-center gap-2">
                <Activity className="w-4 h-4 text-[#38BDF8]" /> Severity Breakdown
              </h3>
              <div className="grid grid-cols-2 gap-2 text-center text-xs">
                {Object.entries(report.severity_breakdown || {}).map(([sev, count]) => (
                  <div key={sev} className="p-3 bg-[#0E1217] border-2 border-black shadow-[1.5px_1.5px_0px_#000]">
                    <span className="text-[10px] text-[#94A3B8] font-mono uppercase tracking-wider block">{sev}</span>
                    <span className="text-base font-mono font-bold text-[#F8FAFC] mt-0.5 block">{count}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>

        {/* Findings Detail Section */}
        <div className="bg-[#141A23] border-2 border-black shadow-[4px_4px_0px_#000] p-6 space-y-4">
          <h3 className="text-sm font-bold text-[#F8FAFC] border-b-2 border-black pb-3 flex items-center justify-between">
            <span className="flex items-center gap-2">
              <ShieldAlert className="w-4 h-4 text-[#E2F952]" /> Detailed Technical Observations
            </span>
            <span className="text-xs text-[#94A3B8] font-mono">{report.findings.length} findings</span>
          </h3>

          <div className="space-y-4">
            {report.findings.map((f, idx) => (
              <div key={idx} className="border-2 border-black bg-[#0E1217] shadow-[3px_3px_0px_#000] p-5 space-y-3">
                <div className="flex justify-between items-center">
                  <div className="flex items-center gap-2.5">
                    <span className={`px-2 py-0.5 border border-black shadow-[1px_1px_0px_#000] text-[10px] font-mono font-extrabold uppercase tracking-wide ${getSeverityStyle(f.severity)}`}>
                      {f.severity}
                    </span>
                    <h4 className="text-xs font-bold text-[#F8FAFC]">{f.title}</h4>
                  </div>
                  <span className="text-xs font-mono font-bold text-[#38BDF8]">{f.finding_id}</span>
                </div>

                <p className="text-xs text-[#CBD5E1] leading-relaxed font-sans">{f.description}</p>

                {f.reasoning && (
                  <div className="p-3 bg-[#181524] border-2 border-black shadow-[2px_2px_0px_#000] text-[#DDD6FE] text-xs font-editorial italic leading-relaxed">
                    <span className="font-bold text-[#C084FC] not-italic block text-[10px] uppercase mb-1 font-mono">Explainable AI Analysis</span>
                    {f.reasoning}
                  </div>
                )}

                {f.evidence && f.evidence.length > 0 && (
                  <div className="bg-[#141A23] border-2 border-black p-3 space-y-1 font-mono text-[10px] text-[#38BDF8]">
                    {f.evidence.map((ev, i) => (
                      <div key={i} className="flex gap-2">
                        <span className="text-[#94A3B8] select-none font-bold">{i + 1}.</span>
                        <span className="break-all">{ev}</span>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  // Otherwise, display the list of all reports
  return (
    <div className="space-y-8 animate-fadeIn">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b-2 border-black pb-6">
        <div>
          <div className="flex items-center gap-2.5">
            <h1 className="text-2xl font-extrabold tracking-tight text-[#F8FAFC]">
              Security Reports <span className="font-editorial italic font-normal text-[#E2F952]">Registry</span>
            </h1>
            <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 text-[11px] font-mono font-bold bg-[#141A23] text-[#38BDF8] border-2 border-black shadow-[1.5px_1.5px_0px_#000]">
              <FileText className="w-3.5 h-3.5 text-[#38BDF8]" />
              {reports?.length || 0} Reports
            </span>
          </div>
          <p className="text-xs text-[#94A3B8] mt-1 font-sans">Audit assessment registry generated after each successful reconnaissance exploration.</p>
        </div>
      </div>

      {/* Unified Platform Metrics Strip */}
      <SecurityMetricsStrip variant="full" />

      {/* Reports Table */}
      <div className="bg-[#141A23] border-2 border-black shadow-[4px_4px_0px_#000] overflow-hidden">
        {isListLoading ? (
          <div className="flex flex-col items-center justify-center py-24 text-center">
            <div className="w-10 h-10 border-2 border-t-transparent border-[#E2F952] animate-spin"></div>
            <span className="text-[#94A3B8] text-xs font-semibold mt-4 font-mono">Loading reports database...</span>
          </div>
        ) : !reports || reports.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-20 text-center space-y-2">
            <FileText className="w-12 h-12 text-[#94A3B8] stroke-1" />
            <p className="text-sm font-bold text-[#F8FAFC]">No reports available yet.</p>
            <p className="text-xs text-[#94A3B8] font-editorial italic">Reports appear once an orchestrator mission completes.</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead>
                <tr className="bg-[#0E1217] border-b-2 border-black text-[#94A3B8] font-bold uppercase tracking-wider text-[10px]">
                  <th className="p-4">Report ID</th>
                  <th className="p-4">Mission ID</th>
                  <th className="p-4">Target Domain</th>
                  <th className="p-4">Generated At</th>
                  <th className="p-4 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-black/60">
                {reports.map((r) => (
                  <tr
                    key={r.report_id}
                    className="hover:bg-[#18202C] transition-all cursor-pointer group"
                    onClick={() => setSearchParams({ id: r.report_id })}
                  >
                    <td className="p-4 font-mono font-bold text-[#38BDF8] text-[11px]">{r.report_id}</td>
                    <td className="p-4 font-mono text-[#94A3B8]">{r.mission_id}</td>
                    <td className="p-4 font-semibold text-[#F8FAFC] truncate max-w-[220px]" title={r.target}>
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
                        className="px-3 py-1 bg-[#0E1217] group-hover:bg-[#E2F952] group-hover:text-black border border-black shadow-[1.5px_1.5px_0px_#000] active:translate-x-[1px] active:translate-y-[1px] text-[11px] font-mono font-bold text-[#CBD5E1] transition-all cursor-pointer"
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
