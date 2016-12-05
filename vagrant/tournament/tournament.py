#!/usr/bin/env python
# 
# tournament.py -- implementation of a Swiss-system tournament
#

import psycopg2


def connect():
    """Connect to the PostgreSQL database.  Returns a database connection."""
    return psycopg2.connect("dbname=tournament")


def deleteMatches():
    """Remove all the match records from the database."""
    conn = connect()
    c = conn.cursor()
    c.execute("delete from matches")
    conn.commit()
    conn.close()

def deletePlayers():
    """Remove all the player records from the database."""
    conn = connect()
    c = conn.cursor()
    c.execute("delete from players")
    conn.commit()
    conn.close()

def countPlayers():
    """Returns the number of players currently registered."""
    conn = connect()
    c = conn.cursor()
    c.execute("select count(id) as num from players;")
    results = c.fetchone()
    conn.close()
    if results:
        return results[0]
    else:
        return '0'

def registerPlayer(name):
    """Adds a player to the tournament database.
  
    The database assigns a unique serial id number for the player.  (This
    should be handled by your SQL database schema, not in your Python code.)
  
    Args:
      name: the player's full name (need not be unique).
    """
    conn = connect()
    c = conn.cursor()
    c.execute("insert into players (name) values (%s);", (name,))
    conn.commit()
    conn.close()
    


def playerStandings():
    """Returns a list of the players and their win records, sorted by wins.

    The first entry in the list should be the player in first place, or a player
    tied for first place if there is currently a tie.

    Returns:
      A list of tuples, each of which contains (id, name, wins, matches):
        id: the player's unique id (assigned by the database)
        name: the player's full name (as registered)
        wins: the number of matches the player has won
        matches: the number of matches the player has played
    """
    conn = connect()
    c = conn.cursor()
    c.execute("DROP VIEW IF EXISTS win_totals;")
    c.execute("select * from matches")
    results = c.fetchall()

    c.execute("\
    CREATE view win_totals as \
    SELECT * FROM \
        (SELECT \
            players.id, players.name, count(players.name) as win_total, \
            count(players.id) as matches\
        FROM players, matches \
        WHERE players.id = matches.winner \
        GROUP BY players.id, players.name \
        UNION \
        select players.id, players.name, 0 as matches, 0 as win_total FROM players order by win_total desc)s;")
    c.execute("create view standings as select id, name, sum(win_total) as win_total, sum(matches) as matches FROM win_totals group by id, name order by win_total desc;")
    c.execute("select * from standings")
    results = c.fetchall()
    return results




CREATE view win_totals as \
SELECT \
            players.id, players.name, count(players.name) as win_total \
        FROM players, matches \
        WHERE players.id = matches.winner \
        GROUP BY players.id, players.name


CREATE view lose_totals as \
SELECT \
            players.id, players.name, count(players.name) as lose_total \
        FROM players, matches \
        WHERE players.id = matches.loser \
        GROUP BY players.id, players.name


SELECT * FROM \
        (SELECT \
            players.id, players.name, count(players.name) as win_total \
        FROM players, matches \
        WHERE players.id = matches.winner \
        GROUP BY players.id, players.name)t
        JOIN \
        (SELECT \
            players.id, players.name, count(players.name) as lose_total \
        FROM players, matches \
        WHERE players.id = matches.loser \
        GROUP BY players.id, players.name)s;


SELECT CONCAT(matches.winner, matches.loser), COUNT(matches.winner) FROM matches GROUP BY CONCAT(matches.winner, matches.loser); 
SELECT VALUE
from matches
UNPIVOT
(
  VALUE
  for COL in (winner, loser)
) un
ORDER BY id, col;

    # if results:
    #     c.execute("CREATE VIEW win_totals as select players.id, players.name, count(players.name) as win_total, count(players.id) as matches from players, matches WHERE players.id = matches.winner group by players.id, players.name order by win_total desc;")
    #     c.execute("select * from win_totals")
    #     results = c.fetchall()
    #     conn.close()
    #     return results
    # else:
    #     c.execute("create view win_totals as select players.id, players.name, 0 as matches, 0 as win_total from players;")
    #     c.execute("select * from win_totals")
    #     results = c.fetchall()
    #     conn.close()
    #     return results


def reportMatch(winner, loser):
    """Records the outcome of a single match between two players.

    Args:
      winner:  the id number of the player who won
      loser:  the id number of the player who lost
    """
    conn = connect()
    c = conn.cursor()
    c.execute("insert into matches (winner, loser) values (%s, %s);", (winner,loser))
    conn.commit()
    conn.close()

def swissPairings():
    """Returns a list of pairs of players for the next round of a match.
  
    Assuming that there are an even number of players registered, each player
    appears exactly once in the pairings.  Each player is paired with another
    player with an equal or nearly-equal win record, that is, a player adjacent
    to him or her in the standings.
  
    Returns:
      A list of tuples, each of which contains (id1, name1, id2, name2)
        id1: the first player's unique id
        name1: the first player's name
        id2: the second player's unique id
        name2: the second player's name
    """
    conn = connect()
    c = conn.cursor()
    c.execute("DROP VIEW IF EXISTS pairings;")
    c.execute("DROP VIEW IF EXISTS win_totals;")
    c.execute("select count(id) as num from players;")
    length = c.fetchone()
    print "length[0]"
    print length[0]
    length = (length[0]/2)
    print "length"
    print length

    ### Basically copied from playerStandings()
    c.execute("select * from matches")
    results = c.fetchall()
    # if results:
    c.execute("create view win_totals as select * from (select players.id, players.name, count(players.name) as win_total, count(players.id) as matches from players, matches WHERE players.id = matches.winner group by players.id, players.name UNION select players.id, players.name, 0 as matches, 0 as win_total from players order by win_total desc)s;")
    c.execute("create view standings as select id, name, sum(win_total) as win_total, sum(matches) as matches from win_totals group by id, name order by win_total desc;")

    # else:
    #     c.execute("create view win_totals as select players.id, players.name, 0 as matches, 0 as win_total from players;")

    ### Just using this to set result as a list with nothing in it, so it can add to itself.
    c.execute("select * from matches limit 0")
    results = c.fetchall()

    for i in range(0,length):
        print "counting i:"
        print i
        offset_number = i * 2
        print "offset_number:"
        print offset_number
        c.execute("select * from (select win_totals.id as id1, win_totals.name as name1 from win_totals offset (%s) limit 1) t cross join (select win_totals.id as id2, win_totals.name as name2 from win_totals offset (%s) limit 1) m", (offset_number, offset_number+1))
        results += c.fetchall()
        print "results"
        print results
    conn.close()
    print "finished tournament.py"
    return results
