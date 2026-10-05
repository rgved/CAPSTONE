import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";

// Layout components
import Sidebar from "./components/layout/Sidebar";
import Header from "./components/layout/Header";

// Page components
import Dashboard from "./pages/Dashboard";
import NewScan from "./pages/NewScan";
import MissionDetail from "./pages/MissionDetail";
import Findings from "./pages/Findings";
import Reports from "./pages/Reports";
import Metrics from "./pages/Metrics";

// Initialize Query Client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1
    }
  }
});

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <Router>
        <div className="flex bg-[#0B1220] min-h-screen text-[#F8FAFC] font-sans antialiased overflow-hidden">
          {/* Sidebar */}
          <Sidebar />

          {/* Main workspace */}
          <div className="flex-1 flex flex-col min-h-screen overflow-hidden">
            {/* Header */}
            <Header />

            {/* Content body */}
            <main className="flex-1 overflow-y-auto p-8">
              <div className="max-w-[1400px] mx-auto">
                <Routes>
                  <Route path="/" element={<Dashboard />} />
                  <Route path="/new-scan" element={<NewScan />} />
                  <Route path="/mission/:id" element={<MissionDetail />} />
                  <Route path="/findings" element={<Findings />} />
                  <Route path="/reports" element={<Reports />} />
                  <Route path="/metrics" element={<Metrics />} />
                </Routes>
              </div>
            </main>
          </div>
        </div>
      </Router>
    </QueryClientProvider>
  );
}
