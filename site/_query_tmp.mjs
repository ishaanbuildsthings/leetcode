import pg from 'pg';
const { Client } = pg;
const conn = process.env.POSTGRES_URL_NON_POOLING.replace('?sslmode=require','?sslmode=no-verify');
const c = new Client({ connectionString: conn });
await c.connect();
const res = await c.query(`
  select
    count(*) filter (where pt.problem_id is not null) as categorized,
    count(*) filter (where pt.problem_id is null) as uncategorized,
    count(*) as total
  from (
    select distinct pr.id
    from problems pr join platforms p on p.id = pr.platform_id
    where p.slug = 'leetcode'
  ) pr
  left join (select distinct problem_id from problem_tags) pt on pt.problem_id = pr.id
`);
console.table(res.rows);
await c.end();
