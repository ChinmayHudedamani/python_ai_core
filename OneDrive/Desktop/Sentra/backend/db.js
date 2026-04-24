const fs = require('fs');
const path = require('path');
const dbPath = path.join(__dirname, 'data', 'db.json');
function readDb(){ return JSON.parse(fs.readFileSync(dbPath,'utf8')); }
function writeDb(data){ fs.writeFileSync(dbPath, JSON.stringify(data,null,2)); }
module.exports = { readDb, writeDb };
