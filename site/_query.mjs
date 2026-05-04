import pg from 'pg';
const { Client } = pg;
const conn = process.env.POSTGRES_URL_NON_POOLING.replace('?sslmode=require','?sslmode=no-verify');
const c = new Client({ connectionString: conn });
await c.connect();
const r = await c.query(
  `INSERT INTO platforms (name, slug) VALUES ($1, $2) RETURNING id, name, slug`,
  ['Eolymp', 'eolymp']
);
console.log(JSON.stringify(r.rows, null, 2));
await c.end();
