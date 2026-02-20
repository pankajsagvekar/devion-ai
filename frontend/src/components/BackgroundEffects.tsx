import React from 'react';
import Threads from './Threads';

const BackgroundEffects = ({ lowPower = false }: { lowPower?: boolean }) => {
    return (
        <div className="fixed inset-0 pointer-events-none z-0 overflow-hidden">
            {/* Cinematic Threads Animation */}
            <div className="absolute inset-0 opacity-70">
                <Threads
                    color={[0.6, 0.4, 1]}
                    amplitude={1.2}
                    distance={0.4}
                    enableMouseInteraction={!lowPower}
                    lowPower={lowPower}
                />
            </div>

            {/* Primary Light Flare */}
            <div className={`absolute top-0 right-0 w-[800px] h-[800px] rounded-full bg-primary/10 blur-[150px] opacity-60 ${lowPower ? '' : 'animate-orb-1'}`} />

            {/* Secondary Soft Glows - Simplified in lowPower */}
            <div className={`absolute -bottom-20 -left-20 w-[600px] h-[600px] rounded-full bg-accent/8 blur-[130px] ${lowPower ? '' : 'animate-orb-2'}`} />

            {/* Animated Drift Particles - Disabled in lowPower */}
            {!lowPower && (
                <div className="absolute top-1/2 right-1/4 w-[300px] h-[300px] rounded-full bg-amber-500/5 blur-[90px] animate-drift" />
            )}

            {/* Grid Overlay with subtle pulse - Static in lowPower */}
            <div className={`absolute inset-0 bg-grid opacity-[0.02] ${lowPower ? '' : 'animate-pulse-slow'}`} />
        </div>
    );
};

export default BackgroundEffects;
