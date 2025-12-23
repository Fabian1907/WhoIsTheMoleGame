from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
import sqlite3
import random
import json
import time

from database import get_db_connection
from games.registry import GAME_LIST, get_game_by_index
from questions import QUESTION_POOL

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def init_system():
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute("DROP TABLE IF EXISTS players")
    cur.execute("DROP TABLE IF EXISTS game_state")
    cur.execute("DROP TABLE IF EXISTS quiz_answers")
    cur.execute("DROP TABLE IF EXISTS score_history")

    cur.execute("""
        CREATE TABLE game_state (
            id INTEGER PRIMARY KEY,
            phase TEXT DEFAULT 'LOBBY', 
            current_game_idx INTEGER DEFAULT 0,
            dynamic_secret TEXT DEFAULT '{}',
            timer_end REAL DEFAULT 0,
            quiz_questions TEXT DEFAULT '[]',
            used_questions TEXT DEFAULT '[]'
        )
    """)
    cur.execute("INSERT INTO game_state (id, phase) VALUES (1, 'LOBBY')")

    cur.execute("""
        CREATE TABLE players (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE,
            score INTEGER DEFAULT 0,
            is_mole BOOLEAN DEFAULT 0,
            is_vip BOOLEAN DEFAULT 0,
            has_finished_quiz BOOLEAN DEFAULT 0
        )
    """)
    cur.execute("CREATE TABLE quiz_answers (player_id INTEGER, question_id INTEGER, answer TEXT)")
    cur.execute("""
        CREATE TABLE score_history (
            round_idx REAL,  -- Changed to REAL for decimals (0.5, 1.0)
            player_id INTEGER,
            score INTEGER
        )
    """)

    # Run game specific setups
    for game in GAME_LIST:
        game.setup_db(cur)

    conn.commit()
    conn.close()

init_system()

# --- HELPERS ---

def pre_generate_quiz(cur):
    """
    Selects 4 random questions + the Mole Identity question.
    Updates the DB so we know what the upcoming quiz is.
    """
    state = cur.execute("SELECT used_questions FROM game_state WHERE id=1").fetchone()
    used_ids = json.loads(state['used_questions'])
    
    # Pool excludes ID 5 (Who is Mole?) and already used questions
    available = [q['id'] for q in QUESTION_POOL if q['id'] not in used_ids and q['id'] != 5]
    
    # Select 4 questions (or fewer if we run out)
    count = 4 
    if len(available) >= count:
        selected = random.sample(available, count)
    else:
        selected = available 
        
    selected.append(5) # Always add "Who is the mole?"
    
    # Update Used History (excluding ID 5 which is reused)
    used_ids.extend([s for s in selected if s != 5])
    
    cur.execute("""
        UPDATE game_state 
        SET quiz_questions = ?, used_questions = ? 
        WHERE id = 1
    """, (json.dumps(selected), json.dumps(used_ids)))

def snapshot_scores(cur, round_val):
    players = cur.execute("SELECT id, score FROM players").fetchall()
    for p in players:
        cur.execute("INSERT INTO score_history (round_idx, player_id, score) VALUES (?, ?, ?)",
                    (round_val, p['id'], p['score']))

def calculate_quiz_and_snapshot(cur, round_idx):
    # 1. Mole Logic
    mole_row = cur.execute("SELECT id, name FROM players WHERE is_mole = 1").fetchone()
    if not mole_row: 
        cur.execute("DELETE FROM quiz_answers")
        return

    mole_id = mole_row['id']
    mole_name = mole_row['name']
    mole_answers = cur.execute("SELECT question_id, answer FROM quiz_answers WHERE player_id = ?", (mole_id,)).fetchall()
    mole_map = {row['question_id']: row['answer'] for row in mole_answers}

    innocents = cur.execute("SELECT id FROM players WHERE is_mole = 0").fetchall()
    mole_points_change = 0

    for p in innocents:
        p_answers = cur.execute("SELECT question_id, answer FROM quiz_answers WHERE player_id = ?", (p['id'],)).fetchall()
        p_points_change = 0
        
        for ans in p_answers:
            qid = ans['question_id']
            val = ans['answer']
            if qid == 5: # Identity question
                if val == mole_name:
                    p_points_change += 100
                    mole_points_change -= 50
            elif qid in mole_map and mole_map[qid] == val: # Match answer
                p_points_change += 50
                mole_points_change += 35
        
        cur.execute("UPDATE players SET score = score + ? WHERE id = ?", (p_points_change, p['id']))

    cur.execute("UPDATE players SET score = score + ? WHERE id = ?", (mole_points_change, mole_id))
    snapshot_scores(cur, round_idx + 1.0)
    cur.execute("DELETE FROM quiz_answers")

# --- CONTROL HANDLERS ---

