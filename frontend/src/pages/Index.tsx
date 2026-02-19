import { DashboardProvider } from "@/context/DashboardContext";
import InputSection from "@/components/InputSection";
import RunSummary from "@/components/RunSummary";
import ScoreBreakdown from "@/components/ScoreBreakdown";
import FixesTable from "@/components/FixesTable";
import CITimeline from "@/components/CITimeline";
import { Bot, Sparkles } from "lucide-react";

const Index = () => {
  return (
    <DashboardProvider>
      <div className="min-h-screen bg-background bg-mesh bg-grid relative overflow-hidden">
        {/* Floating orbs */}
        <div className="fixed top-20 left-10 w-[500px] h-[500px] rounded-full bg-primary/5 blur-[120px] animate-orb-1 pointer-events-none" />
        <div className="fixed bottom-20 right-10 w-[400px] h-[400px] rounded-full bg-cyan/5 blur-[100px] animate-orb-2 pointer-events-none" />
        <div className="fixed top-1/2 left-1/2 w-[300px] h-[300px] rounded-full bg-pink/3 blur-[80px] pointer-events-none" />

        {/* Header */}
        <header className="glass-strong sticky top-0 z-50 border-b border-border/30">
          <div className="container flex items-center justify-between py-4">
            <div className="flex items-center gap-4">
              <div className="relative">
                <div className="absolute inset-0 bg-primary/30 blur-lg rounded-xl" />
                <div className="relative p-2.5 rounded-xl bg-primary/20 border border-primary/30">
                  <Bot className="w-6 h-6 text-primary" />
                </div>
              </div>
              <div>
                <h1 className="text-xl font-heading font-bold text-gradient tracking-tight">CI/CD Agent Dashboard</h1>
                <p className="text-xs text-muted-foreground tracking-wide">Automated Repository Analysis & Bug Fixing</p>
              </div>
            </div>
            <div className="hidden md:flex items-center gap-2 px-3 py-1.5 rounded-full bg-primary/10 border border-primary/20">
              <Sparkles className="w-3.5 h-3.5 text-primary" />
              <span className="text-xs font-medium text-primary">AI-Powered</span>
            </div>
          </div>
        </header>

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

        {/* Footer */}
        <footer className="border-t border-border/20 py-6 mt-12 relative z-10">
          <div className="container text-center text-xs text-muted-foreground">
            Built for <span className="text-gradient font-semibold">RIFT Hackathon</span> — Powered by AI Agent Technology
          </div>
        </footer>
      </div>
    </DashboardProvider>
  );
};

export default Index;
