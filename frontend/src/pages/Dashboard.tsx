import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import { api } from "../services/api";
import SecurityMetricsStrip from "../components/common/SecurityMetricsStrip";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  Legend
} from "recharts";
import {
  Target,
  Clock,
  ExternalLink,
  Plus,
  AlertTriangle,
  Activity,
  CheckCircle2
} from "lucide-react";

const PALETTE = ["#38BDF8", "#10B981", "#F59E0B", "#EF4444", "#8B5CF6", "#EC4899", "#6366F1"];

export default function Dashboard() {
  const { data, isLoading } = useQuery({
    queryKey: ["dashboard"],
    queryFn: api.getDashboard,
    refetchInterval: 5000
  });

  if (isLoading) {
    return (
      <div className="flex-1 flex items-center justify-center bg-[#090D16] min-h-[500px]">
        <div className="flex flex-col items-center gap-4">
          <div className="w-10 h-10 rounded-full border-2 border-t-transparent border-[#38BDF8] animate-spin"></div>
          <span className="text-[#94A3B8] text-xs font-mono tracking-wider uppercase">Loading Security Telemetry...</span>
        </div>
      </div>
    );
  }



  const recentMissions = data?.recent_missions ?? [];
  const findingsSeverity = data?.findings_severity ?? [];
  const featureDistribution = (data?.feature_distribution ?? []).map((item: any) => ({
    ...item,
    name: item.name?.toLowerCase() === "unknown" ? "General Web Surface" : item.name
  }));

  return (
    <div className="space-y-8 animate-fadeIn">
      {/* Executive Command Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-[#1E293B] pb-6">
        <div>
          <div className="flex items-center gap-2.5">
            <h1 className="text-2xl font-bold tracking-tight text-[#F8FAFC]">Security Reconnaissance Center</h1>
            <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[11px] font-semibold bg-[#10B981]/10 text-[#10B981] border border-[#10B981]/20">
              <span className="w-1.5 h-1.5 rounded-full bg-[#10B981] animate-ping"></span>
              Live Engine
            </span>
          </div>
          <p className="text-xs text-[#94A3B8] mt-1">Autonomous multi-agent attack surface discovery and defensive posture auditing.</p>
        </div>

        <Link
          to="/new-scan"
          className="inline-flex items-center justify-center gap-2 px-4 py-2.5 rounded-lg bg-gradient-to-r from-[#0284C7] to-[#0EA5E9] hover:from-[#0369A1] hover:to-[#0284C7] text-white text-xs font-bold shadow-lg shadow-sky-500/15 transition-all"
        >
          <Plus className="w-4 h-4" />
          <span>Launch Scan</span>
        </Link>
      </div>

      {/* Primary Common Telemetry Stat Cards */}
      <SecurityMetricsStrip variant="full" />

      {/* Grid: Recent Missions & Severity Distribution */}
      <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
        {/* Recent Missions Table */}
        <div className="bg-[#0F172A] border border-[#1E293B] rounded-xl p-5 xl:col-span-2 flex flex-col shadow-sm">
          <div className="flex justify-between items-center mb-5 pb-3 border-b border-[#1E293B]">
            <div>
              <h2 className="text-sm font-bold text-[#F8FAFC] tracking-wide">Recent Reconnaissance Missions</h2>
              <p className="text-[11px] text-[#64748B] mt-0.5">Automated crawling, surface extraction, and risk assessment history</p>
            </div>
            <Link to="/new-scan" className="text-xs font-semibold text-[#38BDF8] hover:text-[#0EA5E9] flex items-center gap-1 transition-colors">
              New Target <ExternalLink className="w-3.5 h-3.5" />
            </Link>
          </div>

          <div className="flex-1 overflow-x-auto">
            {recentMissions.length === 0 ? (
              <div className="flex flex-col items-center justify-center py-12 text-center h-full">
                <Target className="w-10 h-10 text-[#475569] stroke-1 mb-2 animate-pulse" />
                <p className="text-xs font-semibold text-[#F8FAFC]">No missions launched yet</p>
                <p className="text-[11px] text-[#64748B] mt-1 mb-4">Execute a scan against any target URL to see live observations.</p>
                <Link to="/new-scan" className="px-3.5 py-1.5 bg-[#0284C7] hover:bg-[#0369A1] text-white text-xs font-bold rounded-lg transition-all">
                  Launch First Scan
                </Link>
              </div>
            ) : (
              <table className="w-full text-left text-xs">
                <thead>
                  <tr className="border-b border-[#1E293B] text-[#64748B] font-semibold uppercase tracking-wider text-[10px]">
                    <th className="pb-3">Mission</th>
                    <th className="pb-3">Target URL</th>
                    <th className="pb-3">Status</th>
                    <th className="pb-3">Findings</th>
                    <th className="pb-3 text-right">Inspect</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-[#1E293B]/60">
                  {recentMissions.map((m: any) => (
                    <tr key={m.mission_id} className="hover:bg-[#1E293B]/30 transition-colors">
                      <td className="py-3.5 font-mono font-bold text-[#38BDF8] text-[11px]">{m.mission_id}</td>
                      <td className="py-3.5 font-medium text-[#F8FAFC] truncate max-w-[220px]" title={m.target}>
                        {m.target}
                      </td>
                      <td className="py-3.5">
                        <span className={`px-2 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-wider border ${
                          m.status === "completed" ? "bg-[#10B981]/10 text-[#10B981] border-[#10B981]/30" :
                          m.status === "failed" ? "bg-[#EF4444]/10 text-[#EF4444] border-[#EF4444]/30" :
                          "bg-[#F59E0B]/10 text-[#F59E0B] border-[#F59E0B]/30 animate-pulse"
                        }`}>
                          {m.status}
                        </span>
                      </td>
                      <td className="py-3.5">
                        <span className={`font-mono font-bold ${m.findings > 0 ? "text-[#EF4444]" : "text-[#10B981]"}`}>
                          {m.findings}
                        </span>
                      </td>
                      <td className="py-3.5 text-right">
                        <Link
                          to={`/mission/${m.mission_id}`}
                          className="px-2.5 py-1 bg-[#1E293B] hover:bg-[#0284C7] hover:text-white rounded text-[11px] font-semibold text-[#94A3B8] transition-all"
                        >
                          View Details
                        </Link>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        </div>

        {/* Findings Severity Chart */}
        <div className="bg-[#0F172A] border border-[#1E293B] rounded-xl p-5 flex flex-col shadow-sm">
          <div className="mb-4 pb-3 border-b border-[#1E293B]">
            <h2 className="text-sm font-bold text-[#F8FAFC] tracking-wide">Vulnerability Severity Profile</h2>
            <p className="text-[11px] text-[#64748B] mt-0.5">Identified risks classified by exploitability</p>
          </div>
          <div className="h-[240px] w-full flex-1">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={findingsSeverity} margin={{ top: 10, right: 10, left: -25, bottom: 0 }}>
                <XAxis dataKey="severity" stroke="#64748B" fontSize={11} tickLine={false} />
                <YAxis stroke="#64748B" fontSize={11} tickLine={false} allowDecimals={false} />
                <Tooltip
                  contentStyle={{ backgroundColor: "#0F172A", borderColor: "#1E293B", borderRadius: "8px", fontSize: "12px" }}
                  labelStyle={{ color: "#F8FAFC", fontWeight: "bold" }}
                />
                <Bar dataKey="count" fill="#38BDF8" radius={[4, 4, 0, 0]}>
                  {findingsSeverity.map((entry: any, index: number) => {
                    const color = entry.severity === "Critical" ? "#DC2626" :
                                  entry.severity === "High" ? "#EF4444" :
                                  entry.severity === "Medium" ? "#F59E0B" :
                                  entry.severity === "Low" ? "#EAB308" : "#38BDF8";
                    return <Cell key={`cell-${index}`} fill={color} />;
                  })}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Grid: Capability Inventory & Executive Remediation Focus */}
      <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
        {/* Capability Inventory Pie Chart */}
        <div className="bg-[#0F172A] border border-[#1E293B] rounded-xl p-5 xl:col-span-1 shadow-sm">
          <div className="mb-4 pb-3 border-b border-[#1E293B]">
            <h2 className="text-sm font-bold text-[#F8FAFC] tracking-wide">Attack Surface Inventory</h2>
            <p className="text-[11px] text-[#64748B] mt-0.5">Evaluated application functional components</p>
          </div>
          <div className="h-[240px] w-full">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={featureDistribution}
                  cx="50%"
                  cy="50%"
                  innerRadius={55}
                  outerRadius={75}
                  paddingAngle={4}
                  dataKey="value"
                >
                  {featureDistribution.map((_entry: any, index: number) => (
                    <Cell key={`cell-${index}`} fill={PALETTE[index % PALETTE.length]} />
                  ))}
                </Pie>
                <Tooltip
                  contentStyle={{ backgroundColor: "#0F172A", borderColor: "#1E293B", borderRadius: "8px", fontSize: "12px" }}
                  itemStyle={{ color: "#F8FAFC" }}
                />
                <Legend verticalAlign="bottom" height={36} iconType="circle" wrapperStyle={{ fontSize: 10, color: "#94A3B8" }} />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Executive Threat Assessment & Remediation Priorities */}
        <div className="bg-[#0F172A] border border-[#1E293B] rounded-xl p-5 xl:col-span-2 flex flex-col justify-between shadow-sm">
          <div>
            <div className="flex justify-between items-center mb-4 pb-3 border-b border-[#1E293B]">
              <div>
                <h2 className="text-sm font-bold text-[#F8FAFC] tracking-wide">Target Threat Surface & Defensive Guidance</h2>
                <p className="text-[11px] text-[#64748B] mt-0.5">Synthesized reconnaissance priorities aligned with OWASP Top 10 standards</p>
              </div>
              <span className="px-2 py-0.5 rounded bg-[#38BDF8]/10 text-[#38BDF8] border border-[#38BDF8]/30 text-[10px] font-mono font-bold">
                Defense Matrix
              </span>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-3.5 mt-4">
              <div className="p-3.5 rounded-lg bg-[#090D16] border border-[#1E293B]">
                <div className="flex items-center gap-2 text-[#EF4444]">
                  <AlertTriangle className="w-4 h-4 shrink-0" />
                  <h4 className="text-xs font-bold">Baseline Hardening</h4>
                </div>
                <p className="text-[11px] text-[#94A3B8] mt-1.5 leading-relaxed">
                  Verify modern HTTP response headers: Content-Security-Policy (CSP), Strict-Transport-Security (HSTS), and anti-clickjacking directives.
                </p>
              </div>

              <div className="p-3.5 rounded-lg bg-[#090D16] border border-[#1E293B]">
                <div className="flex items-center gap-2 text-[#F59E0B]">
                  <Activity className="w-4 h-4 shrink-0" />
                  <h4 className="text-xs font-bold">Access Controls</h4>
                </div>
                <p className="text-[11px] text-[#94A3B8] mt-1.5 leading-relaxed">
                  Audit discovered administrative pathways, actuators, and exposed API gateways. Ensure Multi-Factor Authentication (MFA) enforcement.
                </p>
              </div>

              <div className="p-3.5 rounded-lg bg-[#090D16] border border-[#1E293B]">
                <div className="flex items-center gap-2 text-[#10B981]">
                  <CheckCircle2 className="w-4 h-4 shrink-0" />
                  <h4 className="text-xs font-bold">Input Validation</h4>
                </div>
                <p className="text-[11px] text-[#94A3B8] mt-1.5 leading-relaxed">
                  Enforce strict server-side validation on forms, file uploads, and reflected URL parameters to prevent code execution & XSS vectors.
                </p>
              </div>
            </div>
          </div>

          <div className="border-t border-[#1E293B] mt-5 pt-3 flex justify-between items-center text-[11px] text-[#64748B]">
            <div className="flex items-center gap-1.5">
              <Clock className="w-3.5 h-3.5 text-[#38BDF8]" />
              <span>Real-time polling active</span>
            </div>
            <span className="font-mono text-[10px]">Agentic Web Security Platform</span>
          </div>
        </div>
      </div>
    </div>
  );
}
