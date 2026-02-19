import { useDashboard } from "@/context/DashboardContext";
import { motion } from "framer-motion";
import { Bug, CheckCircle2, Clock, ExternalLink, GitBranch, User, Users, Wrench, XCircle } from "lucide-react";

export default function RunSummary() {
  const { state } = useDashboard();
  if (!state.hasResults) return null;

  const stats = [
    { icon: Bug, label: "Failures Detected", value: state.totalFailures, gradient: "from-destructive/20 to-warning/10", iconColor: "text-warning", borderColor: "border-warning/20" },
    { icon: Wrench, label: "Fixes Applied", value: state.totalFixes, gradient: "from-accent/20 to-cyan/10", iconColor: "text-accent", borderColor: "border-accent/20" },
    { icon: Clock, label: "Time Taken", value: state.timeTaken, gradient: "from-primary/20 to-pink/10", iconColor: "text-primary", borderColor: "border-primary/20" },
  ];

  return (
    <motion.div
      initial={{ opacity: 0, y: 30 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.1, duration: 0.6, ease: [0.22, 1, 0.36, 1] }}
      className="glass-card p-8 h-full"
    >
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-lg font-heading font-bold text-foreground">Run Summary</h2>
        <div
          className={`px-4 py-1.5 rounded-full text-xs font-bold uppercase tracking-widest ${state.ciStatus === "passed" ? "badge-glow-success" : "badge-glow-destructive"
            }`}
        >
          {state.ciStatus === "passed" ? (
            <span className="flex items-center gap-1.5"><CheckCircle2 className="w-3.5 h-3.5" /> Passed</span>
          ) : (
            <span className="flex items-center gap-1.5"><XCircle className="w-3.5 h-3.5" /> Failed</span>
          )}
        </div>
      </div>

      <div className="space-y-3 mb-6">
        <div className="flex items-center gap-2.5 text-sm group">
          <ExternalLink className="w-4 h-4 text-muted-foreground" />
          <span className="text-muted-foreground">Repository:</span>
          <span className="font-mono text-primary/80 truncate group-hover:text-primary transition-colors">{state.repoUrl}</span>
        </div>
        <div className="flex flex-wrap gap-x-6 gap-y-2 text-sm">
          <span className="flex items-center gap-1.5">
            <Users className="w-3.5 h-3.5 text-muted-foreground" />
            <span className="text-muted-foreground">Team:</span>
            <span className="text-foreground font-semibold">{state.teamName}</span>
          </span>
          <span className="flex items-center gap-1.5">
            <User className="w-3.5 h-3.5 text-muted-foreground" />
            <span className="text-muted-foreground">Leader:</span>
            <span className="text-foreground font-semibold">{state.teamLeader}</span>
          </span>
        </div>
        <div className="flex items-center gap-2.5 text-sm">
          <GitBranch className="w-4 h-4 text-accent" />
          <span className="font-mono text-accent font-medium">{state.branchName}</span>
        </div>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
        {stats.map((s, i) => (
          <motion.div
            key={s.label}
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.3 + i * 0.1 }}
            className={`stat-card p-3 md:p-4 text-center bg-gradient-to-br ${s.gradient} border ${s.borderColor}`}
          >
            <s.icon className={`w-4 h-4 md:w-5 md:h-5 mx-auto mb-2 md:mb-2.5 ${s.iconColor}`} />
            <div className="text-xl md:text-2xl font-heading font-extrabold text-foreground">{s.value}</div>
            <div className="text-[9px] md:text-[10px] uppercase tracking-wider text-muted-foreground mt-1 font-medium">{s.label}</div>
          </motion.div>
        ))}
      </div>
    </motion.div>
  );
}
