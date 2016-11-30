-- Table definitions for the tournament project.
--
-- Put your SQL 'create table' statements in this file; also 'create view'
-- statements if you choose to use it.
--
-- You can write comments in this file by starting them with two dashes, like
-- these lines here.

DROP TABLE IF EXISTS players, matches;

CREATE TABLE players (
    id serial NOT NULL,
    name TEXT NOT NULL,
    PRIMARY KEY (id)
);

CREATE TABLE matches (
    id serial PRIMARY KEY,
    winner INTEGER REFERENCES players (id) NOT NULL,
    loser INTEGER REFERENCES players (id) NOT NULL
);