import { motion } from "framer-motion";
import { FileCode, CheckCircle2, XCircle, TableProperties } from "lucide-react";
import { useDashboard, Fix } from "@/context/DashboardContext";

const bugTypeStyles: Record<Fix["bugType"], { bg: string; text: string }> = {
  LINTING: { bg: "bg-primary/15 border-primary/25", text: "text-primary" },
  SYNTAX: { bg: "bg-destructive/15 border-destructive/25", text: "text-destructive" },
  LOGIC: { bg: "bg-warning/15 border-warning/25", text: "text-warning" },
  TYPE_ERROR: { bg: "bg-cyan/15 border-cyan/25", text: "text-cyan" },
  IMPORT: { bg: "bg-pink/15 border-pink/25", text: "text-pink" },
  INDENTATION: { bg: "bg-muted border-border", text: "text-muted-foreground" },
};

export default function FixesTable() {
  const { state } = useDashboard();
  if (!state.hasResults) return null;

  const fixedCount = state.fixes.filter(f => f.status === "fixed").length;

  return (
    <motion.div
      initial={{ opacity: 0, y: 30 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.3, duration: 0.6, ease: [0.22, 1, 0.36, 1] }}
      className="glass-card p-8"
    >
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <div className="p-2 rounded-xl bg-accent/10 border border-accent/20">
            <TableProperties className="w-5 h-5 text-accent" />
          </div>
          <div>
            <h2 className="text-lg font-heading font-bold text-foreground">Fixes Applied</h2>
            <p className="text-xs text-muted-foreground">Detailed log of all automated fixes</p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-2xl font-heading font-black text-gradient">{fixedCount}</span>
          <span className="text-sm text-muted-foreground">/ {state.totalFailures}</span>
        </div>
      </div>

      <div className="overflow-x-auto rounded-xl border border-border/50">
        <table className="w-full text-sm">
          <thead>
            <tr className="bg-secondary/60">
              <th className="text-left py-3.5 px-4 text-[11px] uppercase tracking-wider text-muted-foreground font-semibold">File</th>
              <th className="text-left py-3.5 px-4 text-[11px] uppercase tracking-wider text-muted-foreground font-semibold">Bug Type</th>
              <th className="text-left py-3.5 px-4 text-[11px] uppercase tracking-wider text-muted-foreground font-semibold">Line</th>
              <th className="text-left py-3.5 px-4 text-[11px] uppercase tracking-wider text-muted-foreground font-semibold hidden md:table-cell">Commit Message</th>
              <th className="text-center py-3.5 px-4 text-[11px] uppercase tracking-wider text-muted-foreground font-semibold">Status</th>
            </tr>
          </thead>
          <tbody>
            {state.fixes.map((fix, i) => {
              const style = bugTypeStyles[fix.bugType];
              return (
                <motion.tr
                  key={i}
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.4 + i * 0.04 }}
                  className="border-b border-border/30 table-row-hover"
                >
                  <td className="py-3 px-4 font-mono text-xs text-foreground">
                    <div className="flex items-center gap-2">
                      <FileCode className="w-3.5 h-3.5 text-muted-foreground flex-shrink-0" />
                      {fix.file}
                    </div>
                  </td>
                  <td className="py-3 px-4">
                    <span className={`inline-flex px-2.5 py-1 rounded-md text-[11px] font-bold tracking-wide border ${style.bg} ${style.text}`}>
                      {fix.bugType}
                    </span>
                  </td>
                  <td className="py-3 px-4 font-mono text-xs text-muted-foreground">L{fix.lineNumber}</td>
                  <td className="py-3 px-4 text-xs text-muted-foreground hidden md:table-cell">
                    <span className="truncate block max-w-xs font-mono">{fix.commitMessage}</span>
                  </td>
                  <td className="py-3 px-4 text-center">
                    {fix.status === "fixed" ? (
                      <div className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full bg-success/10 border border-success/20">
                        <CheckCircle2 className="w-3.5 h-3.5 text-success" />
                        <span className="text-[10px] font-bold text-success uppercase">Fixed</span>
                      </div>
                    ) : (
                      <div className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full bg-destructive/10 border border-destructive/20">
                        <XCircle className="w-3.5 h-3.5 text-destructive" />
                        <span className="text-[10px] font-bold text-destructive uppercase">Failed</span>
                      </div>
                    )}
                  </td>
                </motion.tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </motion.div>
  );
}
