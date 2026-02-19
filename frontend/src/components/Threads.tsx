import React, { useEffect, useRef } from 'react';
import { Renderer, Program, Mesh, Triangle, Color } from 'ogl';

interface ThreadsProps {
    color?: [number, number, number];
    amplitude?: number;
    distance?: number;
    enableMouseInteraction?: boolean;
    lowPower?: boolean;
}

const vertexShader = `
attribute vec2 position;
attribute vec2 uv;
varying vec2 vUv;
void main() {
  vUv = uv;
  gl_Position = vec4(position, 0.0, 1.0);
}
`;

const fragmentShader = `
precision highp float;

uniform float iTime;
uniform vec3 iResolution;
uniform vec3 uColor;
uniform float uAmplitude;
uniform float uDistance;
uniform vec2 uMouse;
uniform int uLineCount;

#define PI 3.1415926538

const float u_line_width = 7.0;
const float u_line_blur = 10.0;

float Perlin2D(vec2 P) {
    vec2 Pi = floor(P);
    vec4 Pf_Pfmin1 = P.xyxy - vec4(Pi, Pi + 1.0);
    vec4 Pt = vec4(Pi.xy, Pi.xy + 1.0);
    Pt = Pt - floor(Pt * (1.0 / 71.0)) * 71.0;
    Pt += vec2(26.0, 161.0).xyxy;
    Pt *= Pt;
    Pt = Pt.xzxz * Pt.yyww;
    vec4 hash_x = fract(Pt * (1.0 / 951.135664));
    vec4 hash_y = fract(Pt * (1.0 / 642.949883));
    vec4 grad_x = hash_x - 0.49999;
    vec4 grad_y = hash_y - 0.49999;
    vec4 grad_results = inversesqrt(grad_x * grad_x + grad_y * grad_y)
        * (grad_x * Pf_Pfmin1.xzxz + grad_y * Pf_Pfmin1.yyww);
    grad_results *= 1.4142135623730950;
    vec2 blend = Pf_Pfmin1.xy * Pf_Pfmin1.xy * Pf_Pfmin1.xy
               * (Pf_Pfmin1.xy * (Pf_Pfmin1.xy * 6.0 - 15.0) + 10.0);
    vec4 blend2 = vec4(blend, vec2(1.0 - blend));
    return dot(grad_results, blend2.zxzx * blend2.wwyy);
}

float pixel(float count, vec2 resolution) {
    return (1.0 / max(resolution.x, resolution.y)) * count;
}

float lineFn(vec2 st, float width, float perc, float offset, vec2 mouse, float time, float amplitude, float distance) {
    float split_offset = (perc * 0.4);
    float split_point = 0.1 + split_offset;

    float amplitude_normal = smoothstep(split_point, 0.7, st.x);
    float amplitude_strength = 0.5;
    float finalAmplitude = amplitude_normal * amplitude_strength
                           * amplitude * (1.0 + (mouse.y - 0.5) * 0.2);

    float time_scaled = time / 10.0 + (mouse.x - 0.5) * 1.0;
    float blur = smoothstep(split_point, split_point + 0.05, st.x) * perc;

    float xnoise = mix(
        Perlin2D(vec2(time_scaled, st.x + perc) * 2.5),
        Perlin2D(vec2(time_scaled, st.x + time_scaled) * 3.5) / 1.5,
        st.x * 0.3
    );

    float y = 0.5 + (perc - 0.5) * distance + xnoise / 2.0 * finalAmplitude;

    float line_start = smoothstep(
        y + (width / 2.0) + (u_line_blur * pixel(1.0, iResolution.xy) * blur),
        y,
        st.y
    );

    float line_end = smoothstep(
        y,
        y - (width / 2.0) - (u_line_blur * pixel(1.0, iResolution.xy) * blur),
        st.y
    );

    return clamp(
        (line_start - line_end) * (1.0 - smoothstep(0.0, 1.0, pow(perc, 0.3))),
        0.0,
        1.0
    );
}

void mainImage(out vec4 fragColor, in vec2 fragCoord) {
    vec2 uv = fragCoord / iResolution.xy;

    float line_strength = 1.0;
    
    // Static loop limit for compiler compatibility, but dynamic exit
    for (int i = 0; i < 40; i++) {
        if (i >= uLineCount) break;
        float p = float(i) / float(uLineCount);
        line_strength *= (1.0 - lineFn(
            uv,
            u_line_width * pixel(1.0, iResolution.xy) * (1.0 - p),
            p,
            (PI * 1.0) * p,
            uMouse,
            iTime,
            uAmplitude,
            uDistance
        ));
    }

    float colorVal = 1.0 - line_strength;
    fragColor = vec4(uColor * colorVal, colorVal);
}

void main() {
    mainImage(gl_FragColor, gl_FragCoord.xy);
}
`;

