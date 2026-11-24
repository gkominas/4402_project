-- =====================================================================
-- CSC 4402 Project: Esports Organization Database
-- test_queries.sql - five test queries (PostgreSQL)
--
-- Run schema.sql and seed.sql first, then:
--   psql "$DATABASE_URL" -P pager=off -f test_queries.sql
-- The queries only read data, so they can be run any number of times.
-- =====================================================================

-- ---------------------------------------------------------------------
-- Query 1: Roster
-- Who are each team's starters, what role do they play, and when does
-- their current contract end?  (5-table join)
-- ---------------------------------------------------------------------
SELECT g.title                              AS game,
       t.team_name,
       p.gamer_tag,
       pe.first_name || ' ' || pe.last_name AS player_name,
       p.in_game_role,
       c.end_date                           AS contract_ends
FROM game g
JOIN team t             ON t.game_id = g.game_id
JOIN player p           ON p.team_id = t.team_id
JOIN person pe          ON pe.person_id = p.person_id
JOIN player_contract c  ON c.player_id = p.person_id
WHERE p.is_starter
  AND c.status = 'Active'
ORDER BY g.title, t.roster_type DESC, p.in_game_role;

-- ---------------------------------------------------------------------
-- Query 2: Performance
-- How did each player average in one tournament?  (GROUP BY + AVG)
-- ---------------------------------------------------------------------
SELECT t.team_name,
       p.gamer_tag,
       COUNT(*)                  AS matches_played,
       ROUND(AVG(s.kills), 1)    AS avg_kills,
       ROUND(AVG(s.deaths), 1)   AS avg_deaths,
       ROUND(AVG(s.assists), 1)  AS avg_assists
FROM player_match_stats s
JOIN match m        ON m.match_id = s.match_id
JOIN tournament tr  ON tr.tournament_id = m.tournament_id
JOIN player p       ON p.person_id = s.player_id
JOIN team t         ON t.team_id = m.team_id
WHERE tr.name = 'Spike Circuit Finals 2026'
GROUP BY t.team_name, p.person_id, p.gamer_tag
ORDER BY t.team_name, AVG(s.kills) DESC, p.gamer_tag;

-- ---------------------------------------------------------------------
-- Query 3: Revenue
-- How much is each team's current sponsorship worth per year?
-- LEFT JOIN keeps teams that have no current sponsor.  (SUM + ORDER BY)
-- ---------------------------------------------------------------------
SELECT t.team_name,
       COUNT(sp.sponsorship_id)          AS active_sponsorships,
       COALESCE(SUM(sp.annual_value), 0) AS total_annual_value
FROM team t
LEFT JOIN sponsorship sp
       ON sp.team_id = t.team_id
      AND CURRENT_DATE BETWEEN sp.start_date AND sp.end_date
GROUP BY t.team_id, t.team_name
ORDER BY total_annual_value DESC, t.team_name;

-- ---------------------------------------------------------------------
-- Query 4: Expiring contracts
-- Which active contracts end within the next 90 days?  (date arithmetic)
-- ---------------------------------------------------------------------
SELECT p.gamer_tag,
       pe.first_name || ' ' || pe.last_name AS player_name,
       t.team_name,
       c.annual_salary,
       c.end_date,
       c.end_date - CURRENT_DATE            AS days_left
FROM player_contract c
JOIN player p   ON p.person_id = c.player_id
JOIN person pe  ON pe.person_id = p.person_id
JOIN team t     ON t.team_id = p.team_id
WHERE c.status = 'Active'
  AND c.end_date BETWEEN CURRENT_DATE AND CURRENT_DATE + 90
ORDER BY c.end_date, p.gamer_tag;

-- ---------------------------------------------------------------------
-- Query 5: Standout players
-- Which players with at least 10 matches have a kill/death ratio above
-- their own team's overall ratio?  (CTEs)
-- ---------------------------------------------------------------------
WITH player_kd AS (
    SELECT s.player_id,
           COUNT(*)                                     AS matches_played,
           SUM(s.kills)::NUMERIC / NULLIF(SUM(s.deaths), 0) AS kd
    FROM player_match_stats s
    GROUP BY s.player_id
),
team_kd AS (
    SELECT m.team_id,
           SUM(s.kills)::NUMERIC / NULLIF(SUM(s.deaths), 0) AS kd
    FROM player_match_stats s
    JOIN match m ON m.match_id = s.match_id
    GROUP BY m.team_id
)
SELECT t.team_name,
       p.gamer_tag,
       p.in_game_role,
       pk.matches_played,
       ROUND(pk.kd, 2) AS player_kd,
       ROUND(tk.kd, 2) AS team_kd
FROM player_kd pk
JOIN player p    ON p.person_id = pk.player_id
JOIN team t      ON t.team_id = p.team_id
JOIN team_kd tk  ON tk.team_id = t.team_id
WHERE pk.matches_played >= 10
  AND pk.kd > tk.kd
ORDER BY t.team_name, pk.kd DESC;
