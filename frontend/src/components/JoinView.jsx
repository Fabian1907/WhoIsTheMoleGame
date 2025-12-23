import { styles } from '../styles'
import SecretSection from './SecretSection'

const JoinView = ({ myName, setMyName, handleJoin }) => {
    
    const MOLE_NAME = "The Lars";
    const MOLE_ONLY_NAME = "Lars";

    return (
        <div style={styles.container}>
            <h1 style={{fontSize: '32px', marginBottom: '10px'}}>🫆 Wie is "{MOLE_NAME}"</h1>
            <p style={{color: '#666', marginBottom: '30px'}}>Trust Nobody.</p>
            
            <div style={{marginTop: '40px', textAlign: 'left'}}>
                <SecretSection title="📖 How to Play" content={
                    <div style={{lineHeight: '1.6', color: '#333'}}>
                        <h3>Game Overview</h3>
                        <p>
                            You will work together in a series of games to earn points for the <strong>Team Pot</strong>. 
                            However, one of you is <strong>"{MOLE_NAME}"</strong>, whose goal is to secretly sabotage the team's efforts and keep the pot as low as possible.
                            After every game, you'll take a quiz to test your knowledge about <strong>"{MOLE_NAME}"</strong> and their identity.
                            The player with the highest total points at the end will be crowned the winner! 
                        </p>

                        <h3>The Games</h3>
                        <p>The game consists of several <strong>Games</strong>. In each game you will have to work together to earn points, while also trying to complete your own secret tasks.</p>
                        <p>Before each game, everyone will see an explaination of the game, and perhaps some secret intel. First, split up to read the explanation and the secret intel by yourselves, 
                            and take a minute to consider strategies. After that, everyone will come back together to discuss the game, how the teams should be divided, etc. 
                            When everyone is ready, the game master will start the game.</p>
                        <p>Be careful not to show eachother your explanation screen, as there might be information that reveals your role.
                            The in game screen will be the same for all players, so this can be shown, only if you have hidden your secret tasks for the game.
                        </p>
                        <ol style={{paddingLeft: '20px'}}>
                            <li><strong>Group Tasks:</strong> Challenges that earn points for the Team Pot. These points are given to each of the team players at the end of the game.</li>
                            <li><strong>{MOLE_NAME}'s Sabotage:</strong> Any points <em>missed</em> by the group on the Group Tasks goes to <strong>{MOLE_NAME}'s</strong> personal score.</li>
                            <li><strong>Hidden Individual Tasks:</strong> Secret objectives that earn you personal points. Both team players and <strong>{MOLE_NAME}</strong> earn points from these for themselves upon completion.
                            <strong>DO NOT</strong> reveal anything about them to others. Doing so will result immediate failure of the task.</li>
                        </ol>

                        <h3>The Quiz</h3>
                        <p>
                            After every assignment, everyone takes a <strong>Quiz</strong> containing questions about the identity and behavior of <strong>{MOLE_NAME}</strong>.
                            Every player has to answer the questions as if they were <strong>{MOLE_ONLY_NAME}</strong>.
                            At the end of every quiz, there will be the question: <em>"Who is {MOLE_NAME}?"</em>, answering correctly will earn you bonus points! <strong>{MOLE_NAME}</strong> will lose points if they are identified correctly.
                        </p>
                        <p>
                            <strong>Scoring:</strong> You earn points by matching your answers with <strong>{MOLE_NAME}'s</strong> answers. 
                            (e.g., If <strong>{MOLE_NAME}</strong> says their favorite color is Blue, and you guess Blue, you get points).
                        </p>

                        <ol style={{paddingLeft: '20px'}}>
                            <li><strong>Team Players</strong> Matching answer: 50pts</li>
                            <li><strong>Team Players</strong> Correctly identified <strong>{MOLE_NAME}</strong>: 100pts</li>
                            <li><strong>{MOLE_NAME}</strong> Each matching answer: 35pts</li>
                            <li><strong>{MOLE_NAME}</strong> Team player identified you: -50pts</li>
                        </ol>
                    </div>
                } />
            </div>

            <div style={styles.card}>
                <input 
                    style={{...styles.input, width: '100%', boxSizing: 'border-box'}} 
                    type="text" 
                    placeholder="Enter your name" 
                    value={myName} 
                    onChange={(e) => setMyName(e.target.value)}
                    onKeyDown={(e) => e.key === 'Enter' && handleJoin()}
                />
                <button style={{...styles.button, width: '100%', marginTop: '10px'}} onClick={handleJoin}>
                    Join Game
                </button>
            </div>
        </div>
    )
}

export default JoinView