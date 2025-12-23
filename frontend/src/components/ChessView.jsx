import SecretSection from './SecretSection'
import { styles } from '../styles'

const ChessView = ({ timeLeft, gameSpecific, onAction }) => {
    const stats = gameSpecific.stats || { moves: 0, game_won: false };
    const groupTasks = gameSpecific.group_tasks || [];
    const indivTasks = gameSpecific.indiv_tasks || [];
    const anonTasks = gameSpecific.anonymous_tasks || [];

    const toggleGroup = (index) => {
        onAction('toggle_group', { index });
    }

    const toggleIndiv = (index) => {
        onAction('toggle_indiv', { index });
    }

    const toggleWin = () => {
        onAction('toggle_win');
    }

    return (
        <div>
            {/* 1. Header & Role */}
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '15px' }}>
                <div style={{ fontSize: '24px', fontWeight: 'bold' }}>⏱️ {timeLeft}</div>
            </div>

            {/* 2. Primary Actions */}
            <div style={{ display: 'flex', gap: '10px', marginBottom: '20px' }}>
                <div style={{...styles.metricBox, display: 'flex', flexDirection: 'column', justifyContent: 'center', alignItems: 'center'}}>
                    <small>MOVES</small>
                    <strong style={{fontSize: '28px', margin: '5px 0'}}>{stats.moves}</strong>
                    <button onClick={() => onAction('add_move')} style={{...styles.button, padding: '5px 15px', fontSize: '20px', width: 'auto'}}>+</button>
                </div>

                <div style={{...styles.metricBox, background: stats.game_won ? '#dff0d8' : '#f0f0f0', border: stats.game_won ? '1px solid green' : 'none'}}>
                    <small>GAME STATUS</small>
                    <div style={{marginTop: '10px', display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '5px'}}>
                        <input type="checkbox" checked={stats.game_won} onChange={toggleWin} style={{transform: 'scale(1.5)', cursor: 'pointer'}} />
                        <span style={{fontSize: '12px', fontWeight: 'bold', color: stats.game_won ? 'green' : '#666'}}>GAME WON<br/>(+400 pts)</span>
                    </div>
                </div>
            </div>

            {/* 3. My Group Challenges (Now Local Only) */}
            <div style={{ marginBottom: '15px' }}>
                <SecretSection title="🤝 My Group Challenges" defaultOpen={true} content={
                    <div>
                        {groupTasks.map((t) => (
                            <div key={t.idx} style={{marginBottom: '12px', display: 'flex', alignItems: 'flex-start', gap: '10px', borderBottom: '1px solid #eee', paddingBottom: '8px'}}>
                                <input type="checkbox" checked={t.done} onChange={() => toggleGroup(t.idx)} style={{transform: 'scale(1.5)', marginTop: '4px', cursor: 'pointer'}} />
                                <div style={{textAlign: 'left'}}>
                                    <span style={{textDecoration: t.done ? 'line-through' : 'none', color: t.done ? '#999' : '#000', display: 'block'}}>{t.desc}</span>
                                    <span style={{fontSize:'11px', color: '#666', fontWeight: 'bold'}}>{t.points} pts</span>
                                </div>
                            </div>
                        ))}
                    </div>
                } />
            </div>

            {/* 4. Anonymous Intel (No Checkboxes/Status) */}
            <div style={{ marginBottom: '15px' }}>
                <SecretSection title="🕵️ Intel: Others' Group Tasks" defaultOpen={true} content={
                    <div>
                        <p style={{fontSize: '12px', color: '#666', marginBottom: '10px'}}>
                            Tasks belonging to other players. You don't know who has them or if they are done.
                        </p>
                        {anonTasks.map((t, i) => (
                            <div key={i} style={{marginBottom: '12px', display: 'flex', alignItems: 'flex-start', gap: '10px', borderBottom: '1px solid #eee', paddingBottom: '8px'}}>
                                {/* Status removed for mystery */}
                                <div style={{textAlign: 'left'}}>
                                    <span style={{color: '#000', display: 'block'}}>{t.desc}</span>
                                    <span style={{fontSize:'11px', color: '#666', fontWeight: 'bold'}}>{t.points} pts</span>
                                </div>
                            </div>
                        ))}
                    </div>
                } />
            </div>

            {/* 5. Individual Challenges */}
            <div style={{ marginBottom: '15px' }}>
                <SecretSection title="👤 Individual Challenges" defaultOpen={true} content={
                    <div>
                        {indivTasks.map((t) => (
                            <div key={t.idx} style={{marginBottom: '12px', display: 'flex', alignItems: 'flex-start', gap: '10px', borderBottom: '1px solid #eee', paddingBottom: '8px'}}>
                                <input type="checkbox" checked={t.done} onChange={() => toggleIndiv(t.idx)} style={{transform: 'scale(1.5)', marginTop: '4px', cursor: 'pointer'}} />
                                <div style={{textAlign: 'left'}}>
                                    <span style={{textDecoration: t.done ? 'line-through' : 'none', color: t.done ? '#999' : '#000', display: 'block'}}>{t.desc}</span>
                                    <span style={{fontSize:'11px', color: '#666', fontWeight: 'bold'}}>{t.points} pts</span>
                                </div>
                            </div>
                        ))}
                    </div>
                } />
            </div>
        </div>
    )
}

export default ChessView