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
    c.execute("DROP VIEW IF EXISTS standings, win_totals;")
    c.execute("SELECT * FROM matches")
    results = c.fetchall()

    if results:
        c.execute("CREATE VIEW win_totals AS \
        SELECT players.id, players.name, \
        (SELECT count(matches.winner) \
        FROM matches \
        WHERE players.id = matches.winner) \
        AS total_wins, \
        (SELECT count(matches.id) \
        FROM matches \
        WHERE players.id = matches.winner \
        OR players.id = matches.loser) \
        AS total_matches \
        FROM players \
        ORDER BY total_wins DESC, total_matches DESC;")

        c.execute("SELECT * FROM win_totals")
        results = c.fetchall()
        conn.close()
        return results

    else:
        c.execute("CREATE VIEW win_totals AS \
        SELECT players.id, players.name, 0 as matches, 0 AS win_total \
        FROM players;")
        c.execute("SELECT * FROM win_totals")
        results = c.fetchall()
        conn.close()
        return results


def reportMatch(winner, loser):
    """Records the outcome of a single match between two players.

    Args:
      winner:  the id number of the player who won
      loser:  the id number of the player who lost
    """
    conn = connect()
    c = conn.cursor()
    c.execute("INSERT INTO matches (winner, loser) VALUES (%s, %s);", (winner,loser))
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
    c.execute("DROP VIEW IF EXISTS standings, win_totals;")
    c.execute("select count(id) as num from players;")
    length = c.fetchone()
    print "length[0]"
    print length[0]
    length = (length[0]/2)
    print "length"
    print length

    # Same as playerStandings()
    c.execute("select * from matches")
    results = c.fetchall()
    if results:
        c.execute("CREATE VIEW win_totals AS \
            SELECT players.id, players.name, \
            (SELECT count(matches.winner) \
            FROM matches \
            WHERE players.id = matches.winner) \
            AS win_totals, \
            (SELECT count(matches.id) \
            FROM matches \
            WHERE players.id = matches.winner \
            OR players.id = matches.loser) \
            AS total_matches \
            FROM players \
            ORDER BY win_totals DESC, total_matches DESC;")

    else:
        c.execute("CREATE VIEW win_totals AS \
        SELECT players.id, players.name, 0 AS matches, 0 AS win_total FROM players;")

    ### Just using this to set result as a list with nothing in it, so it can add to itself.
    c.execute("SELECT * FROM matches LIMIT 0")
    results = c.fetchall()

    for i in range(0, length):
        print "counting i:"
        print i
        offset_number = i * 2
        print "offset_number:"
        print offset_number
        c.execute("SELECT * FROM \
        (SELECT win_totals.id AS id1, win_totals.name AS name1 FROM win_totals \
        OFFSET (%s) LIMIT 1)t \
        CROSS JOIN \
        (SELECT win_totals.id AS id2, win_totals.name AS name2 FROM win_totals \
        OFFSET (%s) LIMIT 1)m", (offset_number, offset_number+1))
        results += c.fetchall()
        print "results"
        print results
    conn.close()
    print "finished tournament.py"
    return results
