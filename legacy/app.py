"""Gradio UI for Multi-Agent Alzheimer's Demo."""

import os
import json
import time
import gradio as gr
from dotenv import load_dotenv

load_dotenv()

from agents import ConversationState, therapy_respond, monitor_analyze, generate_caregiver_summary
from tts_engine import text_to_speech
from image_gen import maybe_generate_scene
from patient_profile import PATIENTS, DEFAULT_PATIENT
from memory_store import load_memory, save_memory, extract_and_save_memories, format_memory_prompt, save_session_summary
from trend_tracker import save_trend_entry, create_trend_chart, get_alert_history, load_trends

# ---------------------------------------------------------------------------
# Global state (single-user demo)
# ---------------------------------------------------------------------------
state = ConversationState()
patient_memory = load_memory(DEFAULT_PATIENT)


def transcribe_audio(audio_path: str) -> str:
    """Transcribe audio using Groq Whisper."""
    if not audio_path:
        return ""
    from groq import Groq
    client = Groq(api_key=os.getenv("GROQ_API_KEY", ""))
    with open(audio_path, "rb") as f:
        transcription = client.audio.transcriptions.create(
            model="whisper-large-v3",
            file=f,
        )
    return transcription.text


def _render_history(reports, emotion_colors):
    items = []
    for r in reports:
        ec = emotion_colors.get(r.get("emotion", ""), "#ccc")
        turn = r.get("turn", 0)
        emo = r.get("emotion", "?").title()
        mem = r.get("memory_quality", "?").title()
        eng = r.get("engagement", "?").title()
        items.append(
            f"<div style='font-size:12px;padding:4px 8px;border-left:3px solid {ec};"
            f"margin:4px 0;background:#fff;'>"
            f"<b>Turn {turn}</b> — {emo} · {mem} · {eng}</div>"
        )
    return "".join(items)


