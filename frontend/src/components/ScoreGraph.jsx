const ScoreGraph = ({ history, players }) => {
    // 1. Safety check for data
    if (!history || history.length === 0) return <div style={{padding:'20px', color:'#999'}}>No score history available</div>;

    // 2. Prepare Data
    // Get all unique round indices and sort them
    const rounds = [...new Set(history.map(h => h.round_idx))].sort((a,b) => a - b);
    // Add a "Start" point (Round -1) with score 0
    const allRounds = [-1, ...rounds];
    
    // Dimensions
    const width = 300;
    const height = 200;
    const padding = 20;

    // 3. Calculate Scales
    const scores = history.map(h => h.score);
    // If no scores exist yet, default to 0-100 range
    let maxScore = scores.length ? Math.max(...scores) : 100;
    let minScore = scores.length ? Math.min(...scores) : 0;
    
    // Add visual breathing room
    maxScore += 50; 
    
    // CRITICAL FIX: Prevent division by zero if all scores are identical
    const range = (maxScore - minScore) || 100; 

    const getX = (roundIdx) => {
        const index = allRounds.indexOf(roundIdx);
        // CRITICAL FIX: Prevent division by zero if only 1 data point
        const denominator = Math.max(1, allRounds.length - 1);
        return padding + (index / denominator) * (width - padding * 2);
    }
    
    const getY = (score) => {
        return height - padding - ((score - minScore) / range) * (height - padding * 2);
    }

    const colors = ['#e6194b', '#3cb44b', '#ffe119', '#4363d8', '#f58231', '#911eb4', '#46f0f0', '#f032e6'];

    return (
        <svg width="100%" height="250" viewBox={`0 0 ${width} ${height}`} style={{background: '#fff', borderRadius: '10px', border: '1px solid #eee'}}>
            {/* Grid lines */}
            <line x1={padding} y1={height-padding} x2={width-padding} y2={height-padding} stroke="#ccc" />
            <line x1={padding} y1={padding} x2={padding} y2={height-padding} stroke="#ccc" />
            
            {/* Draw Lines for each player */}
            {players.map((p, i) => {
                // Get this player's specific history sorted by round
                const pHistory = history.filter(h => h.player_id === p.id).sort((a,b) => a.round_idx - b.round_idx);
                // Add the starting 0 point
                const points = [{round_idx: -1, score: 0}, ...pHistory];
                
                // Create SVG path string
                const pathData = points.map((pt, idx) => 
                    `${idx===0?'M':'L'} ${getX(pt.round_idx)} ${getY(pt.score)}`
                ).join(" ");

                const lastPoint = points[points.length-1];

                return (
                    <g key={p.id}>
                        {/* The Line */}
                        <path d={pathData} fill="none" stroke={colors[i % colors.length]} strokeWidth="3" />
                        
                        {/* The Dot at the end */}
                        <circle cx={getX(lastPoint.round_idx)} cy={getY(lastPoint.score)} r="4" fill={colors[i % colors.length]} />
                        
                        {/* The Name Label */}
                        <text x={width-padding} y={getY(lastPoint.score)} fontSize="10" fill={colors[i % colors.length]} dx="5" dy="3">
                            {p.name}
                        </text>
                    </g>
                )
            })}
        </svg>
    )
}

export default ScoreGraph