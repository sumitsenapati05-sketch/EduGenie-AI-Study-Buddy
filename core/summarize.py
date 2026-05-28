from __future__ import annotations

import json
import re
import time
import urllib.error
import urllib.request
from typing import Callable, Dict, List, Optional

# ---------- type alias ----------
Progress = Optional[Callable[[str, int, int], None]]


# ============================================================
#  GROQ CONFIG
# ============================================================
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

# ✅ Best free-tier model for structured educational output (JSON flashcards/quiz)
# llama-3.1-8b-instant  → faster, better instruction-following than llama3-8b-8192
# Fallback: llama3-8b-8192 (original) also works, just slightly slower at JSON
GROQ_MODEL = "llama-3.1-8b-instant"

_RETRY_DELAYS = (1, 3, 7)   # seconds between attempts (3 total tries)


# ============================================================
#  UTILITIES
# ============================================================

def _chunk_text(text: str, max_words: int = 600) -> List[str]:
    sentences = re.split(r"(?<=[.!?])\s+", text.strip())
    chunks: List[str] = []
    current_chunk: List[str] = []
    current_words = 0
    for sentence in sentences:
        word_count = len(sentence.split())
        if current_chunk and current_words + word_count > max_words:
            chunks.append(" ".join(current_chunk))
            current_chunk = [sentence]
            current_words = word_count
        else:
            current_chunk.append(sentence)
            current_words += word_count
    if current_chunk:
        chunks.append(" ".join(current_chunk))
    return chunks if chunks else [text.strip()]


def _count_words(text: str) -> int:
    return len(text.split())


def _within_limits(text: str) -> tuple:
    words = _count_words(text)
    chars = len(text)
    if words > 50_000 or chars > 500_000:
        return False, "Uploaded text too large (max 50 000 words / 500 000 chars)."
    return True, ""


def get_groq_api_key_from_streamlit() -> str:
    """
    Safe helper to pull the Groq key from Streamlit secrets.
    Usage in your app:
        from summarize import get_groq_api_key_from_streamlit
        api_key = get_groq_api_key_from_streamlit()

    Add to .streamlit/secrets.toml:
        GROQ_API_KEY = ""
    """
    try:
        import streamlit as st          # only imported if Streamlit is running
        return st.secrets.get("GROQ_API_KEY", "").strip()
    except Exception:
        return ""


# ============================================================
#  EXPANDED DEFINITIONS  (offline fallback flashcard answers)
# ============================================================

