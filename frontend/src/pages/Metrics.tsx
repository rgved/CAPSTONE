import { useQuery } from "@tanstack/react-query";
import { api } from "../services/api";
import type { MetricsData } from "../types";
import SecurityMetricsStrip from "../components/common/SecurityMetricsStrip";
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
  Layers,
  Activity,
  ShieldCheck,
  Compass
} from "lucide-react";

const COLORS = ["#38BDF8", "#10B981", "#F59E0B", "#EF4444", "#8B5CF6", "#EC4899", "#6366F1"];

export default function Metrics() {
  const { data, isLoading } = useQuery<MetricsData>({
    queryKey: ["metrics"],
    queryFn: api.getMetrics,
    refetchInterval: 5000
  });

  if (isLoading) {
    return (
      <div className="flex-1 flex items-center justify-center bg-[#090D16] min-h-[500px]">
        <div className="flex flex-col items-center gap-4">
          <div className="w-10 h-10 rounded-full border-2 border-t-transparent border-[#38BDF8] animate-spin"></div>
          <span className="text-[#94A3B8] text-xs font-mono uppercase tracking-wider">Aggregating Security Telemetry...</span>
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
      <div className="border-b-2 border-black pb-6">
        <div className="flex items-center gap-2.5 flex-wrap">
          <h1 className="text-2xl font-extrabold tracking-tight text-[#F8FAFC]">
            Security Telemetry & Surface Intelligence
          </h1>
          <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 text-[11px] font-mono font-bold bg-[#141A23] text-[#38BDF8] border-2 border-black shadow-[1.5px_1.5px_0px_#000]">
            <Activity className="w-3 h-3 text-[#38BDF8]" />
            Live Analytics
          </span>
          <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 text-[11px] font-mono font-bold bg-[#141A23] text-[#F59E0B] border-2 border-black shadow-[1.5px_1.5px_0px_#000]">
            Avg Runtime: {metrics.avg_runtime}s
          </span>
        </div>
        <p className="text-xs text-[#94A3B8] mt-1 font-sans">Telemetry overview of evaluated assets, severity breakdown, and <span className="font-editorial italic text-[#E2F952]">reconnaissance performance</span>.</p>
      </div>

      {/* Common Global Telemetry Strip */}
      <SecurityMetricsStrip variant="full" />

      {/* Grid: Charts Row 1 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Chart 1: Findings by Severity */}
        <div className="bg-[#141A23] border-2 border-black shadow-[4px_4px_0px_#000] p-6">
          <div className="flex justify-between items-center mb-5 pb-3 border-b-2 border-black">
            <div>
              <h3 className="text-sm font-bold text-[#F8FAFC]">Vulnerability Distribution by Severity</h3>
              <p className="text-[11px] text-[#94A3B8] mt-0.5 font-editorial italic">Exploitability risk spectrum across all completed scans</p>
            </div>
            <span className="text-[10px] text-white bg-[#EF4444] border border-black shadow-[1px_1px_0px_#000] px-2 py-0.5 font-mono font-bold uppercase">Risk Spectrum</span>
          </div>
          <div className="h-[250px] w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={metrics.findings_by_severity} margin={{ top: 10, right: 10, left: -25, bottom: 0 }}>
                <XAxis dataKey="severity" stroke="#94A3B8" fontSize={11} tickLine={false} />
                <YAxis stroke="#94A3B8" fontSize={11} tickLine={false} allowDecimals={false} />
                <Tooltip
                  contentStyle={{ backgroundColor: "#0E1217", border: "2px solid #000000", boxShadow: "3px 3px 0px #000000", borderRadius: "0px", fontSize: "12px" }}
                  labelStyle={{ color: "#F8FAFC", fontWeight: "bold" }}
                />
                <Bar dataKey="count" fill="#38BDF8" radius={[0, 0, 0, 0]}>
                  {metrics.findings_by_severity.map((entry, index) => {
                    const color = entry.severity === "Critical" ? "#DC2626" :
                                  entry.severity === "High" ? "#EF4444" :
                                  entry.severity === "Medium" ? "#F59E0B" :
                                  entry.severity === "Low" ? "#EAB308" : "#38BDF8";
                    return <Cell key={`cell-${index}`} fill={color} stroke="#000000" strokeWidth={1.5} />;
                  })}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Chart 2: Mission Runtime Trend */}
        <div className="bg-[#141A23] border-2 border-black shadow-[4px_4px_0px_#000] p-6">
          <div className="flex justify-between items-center mb-5 pb-3 border-b-2 border-black">
            <div>
              <h3 className="text-sm font-bold text-[#F8FAFC]">Reconnaissance Latency Trend</h3>
              <p className="text-[11px] text-[#94A3B8] mt-0.5 font-editorial italic">End-to-end mission runtime duration across historical runs</p>
            </div>
            <span className="text-[10px] text-black bg-[#E2F952] border border-black shadow-[1px_1px_0px_#000] px-2 py-0.5 font-mono font-bold uppercase">Latency (s)</span>
          </div>
          <div className="h-[250px] w-full">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={metrics.mission_runtime_trend} margin={{ top: 10, right: 10, left: -25, bottom: 0 }}>
                <XAxis dataKey="mission_id" stroke="#94A3B8" fontSize={11} tickLine={false} />
                <YAxis stroke="#94A3B8" fontSize={11} tickLine={false} unit="s" />
                <Tooltip
                  contentStyle={{ backgroundColor: "#0E1217", border: "2px solid #000000", boxShadow: "3px 3px 0px #000000", borderRadius: "0px", fontSize: "12px" }}
                  labelStyle={{ color: "#F8FAFC", fontWeight: "bold" }}
                />
                <Line type="monotone" dataKey="runtime" stroke="#E2F952" strokeWidth={2.5} activeDot={{ r: 5 }} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Grid: Charts Row 2 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Chart 3: Attack Surface Distribution */}
        <div className="bg-[#141A23] border-2 border-black shadow-[4px_4px_0px_#000] p-6">
          <div className="flex justify-between items-center mb-5 pb-3 border-b-2 border-black">
            <div>
              <h3 className="text-sm font-bold text-[#F8FAFC]">Classified Surface Distribution</h3>
              <p className="text-[11px] text-[#94A3B8] mt-0.5 font-editorial italic">Application components evaluated by feature classification workers</p>
            </div>
            <span className="text-[10px] text-white bg-[#8B5CF6] border border-black shadow-[1px_1px_0px_#000] px-2 py-0.5 font-mono font-bold uppercase">Component Share</span>
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
                  innerRadius={55}
                  outerRadius={75}
                  paddingAngle={4}
                  dataKey="count"
                  nameKey="name"
                >
                  {(metrics.feature_distribution || []).map((_entry: any, index: number) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} stroke="#000000" strokeWidth={1.5} />
                  ))}
                </Pie>
                <Tooltip
                  contentStyle={{ backgroundColor: "#0E1217", border: "2px solid #000000", boxShadow: "3px 3px 0px #000000", borderRadius: "0px", fontSize: "12px" }}
                  itemStyle={{ color: "#F8FAFC" }}
                />
                <Legend verticalAlign="bottom" height={36} iconType="square" wrapperStyle={{ fontSize: 10, color: "#94A3B8" }} />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Telemetry Operational Card */}
        <div className="bg-[#141A23] border-2 border-black shadow-[4px_4px_0px_#000] p-6 flex flex-col justify-between">
          <div>
            <div className="flex justify-between items-center mb-4 pb-3 border-b-2 border-black">
              <div>
                <h3 className="text-sm font-bold text-[#F8FAFC]">Autonomous Pipeline Architecture</h3>
                <p className="text-[11px] text-[#94A3B8] mt-0.5 font-editorial italic">Distributed multi-worker execution pipeline overview</p>
              </div>
              <span className="px-2.5 py-0.5 bg-[#10B981] text-black border border-black shadow-[1px_1px_0px_#000] text-[10px] font-mono font-bold">
                Healthy
              </span>
            </div>

            <div className="space-y-3 mt-4">
              <div className="flex items-center justify-between p-3.5 bg-[#0E1217] border-2 border-black shadow-[2px_2px_0px_#000]">
                <div className="flex items-center gap-2.5">
                  <Compass className="w-4 h-4 text-[#38BDF8]" />
                  <span className="text-xs font-bold text-[#F8FAFC]">Reconnaissance Worker</span>
                </div>
                <span className="text-[10px] text-[#94A3B8] font-mono">DOM & Route Parsing</span>
              </div>

              <div className="flex items-center justify-between p-3.5 bg-[#0E1217] border-2 border-black shadow-[2px_2px_0px_#000]">
                <div className="flex items-center gap-2.5">
                  <Layers className="w-4 h-4 text-[#C084FC]" />
                  <span className="text-xs font-bold text-[#F8FAFC]">Feature Classifier</span>
                </div>
                <span className="text-[10px] text-[#94A3B8] font-mono">Structural Component Tagging</span>
              </div>

              <div className="flex items-center justify-between p-3.5 bg-[#0E1217] border-2 border-black shadow-[2px_2px_0px_#000]">
                <div className="flex items-center gap-2.5">
                  <ShieldCheck className="w-4 h-4 text-[#10B981]" />
                  <span className="text-xs font-bold text-[#F8FAFC]">Security Reasoning Agent</span>
                </div>
                <span className="text-[10px] text-[#94A3B8] font-mono">Vulnerability Discovery</span>
              </div>
            </div>
          </div>

          <div className="border-t-2 border-black mt-5 pt-3 flex justify-between items-center text-[11px] text-[#94A3B8]">
            <span className="font-editorial italic">Automated SQLite persistence</span>
            <span className="font-mono text-[10px] font-bold border-b border-black">Phase 8 Active Mode</span>
          </div>
        </div>
      </div>
    </div>
  );
}
