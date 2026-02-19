import React from 'react';
import { useNavigate } from "react-router-dom";
import { Sparkles, LogOut, Github, User } from "lucide-react";

interface HeaderProps {
    isLoggedIn: boolean;
    userData: any;
    handleLogin: () => void;
    handleLogout: () => void;
    showAiBadge?: boolean;
}

const Header: React.FC<HeaderProps> = ({
    isLoggedIn,
    userData,
    handleLogin,
    handleLogout,
    showAiBadge = true
}) => {
    const navigate = useNavigate();

    return (
        <header className="glass-strong sticky top-0 z-50 border-b border-border/30">
            <div className="container flex items-center justify-between py-2">
                <div
                    className="flex items-center gap-4 cursor-pointer hover:opacity-90 transition-opacity"
                    onClick={() => navigate("/")}
                >
                    <div className="relative group">
                        <img
                            src="/devion.png"
                            alt="Devion-AI Logo"
                            className="relative w-14 h-14 object-contain rounded-xl"
                        />
                    </div>
                    <div>
                        <h1 className="text-2xl font-bold tracking-tight">
                            <span className="text-white/90">
                                Devion-
                            </span>
                            <span className="text-primary">
                                AI
                            </span>
                        </h1>
                        <p className="text-xs text-muted-foreground tracking-wide">Automated Repository Analysis & Bug Fixing</p>
                    </div>
                </div>

                <div className="flex items-center gap-4">
                    {showAiBadge && (
                        <div className="hidden md:flex items-center gap-2 px-3 py-1.5 rounded-full bg-primary/10 border border-primary/20">
                            <Sparkles className="w-3.5 h-3.5 text-primary" />
                            <span className="text-xs font-medium text-primary">AI-Powered</span>
                        </div>
                    )}

                    {isLoggedIn ? (
                        <div className="flex items-center gap-3">
                            <button
                                onClick={() => navigate("/profile")}
                                className="flex items-center gap-2 p-1.5 pr-4 rounded-xl bg-secondary/20 border border-border/50 text-sm font-medium hover:bg-secondary/30 transition-colors"
                            >
                                {userData?.avatar_url ? (
                                    <img src={userData.avatar_url} alt="Profile" className="w-7 h-7 rounded-lg border border-primary/30" />
                                ) : (
                                    <div className="w-7 h-7 rounded-lg bg-primary/20 flex items-center justify-center">
                                        <User className="w-4 h-4 text-primary" />
                                    </div>
                                )}
                                <span className="hidden sm:inline">{userData?.name || userData?.login || "Profile"}</span>
                            </button>
                            <button
                                onClick={handleLogout}
                                className="flex items-center gap-2 px-4 py-2 rounded-xl bg-destructive/10 border border-destructive/20 text-sm font-medium hover:bg-destructive/20 text-destructive transition-colors"
                            >
                                <LogOut className="w-4 h-4" />
                                <span className="hidden lg:inline">Logout</span>
                            </button>
                        </div>
                    ) : (
                        <button
                            onClick={handleLogin}
                            className="flex items-center gap-2 px-4 py-2 rounded-xl bg-primary text-primary-foreground text-sm font-bold hover:opacity-90 transition-opacity"
                        >
                            <Github className="w-4 h-4" />
                            Connect GitHub
                        </button>
                    )}
                </div>
            </div>
        </header>
    );
};

export default Header;
