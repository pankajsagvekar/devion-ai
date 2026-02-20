import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { fetchGithubUser } from "@/lib/api";
import { Bot, Github, Mail, MapPin, User, ArrowLeft, ExternalLink, Calendar, Code2, Globe } from "lucide-react";
import { motion } from "framer-motion";
import Header from "@/components/Header";
import BackgroundEffects from "@/components/BackgroundEffects";

interface GithubUser {
    login: string;
    id: number;
    avatar_url: string;
    name: string;
    company: string;
    blog: string;
    location: string;
    email: string;
    bio: string;
    public_repos: number;
    followers: number;
    following: number;
    created_at: string;
    html_url: string;
}

const Profile = () => {
    const [user, setUser] = useState<any>(null);
    const [loading, setLoading] = useState(true);
    const navigate = useNavigate();

    useEffect(() => {
        const getUserData = async () => {
            const data = await fetchGithubUser();
            if (data) {
                setUser(data);
            } else {
                navigate("/");
            }
            setLoading(false);
        };

        getUserData();
    }, [navigate]);

    const handleLogout = () => {
        localStorage.removeItem("github_token");
        navigate("/");
    };

    const handleLogin = () => {
        const apiUrl = import.meta.env.VITE_API_URL || "http://localhost:8000";
        window.location.href = `${apiUrl}/auth/login`;
    };

    if (loading) {
        return (
            <div className="min-h-screen bg-background flex items-center justify-center">
                <div className="relative">
                    <div className="w-12 h-12 border-4 border-primary/20 border-t-primary rounded-full animate-spin" />
                    <div className="absolute inset-0 blur-xl bg-primary/20 rounded-full animate-pulse" />
                </div>
            </div>
        );
    }

    if (!user) return null;

    return (
        <div className="min-h-screen bg-background bg-mesh bg-grid relative overflow-hidden">
            <BackgroundEffects />

            <Header
                isLoggedIn={true}
                userData={user}
                handleLogin={handleLogin}
                handleLogout={handleLogout}
                showAiBadge={false}
            />

            <main className="container py-12 relative z-10 max-w-4xl">
                <motion.button
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    onClick={() => navigate("/")}
                    className="flex items-center gap-2 text-sm text-muted-foreground hover:text-primary transition-colors mb-8"
                >
                    <ArrowLeft className="w-4 h-4" />
                    Back to Dashboard
                </motion.button>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
                    {/* Sidebar Info */}
                    <motion.div
                        initial={{ opacity: 0, y: 30 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.6 }}
                        className="md:col-span-1 space-y-6"
                    >
                        <div className="glass-card p-6 text-center">
                            <div className="relative inline-block mb-4">
                                <div className="absolute inset-0 bg-primary/30 blur-xl rounded-full" />
                                <img
                                    src={user.avatar_url}
                                    alt={user.name}
                                    className="relative w-32 h-32 rounded-full border-2 border-primary/50 object-cover"
                                />
                            </div>
                            <h2 className="text-xl font-heading font-bold text-foreground">{user.name}</h2>
                            <p className="text-sm text-muted-foreground">@{user.login}</p>

                            <div className="mt-6 pt-6 border-t border-border/50 space-y-4">
                                <div className="flex items-center gap-3 text-sm text-muted-foreground truncate">
                                    <Mail className="w-4 h-4 text-primary" />
                                    <span>{user.email || 'No public email'}</span>
                                </div>
                                <div className="flex items-center gap-3 text-sm text-muted-foreground">
                                    <MapPin className="w-4 h-4 text-primary" />
                                    <span>{user.location || 'Global'}</span>
                                </div>
                                <div className="flex items-center gap-3 text-sm text-muted-foreground">
                                    <Calendar className="w-4 h-4 text-primary" />
                                    <span>Joined {new Date(user.created_at).toLocaleDateString()}</span>
                                </div>
                            </div>

                            <a
                                href={user.html_url}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="mt-8 flex items-center justify-center gap-2 w-full py-2.5 rounded-xl bg-primary text-primary-foreground text-sm font-bold hover:opacity-90 transition-opacity"
                            >
                                <Github className="w-4 h-4" />
                                GitHub Profile
                                <ExternalLink className="w-3 h-3" />
                            </a>
                        </div>
                    </motion.div>

                    {/* Main Profile Content */}
                    <div className="md:col-span-2 space-y-6">
                        <motion.div
                            initial={{ opacity: 0, y: 30 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ duration: 0.6, delay: 0.1 }}
                            className="glass-card p-8"
                        >
                            <h3 className="text-lg font-heading font-bold text-foreground mb-4">About Me</h3>
                            <p className="text-muted-foreground leading-relaxed">
                                {user.bio || "This user hasn't added a bio yet. They are likely busy fixing bugs and optimizing pipelines with Devion-AI!"}
                            </p>

                            <div className="grid grid-cols-2 sm:grid-cols-3 gap-4 mt-8">
                                <div className="stat-card p-4 text-center">
                                    <Code2 className="w-5 h-5 mx-auto mb-2 text-primary" />
                                    <div className="text-2xl font-bold font-heading">{user.public_repos}</div>
                                    <div className="text-xs uppercase tracking-wider text-muted-foreground">Repositories</div>
                                </div>
                                <div className="stat-card p-4 text-center">
                                    <User className="w-5 h-5 mx-auto mb-2 text-accent" />
                                    <div className="text-2xl font-bold font-heading">{user.followers}</div>
                                    <div className="text-xs uppercase tracking-wider text-muted-foreground">Followers</div>
                                </div>
                                <div className="stat-card p-4 text-center">
                                    <Globe className="w-5 h-5 mx-auto mb-2 text-cyan" />
                                    <div className="text-2xl font-bold font-heading">{user.following}</div>
                                    <div className="text-xs uppercase tracking-wider text-muted-foreground">Following</div>
                                </div>
                            </div>
                        </motion.div>

                        <motion.div
                            initial={{ opacity: 0, y: 30 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ duration: 0.6, delay: 0.2 }}
                            className="glass-card p-8"
                        >
                            <h3 className="text-lg font-heading font-bold text-foreground mb-6 flex items-center gap-2">
                                <Bot className="w-5 h-5 text-primary" />
                                Devion-AI Activity
                            </h3>
                            <div className="space-y-4">
                                <div className="p-4 rounded-xl bg-secondary/30 border border-border/50 flex items-center justify-between">
                                    <div className="flex items-center gap-3">
                                        <div className="w-2 h-2 rounded-full bg-success animate-pulse" />
                                        <span className="text-sm font-medium">Active Session</span>
                                    </div>
                                    <span className="text-xs text-muted-foreground">Connected via GitHub OAuth</span>
                                </div>
                                <div className="p-4 rounded-xl bg-secondary/30 border border-border/50 flex items-center justify-between opacity-50">
                                    <div className="flex items-center gap-3">
                                        <div className="w-2 h-2 rounded-full bg-muted-foreground" />
                                        <span className="text-sm font-medium">Past Analysis</span>
                                    </div>
                                    <span className="text-xs text-muted-foreground">No recent history</span>
                                </div>
                            </div>
                        </motion.div>
                    </div>
                </div>
            </main>
        </div>
    );
};

export default Profile;
