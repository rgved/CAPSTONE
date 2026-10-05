import { useQuery } from "@tanstack/react-query";
import { api } from "../services/api";
import type { MetricsData } from "../types";
import {
  LineChart,
  Line,
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
  Clock,
  Info
} from "lucide-react";

const COLORS = ["#3B82F6", "#22C55E", "#F59E0B", "#EF4444", "#8B5CF6", "#EC4899"];

export default function Metrics() {
  const { data, isLoading } = useQuery<MetricsData>({
    queryKey: ["metrics"],
    queryFn: api.getMetrics,
    refetchInterval: 5000 // Poll live to show new runs dynamically
  });

  if (isLoading) {
    return (
      <div className="flex-1 flex items-center justify-center bg-[#0B1220] min-h-[500px]">
        <div className="flex flex-col items-center gap-4">
          <div className="w-12 h-12 rounded-full border-4 border-t-transparent border-[#3B82F6] animate-spin"></div>
          <span className="text-[#94A3B8] text-sm font-medium">Crunching evaluation metrics...</span>
        </div>
      </div>
    );
  }

  const metrics = data ?? {
    total_missions: 0,
    total_findings: 0,
    avg_runtime: 0.0,
    avg_token_reduction: 0.0,
    token_reduction_by_mission: [],
    findings_by_severity: [],
    feature_distribution: [],
    mission_runtime_trend: []
  };

  return (
    <div className="space-y-8 animate-fadeIn">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-[#F8FAFC]">Research Analytics & Evaluation</h1>
        <p className="text-sm text-[#94A3B8] mt-1">Token efficiency and runtime analysis supporting the selective retrieval hypothesis.</p>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-6">
        {/* Total Missions */}
        <div className="bg-[#111827] border border-[#1F2937] p-6 rounded-xl">
          <p className="text-xs font-semibold text-[#94A3B8] uppercase tracking-wider">Total Missions</p>
          <h3 className="text-3xl font-bold text-[#F8FAFC] mt-2">{metrics.total_missions}</h3>
          <div className="mt-3 flex items-center gap-1.5 text-[10px] text-[#3B82F6] font-medium">
            <Target className="w-3.5 h-3.5" /> Full explorative runs
          </div>
        </div>

        {/* Total Findings */}
        <div className="bg-[#111827] border border-[#1F2937] p-6 rounded-xl">
          <p className="text-xs font-semibold text-[#94A3B8] uppercase tracking-wider">Total Findings</p>
          <h3 className="text-3xl font-bold text-[#F8FAFC] mt-2">{metrics.total_findings}</h3>
          <div className="mt-3 flex items-center gap-1.5 text-[10px] text-[#EF4444] font-medium">
            <ShieldAlert className="w-3.5 h-3.5" /> Discovered observations
          </div>
        </div>

        {/* Average Runtime */}
        <div className="bg-[#111827] border border-[#1F2937] p-6 rounded-xl">
          <p className="text-xs font-semibold text-[#94A3B8] uppercase tracking-wider">Average Runtime</p>
          <h3 className="text-3xl font-bold text-[#F8FAFC] mt-2">{metrics.avg_runtime}s</h3>
          <div className="mt-3 flex items-center gap-1.5 text-[10px] text-[#F59E0B] font-medium">
            <Clock className="w-3.5 h-3.5" /> Mean execution duration
          </div>
        </div>

        {/* Average Token Reduction */}
        <div className="bg-[#111827] border border-[#1F2937] p-6 rounded-xl">
          <p className="text-xs font-semibold text-[#94A3B8] uppercase tracking-wider">Average Token Reduction</p>
          <h3 className="text-3xl font-bold text-[#F8FAFC] mt-2">{metrics.avg_token_reduction}%</h3>
          <div className="mt-3 flex items-center gap-1.5 text-[10px] text-[#22C55E] font-medium">
            <Percent className="w-3.5 h-3.5" /> Selective Fetch token savings
          </div>
        </div>
      </div>

      {/* Grid: Charts Row 1 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Chart 1: Token Reduction By Mission */}
        <div className="bg-[#111827] border border-[#1F2937] p-6 rounded-xl">
          <div className="flex justify-between items-center mb-6">
            <h3 className="text-sm font-bold text-[#F8FAFC]">Token Reduction by Mission</h3>
            <span className="text-[10px] text-[#22C55E] bg-[#22C55E]/10 px-2 py-0.5 rounded font-bold uppercase">Efficiency %</span>
          </div>
          <div className="h-[250px] w-full">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={metrics.token_reduction_by_mission} margin={{ top: 10, right: 10, left: -25, bottom: 0 }}>
                <XAxis dataKey="mission_id" stroke="#94A3B8" fontSize={11} tickLine={false} />
                <YAxis stroke="#94A3B8" fontSize={11} tickLine={false} unit="%" />
                <Tooltip
                  contentStyle={{ backgroundColor: "#111827", borderColor: "#1F2937" }}
                  labelStyle={{ color: "#F8FAFC" }}
                />
                <Line type="monotone" dataKey="reduction" stroke="#22C55E" strokeWidth={3} activeDot={{ r: 6 }} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Chart 2: Findings by Severity */}
        <div className="bg-[#111827] border border-[#1F2937] p-6 rounded-xl">
          <div className="flex justify-between items-center mb-6">
            <h3 className="text-sm font-bold text-[#F8FAFC]">Findings by Severity</h3>
            <span className="text-[10px] text-[#EF4444] bg-[#EF4444]/10 px-2 py-0.5 rounded font-bold uppercase">Risk Breakdown</span>
          </div>
          <div className="h-[250px] w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={metrics.findings_by_severity} margin={{ top: 10, right: 10, left: -25, bottom: 0 }}>
                <XAxis dataKey="severity" stroke="#94A3B8" fontSize={11} tickLine={false} />
                <YAxis stroke="#94A3B8" fontSize={11} tickLine={false} allowDecimals={false} />
                <Tooltip
                  contentStyle={{ backgroundColor: "#111827", borderColor: "#1F2937" }}
                  labelStyle={{ color: "#F8FAFC" }}
                />
                <Bar dataKey="count" fill="#3B82F6" radius={[4, 4, 0, 0]}>
                  {metrics.findings_by_severity.map((entry, index) => {
                    const color = entry.severity === "High" ? "#EF4444" :
                                  entry.severity === "Medium" ? "#F59E0B" :
                                  entry.severity === "Low" ? "#EAB308" : "#3B82F6";
                    return <Cell key={`cell-${index}`} fill={color} />;
                  })}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Grid: Charts Row 2 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Chart 3: Feature Distribution */}
        <div className="bg-[#111827] border border-[#1F2937] p-6 rounded-xl">
          <div className="flex justify-between items-center mb-6">
            <h3 className="text-sm font-bold text-[#F8FAFC]">Feature Distribution</h3>
            <span className="text-[10px] text-[#8B5CF6] bg-[#8B5CF6]/10 px-2 py-0.5 rounded font-bold uppercase">App Coverage</span>
          </div>
          <div className="h-[250px] w-full">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={(metrics.feature_distribution || []).map((item) => ({
                    ...item,
                    name: item.name?.toLowerCase() === "unknown" ? "General Web Surface" : item.name
                  }))}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={80}
                  paddingAngle={5}
                  dataKey="count"
                  nameKey="name"
                >
                  {(metrics.feature_distribution || []).map((_entry: any, index: number) => (
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

        {/* Chart 4: Mission Runtime Trend */}
        <div className="bg-[#111827] border border-[#1F2937] p-6 rounded-xl">
          <div className="flex justify-between items-center mb-6">
            <h3 className="text-sm font-bold text-[#F8FAFC]">Mission Runtime Trend</h3>
            <span className="text-[10px] text-[#F59E0B] bg-[#F59E0B]/10 px-2 py-0.5 rounded font-bold uppercase">Latency (s)</span>
          </div>
          <div className="h-[250px] w-full">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={metrics.mission_runtime_trend} margin={{ top: 10, right: 10, left: -25, bottom: 0 }}>
                <XAxis dataKey="mission_id" stroke="#94A3B8" fontSize={11} tickLine={false} />
                <YAxis stroke="#94A3B8" fontSize={11} tickLine={false} unit="s" />
                <Tooltip
                  contentStyle={{ backgroundColor: "#111827", borderColor: "#1F2937" }}
                  labelStyle={{ color: "#F8FAFC" }}
                />
                <Line type="monotone" dataKey="runtime" stroke="#F59E0B" strokeWidth={3} activeDot={{ r: 6 }} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Analysis notice */}
      <div className="p-4 rounded-lg bg-blue-500/5 border border-blue-500/10 text-xs text-[#94A3B8] flex items-start gap-2.5">
        <Info className="w-5 h-5 text-[#3B82F6] shrink-0 mt-0.5" />
        <p className="leading-relaxed">
          The Token Reduction and Runtime metrics are aggregated automatically from execution checkpoints saved to SQLite. In a typical scan, the Selective Fetch Service leverages local semantic similarity lookups (indexing headings, forms, inputs, and button structures) to prune the context before dispatching tasks to LLM reasoning workers. This reduces LLM token overheads while maintaining identical security reasoning capabilities.
        </p>
      </div>
    </div>
  );
}