def handle_start_game(cur):
    players = cur.execute("SELECT id FROM players").fetchall()
    if len(players) < 2:
        raise HTTPException(status_code=400, detail="Need at least 2 players")
    cur.execute("UPDATE players SET is_mole = 0")
    mole_id = random.choice(players)['id']
    cur.execute("UPDATE players SET is_mole = 1 WHERE id = ?", (mole_id,))
    cur.execute("UPDATE game_state SET phase = 'REVEAL' WHERE id = 1")

def handle_start_timer(cur, current_game):
    duration = int(current_game.duration)
    end_time = time.time() + duration
    cur.execute("UPDATE game_state SET phase = 'GAME_RUNNING', timer_end = ? WHERE id = 1", (end_time,))

def handle_explain_round(cur, current_game):
    # 1. Generate Game Secrets
    dynamic_data = current_game.generate_secret_state(cur)
    cur.execute("UPDATE game_state SET phase = 'EXPLANATION', dynamic_secret = ? WHERE id = 1", (json.dumps(dynamic_data),))
    
    # 2. PRE-GENERATE QUIZ (So we can show hints)
    pre_generate_quiz(cur)
    
def handle_start_quiz(cur):
    # Just change phase, questions are already in DB from the Explanation phase
    cur.execute("UPDATE game_state SET phase = 'QUIZ' WHERE id = 1")
    cur.execute("UPDATE players SET has_finished_quiz = 0")

def handle_advance_round(cur):
    row = cur.execute("SELECT current_game_idx FROM game_state WHERE id=1").fetchone()
    current_idx = row['current_game_idx']
    
    # 1. Scoring
    calculate_quiz_and_snapshot(cur, current_idx)
    
    prev_game = get_game_by_index(current_idx)
    if prev_game and hasattr(prev_game, 'calculate_scores'):
        prev_game.calculate_scores(cur)

    next_idx = current_idx + 1
    
    if next_idx < len(GAME_LIST):
        next_game = get_game_by_index(next_idx)
        dynamic_data = next_game.generate_secret_state(cur) 
        
        cur.execute("""
            UPDATE game_state 
            SET phase = 'EXPLANATION', 
                current_game_idx = ?, 
                dynamic_secret = ?,
                timer_end = 0
            WHERE id = 1
        """, (next_idx, json.dumps(dynamic_data)))
        cur.execute("UPDATE players SET has_finished_quiz = 0")
        
        # 2. PRE-GENERATE QUIZ FOR NEXT ROUND
        pre_generate_quiz(cur)
        
    else:
        cur.execute("UPDATE game_state SET phase = 'FINAL_REVEAL' WHERE id = 1")

# --- ENDPOINTS ---

@app.get("/state")
def get_game_state(player_id: int = None):
    conn = get_db_connection()
    game = conn.execute("SELECT * FROM game_state WHERE id=1").fetchone()
    players_db = conn.execute("SELECT id, name, score, is_vip, is_mole, has_finished_quiz FROM players").fetchall()
    
    response = {
        "phase": game['phase'],
        "timer_end": game['timer_end'],
        "players": [dict(p) for p in players_db],
        "round_info": { "current": game['current_game_idx'] + 1, "total": len(GAME_LIST) }
    }

    if game['phase'] == 'FINAL_REVEAL':
        history = conn.execute("SELECT * FROM score_history ORDER BY round_idx").fetchall()
        response["history"] = [dict(h) for h in history]

    if player_id:
        player = next((p for p in players_db if p['id'] == player_id), None)
        if player:
            response["me"] = {
                "id": player['id'],
                "is_vip": bool(player['is_vip']),
                "is_mole": bool(player['is_mole']),
                "has_finished_quiz": bool(player['has_finished_quiz'])
            }

            # DYNAMIC CONTENT LOADING
            if game['phase'] in ['EXPLANATION', 'GAME_RUNNING', 'SCORING']:
                current_game = get_game_by_index(game['current_game_idx'])
                if current_game:
                    response["game_content"] = {
                        "id": current_game.id,
                        "title": current_game.title,
                        "duration": current_game.duration,
                        "max_points": current_game.max_points,
                        "team_distribution": current_game.team_distribution,
                        "description": current_game.description
                    }
                    
                    secrets = json.loads(game['dynamic_secret'])
                    
                    # 1. Get Interactive View Data (for Game Running)
                    view_data = current_game.get_player_view(conn, player['id'], player['is_mole'], secrets)
                    response["game_specific"] = view_data

                    # 2. Get Text Description (for Explanation Screen) <--- ADD THIS BACK
                    # Check if the game class has these methods (Ritual, Chess, WhoAmI all do)
                    if hasattr(current_game, 'get_mole_text'):
                        if player['is_mole']:
                            response["secret_info"] = current_game.get_mole_text(secrets)
                        else:
                            response["secret_info"] = current_game.get_innocent_text(secrets)
                                # --- NEW: QUIZ HINT LOGIC ---
                # 1. Get the pre-generated questions
                q_ids = json.loads(game['quiz_questions'])
                # 2. Filter out "Who is the mole?" (ID 5)
                hint_candidates = [qid for qid in q_ids if qid != 5]
                
                if hint_candidates:
                    # 3. Deterministic Random based on player ID
                    hint_id = hint_candidates[player['id'] % len(hint_candidates)]
                    
                    # 4. Find the full question object
                    q_obj = next((q for q in QUESTION_POOL if q['id'] == hint_id), None)
                    
                    if q_obj:
                        # 5. Send object with Text AND Options
                        response['quiz_hint'] = {
                            "text": q_obj['text'].replace("{target}", "Lars"),
                            "options": q_obj['options']
                        }
            
            
            if game['phase'] == 'SCORING':
                 current_game = get_game_by_index(game['current_game_idx'])
                 response["max_points"] = current_game.max_points

            if game['phase'] == 'QUIZ':
                q_ids = json.loads(game['quiz_questions'])
                questions_to_send = []
                for q in QUESTION_POOL:
                    if q['id'] in q_ids:
                        q_copy = q.copy()
                        q_copy['text'] = q_copy['text'].replace("{target}", "Lars")
                        if q['id'] == 5: 
                            q_copy['options'] = [p['name'] for p in players_db]
                        questions_to_send.append(q_copy)
                response["quiz_data"] = questions_to_send

    conn.close()
    return response

