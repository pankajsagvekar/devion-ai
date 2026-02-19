import { useEffect, useState } from "react";
import { useSearchParams } from "react-router-dom";
import { DashboardProvider } from "@/context/DashboardContext";
import InputSection from "@/components/InputSection";
import RunSummary from "@/components/RunSummary";
import ScoreBreakdown from "@/components/ScoreBreakdown";
import FixesTable from "@/components/FixesTable";
import CITimeline from "@/components/CITimeline";
import Header from "@/components/Header";
import BackgroundEffects from "@/components/BackgroundEffects";
import { fetchGithubUser } from "@/lib/api";

const Index = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const [userData, setUserData] = useState<any>(null);
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
        <BackgroundEffects />

        <Header
          isLoggedIn={isLoggedIn}
          userData={userData}
          handleLogin={handleLogin}
          handleLogout={handleLogout}
        />

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
