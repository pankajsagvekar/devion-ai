import AppliedFixesList from "@/components/AppliedFixesList";
import BackgroundEffects from "@/components/BackgroundEffects";
import CITimeline from "@/components/CITimeline";
import FixesTable from "@/components/FixesTable";
import Header from "@/components/Header";
import InputSection from "@/components/InputSection";
import RunSummary from "@/components/RunSummary";
import ScoreBreakdown from "@/components/ScoreBreakdown";
import ResultsJsonView from "@/components/ResultsJsonView";
import { DashboardProvider, useDashboard } from "@/context/DashboardContext";
import { fetchGithubUser } from "@/lib/api";
import { AnimatePresence, motion } from "framer-motion";
import { useEffect, useState } from "react";
import { useSearchParams } from "react-router-dom";

const IndexContent = ({ isLoggedIn, userData, handleLogin, handleLogout }: any) => {
  const { state } = useDashboard();
  
  // Optimization: Enable lowPower mode during agent execution or if manually enabled
  const lowPower = state.isRunning || state.performanceMode;

  return (
    <div className="min-h-screen bg-background bg-mesh bg-grid relative overflow-hidden selection:bg-primary/30">
      <BackgroundEffects lowPower={lowPower} />

      <Header
        isLoggedIn={isLoggedIn}
        userData={userData}
        handleLogin={handleLogin}
        handleLogout={handleLogout}
      />


      {/* Main Content */}
      <main className="container pb-20 space-y-12 relative z-10 max-w-[1400px]">
        <section className="relative">
          <InputSection lowPower={lowPower} />
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

              <AppliedFixesList />
              <ResultsJsonView />
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
    const apiUrl = import.meta.env.VITE_API_URL || "http://localhost:8000";
    window.location.href = `${apiUrl}/auth/login`;
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
