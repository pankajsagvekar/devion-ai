import { useEffect, useState } from "react";
import { useSearchParams, useNavigate } from "react-router-dom";
import { DashboardProvider } from "@/context/DashboardContext";
import InputSection from "@/components/InputSection";
import RunSummary from "@/components/RunSummary";
import ScoreBreakdown from "@/components/ScoreBreakdown";
import FixesTable from "@/components/FixesTable";
import CITimeline from "@/components/CITimeline";
import { User, Sparkles, LogOut, Github } from "lucide-react";
import { fetchGithubUser } from "@/lib/api";

const Index = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const [userData, setUserData] = useState<any>(null);
  const navigate = useNavigate();
  const token = searchParams.get("token");

  useEffect(() => {
    if (token) {
      localStorage.setItem("github_token", token);
      // Remove token from URL
      const newParams = new URLSearchParams(searchParams);
      newParams.delete("token");
      setSearchParams(newParams);
    }
  }, [token, searchParams, setSearchParams]);

  useEffect(() => {
    const loadUser = async () => {
      const data = await fetchGithubUser();
      if (data) setUserData(data);
    };
    if (localStorage.getItem("github_token")) {
      loadUser();
    }
  }, []);

  const handleLogout = () => {
    localStorage.removeItem("github_token");
    window.location.reload();
  };

  const handleLogin = () => {
    window.location.href = "http://localhost:8000/auth/login";
  };

  const isLoggedIn = !!localStorage.getItem("github_token");

  return (
    <DashboardProvider>
      <div className="min-h-screen bg-background bg-mesh bg-grid relative overflow-hidden">
        {/* Floating orbs */}
        <div className="fixed top-20 right-0 w-[600px] h-[600px] rounded-full bg-primary/10 blur-[130px] animate-orb-1 pointer-events-none" />
        <div className="fixed bottom-0 left-0 w-[400px] h-[400px] rounded-full bg-accent/5 blur-[100px] animate-orb-2 pointer-events-none" />
        <div className="fixed top-1/2 left-1/2 w-[300px] h-[300px] rounded-full bg-primary/3 blur-[120px] pointer-events-none" />

        {/* Header */}
        <header className="glass-strong sticky top-0 z-50 border-b border-border/30">
          <div className="container flex items-center justify-between py-4">
            <div className="flex items-center gap-4">
              <img src="/devion.png" alt="Devion-AI Logo" className="w-20 h-20 object-contain rounded-xl " />
              <div>
                <h1 className="text-2xl font-bold tracking-tight">
                  <span className="text-white/90">
                    Devion-
                  </span>
                  <span className="text-primary">
                    AI
                  </span>
                </h1>
                <p className="text-xs text-muted-foreground tracking-wide">Automated Repository Analysis & Bug Fixing</p>
              </div>
            </div>
            <div className="flex items-center gap-4">
              <div className="hidden md:flex items-center gap-2 px-3 py-1.5 rounded-full bg-primary/10 border border-primary/20">
                <Sparkles className="w-3.5 h-3.5 text-primary" />
                <span className="text-xs font-medium text-primary">AI-Powered</span>
              </div>

              {isLoggedIn ? (
                <div className="flex items-center gap-3">
                  <button
                    onClick={() => navigate("/profile")}
                    className="flex items-center gap-2 p-1.5 pr-4 rounded-xl bg-secondary/20 border border-border/50 text-sm font-medium hover:bg-secondary/30 transition-colors"
                  >
                    {userData?.avatar_url ? (
                      <img src={userData.avatar_url} alt="Profile" className="w-7 h-7 rounded-lg border border-primary/30" />
                    ) : (
                      <div className="w-7 h-7 rounded-lg bg-primary/20 flex items-center justify-center">
                        <User className="w-4 h-4 text-primary" />
                      </div>
                    )}
                    <span className="hidden sm:inline">{userData?.name || userData?.login || "Profile"}</span>
                  </button>
                  <button
                    onClick={handleLogout}
                    className="flex items-center gap-2 px-4 py-2 rounded-xl bg-destructive/10 border border-destructive/20 text-sm font-medium hover:bg-destructive/20 text-destructive transition-colors"
                  >
                    <LogOut className="w-4 h-4" />
                    <span className="hidden lg:inline">Logout</span>
                  </button>
                </div>
              ) : (
                <button
                  onClick={handleLogin}
                  className="flex items-center gap-2 px-4 py-2 rounded-xl bg-primary text-primary-foreground text-sm font-bold hover:opacity-90 transition-opacity"
                >
                  <Github className="w-4 h-4" />
                  Connect GitHub
                </button>
              )}
            </div>
          </div>
        </header>

        {/* Main Content */}
        <main className="container py-8 space-y-6 relative z-10">
          <InputSection />

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="lg:col-span-2">
              <RunSummary />
            </div>
            <div>
              <ScoreBreakdown />
            </div>
          </div>

          <FixesTable />

          <CITimeline />
        </main>


      </div>
    </DashboardProvider>
  );
};

export default Index;