DEFINITIONS: Dict[str, str] = {
    # CS / DBMS
    "DBMS": "A Database Management System (DBMS) is software used to store, retrieve, and manage data in a structured and efficient manner.",
    "SQL": "SQL (Structured Query Language) is a standard language for interacting with relational databases for querying, updating, and managing data.",
    "Normalization": "Normalization organises a database to reduce redundancy and improve data integrity by dividing large tables into smaller ones.",
    "Transaction": "A transaction is a sequence of database operations treated as a single logical unit (ACID properties).",
    "Indexing": "Indexing creates a data structure to speed up record retrieval without scanning every row.",
    "Database": "A database is an organised collection of structured data stored electronically for efficient retrieval and management.",
    "Primary": "A Primary Key uniquely identifies each row in a table and cannot contain NULL values.",
    "Foreign": "A Foreign Key refers to the Primary Key of another table, establishing a relationship between the two tables.",
    "Deadlock": "A deadlock occurs when two or more transactions wait indefinitely for each other to release locks.",
    "Concurrency": "Concurrency control manages simultaneous database access to ensure consistency and prevent conflicts.",
    # OOP / Programming
    "Inheritance": "Inheritance is an OOP concept where a child class acquires properties and behaviours from a parent class.",
    "Encapsulation": "Encapsulation bundles data and methods within a class, hiding internal details from outside.",
    "Polymorphism": "Polymorphism lets objects of different classes be treated as a common superclass type.",
    "Algorithm": "An algorithm is a step-by-step procedure for solving a problem in a finite number of steps.",
    "Recursion": "Recursion is a technique where a function calls itself to solve smaller instances of the same problem.",
    "Pointer": "A pointer stores the memory address of another variable, commonly used in C/C++.",
    # Data Structures
    "Stack": "A stack follows LIFO (Last-In-First-Out); elements are added and removed from the top.",
    "Queue": "A queue follows FIFO (First-In-First-Out); elements are added at the rear and removed from the front.",
    "Array": "An array stores elements of the same type in contiguous memory locations, each identified by an index.",
    "Linked": "A linked list stores nodes non-contiguously; each node holds data and a pointer to the next node.",
    "Binary": "A binary tree is hierarchical; each node has at most two children (left and right).",
    "Hashing": "Hashing maps data to a fixed-size value using a hash function, enabling fast lookup.",
    # OS
    "Process": "A process is an instance of a program in execution, with its own memory and resources.",
    "Thread": "A thread is the smallest CPU execution unit within a process, enabling concurrency.",
    "Memory": "Memory management allocates and deallocates memory to processes to prevent conflicts.",
    "Paging": "Paging eliminates fragmentation by dividing memory into fixed-size pages mapped to physical frames.",
    "Cache": "Cache is fast memory that temporarily holds frequently accessed data to speed up processing.",
    "Semaphore": "A semaphore is a synchronisation tool controlling access to shared resources among concurrent processes.",
    "Scheduling": "Scheduling decides which process gets CPU time and in what order to maximise efficiency.",
    "Interrupt": "An interrupt signals the CPU about an event needing immediate attention, pausing current execution.",
    "Virtual": "Virtual memory uses disk space to compensate for physical memory shortages.",
    # Networking
    "Protocol": "A protocol is a set of rules defining how data is transmitted and received across a network.",
    "Encryption": "Encryption converts plaintext into ciphertext to protect it from unauthorised access.",
    "Firewall": "A firewall monitors and controls network traffic based on predefined security rules.",
    "Routing": "Routing selects the optimal path for data packets from source to destination.",
    "Bandwidth": "Bandwidth is the maximum data-transfer rate across a network path, measured in bps.",
    "Latency": "Latency is the time delay between a user action and the server/network response.",
    "Checksum": "A checksum detects errors in data during transmission or storage.",
    # AI / ML
    "Artificial": "Artificial Intelligence (AI) simulates human intelligence in machines to think, learn, and solve problems.",
    "Machine": "Machine Learning is a subset of AI that enables systems to learn from experience without explicit programming.",
    "Neural": "A neural network processes information through interconnected layers of nodes, modelled on the human brain.",
    "Cloud": "Cloud computing delivers computing services (servers, storage, databases) over the internet on demand.",
    # Misc
    "Compiler": "A compiler translates high-level source code into machine code a computer can execute.",
    "Operating": "An operating system manages hardware resources and provides services for programs.",
    "Object": "OOP (Object-Oriented Programming) models real-world entities as objects with data (attributes) and code (methods).",
    "Function": "A function is a reusable block of code designed to perform a specific task.",
    "Variable": "A variable is a named storage location holding a value that can change during execution.",
    "Exception": "Exception handling manages runtime errors gracefully using try-catch blocks.",
    "Interface": "An interface defines a contract of methods a class must implement, enabling abstraction.",
    "Abstraction": "Abstraction hides complex implementation details and exposes only essential features.",
    "Relational": "A relational database organises data into tables with rows and columns linked by relationships.",
    "Constraint": "A constraint enforces data-integrity rules on columns (NOT NULL, UNIQUE, CHECK, etc.).",
    "Trigger": "A trigger is a stored procedure that auto-executes in response to specific table events.",
    "View": "A database view is a virtual table built from a SELECT query for simplified or controlled access.",
    "Stored": "A stored procedure is a precompiled set of SQL statements in a database, callable with parameters.",
    "Join": "A JOIN combines rows from two or more tables on a related column to produce combined results.",
    "Aggregate": "Aggregate functions (SUM, COUNT, AVG, MAX, MIN) perform calculations on sets of values.",
    "Subquery": "A subquery is a query nested inside another SQL query used to supply data for the outer query's condition.",
    # Physics
    "Newton": "Newton's laws describe the relationship between a body and the forces acting upon it, forming the foundation of classical mechanics.",
    "Thermodynamics": "Thermodynamics studies heat, work, temperature, and energy transfer between systems.",
    "Electromagnetism": "Electromagnetism describes the interaction between electric charges and magnetic fields.",
    "Quantum": "Quantum mechanics describes the behaviour of matter and energy at atomic and subatomic scales.",
    "Gravity": "Gravity is the force of attraction between masses; on Earth it gives objects weight.",
    "Momentum": "Momentum is the product of an object's mass and velocity, a conserved quantity in isolated systems.",
    "Energy": "Energy is the capacity to do work; it exists in many forms including kinetic, potential, thermal, and chemical.",
    "Wave": "A wave is a disturbance that transfers energy through matter or space without bulk movement of matter.",
    "Optics": "Optics is the branch of physics studying the behaviour and properties of light and its interactions with matter.",
    "Relativity": "Einstein's theory of relativity describes how space, time, and gravity are linked, especially at high speeds.",
    # Chemistry
    "Atom": "An atom is the smallest unit of a chemical element that retains its chemical properties.",
    "Molecule": "A molecule is a group of atoms bonded together, representing the smallest unit of a chemical compound.",
    "Reaction": "A chemical reaction transforms reactants into products through the breaking and forming of chemical bonds.",
    "Periodic": "The periodic table organises all known elements by atomic number and shared chemical properties.",
    "Oxidation": "Oxidation is a loss of electrons in a chemical reaction; it always occurs alongside reduction (redox).",
    "Acid": "An acid is a substance that donates protons (H+) or accepts electron pairs in a chemical reaction.",
    "Base": "A base is a substance that accepts protons or donates electron pairs; it reacts with acids to form salts.",
    "Equilibrium": "Chemical equilibrium is the state where forward and reverse reaction rates are equal, keeping concentrations constant.",
    "Catalyst": "A catalyst speeds up a chemical reaction without being consumed or permanently altered.",
    "Polymer": "A polymer is a large molecule made of repeating structural units (monomers) bonded together.",
    # History
    "Revolution": "A revolution is a fundamental and rapid change in political power, societal structure, or dominant ideas.",
    "Empire": "An empire is a large political unit in which one state controls and dominates other states or peoples.",
    "Democracy": "Democracy is a system of government where power is vested in the people, exercised directly or through elected representatives.",
    "Colonialism": "Colonialism is the practice of one nation acquiring political control over another territory and its people.",
    "Renaissance": "The Renaissance (14th-17th century) was a cultural rebirth in Europe emphasising art, science, and humanism.",
    "Industrial": "The Industrial Revolution (18th-19th century) transformed manufacturing through mechanisation and factory production.",
    "World": "World Wars I and II were global conflicts (1914-18, 1939-45) that reshaped international borders and political orders.",
    "Nationalism": "Nationalism is an ideology promoting the interests and culture of a particular nation, often seeking self-governance.",
    "Feudalism": "Feudalism was a medieval social system in which land was exchanged for military service and loyalty.",
    "Constitution": "A constitution is a set of fundamental laws and principles governing a nation, outlining rights and governmental structure.",
    # Biology
    "Cell": "A cell is the basic structural and functional unit of all living organisms.",
    "DNA": "DNA (Deoxyribonucleic Acid) carries the genetic instructions for the development, functioning, and reproduction of organisms.",
    "Evolution": "Evolution is the process of gradual change in inherited traits of populations over successive generations.",
    "Photosynthesis": "Photosynthesis is the process by which plants use sunlight, water, and CO2 to produce glucose and oxygen.",
    "Mitosis": "Mitosis is cell division producing two genetically identical daughter cells for growth and repair.",
    "Ecosystem": "An ecosystem is a community of living organisms interacting with each other and their physical environment.",
    # Maths
    "Calculus": "Calculus is the branch of mathematics studying continuous change through derivatives and integrals.",
    "Matrix": "A matrix is a rectangular array of numbers arranged in rows and columns, used in linear algebra.",
    "Probability": "Probability measures the likelihood of an event occurring, expressed between 0 (impossible) and 1 (certain).",
    "Statistics": "Statistics is the science of collecting, analysing, and interpreting numerical data.",
    "Geometry": "Geometry is the branch of mathematics concerned with shapes, sizes, and properties of figures and spaces.",
    "Algebra": "Algebra is the branch of mathematics dealing with symbols and the rules for manipulating those symbols.",
}


