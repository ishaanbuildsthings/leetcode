import pg from 'pg';
const { Client } = pg;
const conn = process.env.POSTGRES_URL_NON_POOLING.replace('?sslmode=require', '?sslmode=no-verify');
const c = new Client({ connectionString: conn });
await c.connect();

const total = await c.query(`SELECT COUNT(*)::int AS n FROM problems`);
const byPlatform = await c.query(`
  SELECT pl.name AS platform, COUNT(*)::int AS n
  FROM problems p
  JOIN platforms pl ON pl.id = p.platform_id
  GROUP BY pl.name
  ORDER BY n DESC, pl.name
`);

console.log('TOTAL:', total.rows[0].n);
console.log('BY_PLATFORM:', JSON.stringify(byPlatform.rows));

await c.end();
