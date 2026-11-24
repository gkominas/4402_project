-- =====================================================================
-- CSC 4402 Project: Esports Organization Database
-- schema.sql — tables and constraints (PostgreSQL / Supabase)
--
-- Runs on any PostgreSQL 13+ database, including Supabase.
--   Supabase:  paste into the SQL Editor and click Run
--   Local:     psql "$DATABASE_URL" -f schema.sql
--
-- Safe to re-run: drops existing tables first (children before parents).
-- SERIAL = an INT primary key that auto-numbers new rows (1, 2, 3...).
-- =====================================================================

DROP TABLE IF EXISTS sponsorship         CASCADE;
DROP TABLE IF EXISTS sponsor             CASCADE;
DROP TABLE IF EXISTS player_match_stats  CASCADE;
DROP TABLE IF EXISTS match               CASCADE;
DROP TABLE IF EXISTS tournament          CASCADE;
DROP TABLE IF EXISTS player_contract     CASCADE;
DROP TABLE IF EXISTS staff               CASCADE;
DROP TABLE IF EXISTS player              CASCADE;
DROP TABLE IF EXISTS person              CASCADE;
DROP TABLE IF EXISTS team                CASCADE;
DROP TABLE IF EXISTS game                CASCADE;

-- ---------------------------------------------------------------------
-- CORE
-- ---------------------------------------------------------------------

-- Titles the org competes in (Valorant, League of Legends, Rocket League)
CREATE TABLE game (
    game_id    SERIAL       PRIMARY KEY,
    title      VARCHAR(50)  NOT NULL UNIQUE,
    genre      VARCHAR(30)  NOT NULL,
    team_size  SMALLINT     NOT NULL CHECK (team_size BETWEEN 1 AND 10)  -- starters per match
);

-- Each game has a Main roster and can have an Academy (development) roster.
-- Game 1 : N Team
CREATE TABLE team (
    team_id      SERIAL       PRIMARY KEY,
    game_id      INT          NOT NULL REFERENCES game(game_id) ON DELETE RESTRICT,
    team_name    VARCHAR(50)  NOT NULL UNIQUE,
    roster_type  VARCHAR(10)  NOT NULL DEFAULT 'Main'
                 CHECK (roster_type IN ('Main','Academy')),
    UNIQUE (game_id, roster_type)          -- at most one Main + one Academy per game
);

-- Superclass: everyone the org employs
CREATE TABLE person (
    person_id   SERIAL        PRIMARY KEY,
    first_name  VARCHAR(50)   NOT NULL,
    last_name   VARCHAR(50)   NOT NULL,
    email       VARCHAR(100)  NOT NULL UNIQUE
);

-- Subclass of Person (ISA). Shares Person's primary key.
-- Team 1 : N Player
CREATE TABLE player (
    person_id     INT          PRIMARY KEY REFERENCES person(person_id) ON DELETE CASCADE,
    gamer_tag     VARCHAR(30)  NOT NULL UNIQUE,
    in_game_role  VARCHAR(20)  NOT NULL,          -- e.g. Duelist, Support, Jungle
    team_id       INT          NOT NULL REFERENCES team(team_id) ON DELETE RESTRICT,
    is_starter    BOOLEAN      NOT NULL DEFAULT TRUE   -- FALSE = substitute
);

-- Subclass of Person (ISA). team_id NULL = works for the whole org (e.g. GM)
-- Team 1 : N Staff (partial)
CREATE TABLE staff (
    person_id   INT          PRIMARY KEY REFERENCES person(person_id) ON DELETE CASCADE,
    staff_role  VARCHAR(30)  NOT NULL
                CHECK (staff_role IN ('Head Coach','Assistant Coach','Analyst',
                                      'Team Manager','General Manager',
                                      'Partnerships Manager')),
    team_id     INT          REFERENCES team(team_id) ON DELETE SET NULL
);

-- Player 1 : N PlayerContract (renewals create new rows)
CREATE TABLE player_contract (
    contract_id    SERIAL         PRIMARY KEY,
    player_id      INT            NOT NULL REFERENCES player(person_id) ON DELETE CASCADE,
    start_date     DATE           NOT NULL,
    end_date       DATE           NOT NULL,
    annual_salary  NUMERIC(10,2)  NOT NULL CHECK (annual_salary >= 0),
    status         VARCHAR(10)    NOT NULL DEFAULT 'Active'
                   CHECK (status IN ('Active','Expired','Terminated')),
    CHECK (end_date > start_date)
);

-- ---------------------------------------------------------------------
-- COMPETITION
-- ---------------------------------------------------------------------

