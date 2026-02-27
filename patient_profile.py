"""Synthetic patient profiles for demo."""

PATIENTS = {
    "margaret": {
        "name": "Margaret Thompson",
        "age": 78,
        "diagnosis": "Early-stage Alzheimer's Disease (diagnosed 2024)",
        "language": "English",
        "background": """
Margaret was born in Charleston, SC in 1948. She was a high school English teacher 
for 35 years at Wando High School. She married her husband Robert in 1972 — they 
met at a church picnic. Robert passed away in 2019. They have two children: 
David (52, lives in Atlanta) and Susan (48, lives in Columbia, SC).

Margaret loves gardening — especially roses and magnolias. She used to read to her 
students every Friday afternoon, and her favorite book is "To Kill a Mockingbird." 
She has a golden retriever named Biscuit. She enjoys watching old movies, especially 
anything with Audrey Hepburn.

Her favorite memory is the summer of 1985 when the whole family drove to the 
Blue Ridge Mountains and stayed in a cabin for two weeks. David caught his first 
fish and Susan learned to ride a bike there.

Current concerns: She sometimes forgets recent conversations but remembers the past 
vividly. She occasionally misplaces her keys and glasses. She still lives independently 
but her daughter Susan visits twice a week.
""",
        "cognitive_level": "MMSE 22/30 — mild cognitive impairment",
        "preferences": "Prefers morning conversations. Responds well to gentle humor. "
                       "Likes when people ask about her garden and her teaching days.",
        "triggers_to_avoid": "Avoid mentioning Robert's death directly. "
                             "Don't rush her or correct her too abruptly."
    }
}

DEFAULT_PATIENT = "margaret"
