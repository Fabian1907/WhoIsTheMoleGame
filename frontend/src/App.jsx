import { useState, useEffect, useRef } from 'react'
import { styles } from './styles'
import SecretSection from './components/SecretSection'
import JoinView from './components/JoinView'
import WhoAmIView from './components/WhoAmIView'
import ChessView from './components/ChessView'
import DictionaryView from './components/DictionaryView'
import RiskView from './components/RiskView'
import ScoreGraph from './components/ScoreGraph'

// --- AUDIO HELPER ---
// Plays a beep sound. 
const playAlarm = () => {
  const ctx = new (window.AudioContext || window.webkitAudioContext)();
  const osc = ctx.createOscillator();
  const gain = ctx.createGain();
  osc.connect(gain);
  gain.connect(ctx.destination);
  osc.type = 'square';
  
  // Pitch goes up
  osc.frequency.setValueAtTime(440, ctx.currentTime);
  osc.frequency.exponentialRampToValueAtTime(880, ctx.currentTime + 0.5);
  
  // Volume goes down
  gain.gain.setValueAtTime(0.5, ctx.currentTime);
  gain.gain.exponentialRampToValueAtTime(0.01, ctx.currentTime + 0.5);
  
  osc.start();
  osc.stop(ctx.currentTime + 0.5);
}

