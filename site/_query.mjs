import pg from 'pg';
const { Client } = pg;
const conn = process.env.POSTGRES_URL_NON_POOLING.replace('?sslmode=require', '?sslmode=no-verify');
const c = new Client({ connectionString: conn });
await c.connect();

const r = await c.query(`
  SELECT p.title, p.normalized_difficulty AS nd, p.platform_difficulty AS pd
  FROM problems p
  JOIN platforms pl ON pl.id = p.platform_id
  WHERE pl.slug = 'leetcode'
  ORDER BY p.normalized_difficulty DESC NULLS LAST, p.title
  LIMIT 10
`);

console.log(JSON.stringify(r.rows));
await c.end();
