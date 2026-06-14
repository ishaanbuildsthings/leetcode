import pg from 'pg';
const { Client } = pg;
const conn = process.env.POSTGRES_URL_NON_POOLING.replace('?sslmode=require','?sslmode=no-verify');
const c = new Client({ connectionString: conn });
await c.connect();
const total = await c.query(`SELECT COUNT(*) n FROM problems p JOIN platforms pl ON pl.id=p.platform_id WHERE pl.slug='leetcode'`);
const tagged = await c.query(`
  SELECT COUNT(DISTINCT p.id) n
  FROM problems p
  JOIN platforms pl ON pl.id=p.platform_id
  JOIN problem_tags pt ON pt.problem_id=p.id
  WHERE pl.slug='leetcode'`);
console.log('total LC:', total.rows[0].n);
console.log('LC with >=1 tag:', tagged.rows[0].n);
await c.end();
