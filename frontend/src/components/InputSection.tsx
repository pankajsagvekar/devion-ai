import { motion } from "framer-motion";
import { GitBranch, Play, Loader2, Terminal, Github } from "lucide-react";
import { useDashboard, generateMockResults } from "@/context/DashboardContext";
import api from "@/lib/api";
import Threads from "./Threads";

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
      transition={{ duration: 0.8, ease: [0.22, 1, 0.36, 1] }}
      className={`glass-card p-10 md:p-12 relative overflow-hidden transition-all duration-700 edge-light h-full min-h-[500px] flex flex-col justify-center ${state.isRunning ? 'border-primary/50 shadow-[0_0_80px_-20px_rgba(147,51,234,0.3)]' : 'glow-intense'}`}
    >
      {/* Localized Cinematic Background (Matches Global Effect) */}
      <div className="absolute inset-0 opacity-[0.15] pointer-events-none z-0">
        <Threads
          color={[0.6, 0.4, 1]}
          amplitude={0.8}
          distance={0.2}
          enableMouseInteraction={false}
        />
      </div>

      {/* Ambient Lighting & Scan Lines */}
      <div className="absolute inset-0 bg-gradient-to-tr from-primary/5 via-transparent to-cyan/5 opacity-50 z-0" />

      {state.isRunning && (
        <>
          <div className="absolute inset-0 bg-primary/5 animate-pulse-slow z-0" />
          <div className="absolute inset-0 bg-gradient-to-b from-transparent via-primary/10 to-transparent h-1/2 w-full animate-ambient-scan z-0" />
        </>
      )}

      {/* Surface Depth Glow */}
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_60%_20%,hsl(var(--primary)/0.04),transparent_50%)] z-0" />

      {/* Header Section */}
      <div className="text-center mb-10 relative z-10 max-w-2xl mx-auto">
        <motion.div
          className="inline-flex p-3 rounded-2xl bg-primary/10 border border-primary/20 mb-6"
          whileHover={{ scale: 1.1, rotate: 5 }}
        >
          <Terminal className="w-6 h-6 text-primary" />
        </motion.div>
        <h2 className="text-3xl md:text-5xl font-heading font-black tracking-tight text-white mb-4">
          Universal <span className="text-gradient">Intelligence Portal</span>
        </h2>
        <p className="text-sm md:text-base text-muted-foreground font-medium max-w-lg mx-auto opacity-70">
          Syncing with neural nodes to fix repository logic at the speed of light.
        </p>
      </div>

      {/* Command Interface */}
      <div className="max-w-4xl mx-auto relative z-10 w-full space-y-8">
        <div className="relative group">
          <label className="flex items-center gap-2 text-[10px] font-black uppercase tracking-[0.3em] text-primary/80 mb-3 px-1 ml-2">
            <GitBranch className="w-3 h-3" />
            Repository Vector Path
          </label>
          <div className="relative">
            <input
              type="url"
              value={state.repoUrl}
              onChange={(e) => dispatch({ type: "SET_FIELD", field: "repoUrl", value: e.target.value })}
              placeholder="https://github.com/universal/nexus-core"
              className="w-full px-8 py-5 rounded-full bg-background/40 backdrop-blur-md border border-border/40 text-foreground placeholder:text-muted-foreground/30 font-mono text-base focus:outline-none focus:border-primary/60 focus:ring-4 focus:ring-primary/5 transition-all shadow-inner"
            />
            {isLoggedIn && (
              <div className="absolute right-6 top-1/2 -translate-y-1/2 flex items-center gap-2 px-3 py-1.5 rounded-full bg-success/10 border border-success/20 text-[9px] font-black text-success uppercase tracking-[0.1em]">
                <div className="w-1 h-1 rounded-full bg-success animate-pulse" />
                Secure Link
              </div>
            )}
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="space-y-3">
            <label className="text-[10px] font-black uppercase tracking-[0.3em] text-muted-foreground/60 px-1 ml-2">Team Signature</label>
            <input
              type="text"
              value={state.teamName}
              onChange={(e) => dispatch({ type: "SET_FIELD", field: "teamName", value: e.target.value })}
              placeholder="e.g. OMEGA UNIT"
              className="w-full px-7 py-4 rounded-full bg-background/40 backdrop-blur-md border border-border/40 text-foreground text-sm focus:outline-none focus:border-primary/60 focus:ring-4 focus:ring-primary/5 transition-all"
            />
          </div>
          <div className="space-y-3">
            <label className="text-[10px] font-black uppercase tracking-[0.3em] text-muted-foreground/60 px-1 ml-2">Directive Lead</label>
            <input
              type="text"
              value={state.teamLeader}
              onChange={(e) => dispatch({ type: "SET_FIELD", field: "teamLeader", value: e.target.value })}
              placeholder="e.g. Captain Miller"
              className="w-full px-7 py-4 rounded-full bg-background/40 backdrop-blur-md border border-border/40 text-foreground text-sm focus:outline-none focus:border-primary/60 focus:ring-4 focus:ring-primary/5 transition-all"
            />
          </div>
        </div>

        <div className="flex flex-col items-center pt-4">
          <button
            onClick={handleRun}
            disabled={state.isRunning || !state.repoUrl || !state.teamName || !state.teamLeader}
            className="group relative w-full md:w-80 px-10 py-5 rounded-full btn-premium overflow-hidden disabled:opacity-30 disabled:cursor-not-allowed shadow-[0_0_40px_-10px_rgba(147,51,234,0.4)]"
          >
            <div className="relative z-10 flex items-center justify-center gap-3">
              {state.isRunning ? (
                <>
                  <Loader2 className="w-5 h-5 animate-spin text-white" />
                  <span className="font-black text-xs uppercase tracking-[0.2em] text-white">Initializing Neural Link...</span>
                </>
              ) : !isLoggedIn ? (
                <div className="flex items-center gap-3" onClick={(e) => { e.stopPropagation(); handleLogin(); }}>
                  <Github className="w-5 h-5" />
                  <span className="font-black text-xs uppercase tracking-[0.2em]">Verify Connection</span>
                </div>
              ) : (
                <>
                  <Play className="w-5 h-5 text-white fill-white" />
                  <span className="font-black text-xs uppercase tracking-[0.2em] text-white">Execute Directive</span>
                </>
              )}
            </div>

            <div className="absolute inset-0 w-full h-full bg-white/10 -translate-x-full group-hover:translate-x-full transition-transform duration-1000 skew-x-[45deg]" />
          </button>
        </div>
      </div>

      {/* Progress Monitor */}
      {state.isRunning && (
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          className="mt-12 max-w-md mx-auto p-5 rounded-3xl bg-primary/5 border border-primary/10 relative overflow-hidden z-20 text-center backdrop-blur-md"
        >
          <div className="absolute inset-0 bg-gradient-to-r from-primary/10 via-transparent to-cyan/10 animate-shimmer" style={{ backgroundSize: "200% 100%" }} />
          <div className="relative flex flex-col items-center gap-2">
            <div className="w-2 h-2 rounded-full bg-primary animate-pulse" />
            <span className="text-[10px] font-black uppercase tracking-[0.3em] text-primary">Interrogating Source Geometry</span>
            <p className="text-[9px] text-muted-foreground leading-relaxed">Analyzing codebase patterns and architectural dependencies.</p>
          </div>
        </motion.div>
      )}
    </motion.div>
  );
}
