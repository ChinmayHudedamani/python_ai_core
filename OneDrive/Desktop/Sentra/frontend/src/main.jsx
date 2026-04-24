import React, { useEffect, useMemo, useState } from 'react';
import { createRoot } from 'react-dom/client';
import {
  Hotel, LayoutDashboard, Brain, BedDouble, CalendarCheck, Users, Sparkles,
  IndianRupee, Star, Bell, Search, ShieldCheck, Utensils, LogOut,
  CreditCard, MessageSquareText, ClipboardCheck, UserCog, ArrowUpRight,
  Crown, Zap, Clock, Bot, CheckCircle2, AlertTriangle, LockKeyhole, UserRoundCheck
} from 'lucide-react';
import {
  AreaChart, Area, BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell, LineChart, Line
} from 'recharts';
import './style.css';

const API = 'http://localhost:5000/api';
const nav = [
  ['Dashboard', LayoutDashboard], ['AI Command Center', Brain], ['Rooms', BedDouble],
  ['Bookings', CalendarCheck], ['Customers', Users], ['Housekeeping', ClipboardCheck],
  ['Payments', CreditCard], ['Feedback', MessageSquareText], ['Food Orders', Utensils],
  ['Services', Sparkles], ['Amenities', Star], ['Staff', UserCog]
];

