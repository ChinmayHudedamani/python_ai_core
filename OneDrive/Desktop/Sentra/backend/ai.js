function sentiment(text=''){
  const positive=['excellent','good','clean','great','amazing','happy','fast'];
  const negative=['bad','slow','dirty','poor','delay','worst','okay'];
  const t=text.toLowerCase(); let score=0;
  positive.forEach(w=>{ if(t.includes(w)) score++; });
  negative.forEach(w=>{ if(t.includes(w)) score--; });
  return score>0?'Positive':score<0?'Negative':'Neutral';
}
function dynamicPrice(basePrice, occupancy){
  let multiplier = occupancy > 75 ? 1.25 : occupancy > 50 ? 1.1 : occupancy < 30 ? 0.85 : 1;
  return Math.round(basePrice * multiplier);
}
function noShowRisk(booking){
  let risk = 20;
  if(booking.source === 'OTA') risk += 20;
  if(booking.status === 'Reserved') risk += 10;
  return Math.min(risk, 90);
}
function maintenanceRisk(room){
  if(room.status === 'Cleaning') return 'Medium';
  if(room.status === 'Maintenance') return 'High';
  return 'Low';
}
module.exports={sentiment,dynamicPrice,noShowRisk,maintenanceRisk};
