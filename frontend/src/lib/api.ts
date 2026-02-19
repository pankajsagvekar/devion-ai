import axios from "axios";

const api = axios.create({
    baseURL: import.meta.env.VITE_API_URL || "http://localhost:8000",
});

export const fetchGithubUser = async () => {
    const token = localStorage.getItem("github_token");
    if (!token) return null;

    try {
        const response = await fetch("https://api.github.com/user", {
            headers: {
                Authorization: `Bearer ${token}`,
                Accept: "application/json",
            },
        });

        if (!response.ok) {
            if (response.status === 401) {
                localStorage.removeItem("github_token");
            }
            return null;
        }

        return await response.json();
    } catch (error) {
        console.error("Error fetching GitHub user:", error);
        return null;
    }
};

export default api;
