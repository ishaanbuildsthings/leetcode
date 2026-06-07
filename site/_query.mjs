import pg from 'pg';
const { Client } = pg;
const conn = process.env.POSTGRES_URL_NON_POOLING.replace('?sslmode=require','?sslmode=no-verify');
const c = new Client({ connectionString: conn });
await c.connect();
const r = await c.query(`
  SELECT platform_difficulty, COUNT(*) AS n
  FROM problems p JOIN platforms pl ON pl.id = p.platform_id
  WHERE pl.slug = 'leetcode'
  GROUP BY platform_difficulty
  ORDER BY platform_difficulty
`);
console.table(r.rows);
const t = await c.query(`SELECT COUNT(*) AS n FROM problems p JOIN platforms pl ON pl.id=p.platform_id WHERE pl.slug='leetcode'`);
console.log('total:', t.rows[0].n);
await c.end();
