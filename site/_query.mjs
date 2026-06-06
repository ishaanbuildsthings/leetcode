import pg from 'pg';
const { Client } = pg;
const conn = process.env.POSTGRES_URL_NON_POOLING.replace('?sslmode=require', '?sslmode=no-verify');
const c = new Client({ connectionString: conn });
await c.connect();

// First, find the tag IDs to make sure we have the right slugs
const tagCheck = await c.query(`
  SELECT id, name, slug FROM tags
  WHERE slug ILIKE '%inclusion%' OR slug ILIKE '%exclusion%'
     OR slug ILIKE '%dynamic%programming%' OR slug = 'dp'
     OR name ILIKE '%inclusion%exclusion%' OR name ILIKE '%dynamic programming%'
  ORDER BY name
`);
console.log('TAG_MATCHES:', JSON.stringify(tagCheck.rows, null, 2));

// Problems that have BOTH tags (any role)
const r = await c.query(`
  WITH ie AS (
    SELECT pt.problem_id, pt.role AS ie_role
    FROM problem_tags pt
    JOIN tags t ON t.id = pt.tag_id
    WHERE t.name ILIKE '%inclusion%exclusion%' OR t.slug ILIKE '%inclusion%exclusion%'
  ),
  dp AS (
    SELECT pt.problem_id, pt.role AS dp_role
    FROM problem_tags pt
    JOIN tags t ON t.id = pt.tag_id
    WHERE t.name ILIKE '%dynamic programming%' OR t.slug = 'dynamic-programming' OR t.slug = 'dp'
  )
  SELECT
    p.title,
    pl.name AS platform,
    p.platform_difficulty AS pd,
    p.normalized_difficulty AS nd,
    p.is_great_problem AS great,
    ie.ie_role,
    dp.dp_role,
    p.url
  FROM problems p
  JOIN platforms pl ON pl.id = p.platform_id
  JOIN ie ON ie.problem_id = p.id
  JOIN dp ON dp.problem_id = p.id
  ORDER BY p.normalized_difficulty DESC NULLS LAST, p.title
`);
console.log('COUNT:', r.rows.length);
console.log('ROWS:', JSON.stringify(r.rows, null, 2));

await c.end();