# ============================================================
#  QUIZ TEMPLATES
# ============================================================

QUIZ_TEMPLATES = [
    "What is {}?",
    "How does {} work in practice?",
    "Why is {} important in this subject?",
    "Give an example of where {} is used.",
    "What are the advantages of {}?",
    "What problems does {} solve?",
    "How is {} different from other similar concepts?",
    "In what scenarios would you apply {}?",
]


# ============================================================
#  GROQ API CALL  (FIXED + production-ready)
# ============================================================

def _call_groq(prompt: str, api_key: str, max_tokens: int = 1400) -> str:
    """
    POST a prompt to Groq and return the assistant text.
    Retries up to 3 times with exponential back-off.
    Returns "" on unrecoverable failure so callers can fall back to offline.

    Common failure reasons:
      401 -> invalid / expired API key
      403 -> key valid but missing permissions or wrong org header
      429 -> rate-limited (free tier: ~30 req/min)
      5xx -> Groq-side server error
    """
    print(f"[Groq] model={GROQ_MODEL}  key_prefix={api_key[:8]}...")

    payload = json.dumps({
        "model":       GROQ_MODEL,
        "messages":    [{"role": "user", "content": prompt}],
        "max_tokens":  max_tokens,
        "temperature": 0.3,
    }).encode("utf-8")

    headers = {
        "Authorization": f"Bearer {api_key.strip()}",
        "Content-Type":  "application/json",
        "User-Agent":    "StudyAssistant/1.0 (python-urllib)",
    }

    last_error = ""
    for attempt, delay in enumerate((*_RETRY_DELAYS, None), start=1):
        req = urllib.request.Request(
            GROQ_API_URL,
            data=payload,
            headers=headers,
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=25) as resp:
                body = json.loads(resp.read().decode("utf-8"))
                return body["choices"][0]["message"]["content"].strip()

        except urllib.error.HTTPError as exc:
            status = exc.code
            try:
                err_body = exc.read().decode("utf-8", errors="replace")
            except Exception:
                err_body = "(unreadable)"

            last_error = f"HTTP {status}: {err_body[:300]}"
            print(f"[Groq] attempt {attempt} -> {last_error}")

            if status in (401, 403):
                print("[Groq] Auth error. Check your API key and Groq dashboard permissions.")
                return ""
            if status == 429:
                wait = (delay or 15) * 2
                print(f"[Groq] Rate-limited. Waiting {wait}s before retry...")
                time.sleep(wait)
                continue
            if 500 <= status < 600:
                if delay is not None:
                    time.sleep(delay)
                continue
            return ""

        except urllib.error.URLError as exc:
            last_error = f"URLError: {exc.reason}"
            print(f"[Groq] attempt {attempt} -> {last_error}")
            if delay is not None:
                time.sleep(delay)

        except TimeoutError:
            last_error = "Request timed out"
            print(f"[Groq] attempt {attempt} -> {last_error}")
            if delay is not None:
                time.sleep(delay)

        except Exception as exc:
            last_error = str(exc)
            print(f"[Groq] attempt {attempt} -> unexpected error: {last_error}")
            return ""

    print(f"[Groq] All retries exhausted. Last error: {last_error}")
    return ""