def format_monitor_html(reports: list) -> str:
    if not reports:
        return "<div style='color:#888; padding:20px;'>Session not started yet. Begin chatting with Margaret to see real-time monitoring.</div>"
    
    latest = reports[-1]
    
    emotion_colors = {
        "happy": "#4CAF50", "nostalgic": "#9C27B0", "calm": "#2196F3",
        "confused": "#FF9800", "anxious": "#f44336", "frustrated": "#f44336",
    }
    emotion_color = emotion_colors.get(latest.get("emotion", ""), "#607D8B")
    
    engagement_bar = {"low": "25%", "medium": "60%", "high": "90%"}
    eng_width = engagement_bar.get(latest.get("engagement", "medium"), "50%")
    
    memory_icons = {"clear": "🟢", "partial": "🟡", "confused": "🟠", "fabricated": "🔴"}
    mem_icon = memory_icons.get(latest.get("memory_quality", ""), "⚪")
    
    risk = latest.get("risk_flags", "")
    risk_html = f"<div style='background:#fff3e0;padding:8px;border-radius:4px;margin:8px 0;'>⚠️ {risk}</div>" if risk else ""
    
    html = f"""
    <div style='font-family:system-ui;max-width:500px;'>
      <div style='background:linear-gradient(135deg,#667eea,#764ba2);color:white;padding:16px;border-radius:12px 12px 0 0;'>
        <h3 style='margin:0;'>🧠 Real-Time Cognitive Monitor</h3>
        <small>Turn {latest.get('turn',0)} · {latest.get('timestamp','')}</small>
      </div>
      <div style='background:#f8f9fa;padding:16px;border-radius:0 0 12px 12px;'>
        <div style='display:flex;gap:12px;margin-bottom:12px;'>
          <div style='flex:1;background:white;padding:12px;border-radius:8px;box-shadow:0 1px 3px rgba(0,0,0,0.1);'>
            <div style='font-size:12px;color:#666;'>Emotion</div>
            <div style='font-size:18px;font-weight:600;color:{emotion_color};'>{latest.get('emotion','—').title()}</div>
          </div>
          <div style='flex:1;background:white;padding:12px;border-radius:8px;box-shadow:0 1px 3px rgba(0,0,0,0.1);'>
            <div style='font-size:12px;color:#666;'>Memory Quality</div>
            <div style='font-size:18px;font-weight:600;'>{mem_icon} {latest.get('memory_quality','—').title()}</div>
          </div>
        </div>
        <div style='background:white;padding:12px;border-radius:8px;margin-bottom:12px;box-shadow:0 1px 3px rgba(0,0,0,0.1);'>
          <div style='font-size:12px;color:#666;margin-bottom:4px;'>Engagement</div>
          <div style='background:#e0e0e0;border-radius:10px;height:20px;'>
            <div style='background:linear-gradient(90deg,#667eea,#764ba2);height:100%;border-radius:10px;width:{eng_width};transition:width 0.5s;'></div>
          </div>
          <div style='font-size:11px;color:#888;margin-top:2px;'>{latest.get('engagement','medium').title()}</div>
        </div>
        <div style='background:white;padding:12px;border-radius:8px;margin-bottom:8px;box-shadow:0 1px 3px rgba(0,0,0,0.1);'>
          <div style='font-size:12px;color:#666;'>Cognitive Observations</div>
          <div style='font-size:13px;margin-top:4px;'>{latest.get('cognitive_signs','—')}</div>
        </div>
        {risk_html}
        <div style='background:#e8f5e9;padding:10px;border-radius:8px;'>
          <div style='font-size:12px;color:#2e7d32;font-weight:600;'>💡 Recommendation</div>
          <div style='font-size:13px;color:#1b5e20;margin-top:4px;'>{latest.get('recommendation','—')}</div>
        </div>
      </div>
      <div style='margin-top:12px;'>
        <details>
          <summary style='cursor:pointer;font-size:13px;color:#666;'>📊 Session History ({len(reports)} turns)</summary>
          <div style='max-height:200px;overflow-y:auto;margin-top:8px;'>
            {_render_history(reports, emotion_colors)}
          </div>
        </details>
      </div>
    </div>
    """
    return html


def chat_respond(message: str, history: list):
    """Handle chat input, run both agents, return response + audio + monitor + image + trend."""
    global state, patient_memory
    
    # Inject memory context
    memory_context = format_memory_prompt(patient_memory)
    response = therapy_respond(state, message, memory_context)
    
    # Monitor agent analyzes
    monitor_report = monitor_analyze(state, message, response)
    
    # Save trend data
    save_trend_entry(state.patient_id, monitor_report)
    
    # Extract memories every 5 turns
    if state.turn_count % 5 == 0 and state.turn_count > 0:
        patient_memory = extract_and_save_memories(state.patient_id, state.therapy_history, patient_memory)
    
    # Generate TTS
    try:
        audio_path = text_to_speech(response)
    except Exception:
        audio_path = None
    
    # Generate scene image
    try:
        scene_image = maybe_generate_scene(message, response)
    except Exception:
        scene_image = None
    
    # Format outputs
    monitor_html = format_monitor_html(state.monitor_reports)
    trend_fig = create_trend_chart(state.patient_id)
    
    return response, audio_path, monitor_html, scene_image, trend_fig


def get_summary():
    global state
    if state.turn_count == 0:
        return "No conversation data yet. Chat with Margaret first!"
    summary = generate_caregiver_summary(state)
    return summary


def reset_session():
    global state, patient_memory
    # Save session summary before reset
    if state.turn_count > 0:
        try:
            summary = generate_caregiver_summary(state)
            save_session_summary(state.patient_id, patient_memory, state.turn_count, [], summary)
            patient_memory = extract_and_save_memories(state.patient_id, state.therapy_history, patient_memory)
        except Exception:
            pass
    state = ConversationState()
    return [], None, format_monitor_html([]), "", None, None


