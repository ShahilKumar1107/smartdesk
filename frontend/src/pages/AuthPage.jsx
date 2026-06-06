import { useState } from 'react';
import { useAuth } from '../context/AuthContext';

export default function AuthPage() {
  const [isLogin, setIsLogin] = useState(true);
  const [email, setEmail] = useState('');
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const { login, register, loading, error } = useAuth();

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (isLogin) await login(email, password);
    else await register(email, username, password);
  };

  return (
    <div style={{minHeight:'100vh', background:'#0a0a0f', display:'flex', alignItems:'center', justifyContent:'center', padding:'1rem', fontFamily:"'DM Sans', sans-serif"}}>
      <link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500&family=Syne:wght@600;700&display=swap" rel="stylesheet"/>
      
      <div style={{width:'100%', maxWidth:'420px'}}>
        
        {/* Logo */}
        <div style={{textAlign:'center', marginBottom:'2rem'}}>
          <h1 style={{fontFamily:"'Syne', sans-serif", fontSize:'28px', fontWeight:'700', color:'#fff', letterSpacing:'-0.5px'}}>
            Smart<span style={{color:'#6C63FF'}}>Desk</span>
          </h1>
          <p style={{color:'rgba(255,255,255,0.3)', fontSize:'12px', marginTop:'4px', letterSpacing:'1px', textTransform:'uppercase'}}>
            AI Customer Support
          </p>
        </div>

        {/* Card */}
        <div style={{background:'#0e0e16', border:'1px solid rgba(255,255,255,0.08)', borderRadius:'16px', padding:'2rem'}}>
          
          {/* Toggle */}
          <div style={{display:'flex', background:'rgba(255,255,255,0.04)', borderRadius:'10px', padding:'4px', marginBottom:'1.5rem'}}>
            {['Login', 'Register'].map((tab) => (
              <button key={tab} onClick={() => setIsLogin(tab === 'Login')}
                style={{flex:1, padding:'8px', borderRadius:'8px', border:'none', cursor:'pointer', fontSize:'13px', fontWeight:'500', fontFamily:"'DM Sans', sans-serif", transition:'all 0.2s',
                  background: (isLogin && tab==='Login') || (!isLogin && tab==='Register') ? 'linear-gradient(135deg, #6C63FF, #9B8FFF)' : 'transparent',
                  color: (isLogin && tab==='Login') || (!isLogin && tab==='Register') ? '#fff' : 'rgba(255,255,255,0.35)'
                }}>
                {tab}
              </button>
            ))}
          </div>

          {/* Error */}
          {error && (
            <div style={{background:'rgba(255,80,80,0.1)', border:'1px solid rgba(255,80,80,0.3)', borderRadius:'8px', padding:'10px 14px', marginBottom:'1rem', fontSize:'12px', color:'#FF6B6B'}}>
              {error}
            </div>
          )}

          {/* Form */}
          <form onSubmit={handleSubmit} style={{display:'flex', flexDirection:'column', gap:'1rem'}}>
            {[
              {label:'Email', type:'email', value:email, setter:setEmail, placeholder:'you@example.com', show:true},
              {label:'Username', type:'text', value:username, setter:setUsername, placeholder:'johndoe', show:!isLogin},
              {label:'Password', type:'password', value:password, setter:setPassword, placeholder:'••••••••', show:true},
            ].filter(f => f.show).map(field => (
              <div key={field.label}>
                <label style={{display:'block', fontSize:'11px', color:'rgba(255,255,255,0.4)', marginBottom:'6px', letterSpacing:'0.5px', textTransform:'uppercase'}}>
                  {field.label}
                </label>
                <input type={field.type} value={field.value} onChange={e => field.setter(e.target.value)}
                  placeholder={field.placeholder} required
                  style={{width:'100%', background:'rgba(255,255,255,0.05)', border:'1px solid rgba(255,255,255,0.08)', borderRadius:'10px', padding:'11px 14px', color:'#fff', fontSize:'13px', fontFamily:"'DM Sans', sans-serif", outline:'none', boxSizing:'border-box'}}
                />
              </div>
            ))}

            <button type="submit" disabled={loading}
              style={{marginTop:'0.5rem', background:'linear-gradient(135deg, #6C63FF, #9B8FFF)', border:'none', borderRadius:'10px', padding:'13px', color:'#fff', fontSize:'14px', fontWeight:'500', fontFamily:"'DM Sans', sans-serif", cursor:'pointer', opacity:loading?0.7:1}}>
              {loading ? 'Please wait...' : isLogin ? 'Sign in' : 'Create account'}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}