# ============================================================
#  GROQ-POWERED SUMMARIZER
# ============================================================

# Educational system prompt — injected once per request
_SYSTEM_PROMPT = (
    "You are an expert study assistant. "
    "You produce concise, accurate, and pedagogically clear educational content. "
    "You ALWAYS respond with valid JSON only — no prose, no markdown fences."
)

# ✅ FIX: All literal JSON braces are escaped as {{ and }}
# Only {min} and {max} remain as real .format() placeholders
_JSON_SCHEMA_HINT = """{{
  "summary":    "<string: {min}-{max} words>",
  "keywords":   ["<keyword1>", ..., "<keyword12>"],
  "quiz":       ["<question1>", ..., "<question8>"],
  "flashcards": [
    {{"question": "<Define/explain term>", "answer": "<clear explanation>"}},
    "...8 total"
  ]
}}"""


def _groq_summarize(
    text: str,
    min_length: int,
    max_length: int,
    api_key: str,
    progress_callback: Progress,
) -> Dict:
    if progress_callback:
        progress_callback("Connecting to Groq AI...", 1, 5)

    # Trim to first 1500 words to stay well within context + token budget
    words = text.split()
    trimmed = " ".join(words[:1500]) if len(words) > 1500 else text

    schema = _JSON_SCHEMA_HINT.format(min=min_length, max=max_length)

    payload_messages = [
        {"role": "system", "content": _SYSTEM_PROMPT},
        {
            "role": "user",
            "content": (
                f"Analyse the study text below and respond ONLY with a JSON object "
                f"matching this exact schema:\n{schema}\n\n"
                f"Rules:\n"
                f"- summary must be {min_length}-{max_length} words, educational and clear\n"
                f"- keywords: 8-12 important terms from the text\n"
                f"- quiz: 8 varied questions (what/why/how/compare) testing understanding\n"
                f"- flashcards: 8 cards, answers 1-3 sentences, exam-focused\n"
                f"- NO markdown, NO explanation outside the JSON\n\n"
                f"Study text:\n\"\"\"\n{trimmed}\n\"\"\""
            ),
        },
    ]

    if progress_callback:
        progress_callback("AI is reading your notes...", 2, 5)

    raw_payload = json.dumps({
        "model":       GROQ_MODEL,
        "messages":    payload_messages,
        "max_tokens":  1400,
        "temperature": 0.3,
    }).encode("utf-8")

    headers = {
        "Authorization": f"Bearer {api_key.strip()}",
        "Content-Type":  "application/json",
        "User-Agent":    "StudyAssistant/1.0 (python-urllib)",
    }

    raw = ""
    last_err = ""
    for attempt, delay in enumerate((*_RETRY_DELAYS, None), start=1):
        req = urllib.request.Request(
            GROQ_API_URL,
            data=raw_payload,
            headers=headers,
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=25) as resp:
                body = json.loads(resp.read().decode("utf-8"))
                raw = body["choices"][0]["message"]["content"].strip()
                break

        except urllib.error.HTTPError as exc:
            status = exc.code
            try:
                err_body = exc.read().decode("utf-8", errors="replace")
            except Exception:
                err_body = ""
            last_err = f"HTTP {status}: {err_body[:200]}"
            print(f"[Groq summarize] attempt {attempt} -> {last_err}")
            if status in (401, 403):
                break
            if status == 429:
                time.sleep((delay or 15) * 2)
                continue
            if 500 <= status < 600 and delay is not None:
                time.sleep(delay)
                continue
            break

        except Exception as exc:
            last_err = str(exc)
            print(f"[Groq summarize] attempt {attempt} -> {last_err}")
            if delay is not None:
                time.sleep(delay)

    if not raw:
        if progress_callback:
            progress_callback("Groq unavailable — switching to offline mode...", 2, 5)
        return _offline_summarize(text, min_length, max_length, progress_callback)

    if progress_callback:
        progress_callback("Parsing AI response...", 3, 5)

    # Robust JSON extraction: strip all markdown fence variations
    raw = re.sub(r"^```(?:json)?\s*", "", raw, flags=re.IGNORECASE | re.MULTILINE)
    raw = re.sub(r"\s*```\s*$", "",    raw, flags=re.IGNORECASE | re.MULTILINE)
    json_match = re.search(r"\{[\s\S]*\}", raw)
    if json_match:
        raw = json_match.group(0)
    raw = raw.strip()

    try:
        result = json.loads(raw)
        for key in ("summary", "keywords", "quiz", "flashcards"):
            if key not in result:
                raise ValueError(f"Missing key: {key}")

        if progress_callback:
            progress_callback("Done!", 5, 5)

        return {
            "summary":    str(result["summary"]),
            "keywords":   [str(k) for k in result["keywords"]][:12],
            "quiz":       [str(q) for q in result["quiz"]][:8],
            "flashcards": [
                {
                    "question": str(fc.get("question", "")),
                    "answer":   str(fc.get("answer",   "")),
                }
                for fc in result["flashcards"]
            ][:8],
        }

    except Exception as parse_err:
        print(f"[Groq] JSON parse failed: {parse_err}\nRaw snippet: {raw[:300]}")
        if progress_callback:
            progress_callback("Parsing failed — switching to offline mode...", 3, 5)
        return _offline_summarize(text, min_length, max_length, progress_callback)


