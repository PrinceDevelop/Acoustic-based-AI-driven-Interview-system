from flask import Flask, render_template, request, redirect, session, jsonify
import os, re, uuid, threading, json, concurrent.futures
from database import connect_db, create_table
from video_processing import extract_audio
from speech_to_text import transcribe_audio
from audio_processing import extract_audio_features
from nlp_analysis import analyze_text
from model import evaluate_candidate
from email_service import send_results_email
from resume_parser import parse_resume

app = Flask(__name__)
app.secret_key = "secret123"

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

create_table()

# ---------------- AUTH ---------------- #

@app.route('/')
def login():
    return render_template('login.html')

@app.route('/signup')
def signup():
    return render_template('signup.html')

@app.route('/reset')
def reset():
    return render_template('reset.html')

@app.route('/services')
def services():
    return render_template('services.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

@app.route('/register', methods=['POST'])
def register():
    username = request.form['username'].strip()
    email = request.form['email'].strip()
    password = request.form['password'].strip()

    pattern = r'^[A-Z][A-Za-z0-9@#$%^&*!]{7,}$'
    if not re.match(pattern, password):
        return redirect('/signup?msg=❌ Invalid Password Format')

    conn = connect_db()
    cur = conn.cursor()

    try:
        cur.execute("INSERT INTO users(username,email,password) VALUES(%s,%s,%s)",
                    (username, email, password))
        conn.commit()
    except Exception as e:
        conn.close()
        return redirect(f'/?msg=❌ Registration failed: {str(e)}')

    conn.close()

    return redirect('/?msg=Signup successful!')

@app.route('/login_user', methods=['POST'])
def login_user():
    username = request.form['username'].strip()
    password = request.form['password'].strip()

    conn = connect_db()
    cur = conn.cursor()

    cur.execute("SELECT username, password FROM users WHERE username=%s", (username,))
    user = cur.fetchone()

    conn.close()

    if user:
        db_username = user['username']
        db_password = user['password']

        if username == db_username.strip() and password == db_password.strip():
            session['user'] = username
            return redirect('/dashboard')

    return redirect('/?msg=❌ Invalid username or password')

@app.route('/reset_password', methods=['POST'])
def reset_password():
    email = request.form['email']
    new_password = request.form['password']

    conn = connect_db()
    cur = conn.cursor()

    cur.execute("UPDATE users SET password=%s WHERE email=%s", (new_password, email))

    conn.commit()
    conn.close()

    return redirect('/')

# ---------------- DASHBOARD ---------------- #

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect('/')
    return render_template('dashboard.html')

@app.route('/interview')
def interview():
    return render_template('interview.html')

@app.route('/upload_resume', methods=['POST'])
def upload_resume():
    if 'user' not in session:
        return redirect('/')
    
    if 'resume' not in request.files:
        return redirect('/dashboard?msg=❌ No file uploaded')
        
    file = request.files['resume']
    if file.filename == '':
        return redirect('/dashboard?msg=❌ No selected file')
        
    if file:
        file_path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(file_path)
        
        # Analyze resume
        result = parse_resume(file_path)
        
        return render_template('resume_result.html', result=result)


# ---------------- VIDEO PROCESS ---------------- #

def process_video_job(job_id, video_path, job_role, username, email_address):
    """Worker thread that processes the video and updates the database status."""
    try:
        # Step 1: Extract Audio
        audio_path = extract_audio(video_path)
        if not os.path.exists(audio_path) or not audio_path.endswith('.wav'):
             db_update_job(job_id, 'error', {'error': f'Audio extraction failed: {audio_path}'})
             return

        # Step 2 & 3: Run Transcribe and Audio Features Concurrently
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future_text = executor.submit(transcribe_audio, audio_path)
            future_audio = executor.submit(extract_audio_features, audio_path)
            
            # Get transcription text
            text = future_text.result()
            if not text or "Error" in text or "No speech" in text:
                text = "No meaningful speech detected."
                
            # Get audio features
            try:
                audio_features = future_audio.result()
            except Exception as e:
                db_update_job(job_id, 'error', {'error': f'Audio analysis error: {str(e)}'})
                return

        # Step 4: NLP Analysis
        nlp_features = analyze_text(text)

        # Step 5: Final Score / Feedback
        score, feedback = evaluate_candidate(audio_features, nlp_features)

        # Step 6: Save Results to Interview History
        if username:
            conn = connect_db()
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO interview_results (username, job_role, score, feedback, transcript) VALUES (%s, %s, %s, %s, %s)",
                (username, job_role, score, feedback, text)
            )
            conn.commit()
            conn.close()

        # Step 7: Email Results
        email_sent = False
        if email_address:
            email_sent = send_results_email(
                receiver_email=email_address,
                username=username or "Candidate",
                score=score,
                feedback=feedback,
                transcript=text,
                job_role=job_role
            )

        # Final Success Result
        result_data = {
            'score': score,
            'feedback': feedback,
            'transcript': text,
            'job_role': job_role,
            'email_sent': email_sent,
            'email_address': email_address
        }
        db_update_job(job_id, 'done', result_data)

    except Exception as e:
        db_update_job(job_id, 'error', {'error': f'Background processing crashed: {str(e)}'})


