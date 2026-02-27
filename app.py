"""Gradio UI for Multi-Agent Alzheimer's Demo."""

import os
import json
import gradio as gr
from dotenv import load_dotenv

load_dotenv()

from agents import ConversationState, therapy_respond, monitor_analyze, generate_caregiver_summary
from tts_engine import text_to_speech
from image_gen import maybe_generate_scene
from patient_profile import PATIENTS, DEFAULT_PATIENT

# ---------------------------------------------------------------------------
# Global state (single-user demo)
# ---------------------------------------------------------------------------
state = ConversationState()


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
    """Format monitor reports as HTML dashboard."""
    if not reports:
        return "<div style='color:#888; padding:20px;'>Session not started yet. Begin chatting with Margaret to see real-time monitoring.</div>"
    
    # Latest report card
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
    """Handle chat input, run both agents, return response + audio + monitor + image."""
    global state
    
    # Therapy agent responds
    response = therapy_respond(state, message)
    
    # Monitor agent analyzes
    monitor_report = monitor_analyze(state, message, response)
    
    # Generate TTS
    try:
        audio_path = text_to_speech(response)
    except Exception:
        audio_path = None
    
    # Generate scene image (if conversation mentions a visual scene)
    try:
        scene_image = maybe_generate_scene(message, response)
    except Exception:
        scene_image = None
    
    # Format monitor dashboard
    monitor_html = format_monitor_html(state.monitor_reports)
    
    return response, audio_path, monitor_html, scene_image


def get_summary():
    """Generate caregiver summary."""
    global state
    if state.turn_count == 0:
        return "No conversation data yet. Chat with Margaret first!"
    summary = generate_caregiver_summary(state)
    return summary


def reset_session():
    """Reset conversation."""
    global state
    state = ConversationState()
    return [], None, format_monitor_html([]), "", None


def build_ui():
    patient = PATIENTS[DEFAULT_PATIENT]
    
    with gr.Blocks(
        title="🧠 Multi-Agent AD Companion",
    ) as demo:
        gr.HTML("""
        <div class='main-header'>
            <h1>🧠 Multi-Agent Alzheimer's Companion</h1>
            <p style='color:#666;'>Reminiscence Therapy Demo · Powered by Dual AI Agents</p>
        </div>
        """)
        
        # Patient card
        gr.HTML(f"""
        <div class='patient-card'>
            <h3>👤 Patient: {patient['name']} (Age {patient['age']})</h3>
            <p><b>Diagnosis:</b> {patient['diagnosis']} · <b>Cognitive Level:</b> {patient['cognitive_level']}</p>
            <p><i>You are role-playing as Margaret in a therapy session. Type as if you are Margaret speaking to your companion.</i></p>
        </div>
        """)
        
        with gr.Row():
            # Left: Chat
            with gr.Column(scale=3):
                chatbot = gr.Chatbot(
                    label="💬 Therapy Session",
                    height=450,
                )
                
                with gr.Row():
                    msg_input = gr.Textbox(
                        placeholder="Speak as Margaret... (e.g., 'I was just thinking about my garden today.')",
                        label="",
                        scale=5,
                        container=False,
                    )
                    send_btn = gr.Button("Send 💬", variant="primary", scale=1)
                
                with gr.Row():
                    audio_output = gr.Audio(label="🔊 Companion Voice", autoplay=True, visible=True)
                    scene_output = gr.Image(label="🖼️ Memory Scene", visible=True, height=256)
                
                with gr.Row():
                    summary_btn = gr.Button("📋 Generate Caregiver Summary", variant="secondary")
                    reset_btn = gr.Button("🔄 New Session", variant="stop")
            
            # Right: Monitor Dashboard
            with gr.Column(scale=2):
                monitor_display = gr.HTML(
                    value=format_monitor_html([]),
                    label="Monitor"
                )
                
                summary_output = gr.Textbox(
                    label="📋 Caregiver Summary Report",
                    lines=12,
                    visible=True,
                    interactive=False,
                )
        
        # --- Event handlers ---
        def on_send(message, history):
            if not message.strip():
                return history, "", None, format_monitor_html(state.monitor_reports), None
            
            response, audio, monitor_html, scene_img = chat_respond(message, history)
            history = history + [
                {"role": "user", "content": message},
                {"role": "assistant", "content": response}
            ]
            return history, "", audio, monitor_html, scene_img
        
        send_btn.click(
            on_send,
            inputs=[msg_input, chatbot],
            outputs=[chatbot, msg_input, audio_output, monitor_display, scene_output],
        )
        msg_input.submit(
            on_send,
            inputs=[msg_input, chatbot],
            outputs=[chatbot, msg_input, audio_output, monitor_display, scene_output],
        )
        
        summary_btn.click(get_summary, outputs=[summary_output])
        reset_btn.click(reset_session, outputs=[chatbot, audio_output, monitor_display, summary_output, scene_output])
    
    return demo


if __name__ == "__main__":
    demo = build_ui()
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=True,
        show_error=True,
    )
