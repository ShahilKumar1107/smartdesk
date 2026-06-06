import { useState, useEffect, useRef } from 'react';
import { useAuth } from '../context/AuthContext';
import { getToken } from '../utils/api';
import api from '../utils/api';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

function TypingDots() {
  return (
    <div style={{display:'flex', gap:'4px', alignItems:'center', padding:'4px 0'}}>
      {[0,1,2].map(i => (
        <div key={i} style={{width:'6px', height:'6px', borderRadius:'50%', background:'rgba(255,255,255,0.3)',
          animation:'bounce 1.2s infinite', animationDelay:`${i*0.2}s`}}/>
      ))}
      <style>{`@keyframes bounce{0%,60%,100%{transform:translateY(0)}30%{transform:translateY(-5px)}}`}</style>
    </div>
  );
}

function MessageBubble({ message }) {
  const isUser = message.role === 'user';
  return (
    <div style={{display:'flex', gap:'8px', alignItems:'flex-end', flexDirection:isUser?'row-reverse':'row', marginBottom:'12px'}}>
      <div style={{width:'26px', height:'26px', borderRadius:'8px', flexShrink:0, display:'flex', alignItems:'center', justifyContent:'center', fontSize:'10px', fontWeight:'500', color:'#fff',
        background: isUser ? 'rgba(255,255,255,0.1)' : 'linear-gradient(135deg, #6C63FF, #9B8FFF)'}}>
        {isUser ? 'Y' : 'AI'}
      </div>
      <div style={{maxWidth:'75%', padding:'10px 14px', borderRadius:'14px', fontSize:'13px', lineHeight:'1.6',
        background: isUser ? 'linear-gradient(135deg, #6C63FF, #7B74FF)' : 'rgba(255,255,255,0.06)',
        color: isUser ? '#fff' : 'rgba(255,255,255,0.85)',
        borderBottomRightRadius: isUser ? '4px' : '14px',
        borderBottomLeftRadius: isUser ? '14px' : '4px',
        fontFamily:"'DM Sans', sans-serif",
        whiteSpace:'pre-wrap'
      }}>
        {message.content || <TypingDots />}
      </div>
    </div>
  );
}

