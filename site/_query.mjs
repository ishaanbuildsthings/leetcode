import pg from 'pg';
const { Client } = pg;
const conn = process.env.POSTGRES_URL_NON_POOLING.replace('?sslmode=require','?sslmode=no-verify');
const c = new Client({ connectionString: conn });
await c.connect();
const r = await c.query(`
  SELECT normalized_difficulty AS d, COUNT(*)::int AS n
  FROM problems
  GROUP BY normalized_difficulty
  ORDER BY normalized_difficulty NULLS LAST
`);
console.log(JSON.stringify(r.rows));
await c.end();
