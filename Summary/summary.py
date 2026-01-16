import torch
from transformers import pipeline

# Load TinyLlama chat model
pipe = pipeline(
    "text-generation",
    model="TinyLlama/TinyLlama-1.1B-Chat-v1.0",
    torch_dtype=torch.bfloat16,
    device_map="auto"
)

# Define the full SCoTD-style teacher prompt template
def make_SCoTD_prompt(new_transcript):
    prompt = f"""
            Q (input): Summarise this ICU handover into Identify–Situation–Background–Assessment–Recommendation format.

            Transcript:
            Bed eight, Michael I Wu. Forty-eight years under Dr Hanlen. He came in with headache and vertigo. He's got a history of headache, tinnitus, Bell's Palsy to the left side of his face. That's where his headache has been for the last three years. He's also got photophobia. His GCS is 15 pupils equal and reactive. He's just came back from a brain MRI in Woden. He's ambulant and self-caring but he's a little bit unsteady at times. OBS are stable. He is for carotid doppler, he was supposed to have this morning at 950 but that pushed it back to 1050. Hmmm. 1030, sorry. Then the team were here and they said it's cutting it too close to his MRI so he needs another carotid doppler appointment.

            Teacher Chain-of-Thought:
            1) Identify patient identity first. 
            2) Identify presenting problem. 
            3) Extract past relevant neurological history. 
            4) Extract objective assessment parameters (GCS, pupils, OBS, mobility). 
            5) Extract any emerging information (MRI) and plan (carotid doppler rebooking). 
            6) Map these into the Identify–Situation–Background–Assessment–Recommendation template.

            Teacher Output Target:
            Identify: Bed 8, Michael I Wu, 48, under Dr Hanlen.
            Situation: Presented with headache and vertigo.
            Background: History of headaches, tinnitus, Bell’s Palsy, photophobia.
            Assessment: GCS 15, pupils equal/reactive, OBS stable, ambulant but intermittently unsteady.
            Recommendation: Requires new carotid doppler appointment; continue monitoring.

            ---

            Q (input): Summarise this ICU handover into Identify–Situation–Background–Assessment–Recommendation format.

            Transcript:
            {new_transcript}

            Student Output:
            """
    return prompt.strip()


def Summarize(transcript):
    prompt = make_SCoTD_prompt(transcript)
    outputs = pipe(prompt, max_new_tokens=256, do_sample=True, temperature=0.94, top_k=50, top_p=0.95)
    return outputs[0]["generated_text"].split("Student Output:")[-1].strip()

