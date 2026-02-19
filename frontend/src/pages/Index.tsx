import { useEffect, useState } from "react";
import { useSearchParams } from "react-router-dom";
import { motion, AnimatePresence } from "framer-motion";
import { DashboardProvider, useDashboard } from "@/context/DashboardContext";
import InputSection from "@/components/InputSection";
import RunSummary from "@/components/RunSummary";
import ScoreBreakdown from "@/components/ScoreBreakdown";
import FixesTable from "@/components/FixesTable";
import CITimeline from "@/components/CITimeline";
import Header from "@/components/Header";
import BackgroundEffects from "@/components/BackgroundEffects";
import { fetchGithubUser } from "@/lib/api";

const IndexContent = ({ isLoggedIn, userData, handleLogin, handleLogout }: any) => {
  const { state } = useDashboard();

  return (
    <div className="min-h-screen bg-background bg-mesh bg-grid relative overflow-hidden selection:bg-primary/30">
      <BackgroundEffects />

      <Header
        isLoggedIn={isLoggedIn}
        userData={userData}
        handleLogin={handleLogin}
        handleLogout={handleLogout}
      />

      {/* Universal Controller Header */}
      <div className="container mt-12 mb-8 relative z-10">
        <motion.div
          initial={{ opacity: 0, filter: "blur(10px)" }}
          animate={{ opacity: 1, filter: "blur(0px)" }}
          transition={{ duration: 1 }}
          className="flex flex-col md:flex-row md:items-end justify-between gap-6"
        >
          <div className="space-y-1">
            <div className="flex items-center gap-2 text-[10px] font-black uppercase tracking-[0.3em] text-primary">
              <div className="w-2 h-2 rounded-full bg-primary animate-pulse" />
              Universal System Portal V3.0
            </div>
            <h1 className="text-4xl md:text-5xl font-heading font-black text-white tracking-tighter">
              Command <span className="text-gradient">Horizon</span>
            </h1>
          </div>

          <div className="flex items-center gap-8 text-muted-foreground">
            <div className="text-right">
              <div className="text-[10px] font-bold uppercase tracking-widest mb-1 opacity-50">Global Status</div>
              <div className="text-sm font-mono text-success font-bold flex items-center gap-2 justify-end">
                <div className="w-1.5 h-1.5 rounded-full bg-success" />
                OPERATIONAL
              </div>
            </div>
            <div className="text-right border-l border-border/50 pl-8">
              <div className="text-[10px] font-bold uppercase tracking-widest mb-1 opacity-50">Node Latency</div>
              <div className="text-sm font-mono text-primary font-bold">12ms</div>
            </div>
          </div>
        </motion.div>
      </div>

      {/* Main Content */}
      <main className="container pb-20 space-y-12 relative z-10 max-w-[1400px]">
        <section className="relative">
          <InputSection />
        </section>

        <AnimatePresence>
          {state.hasResults && (
            <motion.section
              initial={{ opacity: 0, y: 40 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -40 }}
              transition={{ duration: 0.8, ease: [0.22, 1, 0.36, 1] }}
              className="space-y-8"
            >
              <div className="flex items-center gap-4">
                <div className="h-px flex-1 bg-gradient-to-r from-transparent via-border to-transparent" />
                <h3 className="text-[10px] font-black uppercase tracking-[0.4em] text-muted-foreground whitespace-nowrap">Intelligence Report</h3>
                <div className="h-px flex-1 bg-gradient-to-r from-transparent via-border to-transparent" />
              </div>

              <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
                <div className="lg:col-span-3">
                  <RunSummary />
                </div>
                <div>
                  <ScoreBreakdown />
                </div>
              </div>

              <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 items-start">
                <div className="lg:col-span-2">
                  <FixesTable />
                </div>
                <div className="h-full">
                  <CITimeline />
                </div>
              </div>
            </motion.section>
          )}
        </AnimatePresence>

        {!state.hasResults && !state.isRunning && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 0.5 }}
            transition={{ delay: 1 }}
            className="py-20 text-center border-t border-dashed border-border/30"
          >
            <p className="text-xs font-mono uppercase tracking-[0.2em] text-muted-foreground">
              System Idle — Standing by for Repository Directives
            </p>
          </motion.div>
        )}
      </main>
    </div>
  );
};

const Index = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const [userData, setUserData] = useState<any>(null);
  const token = searchParams.get("token");

  useEffect(() => {
    if (token) {
      localStorage.setItem("github_token", token);
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
      <IndexContent
        isLoggedIn={isLoggedIn}
        userData={userData}
        handleLogin={handleLogin}
        handleLogout={handleLogout}
      />
    </DashboardProvider>
  );
};

export default Index;
