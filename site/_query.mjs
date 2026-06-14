import pg from 'pg';
const { Client } = pg;
const conn = process.env.POSTGRES_URL_NON_POOLING.replace('?sslmode=require','?sslmode=no-verify');
const c = new Client({ connectionString: conn });
await c.connect();
const r = await c.query(`SELECT COUNT(*) n FROM problems p JOIN platforms pl ON pl.id=p.platform_id WHERE pl.slug='leetcode'`);
console.log(r.rows[0].n);
await c.end();
