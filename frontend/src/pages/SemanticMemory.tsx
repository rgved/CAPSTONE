import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { api } from "../services/api";
import SecurityMetricsStrip from "../components/common/SecurityMetricsStrip";
import {
  Database,
  Search,
  BrainCircuit,
  Sparkles,
  ShieldAlert,
  Layers,
  Compass,
  Cpu,
  RefreshCw,
  Zap
} from "lucide-react";

export default function SemanticMemory() {
  const [searchQuery, setSearchQuery] = useState("");
  const [collection, setCollection] = useState("findings");
  const [searchResults, setSearchResults] = useState<any[] | null>(null);
  const [searching, setSearching] = useState(false);

  const { data: memorySummary, isLoading, refetch } = useQuery({
    queryKey: ["memory-summary"],
    queryFn: api.getMemorySummary,
    refetchInterval: 10000,
  });

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!searchQuery.trim()) return;
    try {
      setSearching(true);
      const res = await api.searchMemory(searchQuery, collection);
      setSearchResults(res.results || []);
    } catch (err) {
      console.error("Semantic search failed", err);
    } finally {
      setSearching(false);
    }
  };

  const getSeverityBadgeClass = (severity: string) => {
    switch (severity?.toLowerCase()) {
      case "critical":
        return "bg-[#DC2626]/10 text-[#DC2626] border-[#DC2626]/30";
      case "high":
        return "bg-[#EF4444]/10 text-[#EF4444] border-[#EF4444]/30";
      case "medium":
        return "bg-[#F59E0B]/10 text-[#F59E0B] border-[#F59E0B]/30";
      case "low":
        return "bg-[#EAB308]/10 text-[#EAB308] border-[#EAB308]/30";
      default:
        return "bg-[#3B82F6]/10 text-[#3B82F6] border-[#3B82F6]/30";
    }
  };

  return (
    <div className="space-y-8 animate-fadeIn">
      {/* Top Banner / Title */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-2xl font-bold text-[#F8FAFC]">ChromaDB Semantic Memory</h1>
            <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold uppercase bg-[#3B82F6]/10 border border-[#3B82F6]/30 text-[#38BDF8] flex items-center gap-1">
              <Sparkles className="w-3 h-3" /> Vector RAG Store
            </span>
          </div>
          <p className="text-sm text-[#94A3B8] mt-1">
            Persistent embedding store that indexes prior observations to improve subsequent reconnaissance and vulnerability reasoning.
          </p>
        </div>
        <button
          onClick={() => refetch()}
          className="flex items-center gap-2 px-3.5 py-2 bg-[#0F172A] hover:bg-[#1E293B] border border-[#1E293B] rounded-xl text-xs font-semibold text-[#94A3B8] hover:text-[#F8FAFC] transition-all self-start md:self-auto"
        >
          <RefreshCw className="w-3.5 h-3.5" /> Refresh Store
        </button>
      </div>

      {/* Unified Platform Metrics Strip */}
      <SecurityMetricsStrip variant="full" />

      {/* Vector Collection Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-[#0F172A] border border-[#1E293B] p-6 rounded-xl relative overflow-hidden group hover:border-[#EF4444]/50 transition-all">
          <div className="flex justify-between items-start">
            <div>
              <p className="text-xs font-semibold text-[#94A3B8] uppercase tracking-wider">Findings Collection</p>
              <h3 className="text-3xl font-bold text-[#F8FAFC] mt-2">
                {isLoading ? "..." : memorySummary?.counts?.findings_indexed ?? 0}
              </h3>
            </div>
            <div className="p-3 bg-[#EF4444]/10 rounded-lg text-[#EF4444]">
              <ShieldAlert className="w-6 h-6" />
            </div>
          </div>
          <div className="mt-4 flex items-center gap-1.5 text-[11px] text-[#94A3B8]">
            <span>Indexed vulnerability reasoning & evidence vectors</span>
          </div>
        </div>

        <div className="bg-[#0F172A] border border-[#1E293B] p-6 rounded-xl relative overflow-hidden group hover:border-[#8B5CF6]/50 transition-all">
          <div className="flex justify-between items-start">
            <div>
              <p className="text-xs font-semibold text-[#94A3B8] uppercase tracking-wider">Features Collection</p>
              <h3 className="text-3xl font-bold text-[#F8FAFC] mt-2">
                {isLoading ? "..." : memorySummary?.counts?.features_indexed ?? 0}
              </h3>
            </div>
            <div className="p-3 bg-[#8B5CF6]/10 rounded-lg text-[#8B5CF6]">
              <Layers className="w-6 h-6" />
            </div>
          </div>
          <div className="mt-4 flex items-center gap-1.5 text-[11px] text-[#94A3B8]">
            <span>Semantic capability fingerprints & route patterns</span>
          </div>
        </div>

        <div className="bg-[#0F172A] border border-[#1E293B] p-6 rounded-xl relative overflow-hidden group hover:border-[#38BDF8]/50 transition-all">
          <div className="flex justify-between items-start">
            <div>
              <p className="text-xs font-semibold text-[#94A3B8] uppercase tracking-wider">Routes Collection</p>
              <h3 className="text-3xl font-bold text-[#F8FAFC] mt-2">
                {isLoading ? "..." : memorySummary?.counts?.routes_indexed ?? 0}
              </h3>
            </div>
            <div className="p-3 bg-[#38BDF8]/10 rounded-lg text-[#38BDF8]">
              <Compass className="w-6 h-6" />
            </div>
          </div>
          <div className="mt-4 flex items-center gap-1.5 text-[11px] text-[#94A3B8]">
            <span>Discovered URL endpoints & structural DOM summaries</span>
          </div>
        </div>
      </div>

      {/* How Future Missions Use Semantic Memory */}
      <div className="bg-[#0F172A] border border-[#1E293B] rounded-2xl p-6 lg:p-8 space-y-6">
        <div className="flex items-center gap-3">
          <div className="p-2.5 bg-[#3B82F6]/10 rounded-xl text-[#3B82F6]">
            <BrainCircuit className="w-5 h-5" />
          </div>
          <div>
            <h2 className="text-base font-bold text-[#F8FAFC]">How Future Missions Use Semantic Memory</h2>
            <p className="text-xs text-[#94A3B8]">Cross-mission memory transfers knowledge so each scan is smarter than the last.</p>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="p-4 rounded-xl bg-[#090D16] border border-[#1E293B] space-y-2">
            <div className="flex items-center gap-2 text-xs font-bold text-[#38BDF8]">
              <Compass className="w-4 h-4" /> 1. Capability Matching
            </div>
            <p className="text-xs text-[#94A3B8] leading-relaxed">
              When encountering an ambiguous endpoint, the feature extractor queries ChromaDB vectors to find which capabilities similar pages mapped to in previous targets.
            </p>
          </div>

          <div className="p-4 rounded-xl bg-[#090D16] border border-[#1E293B] space-y-2">
            <div className="flex items-center gap-2 text-xs font-bold text-[#A855F7]">
              <Cpu className="w-4 h-4" /> 2. Few-Shot In-Context Injection
            </div>
            <p className="text-xs text-[#94A3B8] leading-relaxed">
              During <code className="text-[#F8FAFC] bg-[#1E293B] px-1 py-0.5 rounded">RUN_ANALYSIS</code>, the orchestrator retrieves the 3 closest past findings and supplies them to Groq LLM as historical evidence context.
            </p>
          </div>

          <div className="p-4 rounded-xl bg-[#090D16] border border-[#1E293B] space-y-2">
            <div className="flex items-center gap-2 text-xs font-bold text-[#22C55E]">
              <Zap className="w-4 h-4" /> 3. High-Yield Crawl Elevation
            </div>
            <p className="text-xs text-[#94A3B8] leading-relaxed">
              The risk scorer boosts parameters and routes that share vector patterns with previously confirmed vulnerabilities, guiding the crawler toward fertile attack surfaces.
            </p>
          </div>
        </div>
      </div>

      {/* Interactive Semantic Search Bar */}
      <div className="bg-[#0F172A] border border-[#1E293B] rounded-2xl p-6 lg:p-8 space-y-6">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <h2 className="text-base font-bold text-[#F8FAFC] flex items-center gap-2">
              <Search className="w-4 h-4 text-[#38BDF8]" /> Query Vector Index
            </h2>
            <p className="text-xs text-[#94A3B8]">Test semantic similarity search across vector collections in real-time.</p>
          </div>

          {/* Collection Filter */}
          <div className="flex bg-[#090D16] p-1 rounded-lg border border-[#1E293B] self-start sm:self-auto">
            {["findings", "features", "routes"].map((col) => (
              <button
                key={col}
                type="button"
                onClick={() => {
                  setCollection(col);
                  setSearchResults(null);
                }}
                className={`px-3 py-1.5 text-xs font-semibold rounded-md capitalize transition-all ${
                  collection === col
                    ? "bg-[#0284C7] text-white shadow"
                    : "text-[#94A3B8] hover:text-[#F8FAFC]"
                }`}
              >
                {col}
              </button>
            ))}
          </div>
        </div>

        <form onSubmit={handleSearch} className="flex gap-3">
          <div className="relative flex-1">
            <Search className="w-4 h-4 text-[#64748B] absolute left-4 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder={`Search ${collection} by meaning (e.g. "missing csrf token", "admin authentication", "file extension validation")...`}
              className="w-full bg-[#090D16] border border-[#1E293B] rounded-xl pl-11 pr-4 py-3 text-sm text-[#F8FAFC] placeholder-[#64748B] focus:border-[#38BDF8] focus:ring-2 focus:ring-[#38BDF8]/20 outline-none transition-all"
            />
          </div>
          <button
            type="submit"
            disabled={searching}
            className="px-6 py-3 bg-[#0284C7] hover:bg-[#0369A1] disabled:opacity-50 text-white font-bold text-xs rounded-xl shadow-lg shadow-sky-500/20 transition-all flex items-center gap-2 shrink-0"
          >
            {searching ? (
              <RefreshCw className="w-4 h-4 animate-spin" />
            ) : (
              <Search className="w-4 h-4" />
            )}
            Vector Search
          </button>
        </form>

        {/* Live Search Results */}
        {searchResults !== null && (
          <div className="space-y-3 pt-4 border-t border-[#1E293B]">
            <div className="flex justify-between items-center">
              <span className="text-xs font-semibold text-[#94A3B8]">
                Matched {searchResults.length} {searchResults.length === 1 ? "document" : "documents"} for "{searchQuery}"
              </span>
              <button
                type="button"
                onClick={() => setSearchResults(null)}
                className="text-xs text-[#64748B] hover:text-[#94A3B8]"
              >
                Clear Results
              </button>
            </div>

            {searchResults.length === 0 ? (
              <div className="p-8 text-center text-xs text-[#94A3B8] bg-[#090D16] rounded-xl border border-[#1E293B]">
                No vector matches found with current query threshold.
              </div>
            ) : (
              <div className="grid grid-cols-1 gap-3">
                {searchResults.map((res, i) => (
                  <div
                    key={i}
                    className="p-4 rounded-xl bg-[#090D16] border border-[#1E293B] hover:border-[#38BDF8]/40 transition-all space-y-2"
                  >
                    <div className="flex items-center justify-between gap-2 flex-wrap">
                      <div className="flex items-center gap-2">
                        <span className="font-mono text-xs font-bold text-[#F8FAFC] bg-[#1E293B] px-2 py-0.5 rounded">
                          {res.document_id}
                        </span>
                        {res.metadata?.severity && (
                          <span
                            className={`text-[10px] font-bold uppercase px-2 py-0.5 rounded border ${getSeverityBadgeClass(
                              res.metadata.severity
                            )}`}
                          >
                            {res.metadata.severity}
                          </span>
                        )}
                        {res.metadata?.feature && (
                          <span className="text-[10px] text-[#94A3B8] bg-[#0F172A] px-2 py-0.5 rounded border border-[#1E293B]">
                            {res.metadata.feature}
                          </span>
                        )}
                      </div>
                      <span className="text-xs font-mono font-bold text-[#22C55E] bg-[#22C55E]/10 px-2 py-0.5 rounded">
                        {res.similarity_score}% Match
                      </span>
                    </div>
                    <p className="text-xs font-mono text-[#CBD5E1] whitespace-pre-wrap leading-relaxed line-clamp-3">
                      {res.document}
                    </p>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>

      {/* Stored Historical Findings Preview */}
      <div className="bg-[#0F172A] border border-[#1E293B] rounded-2xl p-6 lg:p-8 space-y-6">
        <div>
          <h2 className="text-base font-bold text-[#F8FAFC] flex items-center gap-2">
            <Database className="w-4 h-4 text-[#38BDF8]" /> Stored Semantic Knowledge Base
          </h2>
          <p className="text-xs text-[#94A3B8]">Observations currently embedded and available to subsequent analysis workflows.</p>
        </div>

        {memorySummary?.recent_stored_findings?.length === 0 ? (
          <div className="p-8 text-center text-xs text-[#94A3B8] bg-[#090D16] rounded-xl border border-[#1E293B]">
            No findings indexed yet. Run your first mission to populate semantic memory!
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead>
                <tr className="border-b border-[#1E293B] text-[#94A3B8] uppercase tracking-wider font-semibold">
                  <th className="pb-3">ID</th>
                  <th className="pb-3">Title</th>
                  <th className="pb-3">Category</th>
                  <th className="pb-3">Feature Context</th>
                  <th className="pb-3">Severity</th>
                  <th className="pb-3">Embedded Excerpt</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[#1E293B]">
                {memorySummary?.recent_stored_findings?.map((f: any, idx: number) => (
                  <tr key={idx} className="hover:bg-[#090D16]/50 transition-colors">
                    <td className="py-3 font-mono text-[#38BDF8] font-bold">{f.id}</td>
                    <td className="py-3 font-semibold text-[#F8FAFC] max-w-[200px] truncate" title={f.title}>
                      {f.title}
                    </td>
                    <td className="py-3 text-[#94A3B8]">{f.type}</td>
                    <td className="py-3 text-[#94A3B8]">{f.feature}</td>
                    <td className="py-3">
                      <span className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase border ${getSeverityBadgeClass(f.severity)}`}>
                        {f.severity}
                      </span>
                    </td>
                    <td className="py-3 text-[#94A3B8] max-w-[320px] truncate font-mono text-[11px]" title={f.snippet}>
                      {f.snippet}
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
