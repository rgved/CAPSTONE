import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import { api } from "../services/api";
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
  ShieldAlert,
  Percent,
  Atom,
  Clock,
  ExternalLink
} from "lucide-react";

const COLORS = ["#3B82F6", "#22C55E", "#F59E0B", "#EF4444", "#8B5CF6", "#EC4899"];

export default function Dashboard() {
  const { data, isLoading } = useQuery({
    queryKey: ["dashboard"],
    queryFn: api.getDashboard,
    refetchInterval: 5000 // Keep homepage statistics updated live
  });

  if (isLoading) {
    return (
      <div className="flex-1 flex items-center justify-center bg-[#0B1220] min-h-[500px]">
        <div className="flex flex-col items-center gap-4">
          <div className="w-12 h-12 rounded-full border-4 border-t-transparent border-[#3B82F6] animate-spin"></div>
          <span className="text-[#94A3B8] text-sm font-medium">Loading platform metrics...</span>
        </div>
      </div>
    );
  }

  const stats = data?.stats ?? {
    total_missions: 0,
    total_findings: 0,
    avg_token_reduction: 0.0,
    features_identified: 0
  };

  const recentMissions = data?.recent_missions ?? [];
  const findingsSeverity = data?.findings_severity ?? [];
  const featureDistribution = (data?.feature_distribution ?? []).map((item: any) => ({
    ...item,
    name: item.name?.toLowerCase() === "unknown" ? "General Web Surface" : item.name
  }));

  return (
    <div className="space-y-8 animate-fadeIn">
      {/* Page Header */}
      <div>
        <h1 className="text-2xl font-bold text-[#F8FAFC]">Security Dashboard</h1>
        <p className="text-sm text-[#94A3B8] mt-1">Real-time status overview of the Web Reconnaissance Platform.</p>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-6">
        {/* Total Missions */}
        <div className="bg-[#111827] border border-[#1F2937] p-6 rounded-xl hover:border-[#3B82F6] transition-all duration-300">
          <div className="flex justify-between items-start">
            <div>
              <p className="text-xs font-semibold text-[#94A3B8] uppercase tracking-wider">Total Missions</p>
              <h3 className="text-3xl font-bold text-[#F8FAFC] mt-2">{stats.total_missions}</h3>
            </div>
            <div className="p-3 bg-[#3B82F6]/10 rounded-lg text-[#3B82F6]">
              <Target className="w-6 h-6" />
            </div>
          </div>
          <div className="mt-4 flex items-center gap-1 text-[11px] text-[#22C55E]">
            <span>Active target explorations</span>
          </div>
        </div>

        {/* Total Findings */}
        <div className="bg-[#111827] border border-[#1F2937] p-6 rounded-xl hover:border-[#EF4444] transition-all duration-300">
          <div className="flex justify-between items-start">
            <div>
              <p className="text-xs font-semibold text-[#94A3B8] uppercase tracking-wider">Total Findings</p>
              <h3 className="text-3xl font-bold text-[#F8FAFC] mt-2">{stats.total_findings}</h3>
            </div>
            <div className="p-3 bg-[#EF4444]/10 rounded-lg text-[#EF4444]">
              <ShieldAlert className="w-6 h-6" />
            </div>
          </div>
          <div className="mt-4 flex items-center gap-1 text-[11px] text-[#EF4444]">
            <span>Identified potential weaknesses</span>
          </div>
        </div>

        {/* Avg Token Reduction */}
        <div className="bg-[#111827] border border-[#1F2937] p-6 rounded-xl hover:border-[#22C55E] transition-all duration-300">
          <div className="flex justify-between items-start">
            <div>
              <p className="text-xs font-semibold text-[#94A3B8] uppercase tracking-wider">Avg Token Reduction</p>
              <h3 className="text-3xl font-bold text-[#F8FAFC] mt-2">{stats.avg_token_reduction}%</h3>
            </div>
            <div className="p-3 bg-[#22C55E]/10 rounded-lg text-[#22C55E]">
              <Percent className="w-6 h-6" />
            </div>
          </div>
          <div className="mt-4 flex items-center gap-1 text-[11px] text-[#22C55E]">
            <span>Research selective fetch savings</span>
          </div>
        </div>

        {/* Features Identified */}
        <div className="bg-[#111827] border border-[#1F2937] p-6 rounded-xl hover:border-[#8B5CF6] transition-all duration-300">
          <div className="flex justify-between items-start">
            <div>
              <p className="text-xs font-semibold text-[#94A3B8] uppercase tracking-wider">Capabilities Identified</p>
              <h3 className="text-3xl font-bold text-[#F8FAFC] mt-2">{stats.features_identified}</h3>
            </div>
            <div className="p-3 bg-[#8B5CF6]/10 rounded-lg text-[#8B5CF6]">
              <Atom className="w-6 h-6" />
            </div>
          </div>
          <div className="mt-4 flex items-center gap-1 text-[11px] text-[#8B5CF6]">
            <span>Classified app functionality types</span>
          </div>
        </div>
      </div>

      {/* Grid: Recent Scans and Charts */}
      <div className="grid grid-cols-1 xl:grid-cols-3 gap-8">
        {/* Recent Missions Table */}
        <div className="bg-[#111827] border border-[#1F2937] rounded-xl p-6 xl:col-span-2 flex flex-col">
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-base font-bold text-[#F8FAFC]">Recent Missions</h2>
            <Link to="/new-scan" className="text-xs font-semibold text-[#3B82F6] hover:underline flex items-center gap-1">
              New Scan <ExternalLink className="w-3.5 h-3.5" />
            </Link>
          </div>
          
          <div className="flex-1 overflow-x-auto">
            {recentMissions.length === 0 ? (
              <div className="flex flex-col items-center justify-center py-12 text-center h-full">
                <Target className="w-12 h-12 text-[#94A3B8] stroke-1 mb-3 animate-pulse" />
                <p className="text-sm font-semibold text-[#F8FAFC]">No missions found.</p>
                <p className="text-xs text-[#94A3B8] mt-1 mb-4">Start your first scan to populate this list.</p>
                <Link to="/new-scan" className="px-4 py-2 bg-[#3B82F6] hover:bg-[#2563EB] text-white text-xs font-bold rounded-lg transition-all">
                  Start Scan
                </Link>
              </div>
            ) : (
              <table className="w-full text-left text-sm">
                <thead>
                  <tr className="border-b border-[#1F2937] text-[#94A3B8] font-medium text-xs uppercase tracking-wider">
                    <th className="pb-3">Mission ID</th>
                    <th className="pb-3">Target</th>
                    <th className="pb-3">Status</th>
                    <th className="pb-3">Findings</th>
                    <th className="pb-3 text-right">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-[#1F2937]">
                  {recentMissions.map((m: any) => (
                    <tr key={m.mission_id} className="hover:bg-[#1F2937]/30 transition-colors">
                      <td className="py-4 font-mono font-bold text-xs text-[#3B82F6]">{m.mission_id}</td>
                      <td className="py-4 font-medium text-[#F8FAFC] truncate max-w-[200px]" title={m.target}>
                        {m.target}
                      </td>
                      <td className="py-4">
                        <span className={`px-2.5 py-1 rounded-full text-[10px] font-bold uppercase tracking-wide ${
                          m.status === "completed" ? "bg-[#22C55E]/10 text-[#22C55E]" :
                          m.status === "failed" ? "bg-[#EF4444]/10 text-[#EF4444]" :
                          "bg-[#F59E0B]/10 text-[#F59E0B] animate-pulse"
                        }`}>
                          {m.status}
                        </span>
                      </td>
                      <td className="py-4 text-[#F8FAFC] font-semibold">{m.findings}</td>
                      <td className="py-4 text-right">
                        <Link to={`/mission/${m.mission_id}`} className="px-3 py-1 bg-[#1F2937] hover:bg-[#3B82F6] hover:text-white rounded text-xs font-semibold transition-all">
                          Inspect
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
        <div className="bg-[#111827] border border-[#1F2937] rounded-xl p-6">
          <h2 className="text-base font-bold text-[#F8FAFC] mb-6">Findings Severity</h2>
          <div className="h-[250px] w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={findingsSeverity} margin={{ top: 10, right: 10, left: -25, bottom: 0 }}>
                <XAxis dataKey="severity" stroke="#94A3B8" fontSize={11} tickLine={false} />
                <YAxis stroke="#94A3B8" fontSize={11} tickLine={false} allowDecimals={false} />
                <Tooltip
                  contentStyle={{ backgroundColor: "#111827", borderColor: "#1F2937" }}
                  labelStyle={{ color: "#F8FAFC" }}
                />
                <Bar dataKey="count" fill="#3B82F6" radius={[4, 4, 0, 0]}>
                  {findingsSeverity.map((entry: any, index: number) => {
                    const color = entry.severity === "High" ? "#EF4444" :
                                  entry.severity === "Medium" ? "#F59E0B" : "#EAB308";
                    return <Cell key={`cell-${index}`} fill={color} />;
                  })}
                </Bar>

              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Feature Distribution Pie Chart */}
      <div className="grid grid-cols-1 xl:grid-cols-3 gap-8">
        <div className="bg-[#111827] border border-[#1F2937] rounded-xl p-6 xl:col-span-1">
          <h2 className="text-base font-bold text-[#F8FAFC] mb-6">Capability Inventory</h2>
          <div className="h-[250px] w-full">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={featureDistribution}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={80}
                  paddingAngle={5}
                  dataKey="value"
                >
                  {featureDistribution.map((_entry: any, index: number) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip
                  contentStyle={{ backgroundColor: "#111827", borderColor: "#1F2937" }}
                  itemStyle={{ color: "#F8FAFC" }}
                />
                <Legend verticalAlign="bottom" height={36} iconType="circle" wrapperStyle={{ fontSize: 10, color: "#94A3B8" }} />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Info panel */}
        <div className="bg-[#111827] border border-[#1F2937] rounded-xl p-6 xl:col-span-2 flex flex-col justify-between">
          <div>
            <h2 className="text-base font-bold text-[#F8FAFC] mb-4">Selective Fetch Research Analysis</h2>
            <p className="text-xs text-[#94A3B8] leading-relaxed">
              This dashboard provides real-time access to the platform's key research metrics. The primary objective is to prove that selective retrieval (retrieving only contextually relevant parts of web application structures) achieves significant token reductions for Large Language Model (LLM) agents without degrading the overall security assessment accuracy.
            </p>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-6">
              <div className="p-4 rounded-lg bg-[#0B1220] border border-[#1F2937]">
                <h4 className="text-xs font-bold text-[#3B82F6]">Baseline Flow</h4>
                <p className="text-[11px] text-[#94A3B8] mt-1">Full HTML source extraction and submission to the LLM agent. Results in excessive token consumption and high latencies.</p>
              </div>
              <div className="p-4 rounded-lg bg-[#0B1220] border border-[#1F2937]">
                <h4 className="text-xs font-bold text-[#22C55E]">Proposed Selective Fetch Flow</h4>
                <p className="text-[11px] text-[#94A3B8] mt-1">Structure extraction and similarity embedding-based ranking filter. Submits only targeted web context to the LLM, reducing tokens by up to 60%+.</p>
              </div>
            </div>
          </div>
          <div className="border-t border-[#1F2937] mt-6 pt-4 flex justify-between items-center text-xs text-[#94A3B8]">
            <div className="flex items-center gap-1.5">
              <Clock className="w-3.5 h-3.5" />
              <span>Auto-refreshes statistics dynamically</span>
            </div>
            <span>Agentic Web Recon Platform</span>
          </div>
        </div>
      </div>
    </div>
  );
}
