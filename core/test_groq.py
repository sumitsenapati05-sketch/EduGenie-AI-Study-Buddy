from summarize import summarize_text

result = summarize_text(
    text="A database is an organised collection of data. SQL is used to query it. Normalization reduces redundancy.",
    min_length=30,
    max_length=80,
    config={
        "mode": "groq",
        "api_key": "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"  
    },
)

print("✅ SUMMARY:", result["summary"])
print("✅ KEYWORDS:", result["keywords"])
print("✅ FLASHCARDS:", result["flashcards"][0])