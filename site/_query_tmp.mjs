import pg from 'pg';
const { Client } = pg;
const conn = process.env.POSTGRES_URL_NON_POOLING.replace('?sslmode=require','?sslmode=no-verify');
const c = new Client({ connectionString: conn });
await c.connect();
const res = await c.query(`
  select count(*) as total
  from problems pr join platforms p on p.id = pr.platform_id
  where p.slug = 'leetcode'
`);
console.table(res.rows);
await c.end();
