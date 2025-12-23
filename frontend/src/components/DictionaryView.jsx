import { useState } from 'react'
import { styles } from '../styles'

const DictionaryView = ({ timeLeft, gameSpecific }) => {
    const [isRevealed, setIsRevealed] = useState(false);
    const words = gameSpecific.word_list || [];

    return (
        <div>
            {/* 1. Header & Role */}
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '15px' }}>
                <div style={{ fontSize: '24px', fontWeight: 'bold' }}>⏱️ {timeLeft}</div>
            </div>

            <div style={{...styles.card, background: '#fff', border: '1px solid #ccc', padding: '20px'}}>
                <h2 style={{marginTop:0}}>Word List</h2>
                <p>Only the <strong>Solo Players</strong> (Drawer & Writer) should look at this list.</p>
                
                {!isRevealed ? (
                    <button 
                        onClick={() => { if(confirm("Are you sure? Only click this if you are a Solo Player!")) setIsRevealed(true); }}
                        style={{
                            ...styles.button, 
                            background: '#c0392b', 
                            padding: '20px', 
                            fontSize: '18px', 
                            fontWeight: 'bold', 
                            border: '3px solid #e74c3c',
                            width: '100%',
                            whiteSpace: 'pre-wrap'
                        }}
                    >
                        ⚠️ REVEAL WORD LIST ⚠️{"\n"}(DO NOT CLICK IF GUESSING)
                    </button>
                ) : (
                    <div style={{textAlign: 'left', maxHeight: '400px', overflowY: 'auto', border: '1px solid #eee', padding: '10px'}}>
                        <button onClick={() => setIsRevealed(false)} style={{...styles.button, background: '#7f8c8d', width: '100%', marginBottom: '15px'}}>Hide List</button>
                        <ul style={{paddingLeft: '20px'}}>
                            {words.map((w, i) => (
                                <li key={i} style={{marginBottom: '5px', fontSize: '18px', fontWeight: 'bold'}}>
                                    <span style={{color: '#999', marginRight: '10px'}}>{i+1}.</span>
                                    {w}
                                </li>
                            ))}
                        </ul>
                    </div>
                )}
            </div>
        </div>
    )
}

export default DictionaryView