-- Game 1 : N Tournament
CREATE TABLE tournament (
    tournament_id  SERIAL         PRIMARY KEY,
    game_id        INT            NOT NULL REFERENCES game(game_id) ON DELETE RESTRICT,
    name           VARCHAR(100)   NOT NULL,
    start_date     DATE           NOT NULL,
    end_date       DATE           NOT NULL,
    prize_pool     NUMERIC(12,2)  NOT NULL DEFAULT 0 CHECK (prize_pool >= 0),
    CHECK (end_date >= start_date)
);

-- Tournament 1 : N Match, Team 1 : N Match
-- Opponents are outside teams, stored by name only.
-- Scores are NULL until the match is played.
CREATE TABLE match (
    match_id        SERIAL       PRIMARY KEY,
    tournament_id   INT          NOT NULL REFERENCES tournament(tournament_id) ON DELETE CASCADE,
    team_id         INT          NOT NULL REFERENCES team(team_id) ON DELETE RESTRICT,
    opponent_name   VARCHAR(50)  NOT NULL,
    match_date      TIMESTAMP    NOT NULL,
    team_score      SMALLINT     CHECK (team_score >= 0),
    opponent_score  SMALLINT     CHECK (opponent_score >= 0)
);

-- Weak entity: Player M : N Match. Identified by (match_id, player_id).
CREATE TABLE player_match_stats (
    match_id   INT       NOT NULL REFERENCES match(match_id) ON DELETE CASCADE,
    player_id  INT       NOT NULL REFERENCES player(person_id) ON DELETE CASCADE,
    kills      SMALLINT  NOT NULL DEFAULT 0 CHECK (kills   >= 0),
    deaths     SMALLINT  NOT NULL DEFAULT 0 CHECK (deaths  >= 0),
    assists    SMALLINT  NOT NULL DEFAULT 0 CHECK (assists >= 0),
    PRIMARY KEY (match_id, player_id)
);

-- ---------------------------------------------------------------------
-- BUSINESS
-- ---------------------------------------------------------------------

CREATE TABLE sponsor (
    sponsor_id     SERIAL        PRIMARY KEY,
    name           VARCHAR(50)   NOT NULL UNIQUE,
    industry       VARCHAR(30)   NOT NULL,         -- e.g. Energy Drink, Peripherals
    contact_email  VARCHAR(100)
);

-- Sponsor M : N Team, with relationship attributes.
-- Surrogate key so the same sponsor can renew with the same team.
CREATE TABLE sponsorship (
    sponsorship_id  SERIAL         PRIMARY KEY,
    sponsor_id      INT            NOT NULL REFERENCES sponsor(sponsor_id) ON DELETE CASCADE,
    team_id         INT            NOT NULL REFERENCES team(team_id) ON DELETE CASCADE,
    annual_value    NUMERIC(12,2)  NOT NULL CHECK (annual_value > 0),
    start_date      DATE           NOT NULL,
    end_date        DATE           NOT NULL,
    CHECK (end_date > start_date)
);

-- ---------------------------------------------------------------------
-- INDEXES on foreign keys used in joins (Postgres doesn't add these automatically)
-- ---------------------------------------------------------------------
CREATE INDEX idx_team_game         ON team(game_id);
CREATE INDEX idx_player_team       ON player(team_id);
CREATE INDEX idx_staff_team        ON staff(team_id);
CREATE INDEX idx_contract_player   ON player_contract(player_id);
CREATE INDEX idx_tournament_game   ON tournament(game_id);
CREATE INDEX idx_match_tournament  ON match(tournament_id);
CREATE INDEX idx_match_team        ON match(team_id);
CREATE INDEX idx_stats_player      ON player_match_stats(player_id);
CREATE INDEX idx_sponsorship_team  ON sponsorship(team_id);

-- ---------------------------------------------------------------------
-- SMOKE TEST DATA (a few rows so you can confirm it works;
-- replace with output from generate_data.py)
-- ---------------------------------------------------------------------
INSERT INTO game (title, genre, team_size) VALUES
  ('Valorant',          'Tactical FPS', 5),
  ('League of Legends', 'MOBA',         5),
  ('Rocket League',     'Sports',       3);

INSERT INTO team (game_id, team_name, roster_type) VALUES
  (1, 'Bayou Bolt Valorant',         'Main'),
  (1, 'Bayou Bolt Valorant Academy', 'Academy'),
  (2, 'Bayou Bolt LoL',              'Main'),
  (3, 'Bayou Bolt RL',               'Main');
