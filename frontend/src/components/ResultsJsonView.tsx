import { useDashboard } from "@/context/DashboardContext";
import { motion } from "framer-motion";
import { Code, Copy, Check } from "lucide-react";
import { useState } from "react";
import { toast } from "sonner";

export default function ResultsJsonView() {
  const { state } = useDashboard();
  const [copied, setCopied] = useState(false);

  if (!state.rawJson) return null;

  const jsonString = JSON.stringify(state.rawJson, null, 2);

  const handleCopy = () => {
    navigator.clipboard.writeText(jsonString);
    setCopied(true);
    toast.success("JSON copied to clipboard");
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className="glass-card overflow-hidden"
    >
      <div className="flex items-center justify-between p-6 border-b border-border/40 bg-muted/30">
        <div className="flex items-center gap-3">
          <div className="p-2 rounded-lg bg-primary/10">
            <Code className="w-5 h-5 text-primary" />
          </div>
          <div>
            <h3 className="text-lg font-heading font-bold">Results.json</h3>
            <p className="text-xs text-muted-foreground">The direct output from the AI Healing Agent</p>
          </div>
        </div>
        <button
          onClick={handleCopy}
          className="flex items-center gap-2 px-4 py-2 rounded-xl bg-background/50 border border-border/40 hover:bg-background/80 transition-all text-xs font-bold"
        >
          {copied ? <Check className="w-4 h-4 text-success" /> : <Copy className="w-4 h-4" />}
          {copied ? "Copied" : "Copy JSON"}
        </button>
      </div>

      <div className="relative group">
        <div className="absolute inset-0 bg-gradient-to-b from-primary/5 to-transparent pointer-events-none" />
        <pre className="p-6 max-h-[500px] overflow-auto font-mono text-sm text-foreground/80 scrollbar-thin scrollbar-thumb-primary/20 scrollbar-track-transparent">
          <code className="language-json">
            {jsonString}
          </code>
        </pre>
      </div>
    </motion.div>
  );
}