# ============================================================
#  OFFLINE NLP SUMMARIZER  (no API needed)
# ============================================================

def _offline_summarize(
    text: str,
    min_length: int,
    max_length: int,
    progress_callback: Progress,
) -> Dict:
    """Pure-Python NLP summarizer — zero external dependencies."""

    if progress_callback:
        progress_callback("Cleaning text...", 1, 5)

    cleaned = re.sub(r'\s+', ' ', text.replace("\n", " ")).strip()
    sentences = re.split(r'(?<=[.!?])\s+', cleaned)
    sentences = [s.strip() for s in sentences if len(s.strip()) > 10]

    if progress_callback:
        progress_callback("Generating smart summary...", 2, 5)

    # Score sentences
    scored = []
    for i, sentence in enumerate(sentences):
        wc = len(sentence.split())
        if wc < 5:
            continue
        score = 0
        if any(m in sentence.lower() for m in
               [" is ", " are ", " refers to ", " used to ", " allows ", " enables "]):
            score += 3
        score += 2 if i < 5 else (1 if i < 10 else 0)
        if 10 <= wc <= 40:
            score += 2
        scored.append((score, sentence))

    scored.sort(key=lambda x: x[0], reverse=True)
    top = [s for _, s in scored[:8]]
    ordered = [s for s in sentences if s in top]
    summary = " ".join(ordered)

    sw = summary.split()
    if len(sw) > max_length:
        summary = " ".join(sw[:max_length])
    elif len(sw) < min_length:
        remaining = [s for s in sentences if s not in ordered]
        for extra in remaining:
            summary += " " + extra
            if len(summary.split()) >= min_length:
                break
    if not summary.strip():
        summary = cleaned[:600]

    if progress_callback:
        progress_callback("Extracting keywords...", 3, 5)

    stopwords = {
        "this","that","with","from","have","were","their","there","which","about",
        "these","those","into","using","used","they","them","such","also","only",
        "than","then","being","been","system","notes","quick","introduction",
        "chapter","subject","important","concept","understanding","management",
        "process","control","each","will","when","where","what","while","does",
        "done","data","more","most","some","same","both","many","other","called",
        "known","given","help","make","allows","enables","ensures","provides",
        "between","within","without","through","during","after","before","under","over",
    }

    words_list = re.findall(r'\b[A-Za-z]{4,}\b', cleaned)
    freq: Dict[str, int] = {}
    for w in words_list:
        cw = w.capitalize()
        if cw.lower() not in stopwords and len(cw) > 3:
            freq[cw] = freq.get(cw, 0) + 1

    bigram_patterns = [
        r'\bPrimary\s+Key\b', r'\bForeign\s+Key\b', r'\bBinary\s+Tree\b',
        r'\bLinked\s+List\b', r'\bMachine\s+Learning\b', r'\bNeural\s+Network\b',
        r'\bOperating\s+System\b', r'\bVirtual\s+Memory\b', r'\bStored\s+Procedure\b',
        r'\bObject[- ]Oriented\b', r'\bWorld\s+War\b', r'\bChemical\s+Reaction\b',
        r'\bNatural\s+Selection\b', r'\bElectric\s+Field\b', r'\bKinetic\s+Energy\b',
    ]
    bigrams = []
    for pat in bigram_patterns:
        m = re.search(pat, cleaned, re.IGNORECASE)
        if m:
            bigrams.append(m.group(0).title())

    sorted_kw = sorted(freq.items(), key=lambda x: x[1], reverse=True)
    found_kw: List[str] = []
    for kw in bigrams:
        if kw not in found_kw:
            found_kw.append(kw)
    for word, _ in sorted_kw:
        if len(found_kw) >= 12:
            break
        if word not in found_kw:
            found_kw.append(word)
    found_kw = found_kw[:12]

    if progress_callback:
        progress_callback("Generating quiz & flashcards...", 4, 5)

    quiz = [
        QUIZ_TEMPLATES[i % len(QUIZ_TEMPLATES)].format(kw)
        for i, kw in enumerate(found_kw)
    ]

    flashcards = []
    for kw in found_kw:
        answer = ""
        base = kw.split()[0]
        for sentence in sentences:
            if kw.lower() in sentence.lower():
                if any(m in sentence.lower() for m in
                       [" is ", " are ", " refers to ", " used to ", " allows ", " enables "]):
                    if len(sentence.split()) >= 6:
                        answer = sentence.strip()
                        break
        if not answer and base != kw:
            for sentence in sentences:
                if base.lower() in sentence.lower():
                    if any(m in sentence.lower() for m in [" is ", " are ", " refers to "]):
                        if len(sentence.split()) >= 6:
                            answer = sentence.strip()
                            break
        if not answer:
            answer = DEFINITIONS.get(
                kw,
                DEFINITIONS.get(
                    base,
                    f"{kw} is a key concept in this material. Review your notes for details.",
                ),
            )
        answer = re.sub(r'\s+', ' ', answer).strip()
        if len(answer) > 220:
            answer = answer[:220].rsplit(' ', 1)[0] + "..."
        flashcards.append({"question": f"Define and explain: {kw}", "answer": answer})

    if progress_callback:
        progress_callback("Completed!", 5, 5)

    return {
        "summary":    summary,
        "keywords":   found_kw,
        "quiz":       quiz,
        "flashcards": flashcards,
    }


