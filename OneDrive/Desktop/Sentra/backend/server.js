require('dotenv').config();
const express = require('express');
const cors = require('cors');
const { v4: uuid } = require('uuid');
const { readDb, writeDb } = require('./db');
const ai = require('./ai');
const app = express();
app.use(cors());
app.use(express.json());

const makeCrud = (name) => {
  app.get(`/api/${name}`, (req,res)=> res.json(readDb()[name] || []));
  app.post(`/api/${name}`, (req,res)=> { const db=readDb(); const item={id:req.body.id || uuid(), ...req.body}; db[name].push(item); writeDb(db); res.status(201).json(item); });
  app.put(`/api/${name}/:id`, (req,res)=> { const db=readDb(); const i=db[name].findIndex(x=>x.id===req.params.id); if(i<0) return res.status(404).json({message:'Not found'}); db[name][i]={...db[name][i],...req.body}; writeDb(db); res.json(db[name][i]); });
  app.delete(`/api/${name}/:id`, (req,res)=> { const db=readDb(); db[name]=db[name].filter(x=>x.id!==req.params.id); writeDb(db); res.json({success:true}); });
};
['rooms','customers','bookings','housekeeping','payments','feedback','foodOrders','services','amenities','staff'].forEach(makeCrud);
app.get('/api/revenueSeries', (req,res)=> res.json(readDb().revenueSeries || []));

app.post('/api/login', (req,res)=> {
  const { email, password } = req.body;
  const users = [
    { name: 'Chinmay', email: 'chinmay@hoteliq.com', password: 'chinmay123', role: 'Owner / Admin' },
    { name: 'Krutick', email: 'krutick@hoteliq.com', password: 'krutick123', role: 'Co-Founder / Manager' },
    { name: 'Hotel Team', email: 'team@hoteliq.com', password: 'team123', role: 'Operations Staff' }
  ];
  const user = users.find(u => u.email.toLowerCase() === String(email || '').toLowerCase() && u.password === password);
  if(!user) return res.status(401).json({message:'Invalid email or password'});
  const { password: _, ...safeUser } = user;
  res.json({token:`demo-token-${safeUser.role.toLowerCase().replaceAll(' ','-')}`, user:safeUser});
});

app.get('/api/dashboard', (req,res)=> {
  const db=readDb();
  const totalRooms=db.rooms.length;
  const occupied=db.rooms.filter(r=>r.status==='Occupied').length;
  const occupancy=Math.round((occupied/totalRooms)*100);
  const revenue=db.payments.filter(p=>p.status==='Paid').reduce((s,p)=>s+p.amount,0);
  const pendingTasks=db.housekeeping.filter(h=>h.status!=='Done').length;
  const available=db.rooms.filter(r=>r.status==='Available').length; const maintenance=db.rooms.filter(r=>r.status==='Maintenance').length; const avgRating=Math.round((db.feedback.reduce((s,f)=>s+f.rating,0)/db.feedback.length)*10)/10; res.json({totalRooms, occupied, available, maintenance, occupancy, revenue, pendingTasks, bookings:db.bookings.length, customers:db.customers.length, avgRating});
});

app.get('/api/ai/command-center', (req,res)=> {
  const db=readDb();
  const occupancy = Math.round((db.rooms.filter(r=>r.status==='Occupied').length / db.rooms.length) * 100);
  const pricing = db.rooms.map(r=>({room:r.number,type:r.type,currentPrice:r.price,suggestedPrice:ai.dynamicPrice(r.price,occupancy)}));
  const feedback = db.feedback.map(f=>({...f, sentiment: ai.sentiment(f.comment)}));
  const noShow = db.bookings.map(b=>({...b, riskPercent: ai.noShowRisk(b)}));
  const maintenance = db.rooms.map(r=>({room:r.number, risk: ai.maintenanceRisk(r)}));
  const alerts = [
    occupancy > 70 ? 'High occupancy detected: increase room rates.' : 'Occupancy normal.',
    db.housekeeping.some(h=>h.priority==='High' && h.status!=='Done') ? 'High priority housekeeping pending.' : 'Housekeeping normal.',
    feedback.some(f=>f.sentiment==='Negative') ? 'Negative feedback detected: manager review needed.' : 'Guest sentiment healthy.'
  ];
  res.json({occupancy, pricing, feedback, noShow, maintenance, alerts});
});

app.post('/api/ai/assistant', (req,res)=> {
  const q=(req.body.question||'').toLowerCase(); const db=readDb();
  if(q.includes('occupancy')) return res.json({answer:`Current occupancy is ${Math.round((db.rooms.filter(r=>r.status==='Occupied').length/db.rooms.length)*100)}%.`});
  if(q.includes('revenue')) return res.json({answer:`Total paid revenue is ₹${db.payments.filter(p=>p.status==='Paid').reduce((s,p)=>s+p.amount,0)}.`});
  if(q.includes('clean')) return res.json({answer:`${db.housekeeping.filter(h=>h.status!=='Done').length} housekeeping tasks are pending.`});
  res.json({answer:'I can answer about occupancy, revenue, rooms, bookings, housekeeping and AI alerts.'});
});

const PORT=process.env.PORT || 5000;
app.listen(PORT, ()=> console.log(`Smart Hotel backend running on http://localhost:${PORT}`));
