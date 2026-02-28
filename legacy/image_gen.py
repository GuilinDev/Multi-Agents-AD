"""Image generation for reminiscence therapy scenes."""

import os
import hashlib
from huggingface_hub import InferenceClient
from groq import Groq

IMAGE_DIR = os.path.join(os.path.dirname(__file__), "image_cache")
os.makedirs(IMAGE_DIR, exist_ok=True)

hf_client = InferenceClient()

def extract_scene_prompt(therapy_response: str, patient_message: str) -> str | None:
    """Use LLM to decide if an image should be generated and extract a scene prompt."""
    client = Groq(api_key=os.getenv("GROQ_API_KEY", ""))
    
    system = """You analyze therapy conversations with Alzheimer's patients. 
When the conversation mentions a vivid scene, memory, place, or object that could 
be visualized to aid reminiscence therapy, output a short image generation prompt.

Rules:
- Only generate a prompt if there's a clear visual scene (garden, family trip, classroom, etc.)
- Make it warm, gentle, nostalgic — watercolor or soft photography style
- Include relevant details from the conversation
- If no clear visual scene, output exactly: NONE
- Keep prompt under 50 words
- Never include people's faces or identifiable persons
- Focus on places, objects, nature, settings

Output ONLY the prompt or NONE. Nothing else."""

    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": f"Patient said: {patient_message}\nCompanion replied: {therapy_response}"}
    ]
    
    result = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=messages,
        temperature=0.3,
        max_tokens=100,
    )
    
    prompt = result.choices[0].message.content.strip()
    if prompt.upper() == "NONE" or len(prompt) < 10:
        return None
    return prompt


def generate_image(prompt: str) -> str | None:
    """Generate an image from prompt, return file path."""
    h = hashlib.md5(prompt.encode()).hexdigest()[:12]
    path = os.path.join(IMAGE_DIR, f"{h}.png")
    
    if os.path.exists(path):
        return path
    
    try:
        image = hf_client.text_to_image(
            prompt,
            model="black-forest-labs/FLUX.1-schnell",
        )
        image.save(path)
        return path
    except Exception as e:
        print(f"Image generation failed: {e}")
        return None


def maybe_generate_scene(patient_msg: str, therapy_response: str) -> str | None:
    """Full pipeline: extract scene → generate image if appropriate."""
    try:
        prompt = extract_scene_prompt(therapy_response, patient_msg)
        if prompt is None:
            return None
        return generate_image(prompt)
    except Exception as e:
        print(f"Scene generation error: {e}")
        return None
