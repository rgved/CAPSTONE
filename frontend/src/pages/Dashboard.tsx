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
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b-2 border-black pb-6">
        <div>
          <div className="flex items-center gap-2.5">
            <h1 className="text-2xl font-black tracking-tight text-[#F8FAFC]">Security Reconnaissance Center</h1>
            <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-md text-[11px] font-bold bg-[#E2F952] text-black border-2 border-black shadow-[1.5px_1.5px_0px_#000] font-mono">
              Live Engine
            </span>
          </div>
          <p className="text-xs text-[#94A3B8] mt-1 font-editorial italic">
            Autonomous multi-agent attack surface discovery and defensive posture auditing.
          </p>
        </div>

        <Link
          to="/new-scan"
          className="inline-flex items-center justify-center gap-2 px-4 py-2.5 rounded-lg bg-[#E2F952] text-black text-xs font-black border-2 border-black shadow-[3px_3px_0px_#000] hover:-translate-x-0.5 hover:-translate-y-0.5 hover:shadow-[4.5px_4.5px_0px_#000] active:translate-x-0.5 active:translate-y-0.5 active:shadow-[1px_1px_0px_#000] transition-all duration-150 cursor-pointer"
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
        <div className="bg-[#141A23] border-2 border-black shadow-[3px_3px_0px_#000] rounded-xl p-5 xl:col-span-2 flex flex-col">
          <div className="flex justify-between items-center mb-5 pb-3 border-b-2 border-black">
            <div>
              <h2 className="text-sm font-black text-[#F8FAFC] tracking-wide">Recent Reconnaissance Missions</h2>
              <p className="text-[11px] text-[#94A3B8] mt-0.5 font-editorial italic">Automated crawling, surface extraction, and risk assessment history</p>
            </div>
            <Link to="/new-scan" className="text-xs font-bold text-[#E2F952] hover:underline flex items-center gap-1 font-mono">
              New Target <ExternalLink className="w-3.5 h-3.5" />
            </Link>
          </div>

          <div className="flex-1 overflow-x-auto">
            {recentMissions.length === 0 ? (
              <div className="flex flex-col items-center justify-center py-12 text-center h-full">
                <Target className="w-10 h-10 text-[#475569] stroke-1 mb-2 animate-pulse" />
                <p className="text-xs font-bold text-[#F8FAFC]">No missions launched yet</p>
                <p className="text-[11px] text-[#94A3B8] mt-1 mb-4 font-editorial italic">Execute a scan against any target URL to see live observations.</p>
                <Link to="/new-scan" className="px-4 py-2 bg-[#E2F952] text-black text-xs font-black border-2 border-black shadow-[2.5px_2.5px_0px_#000] hover:-translate-x-0.5 hover:-translate-y-0.5 hover:shadow-[4px_4px_0px_#000] active:translate-x-0.5 active:translate-y-0.5 rounded-lg transition-all">
                  Launch First Scan
                </Link>
              </div>
            ) : (
              <table className="w-full text-left text-xs">
                <thead>
                  <tr className="border-b-2 border-black text-[#94A3B8] font-bold uppercase tracking-wider text-[10px] font-mono">
                    <th className="pb-3">Mission</th>
                    <th className="pb-3">Target URL</th>
                    <th className="pb-3">Status</th>
                    <th className="pb-3">Findings</th>
                    <th className="pb-3 text-right">Inspect</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-[#202938]">
                  {recentMissions.map((m: any) => (
                    <tr key={m.mission_id} className="hover:bg-[#181F2A] transition-colors">
                      <td className="py-3.5 font-mono font-bold text-[#38BDF8] text-[11px]">{m.mission_id}</td>
                      <td className="py-3.5 font-medium text-[#F8FAFC] truncate max-w-[220px]" title={m.target}>
                        {m.target}
                      </td>
                      <td className="py-3.5">
                        <span className={`px-2 py-0.5 rounded text-[10px] font-black uppercase tracking-wider border-1.5 border-black shadow-[1px_1px_0px_#000] font-mono ${
                          m.status === "completed" ? "bg-[#10B981] text-black" :
                          m.status === "failed" ? "bg-[#EF4444] text-black" :
                          "bg-[#F59E0B] text-black animate-pulse"
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
                          className="px-3 py-1 bg-[#181F2A] text-white border-2 border-black shadow-[2px_2px_0px_#000] hover:bg-[#E2F952] hover:text-black hover:shadow-[3px_3px_0px_#000] rounded text-[11px] font-bold transition-all"
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
        <div className="bg-[#141A23] border-2 border-black shadow-[3px_3px_0px_#000] rounded-xl p-5 flex flex-col">
          <div className="mb-4 pb-3 border-b-2 border-black">
            <h2 className="text-sm font-black text-[#F8FAFC] tracking-wide">Vulnerability Severity Profile</h2>
            <p className="text-[11px] text-[#94A3B8] mt-0.5 font-editorial italic">Identified risks classified by exploitability</p>
          </div>
          <div className="h-[240px] w-full flex-1">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={findingsSeverity} margin={{ top: 10, right: 10, left: -25, bottom: 0 }}>
                <XAxis dataKey="severity" stroke="#94A3B8" fontSize={11} tickLine={false} />
                <YAxis stroke="#94A3B8" fontSize={11} tickLine={false} allowDecimals={false} />
                <Tooltip
                  contentStyle={{ backgroundColor: "#141A23", border: "2px solid #000000", boxShadow: "3px 3px 0px #000000", borderRadius: "8px", fontSize: "12px" }}
                  labelStyle={{ color: "#F8FAFC", fontWeight: "bold" }}
                />
                <Bar dataKey="count" fill="#E2F952" radius={[4, 4, 0, 0]}>
                  {findingsSeverity.map((entry: any, index: number) => {
                    const color = entry.severity === "Critical" ? "#DC2626" :
                                  entry.severity === "High" ? "#EF4444" :
                                  entry.severity === "Medium" ? "#F59E0B" :
                                  entry.severity === "Low" ? "#38BDF8" : "#E2F952";
                    return <Cell key={`cell-${index}`} fill={color} stroke="#000" strokeWidth={1.5} />;
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
        <div className="bg-[#141A23] border-2 border-black shadow-[3px_3px_0px_#000] rounded-xl p-5 xl:col-span-1">
          <div className="mb-4 pb-3 border-b-2 border-black">
            <h2 className="text-sm font-black text-[#F8FAFC] tracking-wide">Attack Surface Inventory</h2>
            <p className="text-[11px] text-[#94A3B8] mt-0.5 font-editorial italic">Evaluated application functional components</p>
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
                  stroke="#000"
                  strokeWidth={2}
                >
                  {featureDistribution.map((_entry: any, index: number) => (
                    <Cell key={`cell-${index}`} fill={PALETTE[index % PALETTE.length]} />
                  ))}
                </Pie>
                <Tooltip
                  contentStyle={{ backgroundColor: "#141A23", border: "2px solid #000", boxShadow: "3px 3px 0px #000", borderRadius: "8px", fontSize: "12px" }}
                  itemStyle={{ color: "#F8FAFC" }}
                />
                <Legend verticalAlign="bottom" height={36} iconType="circle" wrapperStyle={{ fontSize: 10, color: "#94A3B8" }} />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Executive Threat Assessment & Remediation Priorities */}
        <div className="bg-[#141A23] border-2 border-black shadow-[3px_3px_0px_#000] rounded-xl p-5 xl:col-span-2 flex flex-col justify-between">
          <div>
            <div className="flex justify-between items-center mb-4 pb-3 border-b-2 border-black">
              <div>
                <h2 className="text-sm font-black text-[#F8FAFC] tracking-wide">Target Threat Surface & Defensive Guidance</h2>
                <p className="text-[11px] text-[#94A3B8] mt-0.5 font-editorial italic">Synthesized reconnaissance priorities aligned with OWASP Top 10 standards</p>
              </div>
              <span className="px-2.5 py-0.5 rounded border-2 border-black bg-[#E2F952] text-black text-[10px] font-mono font-black shadow-[1.5px_1.5px_0px_#000]">
                Defense Matrix
              </span>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-3.5 mt-4">
              <div className="p-3.5 rounded-lg bg-[#0E1217] border-2 border-black shadow-[2px_2px_0px_#000]">
                <div className="flex items-center gap-2 text-[#EF4444]">
                  <AlertTriangle className="w-4 h-4 shrink-0" />
                  <h4 className="text-xs font-black">Baseline Hardening</h4>
                </div>
                <p className="text-[11px] text-[#94A3B8] mt-1.5 leading-relaxed font-editorial italic">
                  Verify modern HTTP response headers: Content-Security-Policy (CSP), Strict-Transport-Security (HSTS), and anti-clickjacking directives.
                </p>
              </div>

              <div className="p-3.5 rounded-lg bg-[#0E1217] border-2 border-black shadow-[2px_2px_0px_#000]">
                <div className="flex items-center gap-2 text-[#F59E0B]">
                  <Activity className="w-4 h-4 shrink-0" />
                  <h4 className="text-xs font-black">Access Controls</h4>
                </div>
                <p className="text-[11px] text-[#94A3B8] mt-1.5 leading-relaxed font-editorial italic">
                  Audit discovered administrative pathways, actuators, and exposed API gateways. Ensure Multi-Factor Authentication (MFA) enforcement.
                </p>
              </div>

              <div className="p-3.5 rounded-lg bg-[#0E1217] border-2 border-black shadow-[2px_2px_0px_#000]">
                <div className="flex items-center gap-2 text-[#10B981]">
                  <CheckCircle2 className="w-4 h-4 shrink-0" />
                  <h4 className="text-xs font-black">Input Validation</h4>
                </div>
                <p className="text-[11px] text-[#94A3B8] mt-1.5 leading-relaxed font-editorial italic">
                  Enforce strict server-side validation on forms, file uploads, and reflected URL parameters to prevent code execution & XSS vectors.
                </p>
              </div>
            </div>
          </div>

          <div className="border-t-2 border-black mt-5 pt-3 flex justify-between items-center text-[11px] text-[#94A3B8]">
            <div className="flex items-center gap-1.5 font-mono">
              <Clock className="w-3.5 h-3.5 text-[#E2F952]" />
              <span>Real-time polling active</span>
            </div>
            <span className="font-mono text-[10px] font-bold">Agentic Web Security Platform</span>
          </div>
        </div>
      </div>
    </div>
  );
}