# ---------------------------------------------------------------------------
# Caregiver Dashboard helpers
# ---------------------------------------------------------------------------

def refresh_caregiver_dashboard():
    """Refresh all caregiver dashboard components."""
    patient = PATIENTS[DEFAULT_PATIENT]
    memory = load_memory(DEFAULT_PATIENT)
    trends = load_trends(DEFAULT_PATIENT)
    alerts = get_alert_history(DEFAULT_PATIENT)
    
    # Patient overview
    overview_html = f"""
    <div style='font-family:system-ui;background:linear-gradient(135deg,#667eea,#764ba2);color:white;padding:20px;border-radius:12px;margin-bottom:16px;'>
        <h2 style='margin:0;'>👤 {patient['name']}</h2>
        <p style='margin:8px 0 0;opacity:0.9;'>Age {patient['age']} · {patient['diagnosis']}</p>
        <p style='margin:4px 0 0;opacity:0.9;'>Cognitive Level: {patient['cognitive_level']}</p>
    </div>
    """
    
    # Latest session summary
    if memory["session_history"]:
        last = memory["session_history"][-1]
        summary_text = f"**{last['date']}** ({last['turns']} turns)\n\n{last['summary']}"
    else:
        summary_text = "No sessions recorded yet."
    
    # Trend chart (bigger)
    trend_fig = create_trend_chart(DEFAULT_PATIENT, figsize=(12, 5))
    
    # Alert history
    if alerts:
        alert_items = []
        for a in reversed(alerts[-20:]):
            alert_items.append(f"<div style='padding:8px;border-left:3px solid #f44336;margin:4px 0;background:#fff3e0;border-radius:4px;'>"
                             f"<b>{a['date']}</b> (Turn {a['turn']}) — {a['emotion'].title()}<br/>"
                             f"⚠️ {a['flag']}</div>")
        alerts_html = "".join(alert_items)
    else:
        alerts_html = "<div style='color:#888;padding:20px;'>No alerts recorded.</div>"
    
    # Session log
    if memory["session_history"]:
        log_items = []
        for s in reversed(memory["session_history"][-20:]):
            topics = ", ".join(s.get("key_topics", [])) or "—"
            log_items.append(f"<div style='padding:10px;background:white;border-radius:8px;margin:6px 0;box-shadow:0 1px 3px rgba(0,0,0,0.1);'>"
                           f"<b>{s['date']}</b> · {s['turns']} turns<br/>"
                           f"<span style='font-size:13px;color:#555;'>{s['summary'][:150]}...</span></div>")
        session_log_html = "".join(log_items)
    else:
        session_log_html = "<div style='color:#888;padding:20px;'>No sessions recorded yet.</div>"
    
    return overview_html, summary_text, trend_fig, alerts_html, session_log_html


