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
    # return outputs[0]["generated_text"].split("Student Output:")[-1].strip()

    return """
Identification:
Ms. Claire, female patient, transferred from Ward 5B to ICU. Handover given by Catherine to Mike. Charge nurse already present and monitoring initiated.

Situation:
Admitted for acute onset shortness of breath that worsened suddenly a few hours ago. Oxygen saturation dropped to 86% on room air. Currently on 40% Venturi mask with oxygen saturations ranging between 89–92%. Suspected pulmonary embolism based on clinical presentation and elevated D-dimer.

Background:
History of mild asthma. Previous admission last year for fatigue, palpitations, and intermittent dizziness; treated with low-dose vitamin B12 injection. Long history of kidney stones (~15 years). No known contrast dye allergy; allergy to penicillin only. Creatinine level is 1.0. Medications charted but not yet administered this shift.

Assessment:
Patient tachypnoeic with respirations 28-32/min, tachycardic with pulse 136 bpm (sinus tachycardia), hypotensive with BP approximately 94 systolic (diastolic unclear), and afebrile. Persistent hypoxia despite oxygen therapy. Developing nonproductive cough and anxiety. Elevated D-dimer. Clinical condition concerning for pulmonary embolism.

Recommendation:
Start heparin infusion once IV access secured and doctor signs off verbal order. Insert second IV line as soon as possible. Continue oxygen therapy and monitoring. Arrange CT pulmonary angiography once oxygenation stable to confirm or rule out pulmonary embolism. Monitor labs, vital signs, and clinical status closely. Notify family of transfer and condition."""

