import torch
from transformers import pipeline

pipe = pipeline("text-generation", model="TinyLlama/TinyLlama-1.1B-Chat-v1.0", torch_dtype=torch.bfloat16, device_map="auto")

def Summarize(message):
    messages = [
        {
            "role": "system",
            "content": (
                "You are a medical expert who summarizes clinical handovers "
                "strictly in the ISBAR format. "
                "You must output **all five sections** exactly in this order and format:\n\n"
                "Identify: <brief identification of patient and role of speaker, or 'Insufficient information'>\n"
                "Situation: <current problem or reason for handover, or 'Insufficient information'>\n"
                "Background: <relevant history, or 'Insufficient information'>\n"
                "Assessment: <key findings, current status, or 'Insufficient information'>\n"
                "Recommendation: <next steps or plan, or 'Insufficient information'>\n\n"
                "If any information is missing or unclear, explicitly write 'Insufficient information'. "
                "Keep your language concise, factual, and clinical."
            )},
        {"role": "user", "content": message},
    ]
    prompt = pipe.tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    outputs = pipe(prompt, max_new_tokens=256, do_sample=True, temperature=0.7, top_k=50, top_p=0.95)
        
    return(outputs.split("<|assistant|>")[-1][0]["generated_text"])

print(Summarize("Vera Abbott,93, bed four, under Dr Liu came in with chest pain with a history of stroke and previous chest pains,asthma,cataract and glaucoma.almost blind and needs assistance.had 3 nitros with no effect.still under monitoring."))