# NEW ENDPOINT FOR GAME ACTIONS (GUESSES, ETC)
@app.post("/game_action")
def game_action(player_id: int, action: str, payload: dict = {}):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        # Determine current game
        row = cur.execute("SELECT current_game_idx FROM game_state WHERE id=1").fetchone()
        current_game = get_game_by_index(row['current_game_idx'])
        
        # Delegate to game class
        result = current_game.handle_action(cur, player_id, action, payload)
        
        conn.commit()
        return result
    except Exception as e:
        print(f"Game Action Error: {e}")
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

# Existing control endpoint
@app.post("/control")
def game_control(action: str, payload: dict = {}):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        state = cur.execute("SELECT current_game_idx FROM game_state WHERE id=1").fetchone()
        current_game = get_game_by_index(state['current_game_idx'])

        if action == "start_game":
            handle_start_game(cur)
        elif action == "explain_round":
            handle_explain_round(cur, current_game)
        elif action == "start_timer":
            handle_start_timer(cur, current_game)
        elif action == "end_game_early":
            cur.execute("UPDATE game_state SET phase = 'SCORING' WHERE id = 1")
        elif action == "submit_score":
            row = cur.execute("SELECT current_game_idx FROM game_state WHERE id=1").fetchone()
            current_idx = row['current_game_idx']
            
            # 1. Apply Manual Points (Group Pot)
            if current_game.id in ['ritual', 'dictionary-dudes', 'risky-business']:
                points = int(payload.get('points', 0))
                max_pts = current_game.max_points
                if isinstance(max_pts, str): max_pts = 1600 # Fallback for Risk
                
                mole_pts = max_pts - points
                
                cur.execute("UPDATE players SET score = score + ? WHERE is_mole = 0", (points,))
                cur.execute("UPDATE players SET score = score + ? WHERE is_mole = 1", (mole_pts,))
            
            # 2. Apply Automated Task Bonuses (Risk, WhoAmI, Chess)
            # Note: We use 'if' instead of 'elif' here so Risk runs BOTH blocks
            if hasattr(current_game, 'calculate_scores'):
                current_game.calculate_scores(cur)

            snapshot_scores(cur, current_idx + 0.5)
            cur.execute("UPDATE game_state SET phase = 'QUIZ_INTRO' WHERE id = 1")
            
        elif action == "start_quiz":
            handle_start_quiz(cur)

        elif action == "advance_round":
            handle_advance_round(cur)

        conn.commit()
        return {"status": "ok"}
    except Exception as e:
        conn.rollback()
        print(f"Control Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

@app.post("/join")
def join_game(name: str):
    conn = get_db_connection()
    cur = conn.cursor()
    existing = cur.execute("SELECT id FROM players WHERE name = ?", (name,)).fetchone()
    if existing:
        conn.close()
        return {"player_id": existing['id']}
    count = cur.execute("SELECT count(*) FROM players").fetchone()[0]
    is_vip = (count == 0)
    cur.execute("INSERT INTO players (name, is_vip) VALUES (?, ?)", (name, is_vip))
    new_id = cur.lastrowid
    conn.commit()
    conn.close()
    return {"player_id": new_id}

@app.post("/submit_quiz")
def submit_quiz(player_id: int, answers: dict):
    conn = get_db_connection()
    cur = conn.cursor()
    for q_id, ans_text in answers.items():
        cur.execute("INSERT INTO quiz_answers (player_id, question_id, answer) VALUES (?,?,?)", 
                    (player_id, q_id, ans_text))
    cur.execute("UPDATE players SET has_finished_quiz = 1 WHERE id = ?", (player_id,))
    conn.commit()
    conn.close()
    return {"status": "submitted"}

@app.post("/reset")
def reset_game():
    init_system()
    return {"message": "Game reset"}