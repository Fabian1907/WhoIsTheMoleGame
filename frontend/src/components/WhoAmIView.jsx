import { useState } from 'react'
import SecretSection from './SecretSection'
import { styles } from '../styles'

const WhoAmIView = ({ timeLeft, gameSpecific, onAction }) => {
    const [guessInput, setGuessInput] = useState("");
    const stats = gameSpecific.stats || {};

    const handleGuess = async () => {
        if (!guessInput) return;
        const res = await onAction('guess', { guess: guessInput });
        if (res.result === 'correct') {
            alert(`CORRECT! You are ${res.real_name}. You earned ${res.points} points for the POT.`);
        } else if (res.result === 'incorrect') {
            alert("WRONG! -25 Points.");
        }
        setGuessInput("");
    };

    const toggleTask = (index) => {
        onAction('toggle_task', { task_index: index });
    }

    return (
        <div>
            {/* 1. Timer & Role */}
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '15px' }}>
                <div style={{ fontSize: '24px', fontWeight: 'bold' }}>⏱️ {timeLeft}</div>
            </div>

            {/* 2. Victory Banner */}
            {stats.solved && (
                <div style={{ padding: '15px', background: '#dff0d8', borderRadius: '5px', color: '#3c763d', marginBottom: '20px' }}>
                    <strong>✅ IDENTITY FOUND (+{stats.points} pts)</strong>
                    <br/><small>You can still complete your secret tasks!</small>
                </div>
            )}

            {/* 3. Stats Dashboard */}
            <div style={{ display: 'flex', gap: '10px', marginBottom: '20px' }}>
                <div style={styles.metricBox}>
                    <small>QUESTIONS</small><br/>
                    <strong style={{fontSize: '24px'}}>{stats.questions}</strong>
                </div>
                <div style={{...styles.metricBox, background: '#fdeded', color: '#c0392b'}}>
                    <small>STRIKES</small><br/>
                    <strong style={{fontSize: '24px'}}>{stats.strikes}</strong>
                </div>
            </div>

            {/* 5. Interaction Area */}
            {!stats.solved && (
                <>
                    <div style={styles.card}>
                        <h3>Question Counter</h3>
                        <p style={{fontSize: '14px', color: '#555', marginBottom: '10px'}}>Asked a question? Tap + to log it.</p>
                        <button 
                            onClick={() => onAction('add_question')}
                            style={{...styles.button, width: '60px', height: '60px', borderRadius: '50%', fontSize: '30px', padding: 0}}
                        >
                            +
                        </button>
                    </div>

                    <div style={{...styles.card, marginTop: '15px'}}>
                        <h3>Make a Guess</h3>
                        <input 
                            type="text" 
                            placeholder="Who are you?" 
                            value={guessInput}
                            onChange={(e) => setGuessInput(e.target.value)}
                            style={{...styles.input, width: '100%', boxSizing: 'border-box'}}
                        />
                        <button 
                            onClick={handleGuess}
                            style={{...styles.button, width: '100%', marginTop: '10px', background: '#2980b9'}}
                        >
                            Submit Guess
                        </button>
                    </div>
                </>
            )}

            {/* 4. Secret Tasks */}
            <div style={{ marginBottom: '15px' }}>
                <SecretSection 
                    title="📜 Secret Tasks" 
                    defaultOpen={true}
                    content={
                        <div>
                            {gameSpecific.tasks && gameSpecific.tasks.map((t, i) => (
                                <div key={i} style={{marginBottom: '12px', display: 'flex', alignItems: 'flex-start', gap: '10px', borderBottom: '1px solid #eee', paddingBottom: '8px'}}>
                                    <input 
                                        type="checkbox" 
                                        checked={t.done} 
                                        onChange={() => toggleTask(i)}
                                        style={{transform: 'scale(1.5)', marginTop: '4px', cursor: 'pointer'}} 
                                    />
                                    <div style={{textAlign: 'left'}}>
                                        <span style={{
                                            textDecoration: t.done ? 'line-through' : 'none', 
                                            color: t.done ? '#999' : '#000',
                                            display: 'block'
                                        }}>
                                            {t.desc}
                                        </span>
                                        <span style={{fontSize:'11px', color: '#666', fontWeight: 'bold'}}>
                                            {t.type === 'easy' ? '100 pts' : '250 pts'}
                                        </span>
                                    </div>
                                </div>
                            ))}
                        </div>
                    } 
                />
            </div>



            {/* 6. Others' Characters */}
            <div style={{ marginTop: '20px' }}>
                {gameSpecific.others && (
                    <SecretSection 
                        title="👥 Others' Characters" 
                        defaultOpen={true}
                        content={
                            <ul style={{paddingLeft: '20px', margin: 0}}>
                                {gameSpecific.others.map((p, i) => (
                                    <li key={i} style={{marginBottom:'8px'}}>
                                        <strong>{p.name}</strong> is <span style={{color: '#d35400', fontWeight:'bold'}}>{p.char.toUpperCase()}</span>
                                    </li>
                                ))}
                            </ul>
                        } 
                    />
                )}
            </div>
        </div>
    )
}

export default WhoAmIView