export default function ChatPage() {
  const { user, logout } = useAuth();
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId, setSessionId] = useState(() => crypto.randomUUID());
  const [sessions, setSessions] = useState([]);
  const messagesEndRef = useRef(null);

  useEffect(() => { messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' }); }, [messages]);
  useEffect(() => { loadSessions(); }, []);

  const loadSessions = async () => {
    try {
      const r = await api.get('/api/v1/chat/sessions');
      setSessions(r.data.sessions || []);
    } catch {}
  };

  const loadHistory = async (sid) => {
    try {
      const r = await api.get(`/api/v1/chat/history/${sid}`);
      setMessages(r.data.messages || []);
      setSessionId(sid);
    } catch {}
  };

  const startNewChat = () => { setMessages([]); setSessionId(crypto.randomUUID()); };

  const sendMessage = async (text) => {
    const msg = text || input;
    if (!msg.trim() || isLoading) return;
    setMessages(prev => [...prev, {role:'user', content:msg}]);
    setInput('');
    setIsLoading(true);
    setMessages(prev => [...prev, {role:'assistant', content:''}]);

    try {
      const res = await fetch(`${API_BASE_URL}/api/v1/chat/`, {
        method:'POST',
        headers:{'Content-Type':'application/json','Authorization':`Bearer ${getToken()}`},
        body: JSON.stringify({message:msg, session_id:sessionId})
      });
      const reader = res.body.getReader();
      const decoder = new TextDecoder();
      while(true) {
        const {done, value} = await reader.read();
        if(done) break;
        const lines = decoder.decode(value).split('\n');
        for(const line of lines) {
          if(line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.slice(6));
              if(data.content && !data.done) {
                setMessages(prev => {
                  const u = [...prev];
                  u[u.length-1] = {...u[u.length-1], content: u[u.length-1].content + data.content};
                  return u;
                });
              }
            } catch {}
          }
        }
      }
      loadSessions();
    } catch {
      setMessages(prev => { const u=[...prev]; u[u.length-1].content='Sorry, something went wrong.'; return u; });
    } finally { setIsLoading(false); }
  };

  const suggestions = ["What is your return policy?", "Where is my order ORD-001?", "How long does shipping take?"];

  return (
    <div style={{display:'flex', height:'100vh', background:'#0a0a0f', fontFamily:"'DM Sans', sans-serif", overflow:'hidden'}}>
      <link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500&family=Syne:wght@600;700&display=swap" rel="stylesheet"/>

      {/* Sidebar */}
      <div style={{width:'240px', background:'#0a0a12', borderRight:'1px solid rgba(255,255,255,0.06)', display:'flex', flexDirection:'column', flexShrink:0}}>
        <div style={{padding:'20px 16px 14px', borderBottom:'1px solid rgba(255,255,255,0.06)'}}>
          <h1 style={{fontFamily:"'Syne', sans-serif", fontSize:'18px', fontWeight:'700', color:'#fff', letterSpacing:'-0.3px'}}>
            Smart<span style={{color:'#6C63FF'}}>Desk</span>
          </h1>
          <p style={{fontSize:'10px', color:'rgba(255,255,255,0.25)', marginTop:'2px', letterSpacing:'0.5px', textTransform:'uppercase'}}>
            AI Support Platform
          </p>
        </div>

        <div style={{padding:'12px'}}>
          <button onClick={startNewChat}
            style={{width:'100%', background:'linear-gradient(135deg, #6C63FF, #9B8FFF)', border:'none', borderRadius:'10px', padding:'9px 14px', color:'#fff', fontSize:'12px', fontFamily:"'DM Sans', sans-serif", fontWeight:'500', cursor:'pointer', display:'flex', alignItems:'center', gap:'6px'}}>
            <span style={{fontSize:'16px', lineHeight:1}}>+</span> New conversation
          </button>
        </div>

        <div style={{flex:1, overflowY:'auto', padding:'0 8px'}}>
          <p style={{fontSize:'9px', color:'rgba(255,255,255,0.2)', textTransform:'uppercase', letterSpacing:'1px', padding:'8px 8px 4px'}}>Recent</p>
          {sessions.map(s => (
            <button key={s.session_id} onClick={() => loadHistory(s.session_id)}
              style={{width:'100%', textAlign:'left', padding:'8px 10px', borderRadius:'8px', border:'none', cursor:'pointer', marginBottom:'2px', fontFamily:"'DM Sans', sans-serif",
                background: s.session_id === sessionId ? 'rgba(108,99,255,0.15)' : 'transparent'}}>
              <p style={{fontSize:'11px', color: s.session_id===sessionId ? 'rgba(255,255,255,0.8)' : 'rgba(255,255,255,0.4)', whiteSpace:'nowrap', overflow:'hidden', textOverflow:'ellipsis'}}>
                {s.session_id===sessionId && <span style={{width:'6px', height:'6px', borderRadius:'50%', background:'#6C63FF', display:'inline-block', marginRight:'6px', verticalAlign:'middle'}}/>}
                Chat {s.session_id.slice(0,8)}...
              </p>
            </button>
          ))}
        </div>

        <div style={{padding:'12px 14px', borderTop:'1px solid rgba(255,255,255,0.06)', display:'flex', alignItems:'center', gap:'8px'}}>
          <div style={{width:'28px', height:'28px', borderRadius:'50%', background:'linear-gradient(135deg, #6C63FF, #FF6B9D)', display:'flex', alignItems:'center', justifyContent:'center', fontSize:'11px', fontWeight:'500', color:'#fff', flexShrink:0}}>
            {user?.username?.[0]?.toUpperCase() || 'U'}
          </div>
          <div style={{flex:1, minWidth:0}}>
            <p style={{fontSize:'11px', color:'rgba(255,255,255,0.6)', overflow:'hidden', textOverflow:'ellipsis', whiteSpace:'nowrap'}}>{user?.email}</p>
            <button onClick={logout} style={{background:'none', border:'none', cursor:'pointer', fontSize:'10px', color:'rgba(255,255,255,0.25)', padding:0, fontFamily:"'DM Sans', sans-serif"}}>
              Sign out
            </button>
          </div>
        </div>
      </div>

      {/* Chat Area */}
      <div style={{flex:1, display:'flex', flexDirection:'column', minWidth:0}}>
        
        {/* Header */}
        <div style={{padding:'14px 20px', borderBottom:'1px solid rgba(255,255,255,0.06)', display:'flex', alignItems:'center', gap:'10px', background:'#0e0e16'}}>
          <div style={{width:'34px', height:'34px', borderRadius:'10px', background:'linear-gradient(135deg, #6C63FF, #9B8FFF)', display:'flex', alignItems:'center', justifyContent:'center', fontFamily:"'Syne', sans-serif", fontSize:'11px', fontWeight:'700', color:'#fff', flexShrink:0}}>
            SD
          </div>
          <div>
            <p style={{fontSize:'14px', fontWeight:'500', color:'#fff'}}>SmartDesk AI</p>
            <p style={{fontSize:'10px', color:'rgba(255,255,255,0.3)'}}>
              <span style={{width:'6px', height:'6px', background:'#4ADE80', borderRadius:'50%', display:'inline-block', marginRight:'4px', verticalAlign:'middle'}}/>
              Online · Powered by Gemini
            </p>
          </div>
        </div>

        {/* Messages */}
        <div style={{flex:1, overflowY:'auto', padding:'20px'}}>
          {messages.length === 0 && (
            <div style={{display:'flex', flexDirection:'column', alignItems:'center', justifyContent:'center', height:'100%', textAlign:'center', gap:'16px'}}>
              <div style={{width:'56px', height:'56px', borderRadius:'16px', background:'linear-gradient(135deg, #6C63FF, #9B8FFF)', display:'flex', alignItems:'center', justifyContent:'center', fontFamily:"'Syne', sans-serif", fontSize:'18px', fontWeight:'700', color:'#fff'}}>
                SD
              </div>
              <div>
                <h2 style={{fontSize:'20px', fontWeight:'500', color:'#fff', fontFamily:"'Syne', sans-serif"}}>How can I help you?</h2>
                <p style={{fontSize:'13px', color:'rgba(255,255,255,0.3)', marginTop:'6px'}}>Ask about orders, policies, or anything else</p>
              </div>
              <div style={{display:'flex', flexDirection:'column', gap:'8px', width:'100%', maxWidth:'400px', marginTop:'8px'}}>
                {suggestions.map(s => (
                  <button key={s} onClick={() => sendMessage(s)}
                    style={{textAlign:'left', background:'rgba(255,255,255,0.04)', border:'1px solid rgba(255,255,255,0.08)', borderRadius:'10px', padding:'12px 16px', fontSize:'13px', color:'rgba(255,255,255,0.5)', cursor:'pointer', fontFamily:"'DM Sans', sans-serif', transition:'all 0.2s'"}}>
                    {s}
                  </button>
                ))}
              </div>
            </div>
          )}
          {messages.map((m, i) => <MessageBubble key={i} message={m} />)}
          <div ref={messagesEndRef}/>
        </div>

        {/* Input */}
        <div style={{padding:'12px 16px', borderTop:'1px solid rgba(255,255,255,0.06)', background:'#0e0e16'}}>
          <div style={{display:'flex', gap:'8px', alignItems:'center'}}>
            <input value={input} onChange={e => setInput(e.target.value)}
              onKeyDown={e => { if(e.key==='Enter' && !e.shiftKey){e.preventDefault(); sendMessage();}}}
              placeholder="Ask anything about your orders or policies..."
              style={{flex:1, background:'rgba(255,255,255,0.05)', border:'1px solid rgba(255,255,255,0.08)', borderRadius:'12px', padding:'11px 16px', color:'rgba(255,255,255,0.8)', fontSize:'13px', fontFamily:"'DM Sans', sans-serif", outline:'none'}}
            />
            <button onClick={() => sendMessage()} disabled={isLoading || !input.trim()}
              style={{width:'40px', height:'40px', borderRadius:'10px', background: isLoading||!input.trim() ? 'rgba(255,255,255,0.05)' : 'linear-gradient(135deg, #6C63FF, #9B8FFF)', border:'none', cursor: isLoading||!input.trim() ? 'not-allowed' : 'pointer', display:'flex', alignItems:'center', justifyContent:'center', flexShrink:0, transition:'all 0.2s'}}>
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2.5"><line x1="22" y1="2" x2="11" y2="13"/><polygon points="22 2 15 22 11 13 2 9 22 2"/></svg>
            </button>
          </div>
          <p style={{fontSize:'10px', color:'rgba(255,255,255,0.12)', textAlign:'center', marginTop:'8px', letterSpacing:'0.3px'}}>
            SmartDesk AI · Powered by Gemini 2.5
          </p>
        </div>
      </div>
    </div>
  );
}