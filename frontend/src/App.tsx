import { BrowserRouter as Router, Routes, Route, Navigate, useLocation } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { AuthProvider } from "./context/AuthContext";
import AuthModal from "./components/auth/AuthModal";

// Layout components
import Sidebar from "./components/layout/Sidebar";
import Header from "./components/layout/Header";

// Page components
import LandingPage from "./pages/LandingPage";
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

function AppContent() {
  const location = useLocation();
  const isLandingPage = location.pathname === "/";

  if (isLandingPage) {
    return (
      <main className="min-h-screen bg-[#090D16]">
        <LandingPage />
      </main>
    );
  }

  return (
    <div className="flex bg-[#090D16] min-h-screen text-[#F8FAFC] font-sans antialiased overflow-hidden">
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
              <Route path="/dashboard" element={<Dashboard />} />
              <Route path="/new-scan" element={<NewScan />} />
              <Route path="/mission/:id" element={<MissionDetail />} />
              <Route path="/findings" element={<Findings />} />
              <Route path="/reports" element={<Reports />} />
              <Route path="/semantic-memory" element={<Navigate to="/findings?tab=memory" replace />} />
              <Route path="/metrics" element={<Metrics />} />
              {/* Fallback */}
              <Route path="*" element={<Navigate to="/dashboard" replace />} />
            </Routes>
          </div>
        </main>
      </div>
    </div>
  );
}

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <Router>
          <AuthModal />
          <AppContent />
        </Router>
      </AuthProvider>
    </QueryClientProvider>
  );
}
