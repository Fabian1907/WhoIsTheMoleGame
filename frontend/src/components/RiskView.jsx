import { useState } from 'react'
import SecretSection from './SecretSection'
import { styles } from '../styles'

const RiskView = ({ timeLeft, gameSpecific, onAction }) => {
    // Local state for the convenience counters (not synced to backend)
    const [counters, setCounters] = useState({});

    const tasks = gameSpecific.tasks || [];

    const toggleTask = (index) => {
        onAction('toggle_task', { index });
    }

    // Helper to update local counter
    const updateCounter = (index, delta) => {
        setCounters(prev => {
            const current = prev[index] || 0;
            const newVal = Math.max(0, current + delta);
            return { ...prev, [index]: newVal };
        });
    }

    return (
        <div>
            {/* 1. Header & Role */}
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '15px' }}>
                <div style={{ fontSize: '24px', fontWeight: 'bold' }}>⏱️ {timeLeft}</div>
            </div>

            {/* 2. Tasks List */}
            <div style={{ marginBottom: '15px' }}>
                <SecretSection 
                    title="👤 My Secret Tasks" 
                    defaultOpen={true}
                    content={
                        <div>
                            {tasks.map((t) => (
                                <div key={t.idx} style={{marginBottom: '15px', borderBottom: '1px solid #eee', paddingBottom: '10px'}}>
                                    
                                    {/* Task Checkbox & Description */}
                                    <div style={{display: 'flex', alignItems: 'flex-start', gap: '10px', marginBottom: '8px'}}>
                                        <input 
                                            type="checkbox" 
                                            checked={t.done} 
                                            onChange={() => toggleTask(t.idx)}
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
                                                {t.points} pts • {t.type}
                                            </span>
                                        </div>
                                    </div>

                                    {/* Convenience Counter */}
                                    {!t.done && (
                                        <div style={{display: 'flex', alignItems: 'center', gap: '10px', marginLeft: '30px', background: '#f9f9f9', padding: '5px', borderRadius: '5px', width: 'fit-content'}}>
                                            <span style={{fontSize: '12px', color: '#555'}}>Tracker:</span>
                                            <button 
                                                onClick={() => updateCounter(t.idx, -1)}
                                                style={{...styles.button, padding: '2px 8px', fontSize: '14px', height: 'auto', background: '#ddd', color: '#333'}}
                                            >-</button>
                                            
                                            <span style={{fontWeight: 'bold', minWidth: '20px'}}>{counters[t.idx] || 0}</span>
                                            
                                            <button 
                                                onClick={() => updateCounter(t.idx, 1)}
                                                style={{...styles.button, padding: '2px 8px', fontSize: '14px', height: 'auto', background: '#ddd', color: '#333'}}
                                            >+</button>
                                        </div>
                                    )}
                                </div>
                            ))}
                        </div>
                    } 
                />
            </div>
        </div>
    )
}

export default RiskView