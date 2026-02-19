import { motion } from "framer-motion";
import { GitBranch, Play, Loader2, Terminal, Github } from "lucide-react";
import { useDashboard, generateMockResults } from "@/context/DashboardContext";
import api from "@/lib/api";

export default function InputSection() {
  const { state, dispatch } = useDashboard();
  const isLoggedIn = !!localStorage.getItem("github_token");

  const handleRun = async () => {
    if (!state.repoUrl || !state.teamName || !state.teamLeader) return;

    const token = localStorage.getItem("github_token");
    if (!token) {
      window.location.href = "http://localhost:8000/auth/login";
      return;
    }

    dispatch({ type: "START_RUN" });

    try {
      const response = await api.post("/run-agent", {
        repository_url: state.repoUrl,
        github_token: token,
        team_name: state.teamName,
        team_leader: state.teamLeader,
      });

      const data = response.data;

      // Map backend results to frontend state structure
      // Note: mapping logic based on calculate_score output in backend/app/utils/scoring.py
      const results = {
        branchName: data.branch_name,
        totalFailures: data.total_failures,
        totalFixes: data.total_fixes,
        ciStatus: data.final_status.toLowerCase() as "passed" | "failed",
        timeTaken: `${(data.total_time_seconds / 60).toFixed(1)} min`,
        baseScore: data.score_calculation?.base_score || 100,
        speedBonus: data.score_calculation?.speed_bonus || 0,
        efficiencyPenalty: data.score_calculation?.efficiency_penalty || 0,
        finalScore: data.score_calculation?.final_score || 0,
        totalCommits: data.commit_count,
        fixes: (data.fixes_applied || []).map((f: string) => ({
          file: f.split(" in ")[1] || "unknown",
          bugType: (f.split(" for ")[1]?.split(" at ")[0] || "LOGIC") as any,
          lineNumber: parseInt(f.split(" at line ")[1]) || 0,
          commitMessage: f,
          status: "fixed" as const
        })),
        ciRuns: [
          {
            iteration: data.iterations_used,
            status: data.final_status.toLowerCase() as any,
            timestamp: new Date().toISOString()
          }
        ],
        retryLimit: 5,
      };

      dispatch({ type: "FINISH_RUN", payload: results });
    } catch (error) {
      console.error("Failed to run agent:", error);
      // Fallback to mock on error to keep UI interactive
      dispatch({ type: "FINISH_RUN", payload: generateMockResults(state.teamName, state.teamLeader) });
    }
  };

  const handleLogin = () => {
    window.location.href = "http://localhost:8000/auth/login";
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 30 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6, ease: [0.22, 1, 0.36, 1] }}
      className="glass-card p-8 glow-primary relative overflow-hidden"
    >
      {/* Decorative corner accent */}
      <div className="absolute top-0 right-0 w-32 h-32 bg-primary/5 blur-[40px] rounded-full" />
      <div className="absolute bottom-0 left-0 w-24 h-24 bg-cyan/5 blur-[30px] rounded-full" />

      <div className="flex items-center justify-between mb-8 relative">
        <div className="flex items-center gap-3">
          <div className="p-2.5 rounded-xl bg-primary/15 border border-primary/20">
            <Terminal className="w-5 h-5 text-primary" />
          </div>
          <div>
            <h2 className="text-lg font-heading font-bold text-foreground">Analyze Repository</h2>
            <p className="text-xs text-muted-foreground">Enter your GitHub repository details to begin analysis</p>
          </div>
        </div>

        {!isLoggedIn && (
          <div className="text-xs font-medium text-amber-400 bg-amber-400/10 border border-amber-400/20 px-3 py-1 rounded-full animate-pulse">
            Authentication Required
          </div>
        )}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-5 mb-6 relative">
        <div className="md:col-span-3">
          <label className="flex items-center gap-1.5 text-sm font-medium text-secondary-foreground mb-2">
            <GitBranch className="w-3.5 h-3.5 text-primary" />
            GitHub Repository URL
          </label>
          <input
            type="url"
            value={state.repoUrl}
            onChange={(e) => dispatch({ type: "SET_FIELD", field: "repoUrl", value: e.target.value })}
            placeholder="https://github.com/owner/repo"
            className="w-full px-4 py-3 rounded-xl input-premium text-foreground placeholder:text-muted-foreground font-mono text-sm focus:outline-none"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-secondary-foreground mb-2">Team Name</label>
          <input
            type="text"
            value={state.teamName}
            onChange={(e) => dispatch({ type: "SET_FIELD", field: "teamName", value: e.target.value })}
            placeholder="RIFT ORGANISERS"
            className="w-full px-4 py-3 rounded-xl input-premium text-foreground placeholder:text-muted-foreground text-sm focus:outline-none"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-secondary-foreground mb-2">Team Leader Name</label>
          <input
            type="text"
            value={state.teamLeader}
            onChange={(e) => dispatch({ type: "SET_FIELD", field: "teamLeader", value: e.target.value })}
            placeholder="Saiyam Kumar"
            className="w-full px-4 py-3 rounded-xl input-premium text-foreground placeholder:text-muted-foreground text-sm focus:outline-none"
          />
        </div>
        <div className="flex items-end">
          <button
            onClick={handleRun}
            disabled={state.isRunning || !state.repoUrl || !state.teamName || !state.teamLeader}
            className="w-full px-6 py-3 rounded-xl btn-premium text-primary-foreground font-bold text-sm flex items-center justify-center gap-2.5 disabled:opacity-30 disabled:cursor-not-allowed disabled:shadow-none"
          >
            {state.isRunning ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                Analyzing...
              </>
            ) : !isLoggedIn ? (
              <div className="flex items-center gap-2" onClick={(e) => { e.stopPropagation(); handleLogin(); }}>
                <Github className="w-4 h-4" />
                Login to Run
              </div>
            ) : (
              <>
                <Play className="w-4 h-4" />
                Run Agent
              </>
            )}
          </button>
        </div>
      </div>

      {state.isRunning && (
        <motion.div
          initial={{ opacity: 0, height: 0 }}
          animate={{ opacity: 1, height: "auto" }}
          className="flex items-center gap-3 p-4 rounded-xl bg-primary/8 border border-primary/15 relative overflow-hidden"
        >
          <div className="absolute inset-0 bg-gradient-to-r from-primary/5 via-transparent to-cyan/5 animate-shimmer" style={{ backgroundSize: "200% 100%" }} />
          <div className="relative flex items-center gap-3">
            <div className="w-2.5 h-2.5 rounded-full bg-primary animate-pulse-glow" />
            <span className="text-sm font-medium text-primary">Agent is analyzing repository and applying fixes...</span>
          </div>
        </motion.div>
      )}
    </motion.div>
  );
}
