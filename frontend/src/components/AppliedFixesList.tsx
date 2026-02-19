import { useDashboard } from "@/context/DashboardContext";
import { motion } from "framer-motion";
import { CheckCircle2, Wrench } from "lucide-react";

export default function AppliedFixesList() {
    const { state } = useDashboard();
    if (!state.hasResults || !state.fixesApplied || state.fixesApplied.length === 0) return null;

    return (
        <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4, duration: 0.6, ease: [0.22, 1, 0.36, 1] }}
            className="glass-card p-8"
        >
            <div className="flex items-center gap-3 mb-6">
                <div className="p-2 rounded-xl bg-primary/10 border border-primary/20">
                    <Wrench className="w-5 h-5 text-primary" />
                </div>
                <div>
                    <h2 className="text-lg font-heading font-bold text-foreground">Audit Log - Fixes Applied</h2>
                    <p className="text-xs text-muted-foreground">Canonical fix summaries from the AI Agent</p>
                </div>
            </div>

            <div className="space-y-3">
                {state.fixesApplied.map((fix, i) => (
                    <motion.div
                        key={i}
                        initial={{ opacity: 0, x: -20 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: 0.5 + i * 0.05 }}
                        className="flex items-center gap-4 p-4 rounded-xl bg-secondary/30 border border-border/40 hover:border-primary/30 transition-colors group"
                    >
                        <CheckCircle2 className="w-4 h-4 text-success flex-shrink-0" />
                        <span className="text-xs font-mono text-muted-foreground group-hover:text-foreground transition-colors">
                            {fix}
                        </span>
                    </motion.div>
                ))}
            </div>
        </motion.div>
    );
}
