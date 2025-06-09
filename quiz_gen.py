import random
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords

# Suppress NLTK download logs
try:
    nltk.download('punkt', quiet=True)
    nltk.download('stopwords', quiet=True)
except:
    pass


def generate_questions(summary, num_questions=3):
    print("[+] Generating questions from summary...")
    stop_words = set(stopwords.words('english'))
    questions = []

    sentences = sent_tokenize(summary)
    selected_sentences = random.sample(sentences, min(num_questions, len(sentences)))

    for i, sentence in enumerate(selected_sentences):
        words = word_tokenize(sentence)
        keywords = [word for word in words if word.isalpha() and word.lower() not in stop_words]

        if not keywords:
            continue

        answer = random.choice(keywords)
        question = sentence.replace(answer, "_____")
        questions.append({
            "question": f"Q{i+1}. {question}",
            "answer": answer
        })

    return questions
