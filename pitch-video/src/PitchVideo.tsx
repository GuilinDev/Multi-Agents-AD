import React from "react";
import {
  AbsoluteFill,
  useCurrentFrame,
  useVideoConfig,
  interpolate,
  spring,
  Sequence,
  Audio,
  staticFile,
} from "remotion";

// ─── Slide Components ───────────────────────────────────────────────

const Slide: React.FC<{
  children: React.ReactNode;
  bg?: string;
}> = ({ children, bg = "linear-gradient(135deg, #0f0c29, #302b63, #24243e)" }) => {
  const frame = useCurrentFrame();
  const opacity = interpolate(frame, [0, 15], [0, 1], { extrapolateRight: "clamp" });
  return (
    <AbsoluteFill
      style={{
        background: bg,
        display: "flex",
        flexDirection: "column",
        justifyContent: "center",
        alignItems: "center",
        padding: 80,
        opacity,
      }}
    >
      {children}
    </AbsoluteFill>
  );
};

const Title: React.FC<{ text: string; size?: number; color?: string }> = ({
  text,
  size = 72,
  color = "#ffffff",
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const scale = spring({ frame, fps, config: { damping: 12 } });
  return (
    <div
      style={{
        fontSize: size,
        fontWeight: 800,
        color,
        textAlign: "center",
        transform: `scale(${scale})`,
        fontFamily: "system-ui, -apple-system, sans-serif",
        lineHeight: 1.2,
      }}
    >
      {text}
    </div>
  );
};

const Subtitle: React.FC<{ text: string; delay?: number }> = ({ text, delay = 10 }) => {
  const frame = useCurrentFrame();
  const opacity = interpolate(frame, [delay, delay + 15], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const y = interpolate(frame, [delay, delay + 15], [30, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  return (
    <div
      style={{
        fontSize: 36,
        color: "#b0b0cc",
        textAlign: "center",
        marginTop: 24,
        opacity,
        transform: `translateY(${y}px)`,
        fontFamily: "system-ui, sans-serif",
        maxWidth: 1200,
        lineHeight: 1.5,
      }}
    >
      {text}
    </div>
  );
};

const Stat: React.FC<{
  number: string;
  label: string;
  delay: number;
  color?: string;
}> = ({ number, label, delay, color = "#6C63FF" }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const scale = spring({ frame: Math.max(0, frame - delay), fps, config: { damping: 10 } });
  const opacity = interpolate(frame, [delay, delay + 10], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  return (
    <div
      style={{
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        margin: "0 60px",
        opacity,
        transform: `scale(${scale})`,
      }}
    >
      <div style={{ fontSize: 80, fontWeight: 900, color, fontFamily: "system-ui" }}>
        {number}
      </div>
      <div style={{ fontSize: 24, color: "#aaa", marginTop: 8, fontFamily: "system-ui" }}>
        {label}
      </div>
    </div>
  );
};

const BulletPoint: React.FC<{ text: string; icon: string; delay: number }> = ({
  text,
  icon,
  delay,
}) => {
  const frame = useCurrentFrame();
  const opacity = interpolate(frame, [delay, delay + 10], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const x = interpolate(frame, [delay, delay + 10], [-40, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  return (
    <div
      style={{
        display: "flex",
        alignItems: "center",
        fontSize: 36,
        color: "#e0e0e0",
        marginBottom: 28,
        opacity,
        transform: `translateX(${x}px)`,
        fontFamily: "system-ui",
      }}
    >
      <span style={{ fontSize: 48, marginRight: 24 }}>{icon}</span>
      {text}
    </div>
  );
};

// ─── Architecture Diagram ───────────────────────────────────────────

const ArchBox: React.FC<{
  label: string;
  color: string;
  x: number;
  y: number;
  delay: number;
  icon: string;
}> = ({ label, color, x, y, delay, icon }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const scale = spring({ frame: Math.max(0, frame - delay), fps, config: { damping: 12 } });
  return (
    <div
      style={{
        position: "absolute",
        left: x,
        top: y,
        background: color,
        borderRadius: 16,
        padding: "20px 32px",
        color: "white",
        fontSize: 24,
        fontWeight: 700,
        fontFamily: "system-ui",
        transform: `scale(${scale})`,
        boxShadow: "0 8px 32px rgba(0,0,0,0.3)",
        textAlign: "center",
        minWidth: 200,
      }}
    >
      <div style={{ fontSize: 40, marginBottom: 8 }}>{icon}</div>
      {label}
    </div>
  );
};

const Arrow: React.FC<{ x1: number; y1: number; x2: number; y2: number; delay: number }> = ({
  x1, y1, x2, y2, delay,
}) => {
  const frame = useCurrentFrame();
  const progress = interpolate(frame, [delay, delay + 15], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  return (
    <svg
      style={{ position: "absolute", left: 0, top: 0, width: "100%", height: "100%" }}
    >
      <line
        x1={x1}
        y1={y1}
        x2={x1 + (x2 - x1) * progress}
        y2={y1 + (y2 - y1) * progress}
        stroke="#6C63FF"
        strokeWidth={3}
        strokeDasharray="8,4"
      />
    </svg>
  );
};

// ─── Main Video ─────────────────────────────────────────────────────

export const PitchVideo: React.FC = () => {
  return (
    <AbsoluteFill style={{ backgroundColor: "#0f0c29" }}>
      {/* Background Music */}
      <Audio src={staticFile("bgm.mp3")} volume={0.3} />

      {/* Slide 1: Hook (0-6s) */}
      <Sequence from={0} durationInFrames={180}>
        <Slide bg="linear-gradient(135deg, #0f0c29, #302b63, #24243e)">
          <div style={{ fontSize: 120, marginBottom: 20 }}>🧠</div>
          <Title text="6.9 Million Americans" size={80} />
          <Title text="Live with Alzheimer's" size={64} color="#6C63FF" />
          <Subtitle text="Healthcare AI adoption is at just 1%. We're changing that." delay={20} />
        </Slide>
      </Sequence>

      {/* Slide 2: Problem (6-14s) */}
      <Sequence from={180} durationInFrames={240}>
        <Slide bg="linear-gradient(135deg, #1a1a2e, #16213e)">
          <Title text="The Problem" size={56} color="#FF6B6B" />
          <div style={{ marginTop: 40, maxWidth: 1100 }}>
            <BulletPoint icon="😔" text="Patients feel isolated — AI interactions are cold and impersonal" delay={10} />
            <BulletPoint icon="📋" text="Caregivers lack real-time cognitive insights between clinic visits" delay={25} />
            <BulletPoint icon="🏥" text="Clinicians can't monitor patients 24/7" delay={40} />
            <BulletPoint icon="💸" text="U.S. Alzheimer's care costs $360B/year — and rising" delay={55} />
          </div>
        </Slide>
      </Sequence>

      {/* Slide 3: Solution (14-24s) */}
      <Sequence from={420} durationInFrames={300}>
        <Slide bg="linear-gradient(135deg, #0f0c29, #1a1a3e)">
          <Title text="Multi-Agent AD Companion" size={56} />
          <Subtitle text="A dual-AI system for compassionate cognitive care" delay={10} />
          <div style={{ position: "relative", width: 1200, height: 500, marginTop: 40 }}>
            <ArchBox icon="👤" label="Patient" color="#4A4A8A" x={50} y={200} delay={15} />
            <Arrow x1={280} y1={240} x2={420} y2={160} delay={20} />
            <ArchBox icon="💬" label="Therapy Agent" color="#6C63FF" x={420} y={100} delay={25} />
            <Arrow x1={650} y1={160} x2={780} y2={160} delay={30} />
            <ArchBox icon="🔊" label="Voice + Images" color="#9C27B0" x={780} y={100} delay={35} />
            <Arrow x1={540} y1={180} x2={540} y2={300} delay={40} />
            <ArchBox icon="🧠" label="Monitor Agent" color="#FF6B6B" x={420} y={300} delay={45} />
            <Arrow x1={650} y1={340} x2={780} y2={340} delay={50} />
            <ArchBox icon="📋" label="Caregiver Report" color="#4CAF50" x={780} y={300} delay={55} />
          </div>
        </Slide>
      </Sequence>

      {/* Slide 4: Key Features (24-34s) */}
      <Sequence from={720} durationInFrames={300}>
        <Slide bg="linear-gradient(135deg, #1a1a2e, #0f3460)">
          <Title text="How It Works" size={56} />
          <div style={{ marginTop: 40, maxWidth: 1100 }}>
            <BulletPoint icon="🗣️" text="Reminiscence therapy — warm, personalized conversations" delay={10} />
            <BulletPoint icon="🖼️" text="AI-generated memory scenes — visual stimulation" delay={25} />
            <BulletPoint icon="📊" text="Real-time cognitive monitoring — emotion, memory, engagement" delay={40} />
            <BulletPoint icon="📝" text="Caregiver reports — actionable insights after each session" delay={55} />
            <BulletPoint icon="🔒" text="HIPAA-ready architecture — synthetic data, de-identification pipeline" delay={70} />
          </div>
        </Slide>
      </Sequence>

      {/* Slide 5: Market (34-42s) */}
      <Sequence from={1020} durationInFrames={240}>
        <Slide bg="linear-gradient(135deg, #0f0c29, #302b63)">
          <Title text="Market Opportunity" size={56} />
          <div style={{ display: "flex", marginTop: 60 }}>
            <Stat number="$360B" label="Annual AD Care Cost (US)" delay={10} />
            <Stat number="1%" label="Healthcare AI Adoption" delay={25} color="#FF6B6B" />
            <Stat number="6.9M" label="US AD Patients" delay={40} color="#4CAF50" />
          </div>
          <Subtitle
            text="Healthcare AI SaaS is proven ($250M+ rounds, $100M+ ARR). We go deeper — into cognitive care."
            delay={55}
          />
        </Slide>
      </Sequence>

      {/* Slide 6: Team (42-50s) */}
      <Sequence from={1260} durationInFrames={240}>
        <Slide bg="linear-gradient(135deg, #1a1a2e, #16213e)">
          <Title text="The Team" size={56} />
          <div style={{ display: "flex", gap: 80, marginTop: 50 }}>
            {[
              { icon: "⚡", name: "Guilin Zhang", role: "AI Systems Architect", desc: "Agentic AI · Inference Infra · K8s" },
              { icon: "🔗", name: "Kai", role: "Strategy & Partnerships", desc: "Former Professor · Industry Connections" },
              { icon: "🎓", name: "Dr. Dezhi Wu", role: "Domain & Clinical", desc: "USC Professor · HCI · Health Informatics" },
            ].map((m, i) => {
              const frame = useCurrentFrame();
              const { fps } = useVideoConfig();
              const scale = spring({ frame: Math.max(0, frame - 10 - i * 15), fps, config: { damping: 12 } });
              return (
                <div
                  key={m.name}
                  style={{
                    display: "flex",
                    flexDirection: "column",
                    alignItems: "center",
                    transform: `scale(${scale})`,
                  }}
                >
                  <div style={{ fontSize: 72, marginBottom: 16 }}>{m.icon}</div>
                  <div style={{ fontSize: 32, fontWeight: 700, color: "#fff", fontFamily: "system-ui" }}>
                    {m.name}
                  </div>
                  <div style={{ fontSize: 22, color: "#6C63FF", marginTop: 4, fontFamily: "system-ui" }}>
                    {m.role}
                  </div>
                  <div style={{ fontSize: 18, color: "#888", marginTop: 8, fontFamily: "system-ui" }}>
                    {m.desc}
                  </div>
                </div>
              );
            })}
          </div>
        </Slide>
      </Sequence>

      {/* Slide 7: CTA (50-60s) */}
      <Sequence from={1500} durationInFrames={300}>
        <Slide bg="linear-gradient(135deg, #0f0c29, #302b63, #6C63FF)">
          <div style={{ fontSize: 100, marginBottom: 20 }}>🧠</div>
          <Title text="Multi-Agent AD Companion" size={64} />
          <Subtitle text="Compassionate AI for Cognitive Care" delay={10} />
          <div
            style={{
              marginTop: 50,
              padding: "20px 60px",
              background: "rgba(255,255,255,0.15)",
              borderRadius: 16,
              border: "2px solid rgba(255,255,255,0.3)",
            }}
          >
            <Subtitle text="Try the live demo →  Multi-Agents-AD.gradio.live" delay={20} />
          </div>
          <Subtitle text="Contact: guilin@guilindev.xyz" delay={35} />
        </Slide>
      </Sequence>
    </AbsoluteFill>
  );
};