def db_update_job(job_id, status, result_dict=None):
    """Helper to update job status and result JSON in the DB."""
    try:
        conn = connect_db()
        cur = conn.cursor()
        result_json = json.dumps(result_dict) if result_dict else None
        cur.execute(
            "UPDATE processing_jobs SET status=%s, result_json=%s WHERE job_id=%s",
            (status, result_json, job_id)
        )
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"[DB_ERROR] Failed to update job {job_id}: {e}")


@app.route('/upload', methods=['POST'])
def upload():
    if 'video' not in request.files:
        return jsonify({'error': 'No video file provided'}), 400

    file = request.files['video']
    job_role = request.form.get('job_role', 'General')
    
    # Unique filename per job to avoid conflicts
    job_id = str(uuid.uuid4())
    video_path = os.path.join(UPLOAD_FOLDER, f"video_{job_id}.webm")
    file.save(video_path)

    username = session.get('user')
    email_address = ""
    if username:
        conn = connect_db()
        cur = conn.cursor()
        cur.execute("SELECT email FROM users WHERE username=%s", (username,))
        row = cur.fetchone()
        if row: email_address = row['email']
        conn.close()

    # Create the persistent job record
    conn = connect_db()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO processing_jobs (job_id, status) VALUES (%s, %s)",
        (job_id, 'processing')
    )
    conn.commit()
    conn.close()

    # Start the worker thread
    thread = threading.Thread(
        target=process_video_job,
        args=(job_id, video_path, job_role, username, email_address),
        daemon=True
    )
    thread.start()

    return jsonify({'job_id': job_id})


@app.route('/result/<job_id>')
def get_job_result(job_id):
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("SELECT status, result_json FROM processing_jobs WHERE job_id=%s", (job_id,))
    row = cur.fetchone()
    conn.close()

    if not row:
        return jsonify({'status': 'not_found'}), 404

    status = row['status']
    result_data = json.loads(row['result_json']) if row['result_json'] else None

    return jsonify({
        'status': status,
        'result': result_data
    })


# ---------------- HISTORY API ---------------- #

@app.route('/get_history')
def get_history():
    if 'user' not in session:
        return jsonify([])
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT id, job_role, score, feedback, transcript, created_at
        FROM interview_results
        WHERE username = %s
        ORDER BY created_at DESC
        LIMIT 10
    """, (session['user'],))
    rows = cur.fetchall()
    # Convert datetime objects to strings for JSON serialization
    result = []
    for r in rows:
        row_dict = dict(r)
        if row_dict.get('created_at'):
            row_dict['created_at'] = str(row_dict['created_at'])
        result.append(row_dict)
    conn.close()
    return jsonify(result)


@app.route('/health')
def health():
    return {"status": "ok", "python": "working"}


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)