function App() {
  // Local User State
  const [myName, setMyName] = useState("")
  const [isJoined, setIsJoined] = useState(false)
  const [myId, setMyId] = useState(null)
  
  // Game State from Server
  const [gameState, setGameState] = useState({
    phase: "LOBBY", // LOBBY, REVEAL, EXPLANATION, GAME_RUNNING, SCORING, QUIZ_INTRO, QUIZ
    players: [],
    me: { is_vip: false, is_mole: false, has_finished_quiz: false },
    game_content: null,
    secret_info: "",
    timer_end: 0,
    quiz_data: [],
    round_info: { current: 1, total: 1 },
    history: []  // For score graph
  })

  // UI Local State
  const [showSecret, setShowSecret] = useState(false)
  const [timeLeft, setTimeLeft] = useState(null)
  const [teamScoreInput, setTeamScoreInput] = useState("")
  const [quizAnswers, setQuizAnswers] = useState({})
  const [revealStep, setRevealStep] = useState(0) // 0=Rankings, 1=Mole, 2=Graph


  const API_URL = `http://${window.location.hostname}:8000`

  // 1. Polling the Server
  useEffect(() => {
    if (!isJoined) return;
    const interval = setInterval(fetchGameState, 1000); // Poll every second for timer sync
    return () => clearInterval(interval);
  }, [isJoined, myId]);

  useEffect(() => {
    if (gameState.phase === "SCORING") {
      setTeamScoreInput("");
    }
  }, [gameState.phase]);

  // 2. Timer Countdown Logic
  useEffect(() => {
    if (gameState.phase === 'GAME_RUNNING' && gameState.timer_end) {
      const timerInterval = setInterval(() => {
        const now = Date.now() / 1000;
        const remaining = Math.max(0, Math.ceil(gameState.timer_end - now));
        setTimeLeft(remaining);
        
        if (remaining === 0) {
            playAlarm(); // Play sound at 0
            clearInterval(timerInterval);
        }
      }, 500);
      return () => clearInterval(timerInterval);
    }
  }, [gameState.phase, gameState.timer_end]);

  const fetchGameState = async () => {
    try {
      const res = await fetch(`${API_URL}/state?player_id=${myId}`)
      const data = await res.json()
      setGameState(data)
    } catch (e) {
      console.error("Polling error", e)
    }
  }

  const handleJoin = async () => {
    if (!myName) return;
    try {
      const res = await fetch(`${API_URL}/join?name=${myName}`, { method: 'POST' })
      const data = await res.json()
      setMyId(data.player_id)
      setIsJoined(true)
      fetchGameState()
    } catch (e) {
      alert("Failed to join")
    }
  }

  // Unified Action Sender
  const sendAction = async (action, payload = {}) => {
    try {
        await fetch(`${API_URL}/control?action=${action}`, { 
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        })
        fetchGameState() // Instant update
    } catch (e) {
        alert("Action failed: " + action)
    }
  }

  // Helper for game-specific actions (like guessing)
  const sendGameAction = async (action, payload = {}) => {
    const res = await fetch(`${API_URL}/game_action?player_id=${myId}&action=${action}`, { 
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
    })
    const data = await res.json()
    fetchGameState() // Refresh immediately
    return data; 
  }

  const submitQuiz = async () => {
    if (!gameState.quiz_data) return;
    if (Object.keys(quizAnswers).length < gameState.quiz_data.length) {
        alert("Please answer all questions before submitting.");
        return;
    }
    await fetch(`${API_URL}/submit_quiz?player_id=${myId}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(quizAnswers)
    })
    // Optimistic update
    setGameState(prev => ({...prev, me: {...prev.me, has_finished_quiz: true}}))
  }

    const handleReset = async () => {
    if(confirm("Are you sure? This will delete all data.")) {
        await sendAction('reset'); // You might need to update backend/main.py control to include 'reset' or use the /reset endpoint directly
        window.location.reload(); 
    }
  }

  const ProgressBar = ({ current, total }) => (
  <div style={{ padding: '5px', fontSize: '12px', color: '#666', borderBottom: '1px solid #eee', marginBottom: '10px' }}>
    ROUND {current} OF {total}
  </div>
)

  // --- RENDERERS ---

  // 1. Join Screen
  if (!isJoined) {
    return (
      <JoinView 
        myName={myName} 
        setMyName={setMyName} 
        handleJoin={handleJoin} 
      />
    )
  }

  // 2. Lobby (Restored "Waiting" text & Button Text)
  if (gameState.phase === "LOBBY") {
    return (
      <div style={styles.container}>
        <h2>Lobby</h2>
        <p>Waiting for everyone to join...</p>
        <ul style={styles.list}>
          {gameState.players.map(p => (
            <li key={p.id} style={styles.listItem}>{p.name} {p.is_vip ? "👑" : "🐱"}</li>
          ))}
        </ul>
        
        {/* Logic: Only VIP can start, need 2+ players */}
        {gameState.me.is_vip && gameState.players.length > 1 && (
          <button style={styles.vipButton} onClick={() => sendAction('start_game')}>
            Start Game & Assign Mole
          </button>
        )}
        {gameState.me.is_vip && gameState.players.length < 2 && (
          <p style={{color: '#999'}}>Need at least 2 players to start.</p>
        )}
      </div>
    )
  }

  // 3. Reveal (Restored Secret Section)
  if (gameState.phase === "REVEAL") {
    return (
      <div style={styles.container}>
        <h2>Identity Assigned</h2>
        <p>The game has begun. Check your role below.</p>
        
        <SecretSection 
            title="🔍 Your Role"
            content={gameState.me.is_mole ? 
                <h2 style={{color: 'red', margin:0}}>YOU ARE THE MOLE 🐹</h2> : 
                <h2 style={{color: 'green', margin:0}}>YOU ARE A TEAM PLAYER 🐰</h2>
            } 
        />

        {gameState.me.is_vip && (
            <div style={{marginTop: '30px'}}>
                <p><em>Wait for everyone to check their role...</em></p>
                <button style={styles.vipButton} onClick={() => sendAction('explain_round')}>
                    Go to Game Explanation ➡️
                </button>
            </div>
        )}
      </div>
    )
  }

  // Explanation Phase (with Secret Intel and Quiz Hint)
  if (gameState.phase === "EXPLANATION") {
    const content = gameState.game_content || {}
    return (
      <div style={styles.container}>
        <ProgressBar current={gameState.round_info?.current} total={gameState.round_info?.total} />
        
        <h2>{content.title}</h2>
        <p style={{ whiteSpace: 'pre-line' }}>{content.description}</p>
        <div style={styles.grid}>
            <div style={styles.metricBox}><small>DURATION</small><br/><strong>{content.duration}s</strong></div>
            <div style={styles.metricBox}><small>MAX PTS</small><br/><strong>{content.max_points}</strong></div>
        </div>

        {/* Existing Secret Intel */}
        <SecretSection title="Reveal Secret Intel" content={
            <div style={{ textAlign: 'left' }}>
                {gameState.game_specific?.role_text && (
                    <p style={{ whiteSpace: 'pre-line', marginBottom: '15px' }}>
                        <strong>{gameState.game_specific.role_text}</strong>
                    </p>
                )}
                {gameState.secret_info && (
                    <div style={{ whiteSpace: 'pre-line', lineHeight: '1.6', color: '#333' }}>
                        {gameState.secret_info}
                    </div>
                )}
            </div>
        } />

        {/* NEW: Quiz Hint Section */}
        {gameState.quiz_hint && (
            <SecretSection title="💡 Upcoming Quiz Question" content={
                <div style={{ textAlign: 'left', color: '#555' }}>
                    <p style={{marginBottom: '5px'}}><em>Try to subtly find out the opinion of The Lars, without being to obvious and blowing your advantage.</em></p>
                    
                    {/* Question Text */}
                    <p style={{fontSize: '18px', fontWeight: 'bold', color: '#2c3e50', marginBottom: '10px'}}>
                        "{gameState.quiz_hint.text}"
                    </p>
                    
                    {/* Options List */}
                    <ul style={{paddingLeft: '20px', margin: 0, color: '#333'}}>
                        {gameState.quiz_hint.options.map((opt, i) => (
                            <li key={i} style={{marginBottom: '5px'}}>{opt}</li>
                        ))}
                    </ul>
                </div>
            } />
        )}

        {gameState.me.is_vip && (
            <div style={{marginTop: '30px'}}>
                <button style={{...styles.vipButton, background: '#d35400'}} onClick={() => sendAction('start_timer')}>
                    ⏱️ Start Game & Timer
                </button>
            </div>
        )}
      </div>
    )
  }

  // 5. Game Running (Simplified Timer Visuals)
  if (gameState.phase === "GAME_RUNNING") {
    // 1. Check if it's the Who Am I game
    if (gameState.game_content?.id === 'who-am-i') {
        return (
            <div style={styles.container}>
                <WhoAmIView 
                    timeLeft={timeLeft} 
                    gameSpecific={gameState.game_specific || {}} 
                    onAction={sendGameAction} 
                />
                {gameState.me.is_vip && (
                    <button style={{...styles.vipButton, marginTop: '30px', background: '#c0392b'}} onClick={() => sendAction('end_game_early')}>
                        End Round
                    </button>
                )}
            </div>
        )
    }

    if (gameState.game_content?.id === 'chess-challenges') {
        return (
            <div style={styles.container}>
                <ChessView 
                    timeLeft={timeLeft} 
                    gameSpecific={gameState.game_specific || {}} 
                    onAction={sendGameAction} 
                />
                {gameState.me.is_vip && (
                    <button style={{...styles.vipButton, marginTop: '30px', background: '#c0392b'}} onClick={() => sendAction('end_game_early')}>
                        End Round
                    </button>
                )}
            </div>
        )
    }

    if (gameState.game_content?.id === 'dictionary-dudes') {
        return (
            <div style={styles.container}>
                <DictionaryView 
                    timeLeft={timeLeft} 
                    gameSpecific={gameState.game_specific || {}} 
                />
                {gameState.me.is_vip && (
                    <button style={{...styles.vipButton, marginTop: '30px', background: '#c0392b'}} onClick={() => sendAction('end_game_early')}>
                        <strong>CHECK THE WORDS AND COUNT POINTS FIRST</strong> End Round
                    </button>
                )}
            </div>
        )
    }

    // Risk Game (NEW)
    if (gameState.game_content?.id === 'risky-business') {
        return (
            <div style={styles.container}>
                <RiskView 
                    timeLeft={timeLeft} 
                    gameSpecific={gameState.game_specific || {}} 
                    onAction={sendGameAction} 
                />
                {gameState.me.is_vip && (
                    <button style={{...styles.vipButton, marginTop: '30px', background: '#c0392b'}} onClick={() => sendAction('end_game_early')}>
                        End Round
                    </button>
                )}
            </div>
        )
    }

    // 2. Default View (The flashing timer logic you already have)
    let containerStyle = styles.container;
    let timerColor = 'black';

    if (timeLeft <= 10) {
        if (timeLeft % 2 !== 0) {
            containerStyle = { ...styles.container, background: 'black', color: 'white' };
            timerColor = 'white';
        }
    }

    return (
      <div style={containerStyle}>
        <h2>Game in Progress</h2>
        <div style={{ fontSize: '80px', fontWeight: 'bold', margin: '40px 0', color: timerColor }}>
            {timeLeft}
        </div>
        
        {gameState.me.is_vip && (
            <button style={{...styles.vipButton, background: '#c0392b'}} onClick={() => sendAction('end_game_early')}>
                {timeLeft === 0 ? "Finish & Go to Scoring" : "End Game Early"}
            </button>
        )}
      </div>
    )
  }

  // 2. SCORING BLOCK (Updated logic)
  if (gameState.phase === "SCORING") {
    // Defines which games use AUTOMATIC scoring (no input needed)
    // Removed 'risky-business' from here because it needs manual input for Troops
    const isFullyAutomated = ['who-am-i', 'chess-challenges'].includes(gameState.game_content?.id);
    
    // Defines which games need MANUAL input
    const isManual = ['ritual', 'dictionary-dudes', 'risky-business'].includes(gameState.game_content?.id);

    return (
        <div style={styles.container}>
          <h2>Round Over!</h2>
          {gameState.me.is_vip ? (
            <div style={styles.card}>
                <p><strong>Game Master:</strong></p>
                
                {isFullyAutomated && (
                     <p>Scores are calculated automatically. Click Submit to proceed.</p>
                )}

                {/* Specific Text for Risk */}
                {gameState.game_content?.id === 'risky-business' && (
                     <>
                        <p>Count total troops alive on board.</p>
                        <p>Calculate: <strong>(Troops × 5)</strong></p>
                        <p>Enter that number below. (Task bonuses will be added automatically)</p>
                     </>
                )}

                {/* Specific Text for Standard Manual Games */}
                {(gameState.game_content?.id === 'ritual' || gameState.game_content?.id === 'dictionary-dudes') && (
                     <>
                        <p>Please count the points earned by the team.</p>
                        <p><em>(Max possible: {gameState.max_points})</em></p>
                     </>
                )}
                
                {/* Input Field for Manual Games */}
                {isManual && (
                    <input 
                        type="number" 
                        placeholder="Enter Score" 
                        style={{...styles.input, width: '80%'}}
                        value={teamScoreInput}
                        onChange={e => setTeamScoreInput(e.target.value)}
                    />
                )}
                
                <button style={styles.vipButton} onClick={() => sendAction('submit_score', {points: teamScoreInput})}>
                    Submit Scores & Start Quiz
                </button>
            </div>
          ) : (
            <p>Waiting for the Game Master...</p>
          )}
        </div>
    )
  }

  // 7. Quiz Intro (New)
  if (gameState.phase === "QUIZ_INTRO") {
    return (
        <div style={styles.container}>
            <h2>The Quiz</h2>
            <div style={styles.card}>
                <p><strong>Goal:</strong> Answer the questions and get as many matching answers as possible!</p>
            </div>
            {gameState.me.is_vip ? (
                 <button style={styles.vipButton} onClick={() => sendAction('start_quiz')}>Start Quiz</button>
            ) : (
                <p>Waiting for Game Master to start...</p>
            )}
        </div>
    )
  }

  // 8. The Quiz
  if (gameState.phase === "QUIZ") {
    if (gameState.me.has_finished_quiz) {
        const finishedCount = gameState.players.filter(p => p.has_finished_quiz).length;
        const totalPlayers = gameState.players.length;
        const allFinished = finishedCount === totalPlayers;
        const isLastRound = gameState.round_info.current === gameState.round_info.total;

        return (
            <div style={styles.container}>
                <ProgressBar current={gameState.round_info.current} total={gameState.round_info.total} />
                <h2>Quiz Submitted</h2>
                <p>Waiting for others...</p>
                <h3>{finishedCount} / {totalPlayers} finished</h3>
                
                {gameState.me.is_vip && allFinished && (
                    <div style={{marginTop: '30px', padding: '20px', background: '#eef', borderRadius: '10px'}}>
                        <p>Everyone is done.</p>
                        <button 
                            style={styles.vipButton} 
                            onClick={() => sendAction('advance_round')}
                        >
                            {isLastRound ? "🏆 Go to Final Awards" : "➡️ Start Next Game"}
                        </button>
                    </div>
                )}
            </div>
        )
    }

    return (
        <div style={{...styles.container, textAlign:'left'}}>
            <h2 style={{textAlign:'center'}}>Quiz Round</h2>
            {gameState.quiz_data && gameState.quiz_data.map(q => (
                <div key={q.id} style={{marginBottom: '20px', paddingBottom:'10px', borderBottom:'1px solid #eee'}}>
                    <p style={{fontWeight:'bold', fontSize:'18px'}}>{q.text}</p>
                    {q.options.map(opt => (
                        <div key={opt} style={{marginBottom:'8px'}}>
                            <label style={{display:'flex', alignItems:'center', gap:'10px', fontSize:'16px'}}>
                                <input 
                                    type="radio" 
                                    name={`q-${q.id}`} 
                                    value={opt}
                                    onChange={() => setQuizAnswers(prev => ({...prev, [q.id]: opt}))}
                                    style={{transform: 'scale(1.5)'}}
                                /> 
                                {opt}
                            </label>
                        </div>
                    ))}
                </div>
            ))}
            <button style={{...styles.button, width:'100%', marginTop:'20px'}} onClick={submitQuiz}>
                Submit Answers
            </button>
        </div>
    )
  }


  // 3. REPLACE FINAL REVEAL BLOCK
  if (gameState.phase === "FINAL_REVEAL") {
    
    // FIX SORTING: Descending (b - a) = Highest Score First
    const sortedPlayers = [...gameState.players].sort((a,b) => b.score - a.score);
    const mole = gameState.players.find(p => p.is_mole);

    return (
        <div style={styles.container}>
            <h1>🏆 The Results 🏆</h1>

            {/* STEP 1: RANKINGS */}
            <div style={{marginBottom: '30px'}}>
                <h3>Final Rankings</h3>
                <ul style={styles.list}>
                    {sortedPlayers.map((p, i) => (
                        <li key={p.id} style={{
                            ...styles.listItem, 
                            // Simple reveal animation: Items fade in based on step
                            opacity: revealStep >= 0 ? 1 : 0, 
                            fontWeight: 'bold',
                            fontSize: '18px'
                        }}>
                           {/* Add Medals */}
                           {i === 0 ? "🥇 " : i === 1 ? "🥈 " : i === 2 ? "🥉 " : ""} 
                           {p.name}: {p.score} pts
                        </li>
                    ))}
                </ul>
            </div>

            {/* STEP 2: MOLE REVEAL */}
            {revealStep >= 1 && (
                <div style={{...styles.card, background: '#333', color: 'white', marginBottom: '20px'}}>
                    <h2>THE MOLE WAS...</h2>
                    {revealStep >= 2 ? (
                        <h1 style={{color: 'red', fontSize: '40px', margin: '20px 0'}}>{mole?.name}</h1>
                    ) : (
                        // BUTTON FOR EVERYONE (Not just VIP)
                        <button style={styles.button} onClick={() => setRevealStep(2)}>
                            TAP TO REVEAL
                        </button>
                    )}
                </div>
            )}

            {/* STEP 3: GRAPH */}
            {revealStep >= 3 && (
                <div style={{marginTop: '30px'}}>
                    <h3>Score Progression</h3>
                    <ScoreGraph history={gameState.history} players={gameState.players} />
                </div>
            )}

            {/* NAVIGATION CONTROLS (Local) */}
            <div style={{marginTop: '20px', borderTop: '1px solid #ccc', paddingTop: '10px'}}>
                
                {revealStep === 0 && (
                    <button style={styles.vipButton} onClick={() => setRevealStep(1)}>
                        Next: Who is the Mole?
                    </button>
                )}
                
                {/* Note: Step 2 is triggered by the "TAP TO REVEAL" button above */}
                
                {revealStep === 2 && (
                    <button style={styles.vipButton} onClick={() => setRevealStep(3)}>
                        Next: Show Score Graph
                    </button>
                )}
                
                {/* Only VIP can actually Reset the server */}
                {revealStep === 3 && gameState.me.is_vip && (
                    <button style={{...styles.vipButton, background: 'red', marginTop:'20px'}} onClick={() => sendAction('reset')}>
                        Reset Game (New Lobby)
                    </button>
                )}
            </div>
        </div>
    )
  }

  return <div>Loading...</div>
}

export default App