def build_ui():
    patient = PATIENTS[DEFAULT_PATIENT]
    
    with gr.Blocks(title="🧠 Multi-Agent AD Companion") as demo:
        
        with gr.Tabs():
            # ==================== TAB 1: Therapy Session ====================
            with gr.Tab("💬 Therapy Session"):
                gr.HTML("""
                <div class='main-header'>
                    <h1>🧠 Multi-Agent Alzheimer's Companion</h1>
                    <p style='color:#666;'>Reminiscence Therapy Demo · Powered by Dual AI Agents</p>
                </div>
                """)
                
                gr.HTML(f"""
                <div class='patient-card'>
                    <h3>👤 Patient: {patient['name']} (Age {patient['age']})</h3>
                    <p><b>Diagnosis:</b> {patient['diagnosis']} · <b>Cognitive Level:</b> {patient['cognitive_level']}</p>
                    <p><i>You are role-playing as Margaret in a therapy session. Type as if you are Margaret speaking to your companion.</i></p>
                </div>
                """)
                
                with gr.Row():
                    with gr.Column(scale=3):
                        chatbot = gr.Chatbot(label="💬 Therapy Session", height=450)
                        
                        with gr.Row():
                            msg_input = gr.Textbox(
                                placeholder="Speak as Margaret... (e.g., 'I was just thinking about my garden today.')",
                                label="", scale=4, container=False,
                            )
                            audio_input = gr.Audio(
                                sources=["microphone"], type="filepath",
                                label="🎤 Voice", scale=1,
                            )
                            send_btn = gr.Button("Send 💬", variant="primary", scale=1)
                        
                        with gr.Row():
                            audio_output = gr.Audio(label="🔊 Companion Voice", autoplay=True)
                            scene_output = gr.Image(label="🖼️ Memory Scene", height=256)
                        
                        with gr.Row():
                            summary_btn = gr.Button("📋 Generate Caregiver Summary", variant="secondary")
                            reset_btn = gr.Button("🔄 New Session", variant="stop")
                    
                    with gr.Column(scale=2):
                        monitor_display = gr.HTML(value=format_monitor_html([]), label="Monitor")
                        trend_plot = gr.Plot(label="📈 Cognitive Trends")
                        summary_output = gr.Textbox(
                            label="📋 Caregiver Summary Report", lines=12, interactive=False,
                        )
                
                # --- Event handlers ---
                def on_send(message, audio, history):
                    # Transcribe audio if provided
                    if audio and not message.strip():
                        try:
                            message = transcribe_audio(audio)
                        except Exception as e:
                            message = f"[Audio transcription failed: {e}]"
                    
                    if not message or not message.strip():
                        return history, "", None, None, format_monitor_html(state.monitor_reports), None, None
                    
                    response, audio_out, monitor_html, scene_img, trend_fig = chat_respond(message, history)
                    history = history + [
                        {"role": "user", "content": message},
                        {"role": "assistant", "content": response}
                    ]
                    return history, "", None, audio_out, monitor_html, scene_img, trend_fig
                
                send_btn.click(
                    on_send,
                    inputs=[msg_input, audio_input, chatbot],
                    outputs=[chatbot, msg_input, audio_input, audio_output, monitor_display, scene_output, trend_plot],
                )
                msg_input.submit(
                    on_send,
                    inputs=[msg_input, audio_input, chatbot],
                    outputs=[chatbot, msg_input, audio_input, audio_output, monitor_display, scene_output, trend_plot],
                )
                
                summary_btn.click(get_summary, outputs=[summary_output])
                reset_btn.click(reset_session, outputs=[chatbot, audio_output, monitor_display, summary_output, scene_output, trend_plot])
            
            # ==================== TAB 2: Caregiver Dashboard ====================
            with gr.Tab("👨‍⚕️ Caregiver Dashboard"):
                gr.HTML("<h1 style='text-align:center;'>👨‍⚕️ Caregiver Dashboard</h1>")
                
                refresh_btn = gr.Button("🔄 Refresh Dashboard", variant="primary")
                
                cg_overview = gr.HTML(label="Patient Overview")
                
                with gr.Row():
                    with gr.Column(scale=2):
                        cg_summary = gr.Markdown(label="📋 Latest Session Summary")
                    with gr.Column(scale=1):
                        cg_alerts = gr.HTML(label="⚠️ Alert History")
                
                cg_trend = gr.Plot(label="📈 Cognitive Trends Over Time")
                
                gr.HTML("<h3>📝 Session Log</h3>")
                cg_sessions = gr.HTML(label="Session Log")
                
                refresh_btn.click(
                    refresh_caregiver_dashboard,
                    outputs=[cg_overview, cg_summary, cg_trend, cg_alerts, cg_sessions],
                )
                
                # Auto-load on tab visit
                demo.load(
                    refresh_caregiver_dashboard,
                    outputs=[cg_overview, cg_summary, cg_trend, cg_alerts, cg_sessions],
                )
    
    return demo


if __name__ == "__main__":
    demo = build_ui()
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=True,
        show_error=True,
    )
