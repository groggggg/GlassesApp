import torch
from transformers import pipeline

pipe = pipeline("text-generation", model="TinyLlama/TinyLlama-1.1B-Chat-v1.0", torch_dtype=torch.bfloat16, device_map="auto")

def Summarize(message):
    messages = [
        {
            "role": "system",
            "content": "You are a medical expert who summarizes a clinical handover transcription in the ISBAR format",
        },
        {"role": "user", "content": message},
    ]
    prompt = pipe.tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    outputs = pipe(prompt, max_new_tokens=256, do_sample=True, temperature=0.7, top_k=50, top_p=0.95)
    print(outputs[0]["generated_text"])
    return(outputs[0]["generated_text"])


