import { motion } from "framer-motion";
import { Trophy, Zap, AlertTriangle, Award } from "lucide-react";
import { useDashboard } from "@/context/DashboardContext";

export default function ScoreBreakdown() {
  const { state } = useDashboard();
  if (!state.hasResults) return null;

  const maxScore = 110;
  const scorePercent = Math.max(0, Math.min(100, (state.finalScore / maxScore) * 100));

  const items = [
    { label: "Base Score", value: state.baseScore, suffix: "", icon: Trophy, color: "text-primary", bg: "bg-primary/10 border-primary/20" },
    { label: "Speed Bonus", value: state.speedBonus, suffix: "+", icon: Zap, color: "text-accent", bg: "bg-accent/10 border-accent/20" },
    { label: "Efficiency Penalty", value: state.efficiencyPenalty, suffix: state.efficiencyPenalty > 0 ? "-" : "", icon: AlertTriangle, color: "text-warning", bg: "bg-warning/10 border-warning/20" },
  ];

  return (
    <motion.div
      initial={{ opacity: 0, y: 30 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.2, duration: 0.6, ease: [0.22, 1, 0.36, 1] }}
      className="glass-card p-8 h-full"
    >
      <div className="flex items-center gap-2.5 mb-6">
        <Award className="w-5 h-5 text-gold" />
        <h2 className="text-lg font-heading font-bold text-foreground">Score Breakdown</h2>
      </div>

      <div className="flex items-center justify-center mb-8">
        <div className="relative w-40 h-40">
          {/* Outer glow */}
          <div className="absolute inset-[-8px] rounded-full bg-primary/10 blur-xl animate-pulse-glow" />
          <svg className="w-full h-full -rotate-90 relative z-10" viewBox="0 0 120 120">
            <circle cx="60" cy="60" r="50" fill="none" stroke="hsl(var(--secondary))" strokeWidth="8" />
            <motion.circle
              cx="60" cy="60" r="50" fill="none"
              stroke="url(#premiumScoreGradient)" strokeWidth="8"
              strokeLinecap="round"
              strokeDasharray={`${2 * Math.PI * 50}`}
              initial={{ strokeDashoffset: 2 * Math.PI * 50 }}
              animate={{ strokeDashoffset: 2 * Math.PI * 50 * (1 - scorePercent / 100) }}
              transition={{ duration: 2, ease: [0.22, 1, 0.36, 1], delay: 0.5 }}
              filter="url(#glow)"
            />
            <defs>
              <linearGradient id="premiumScoreGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stopColor="hsl(var(--primary))" />
                <stop offset="50%" stopColor="hsl(var(--cyan))" />
                <stop offset="100%" stopColor="hsl(var(--accent))" />
              </linearGradient>
              <filter id="glow">
                <feGaussianBlur stdDeviation="3" result="blur" />
                <feMerge>
                  <feMergeNode in="blur" />
                  <feMergeNode in="SourceGraphic" />
                </feMerge>
              </filter>
            </defs>
          </svg>
          <div className="absolute inset-0 flex flex-col items-center justify-center z-20">
            <motion.span
              className="text-4xl font-heading font-black text-gradient"
              initial={{ opacity: 0, scale: 0.5 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: 1, type: "spring", stiffness: 200 }}
            >
              {state.finalScore}
            </motion.span>
            <span className="text-[10px] uppercase tracking-widest text-muted-foreground font-medium mt-0.5">points</span>
          </div>
        </div>
      </div>

      <div className="space-y-2.5">
        {items.map((item, i) => (
          <motion.div
            key={item.label}
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.6 + i * 0.1 }}
            className={`flex items-center justify-between p-3 rounded-xl ${item.bg} border`}
          >
            <div className="flex items-center gap-3">
              <item.icon className={`w-4 h-4 ${item.color}`} />
              <span className="text-sm text-foreground font-medium">{item.label}</span>
            </div>
            <span className={`font-mono font-bold ${item.color}`}>
              {item.suffix}{item.value}
            </span>
          </motion.div>
        ))}
      </div>

      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 1 }}
        className="mt-4 p-3 rounded-xl bg-secondary/40 border border-border/50 text-xs text-muted-foreground flex items-center justify-between"
      >
        <span>Total Commits</span>
        <span className="font-mono font-bold text-foreground">{state.totalCommits} <span className="text-muted-foreground font-normal">/ 20 max</span></span>
      </motion.div>
    </motion.div>
  );
}
