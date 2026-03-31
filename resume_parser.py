import os
import re
import PyPDF2
from docx import Document

def extract_text_from_pdf(pdf_path):
    text = ""
    try:
        with open(pdf_path, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                text += page.extract_text() + "\n"
    except Exception as e:
        print(f"Error reading PDF: {e}")
    return text

def extract_text_from_docx(docx_path):
    text = ""
    try:
        doc = Document(docx_path)
        for para in doc.paragraphs:
            text += para.text + "\n"
    except Exception as e:
        print(f"Error reading DOCX: {e}")
    return text

def parse_resume(file_path):
    # Extract text based on file format
    ext = os.path.splitext(file_path)[1].lower()
    if ext == ".pdf":
        text = extract_text_from_pdf(file_path)
    elif ext in [".docx", ".doc"]:
        text = extract_text_from_docx(file_path)
    else:
        # Fallback to plain text
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                text = f.read()
        except:
            text = ""
            
    # If we couldn't parse anything
    if not text.strip():
        return {
            "score": 0,
            "skills_found": [],
            "feedback": ["Failed to extract text from the document. Please ensure it is a valid PDF or DOCX."],
            "word_count": 0
        }

    return evaluate_resume_text(text)

def evaluate_resume_text(text):
    text_lower = text.lower()
    words = re.findall(r'\w+', text_lower)
    word_count = len(words)
    
    # 1. Define Skill Keywords to look out for
    skill_keywords = [
        "python", "java", "c++", "c#", "javascript", "react", "node", "html", "css",
        "sql", "mysql", "mongodb", "postgresql", "aws", "docker", "kubernetes", "git",
        "machine learning", "deep learning", "ai", "artificial intelligence", "nlp",
        "linux", "flask", "django", "spring boot", "agile", "scrum", "leadership", 
        "communication", "teamwork", "problem solving", "api", "rest"
    ]
    
    # 2. Extract found skills
    skills_found = set()
    for skill in skill_keywords:
        # Avoid matching partial words (e.g. "c" in "circle")
        pattern = r'\b' + re.escape(skill) + r'\b'
        if re.search(pattern, text_lower):
            skills_found.add(skill.title())
            
    # 3. Compute ATS Score (Max 100)
    # Give up to 40 points for word count/length (optimal 300 to 1000 words)
    length_score = 0
    if 300 <= word_count <= 1000:
        length_score = 40
    elif 150 <= word_count < 300 or 1000 < word_count <= 1500:
        length_score = 25
    else:
        length_score = 10
        
    # Give up to 60 points for skills found (2 points per skill, max 30 skills)
    skill_score = min(len(skills_found) * 5, 60)
    
    total_score = length_score + skill_score
    
    # Ensure minimum score of 10 if we parsed *something*
    if total_score < 10:
        total_score = 10
        
    # 4. Generate Feedback
    feedback = []
    
    if length_score == 40:
        feedback.append("Great resume length! It appears concise and readable.")
    elif length_score == 25:
        if word_count < 300:
            feedback.append("Resume looks a bit too short. Try expanding on your past experiences and projects.")
        else:
            feedback.append("Your resume is quite long. Consider condensing it to the most relevant information.")
    else:
        feedback.append("Your resume length is not optimal (either much too short or way too long). Recruiters prefer punchy 1-2 page resumes.")
        
    if len(skills_found) >= 10:
        feedback.append(f"Excellent! We found a strong array of skills ({len(skills_found)} key terms).")
    elif len(skills_found) >= 5:
        feedback.append("Good start on skills, but you could include more specific keywords related to the job description.")
    else:
        feedback.append("We found very few industry keywords. Make sure to clearly list hard skills, tools, and platforms you know.")
        
    # Action verbs check
    action_verbs = ["developed", "created", "led", "managed", "designed", "implemented", "built", "optimized", "increased", "reduced"]
    if any(verb in text_lower for verb in action_verbs):
        feedback.append("Good use of action verbs in describing your experience.")
    else:
        feedback.append("Your resume lacks strong action verbs. Start bullet points with words like 'Developed', 'Managed', 'Designed'.")
        
    return {
        "score": total_score,
        "skills_found": sorted(list(skills_found)),
        "feedback": feedback,
        "word_count": word_count
    }
