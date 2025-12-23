import { useState } from 'react'

const SecretSection = ({ title, content, defaultOpen=false }) => {
    const [isOpen, setIsOpen] = useState(defaultOpen);
    return (
        <div style={{ marginTop: '10px', border: '1px solid #ddd', borderRadius: '5px', overflow: 'hidden' }}>
            <button 
                onClick={() => setIsOpen(!isOpen)}
                style={{
                    width: '100%', padding: '10px', background: '#eee', border: 'none', 
                    textAlign: 'left', fontWeight: 'bold', cursor: 'pointer', display: 'flex', justifyContent: 'space-between'
                }}
            >
                {title} <span>{isOpen ? "▲" : "▼"}</span>
            </button>
            {isOpen && <div style={{ padding: '10px', background: '#fff', textAlign: 'left' }}>{content}</div>}
        </div>
    )
}

export default SecretSection