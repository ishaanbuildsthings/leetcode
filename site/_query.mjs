import pg from 'pg';
const { Client } = pg;
const conn = process.env.POSTGRES_URL_NON_POOLING.replace('?sslmode=require', '?sslmode=no-verify');
const c = new Client({ connectionString: conn });
await c.connect();

const tagCheck = await c.query(`
  SELECT id, name, slug FROM tags
  WHERE slug ILIKE '%binary-search-tree%' OR name ILIKE '%binary search tree%'
`);
console.log('TAG MATCHES:', JSON.stringify(tagCheck.rows, null, 2));

const r = await c.query(`
  SELECT p.title, p.normalized_difficulty, p.platform_difficulty, p.url
  FROM problems p
  JOIN platforms pl ON pl.id = p.platform_id
  JOIN problem_tags pt ON pt.problem_id = p.id
  JOIN tags t ON t.id = pt.tag_id
  WHERE pl.slug = 'leetcode'
    AND t.slug = 'binary-search-tree'
    AND pt.role = 'core'
    AND pt.is_instructive = true
  ORDER BY p.normalized_difficulty NULLS LAST, p.title
`);
console.log('ROWS:', JSON.stringify(r.rows, null, 2));
await c.end();