function App() {
  const [tab, setTab] = useState('Dashboard');
  const [data, setData] = useState({});
  const [ai, setAi] = useState(null);
  const [query, setQuery] = useState('');
  const [question, setQuestion] = useState('What is the occupancy and revenue today?');
  const [answer, setAnswer] = useState('Ask me about occupancy, revenue, rooms, bookings, housekeeping or alerts.');
  const [loading, setLoading] = useState(true);
  const [auth, setAuth] = useState(() => {
    const saved = localStorage.getItem('hoteliq-auth');
    return saved ? JSON.parse(saved) : null;
  });

  async function load() {
    const keys = ['dashboard', 'rooms', 'customers', 'bookings', 'housekeeping', 'payments', 'feedback', 'foodOrders', 'services', 'amenities', 'staff', 'revenueSeries'];
    const next = {};
    for (const k of keys) next[k] = await (await fetch(`${API}/${k}`)).json();
    setData(next);
    setAi(await (await fetch(`${API}/ai/command-center`)).json());
    setLoading(false);
  }
  useEffect(() => { if (auth) load(); }, [auth]);

  async function askAI() {
    setAnswer('Thinking like a hotel revenue manager...');
    const res = await fetch(`${API}/ai/assistant`, {
      method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ question })
    });
    setAnswer((await res.json()).answer);
  }

  const filteredRooms = useMemo(() => (data.rooms || []).filter(r => JSON.stringify(r).toLowerCase().includes(query.toLowerCase())), [data.rooms, query]);
  const roomMix = useMemo(() => {
    const rooms = data.rooms || [];
    return ['Available', 'Occupied', 'Reserved', 'Cleaning', 'Maintenance'].map(name => ({ name, value: rooms.filter(r => r.status === name).length })).filter(x => x.value);
  }, [data.rooms]);

  async function handleLogin(credentials) {
    const res = await fetch(`${API}/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(credentials)
    });
    const payload = await res.json();
    if (!res.ok) throw new Error(payload.message || 'Login failed');
    localStorage.setItem('hoteliq-auth', JSON.stringify(payload));
    setAuth(payload);
  }

  function logout() {
    localStorage.removeItem('hoteliq-auth');
    setAuth(null);
    setLoading(true);
  }

  if (!auth) return <Login onLogin={handleLogin} />;
  if (loading) return <Splash />;

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand reveal">
          <div className="brand-mark"><Hotel size={28} /></div>
          <div><h2>HotelIQ</h2><p>Smart PMS Suite</p></div>
        </div>
        <div className="nav-list">
          {nav.map(([name, Icon], i) => <button key={name} style={{ animationDelay: `${i * 45}ms` }} className={`nav-btn reveal ${tab === name ? 'active' : ''}`} onClick={() => setTab(name)}><Icon size={18} />{name}</button>)}
        </div>
        <div className="side-card floaty">
          <Crown size={20} />
          <b>Created by</b>
          <span>Chinmay & Krutick</span>
          <small>AI hotel suite • ready for client demo</small>
        </div>
      </aside>

      <main className="main">
        <TopBar tab={tab} user={auth.user} onLogout={logout} />
        {tab === 'Dashboard' && <Dashboard data={data} ai={ai} roomMix={roomMix} setTab={setTab} />}
        {tab === 'AI Command Center' && <AI ai={ai} question={question} setQuestion={setQuestion} askAI={askAI} answer={answer} />}
        {tab === 'Rooms' && <Rooms rows={filteredRooms} query={query} setQuery={setQuery} />}
        {tab === 'Bookings' && <TablePage icon={<CalendarCheck />} title="Booking Pipeline" rows={data.bookings} />}
        {tab === 'Customers' && <Customers rows={data.customers} />}
        {tab === 'Housekeeping' && <TaskBoard rows={data.housekeeping} />}
        {tab === 'Payments' && <TablePage icon={<CreditCard />} title="Payments & Invoices" rows={data.payments} />}
        {tab === 'Feedback' && <Feedback rows={data.feedback} />}
        {tab === 'Food Orders' && <TablePage icon={<Utensils />} title="In-Room Dining Orders" rows={data.foodOrders} />}
        {tab === 'Services' && <Services rows={data.services} />}
        {tab === 'Amenities' && <Amenities rows={data.amenities} />}
        {tab === 'Staff' && <TablePage icon={<UserCog />} title="Staff Console" rows={data.staff} />}
        <footer className="credits">Created by <b>Chinmay</b> and <b>Krutick</b> • Smart Hotel Management System</footer>
      </main>
    </div>
  );
}

function Login({ onLogin }) {
  const [email, setEmail] = useState('chinmay@hoteliq.com');
  const [password, setPassword] = useState('chinmay123');
  const [error, setError] = useState('');
  const [busy, setBusy] = useState(false);
  async function submit(e) {
    e.preventDefault();
    setBusy(true);
    setError('');
    try { await onLogin({ email, password }); }
    catch (err) { setError(err.message); }
    finally { setBusy(false); }
  }
  const quickUsers = [
    ['chinmay@hoteliq.com', 'Chinmay Admin', 'chinmay123'],
    ['krutick@hoteliq.com', 'Krutick Manager', 'krutick123'],
    ['team@hoteliq.com', 'Hotel Team', 'team123']
  ];
  return <div className="login-page">
    <section className="login-showcase reveal-up">
      <div className="brand big"><div className="brand-mark"><Hotel size={34}/></div><div><h2>HotelIQ</h2><p>AI Smart Hotel Management System</p></div></div>
      <h1>Run your hotel like a premium brand.</h1>
      <p>Bookings, rooms, payments, housekeeping, guest intelligence and AI alerts in one beautiful dashboard.</p>
      <div className="login-stats"><span><b>94%</b> peak occupancy</span><span><b>₹5.4L</b> weekly demo revenue</span><span><b>AI</b> command center</span></div>
      <div className="creator-badge">Created by <b>Chinmay</b> & <b>Krutick</b></div>
    </section>
    <form className="login-card reveal" onSubmit={submit}>
      <LockKeyhole size={34}/><h2>Secure Login</h2><p>Use demo credentials or select a role.</p>
      {error && <div className="login-error">{error}</div>}
      <label>Email<input value={email} onChange={e=>setEmail(e.target.value)} placeholder="chinmay@hoteliq.com" /></label>
      <label>Password<input type="password" value={password} onChange={e=>setPassword(e.target.value)} placeholder="chinmay123" /></label>
      <button disabled={busy}>{busy ? 'Signing in...' : 'Login to Dashboard'}</button>
      <div className="quick-login">
        {quickUsers.map(([mail, role, pass]) => <button type="button" className="mini-btn" key={mail} onClick={()=>{setEmail(mail); setPassword(pass)}}><UserRoundCheck size={15}/>{role}</button>)}
      </div>
      <small>Credentials: <b>chinmay@hoteliq.com / chinmay123</b><br/><b>krutick@hoteliq.com / krutick123</b></small>
    </form>
  </div>
}
function Splash() { return <div className="splash"><div className="pulse-logo"><Hotel /></div><h1>Loading HotelIQ</h1><p>Preparing premium hotel dashboard...</p></div>; }
function TopBar({ tab, user, onLogout }) { return <header className="hero reveal"><div><span className="eyebrow"><ShieldCheck size={16} /> Enterprise Hotel Operations</span><h1>{tab}</h1><p>Beautiful, animated and data-rich smart hotel management system.</p></div><div className="hero-actions"><button className="ghost"><Bell size={17} /> 3 alerts</button><button className="ghost user-pill"><UserRoundCheck size={17} /> {user?.name} • {user?.role}</button><button onClick={onLogout}><LogOut size={17} /> Logout</button></div></header>; }
function Dashboard({ data, ai, roomMix, setTab }) {
  const d = data.dashboard || {};
  return <div className="page-grid reveal-up">
    <section className="welcome-card gradient-card">
      <div><span className="eyebrow"><Zap size={16}/> Live Command Dashboard</span><h2>Good evening, Hotel Team 👋</h2><p>Your hotel is running at <b>{d.occupancy}% occupancy</b>. AI recommends reviewing premium room rates and high-priority housekeeping.</p><button onClick={() => setTab('AI Command Center')}>Open AI Command Center <ArrowUpRight size={16}/></button></div>
      <div className="orb orb-a"/><div className="orb orb-b"/>
    </section>
    <div className="kpi-grid">
      <Kpi icon={<BedDouble />} label="Total Rooms" value={d.totalRooms} hint={`${d.available || 0} available`} />
      <Kpi icon={<IndianRupee />} label="Paid Revenue" value={`₹${(d.revenue || 0).toLocaleString('en-IN')}`} hint="Today" />
      <Kpi icon={<CalendarCheck />} label="Bookings" value={d.bookings} hint="Active pipeline" />
      <Kpi icon={<Star />} label="Avg Rating" value={d.avgRating || 0} hint="Guest happiness" />
    </div>
    <section className="chart-card wide"><h3>Weekly Revenue Trend</h3><ResponsiveContainer width="100%" height={290}><AreaChart data={data.revenueSeries}><defs><linearGradient id="rev" x1="0" y1="0" x2="0" y2="1"><stop offset="5%" stopColor="#8b5cf6" stopOpacity={0.8}/><stop offset="95%" stopColor="#8b5cf6" stopOpacity={0.05}/></linearGradient></defs><XAxis dataKey="day"/><YAxis/><Tooltip/><Area type="monotone" dataKey="revenue" stroke="#8b5cf6" fill="url(#rev)" strokeWidth={3}/></AreaChart></ResponsiveContainer></section>
    <section className="chart-card"><h3>Room Status</h3><ResponsiveContainer width="100%" height={260}><PieChart><Pie data={roomMix} dataKey="value" nameKey="name" innerRadius={58} outerRadius={90} paddingAngle={5}>{roomMix.map((_, i) => <Cell key={i} fill={['#22c55e','#3b82f6','#f59e0b','#a855f7','#ef4444'][i % 5]} />)}</Pie><Tooltip/></PieChart></ResponsiveContainer></section>
    <section className="chart-card"><h3>Occupancy Forecast</h3><ResponsiveContainer width="100%" height={260}><LineChart data={data.revenueSeries}><XAxis dataKey="day"/><YAxis/><Tooltip/><Line type="monotone" dataKey="occupancy" stroke="#06b6d4" strokeWidth={3} dot={{ r: 5 }}/></LineChart></ResponsiveContainer></section>
    <HotelGallery />
    <section className="amenity-strip wide"><div><span className="eyebrow"><Star size={16}/> Luxury Amenities</span><h3>Designed for a premium guest experience</h3></div><div className="amenity-mini">{(data.amenities || []).slice(0,6).map(a=><span key={a.id}>{a.icon} {a.name}</span>)}</div><button onClick={() => setTab('Amenities')}>View Amenities</button></section>
    <section className="alerts wide"><h3>Smart Alerts</h3>{(ai?.alerts || []).map((a, i) => <div className="alert-row" key={i}><AlertTriangle size={18}/><span>{a}</span></div>)}</section>
  </div>
}
function AI({ ai, question, setQuestion, askAI, answer }) { return <div className="reveal-up"><div className="ai-hero"><Brain size={42}/><div><h2>AI Command Center</h2><p>Revenue intelligence, no-show risk, maintenance prediction and sentiment analysis in one place.</p></div></div><section className="assistant-card"><div className="bot-bubble"><Bot/><span>{answer}</span></div><div className="ask-row"><input value={question} onChange={e=>setQuestion(e.target.value)} /><button onClick={askAI}>Ask AI</button></div></section><div className="split-grid"><SmartList title="Dynamic Pricing" rows={ai?.pricing || []}/><SmartList title="No-show Risk" rows={ai?.noShow || []}/><SmartList title="Guest Sentiment" rows={ai?.feedback || []}/><SmartList title="Maintenance Risk" rows={ai?.maintenance || []}/></div></div> }
function Rooms({ rows, query, setQuery }) { return <div className="reveal-up"><div className="toolbar"><div className="search"><Search size={18}/><input placeholder="Search rooms, view, features..." value={query} onChange={e=>setQuery(e.target.value)} /></div><button><BedDouble size={16}/> Add Room</button></div><div className="room-grid">{rows.map((r,i)=><RoomCard key={r.id} r={r} i={i}/>)}</div></div>; }
function RoomCard({ r, i }) { return <article className="room-card" style={{animationDelay:`${i*70}ms`}}><div className="room-img"><span>Room {r.number}</span><Status s={r.status}/></div><div className="room-body"><h3>{r.type}</h3><p>{r.view} View • Floor {r.floor}</p><div className="chips">{r.features?.map(f=><span key={f}>{f}</span>)}</div><div className="room-foot"><b>₹{r.price.toLocaleString('en-IN')}</b><button>View</button></div></div></article>; }
function Customers({ rows=[] }) { return <div className="customer-grid reveal-up">{rows.map(c=><section className="customer-card" key={c.id}><div className="avatar">{c.name[0]}</div><h3>{c.name} {c.vip && <Crown size={18}/>}</h3><p>{c.email}</p><div className="chips"><span>{c.loyalty}</span><span>{c.visits} visits</span></div><small>Preferences: {c.preferences}</small></section>)}</div> }
function TaskBoard({ rows=[] }) { return <div className="task-grid reveal-up">{rows.map(t=><section className="task-card" key={t.id}><div><Status s={t.priority}/><h3>{t.task}</h3><p>Room {t.roomId} • {t.assignedTo}</p></div><div className="eta"><Clock size={17}/>{t.eta}</div></section>)}</div> }
function Feedback({ rows=[] }) { return <div className="feedback-grid reveal-up">{rows.map(f=><section className="feedback-card" key={f.id}><div className="stars">{'★'.repeat(f.rating)}{'☆'.repeat(5-f.rating)}</div><p>“{f.comment}”</p><b>{f.customer}</b></section>)}</div> }
function HotelGallery() { const pics = ['Luxury Lobby','Infinity Pool','Premium Suite']; return <section className="gallery-card wide reveal-up"><div className="gallery-head"><div><span className="eyebrow"><Sparkles size={16}/> Visual Experience</span><h3>Modern hotel look for client demos</h3></div><button className="ghost dark">Marketing Ready</button></div><div className="photo-grid">{pics.map((p,i)=><div className={`photo-tile photo-${i+1}`} key={p}><span>{p}</span></div>)}</div></section> }
function Amenities({ rows=[] }) { return <div className="amenities-page reveal-up"><section className="amenities-hero"><div><span className="eyebrow"><Star size={16}/> Guest Amenities</span><h2>Everything guests love, managed beautifully.</h2><p>Showcase hotel facilities with bookings, availability, pricing and guest-ready visuals.</p></div></section><div className="amenity-grid">{rows.map((a,i)=><article className="amenity-card" style={{animationDelay:`${i*70}ms`}} key={a.id}><div className="amenity-photo"><span>{a.icon}</span></div><div><h3>{a.name}</h3><p>{a.description}</p><div className="chips"><span>{a.hours}</span><span>{a.location}</span></div><div className="room-foot"><b>{a.price}</b><Status s={a.status}/></div></div></article>)}</div></div> }

function Services({ rows=[] }) { return <div className="service-grid reveal-up">{rows.map(s=><section className="service-card" key={s.id}><Sparkles/><h3>{s.name}</h3><p>₹{s.price.toLocaleString('en-IN')}</p><small>{s.bookingsToday} bookings today</small><button>Promote</button></section>)}</div> }
function TablePage({ icon, title, rows=[] }) { return <section className="table-card reveal-up"><h2>{icon}{title}</h2><Table rows={rows}/></section>; }
function SmartList({ title, rows=[] }) { return <section className="smart-list"><h3>{title}</h3>{rows.slice(0,6).map((r,i)=><div className="smart-row" key={i}>{Object.entries(r).slice(0,4).map(([k,v])=><span key={k}><small>{k}</small>{Array.isArray(v)?v.join(', '):String(v)}</span>)}</div>)}</section> }
function Kpi({ icon, label, value, hint }) { return <section className="kpi"><span>{icon}</span><p>{label}</p><h2>{value}</h2><small>{hint}</small></section>; }
function Status({ s }) { return <span className={`status ${String(s).toLowerCase().replaceAll(' ','-')}`}>{s}</span>; }
function Table({ rows=[] }) { const keys = rows[0] ? Object.keys(rows[0]) : []; return <div className="table-wrap"><table><thead><tr>{keys.map(k=><th key={k}>{k}</th>)}</tr></thead><tbody>{rows.map((r,i)=><tr key={i}>{keys.map(k=><td key={k}>{Array.isArray(r[k]) ? r[k].join(', ') : typeof r[k] === 'object' ? JSON.stringify(r[k]) : String(r[k])}</td>)}</tr>)}</tbody></table></div>; }

createRoot(document.getElementById('root')).render(<App />);
