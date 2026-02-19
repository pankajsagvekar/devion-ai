import React from 'react';

const BackgroundEffects = () => {
    return (
        <div className="fixed inset-0 pointer-events-none z-0 overflow-hidden">
            {/* Primary Light Flare */}
            <div className="absolute top-0 right-0 w-[800px] h-[800px] rounded-full bg-primary/15 blur-[150px] animate-orb-1 opacity-60" />

            {/* Secondary Soft Glows */}
            <div className="absolute -bottom-20 -left-20 w-[600px] h-[600px] rounded-full bg-accent/10 blur-[130px] animate-orb-2" />
            <div className="absolute top-1/4 left-1/3 w-[400px] h-[400px] rounded-full bg-primary/5 blur-[100px] animate-pulse-slow" />

            {/* Animated Drift Particles */}
            <div className="absolute top-1/2 right-1/4 w-[300px] h-[300px] rounded-full bg-amber-500/5 blur-[90px] animate-drift" />
            <div className="absolute bottom-1/4 left-1/4 w-[500px] h-[500px] rounded-full bg-gold/5 blur-[120px] animate-drift" style={{ animationDelay: '-5s' }} />

            {/* Grid Overlay with subtle pulse */}
            <div className="absolute inset-0 bg-grid opacity-[0.03] animate-pulse-slow" />
        </div>
    );
};

export default BackgroundEffects;