const Threads: React.FC<ThreadsProps> = React.memo(({
    color = [1, 1, 1],
    amplitude = 1,
    distance = 0,
    enableMouseInteraction = false,
    lowPower = false,
    ...rest
}) => {
    const containerRef = useRef<HTMLDivElement>(null);
    const rendererRef = useRef<Renderer | null>(null);
    const programRef = useRef<Program | null>(null);
    const glRef = useRef<any>(null);
    const animationFrameId = useRef<number>(0);
    const mouseRef = useRef({ current: [0.5, 0.5], target: [0.5, 0.5] });

    // Initial setup
    useEffect(() => {
        if (!containerRef.current) return;
        const container = containerRef.current;

        const renderer = new Renderer({ alpha: true, dpr: lowPower ? 1 : Math.min(window.devicePixelRatio, 2) });
        rendererRef.current = renderer;
        const gl = renderer.gl;
        glRef.current = gl;
        gl.clearColor(0, 0, 0, 0);
        gl.enable(gl.BLEND);
        gl.blendFunc(gl.SRC_ALPHA, gl.ONE_MINUS_SRC_ALPHA);
        container.appendChild(gl.canvas);

        const geometry = new Triangle(gl);
        const program = new Program(gl, {
            vertex: vertexShader,
            fragment: fragmentShader,
            uniforms: {
                iTime: { value: 0 },
                iResolution: {
                    value: new Color(gl.canvas.width, gl.canvas.height, gl.canvas.width / gl.canvas.height)
                },
                uColor: { value: new Color(...color) },
                uAmplitude: { value: amplitude },
                uDistance: { value: distance },
                uMouse: { value: new Float32Array([0.5, 0.5]) },
                uLineCount: { value: lowPower ? 15 : 40 }
            }
        });
        programRef.current = program;

        const mesh = new Mesh(gl, { geometry, program });

        function resize() {
            if (!container || !rendererRef.current || !programRef.current) return;
            const { clientWidth, clientHeight } = container;
            rendererRef.current.setSize(clientWidth, clientHeight);
            programRef.current.uniforms.iResolution.value.r = clientWidth;
            programRef.current.uniforms.iResolution.value.g = clientHeight;
            programRef.current.uniforms.iResolution.value.b = clientWidth / clientHeight;
        }
        window.addEventListener('resize', resize);
        resize();

        function update(t: number) {
            if (!programRef.current || !rendererRef.current) return;

            if (enableMouseInteraction) {
                const smoothing = 0.05;
                mouseRef.current.current[0] += smoothing * (mouseRef.current.target[0] - mouseRef.current.current[0]);
                mouseRef.current.current[1] += smoothing * (mouseRef.current.target[1] - mouseRef.current.current[1]);
                programRef.current.uniforms.uMouse.value[0] = mouseRef.current.current[0];
                programRef.current.uniforms.uMouse.value[1] = mouseRef.current.current[1];
            } else {
                programRef.current.uniforms.uMouse.value[0] = 0.5;
                programRef.current.uniforms.uMouse.value[1] = 0.5;
            }
            programRef.current.uniforms.iTime.value = t * 0.001;

            rendererRef.current.render({ scene: mesh });
            animationFrameId.current = requestAnimationFrame(update);
        }
        animationFrameId.current = requestAnimationFrame(update);

        return () => {
            if (animationFrameId.current) cancelAnimationFrame(animationFrameId.current);
            window.removeEventListener('resize', resize);
            if (container && gl.canvas && container.contains(gl.canvas)) {
                container.removeChild(gl.canvas);
            }
            gl.getExtension('WEBGL_lose_context')?.loseContext();
        };
    }, []); // Run only once

    // Update uniforms when props change
    useEffect(() => {
        if (!programRef.current) return;
        programRef.current.uniforms.uColor.value.set(...color);
        programRef.current.uniforms.uAmplitude.value = amplitude;
        programRef.current.uniforms.uDistance.value = distance;
        programRef.current.uniforms.uLineCount.value = lowPower ? 15 : 40;
    }, [color, amplitude, distance, lowPower]);

    // Handle mouse events separately
    useEffect(() => {
        if (!containerRef.current || !enableMouseInteraction) return;
        const container = containerRef.current;

        const handleMouseMove = (e: MouseEvent) => {
            const rect = container.getBoundingClientRect();
            const x = (e.clientX - rect.left) / rect.width;
            const y = 1.0 - (e.clientY - rect.top) / rect.height;
            mouseRef.current.target = [x, y];
        };

        const handleMouseLeave = () => {
            mouseRef.current.target = [0.5, 0.5];
        };

        container.addEventListener('mousemove', handleMouseMove);
        container.addEventListener('mouseleave', handleMouseLeave);

        return () => {
            container.removeEventListener('mousemove', handleMouseMove);
            container.removeEventListener('mouseleave', handleMouseLeave);
        };
    }, [enableMouseInteraction]);

    return <div ref={containerRef} className="w-full h-full relative" {...rest} />;
});

export default Threads;
