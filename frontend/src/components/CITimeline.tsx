import { motion } from "framer-motion";
import { Activity, CheckCircle2, XCircle, Radio } from "lucide-react";
import { useDashboard } from "@/context/DashboardContext";

export default function CITimeline() {
  const { state } = useDashboard();
  if (!state.hasResults) return null;

  const usedRuns = state.ciRuns.length;

  return (
    <motion.div
      initial={{ opacity: 0, y: 30 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.35, duration: 0.6, ease: [0.22, 1, 0.36, 1] }}
      className="glass-card p-8"
    >
      <div className="flex items-center justify-between mb-8">
        <div className="flex items-center gap-3">
          <div className="p-2 rounded-xl bg-cyan/10 border border-cyan/20">
            <Activity className="w-5 h-5 text-cyan" />
          </div>
          <div>
            <h2 className="text-lg font-heading font-bold text-foreground">CI/CD Timeline</h2>
            <p className="text-xs text-muted-foreground">Build iterations and status history</p>
          </div>
        </div>
        <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-secondary border border-border">
          <Radio className="w-3 h-3 text-accent" />
          <span className="text-sm font-mono font-bold text-foreground">{usedRuns}</span>
          <span className="text-xs text-muted-foreground">/ {state.retryLimit} runs</span>
        </div>
      </div>

      <div className="relative pl-4">
        {/* Gradient timeline line */}
        <div className="absolute left-[15px] top-4 bottom-4 w-0.5 timeline-line rounded-full" />

        <div className="space-y-4">
          {state.ciRuns.map((run, i) => {
            const isPassed = run.status === "passed";
            const time = new Date(run.timestamp).toLocaleTimeString();
            const isLast = i === state.ciRuns.length - 1;
            return (
              <motion.div
                key={i}
                initial={{ opacity: 0, x: -30 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.5 + i * 0.15, ease: [0.22, 1, 0.36, 1] }}
                className="flex items-start gap-5"
              >
                <div className={`relative z-10 w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 border ${
                  isPassed
                    ? "bg-success/15 border-success/30"
                    : "bg-destructive/15 border-destructive/30"
                } ${isLast && isPassed ? "glow-success" : ""}`}>
                  {isPassed ? (
                    <CheckCircle2 className="w-4 h-4 text-success" />
                  ) : (
                    <XCircle className="w-4 h-4 text-destructive" />
                  )}
                </div>
                <div className={`flex-1 p-4 rounded-xl border transition-all ${
                  isPassed
                    ? "bg-success/5 border-success/15 hover:border-success/30"
                    : "bg-destructive/5 border-destructive/15 hover:border-destructive/30"
                }`}>
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-heading font-semibold text-foreground">
                      Iteration #{run.iteration}
                    </span>
                    <span className={`px-2.5 py-1 rounded-md text-[10px] font-bold uppercase tracking-widest border ${
                      isPassed
                        ? "bg-success/15 text-success border-success/20"
                        : "bg-destructive/15 text-destructive border-destructive/20"
                    }`}>
                      {run.status}
                    </span>
                  </div>
                  <span className="text-xs text-muted-foreground mt-1.5 block font-mono">{time}</span>
                </div>
              </motion.div>
            );
          })}
        </div>

        {usedRuns < state.retryLimit && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 1.2 }}
            className="mt-6 ml-12 flex items-center gap-2 text-xs text-muted-foreground"
          >
            <div className="w-1.5 h-1.5 rounded-full bg-muted-foreground/40 animate-pulse" />
            {state.retryLimit - usedRuns} remaining {state.retryLimit - usedRuns === 1 ? "attempt" : "attempts"} available
          </motion.div>
        )}
      </div>
    </motion.div>
  );
}
