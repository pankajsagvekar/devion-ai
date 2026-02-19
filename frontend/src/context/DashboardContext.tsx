import React, { createContext, ReactNode, useContext, useReducer } from "react";

export interface Fix {
  file: string;
  bugType: "LINTING" | "SYNTAX" | "LOGIC" | "TYPE_ERROR" | "IMPORT" | "INDENTATION" | "DEFAULT";
  lineNumber: number;
  commitMessage: string;
  status: "fixed" | "failed" | "deleted";
}

export interface CIRun {
  iteration: number;
  status: "passed" | "failed";
  timestamp: string;
}

export interface DashboardState {
  repoUrl: string;
  teamName: string;
  teamLeader: string;
  githubToken: string;
  isRunning: boolean;
  hasResults: boolean;
  branchName: string;
  totalFailures: number;
  totalFixes: number;
  ciStatus: "passed" | "failed" | null;
  timeTaken: string;
  baseScore: number;
  speedBonus: number;
  efficiencyPenalty: number;
  finalScore: number;
  totalCommits: number;
  fixes: Fix[];
  fixesApplied: string[];
  ciRuns: CIRun[];
  retryLimit: number;
  error?: string;
}

type Action =
  | { type: "SET_FIELD"; field: string; value: string }
  | { type: "START_RUN" }
  | { type: "FINISH_RUN"; payload: Omit<DashboardState, "repoUrl" | "teamName" | "teamLeader" | "githubToken" | "isRunning" | "hasResults"> }
  | { type: "SET_ERROR"; error: string };

const initialState: DashboardState = {
  repoUrl: "",
  teamName: "",
  teamLeader: "",
  githubToken: "",
  isRunning: false,
  hasResults: false,
  branchName: "",
  totalFailures: 0,
  totalFixes: 0,
  ciStatus: null,
  timeTaken: "",
  baseScore: 100,
  speedBonus: 0,
  efficiencyPenalty: 0,
  finalScore: 0,
  totalCommits: 0,
  fixes: [],
  fixesApplied: [],
  ciRuns: [],
  retryLimit: 5,
};

function reducer(state: DashboardState, action: Action): DashboardState {
  switch (action.type) {
    case "SET_FIELD":
      return { ...state, [action.field]: action.value, error: undefined };
    case "START_RUN":
      return { ...state, isRunning: true, hasResults: false, error: undefined };
    case "FINISH_RUN":
      return { ...state, isRunning: false, hasResults: true, ...action.payload };
    case "SET_ERROR":
      return { ...state, isRunning: false, error: action.error };
    default:
      return state;
  }
}

const DashboardContext = createContext<{
  state: DashboardState;
  dispatch: React.Dispatch<Action>;
} | null>(null);

export function DashboardProvider({ children }: { children: ReactNode }) {
  const [state, dispatch] = useReducer(reducer, initialState);
  return (
    <DashboardContext.Provider value={{ state, dispatch }}>
      {children}
    </DashboardContext.Provider>
  );
}

export function useDashboard() {
  const ctx = useContext(DashboardContext);
  if (!ctx) throw new Error("useDashboard must be used within DashboardProvider");
  return ctx;
}

// Mock data generator for demo
export function generateMockResults(teamName: string, teamLeader: string): Omit<DashboardState, "repoUrl" | "teamName" | "teamLeader" | "githubToken" | "isRunning" | "hasResults"> {
  const bugTypes: Fix["bugType"][] = ["LINTING", "SYNTAX", "LOGIC", "TYPE_ERROR", "IMPORT", "INDENTATION"];
  const files = ["src/index.ts", "src/utils/parser.ts", "src/components/App.tsx", "lib/helpers.js", "src/api/handler.ts", "config/webpack.config.js", "src/models/user.ts", "tests/unit.test.ts"];

  const fixes: Fix[] = Array.from({ length: 12 }, (_, i) => ({
    file: files[i % files.length],
    bugType: bugTypes[i % bugTypes.length],
    lineNumber: Math.floor(Math.random() * 200) + 1,
    commitMessage: `fix(${bugTypes[i % bugTypes.length].toLowerCase()}): resolve ${bugTypes[i % bugTypes.length].toLowerCase()} issue in ${files[i % files.length].split("/").pop()}`,
    status: Math.random() > 0.15 ? "fixed" as const : "failed" as const,
  }));

  const totalFixes = fixes.filter(f => f.status === "fixed").length;
  const totalFailures = fixes.length;
  const totalCommits = 15;
  const timeTakenMinutes = 3.7;
  const speedBonus = timeTakenMinutes < 5 ? 10 : 0;
  const efficiencyPenalty = totalCommits > 20 ? (totalCommits - 20) * 2 : 0;

  const ciRuns: CIRun[] = [
    { iteration: 1, status: "failed", timestamp: new Date(Date.now() - 200000).toISOString() },
    { iteration: 2, status: "failed", timestamp: new Date(Date.now() - 140000).toISOString() },
    { iteration: 3, status: "passed", timestamp: new Date(Date.now() - 80000).toISOString() },
  ];

  const branchSafe = teamName.replace(/\s+/g, "_").toUpperCase();
  const leaderSafe = teamLeader.replace(/\s+/g, "_");

  return {
    branchName: `${branchSafe}_${leaderSafe}_AI_Fix`,
    totalFailures,
    totalFixes,
    ciStatus: "passed",
    timeTaken: `${timeTakenMinutes.toFixed(1)} min`,
    baseScore: 100,
    speedBonus,
    efficiencyPenalty,
    finalScore: 100 + speedBonus - efficiencyPenalty,
    totalCommits,
    fixes,
    fixesApplied: fixes.map(f => `[AI-AGENT] Fixed ${f.bugType} in ${f.file} at line ${f.lineNumber}`),
    ciRuns,
    retryLimit: 5,
  };
}