# ============================================================
#  PUBLIC ENTRY POINT  <- called by core/io.py
# ============================================================

def summarize_text(
    text: str,
    min_length: int,
    max_length: int,
    config: Dict[str, str],
    progress_callback: Progress = None,
) -> Dict:
    """
    Main entry point. Compatible with core/io.py -> process_file().

    config keys
    -----------
    mode     : "groq" | "online" | "offline"  (default: "offline")
    api_key  : Groq API key  (required when mode == "groq" / "online")
               Leave blank to auto-read from Streamlit secrets if available.

    Streamlit secrets (.streamlit/secrets.toml)
    -------------------------------------------
    GROQ_API_KEY = ""
    """
    ok, msg = _within_limits(text)
    if not ok:
        raise ValueError(msg)

    mode    = (config.get("mode") or "offline").lower()
    api_key = (config.get("api_key") or "").strip()

    # Auto-read from Streamlit secrets if key not passed directly
    if not api_key and mode in ("groq", "online"):
        api_key = get_groq_api_key_from_streamlit()

    use_groq = (mode in ("groq", "online")) and bool(api_key)

    if not use_groq and mode in ("groq", "online"):
        if progress_callback:
            progress_callback("No API key found — using offline mode...", 1, 5)

    if use_groq:
        return _groq_summarize(text, min_length, max_length, api_key, progress_callback)
    return _offline_summarize(text, min_length, max_length, progress_callback)