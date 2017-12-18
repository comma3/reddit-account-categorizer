import re
import time
import sqlite3
import glob

import praw

def read_patterns(filename):
    """
    Open files and generate strings for regex searches.
    """
    # input files have ' so be sure to use " throughout.
    with open(filename) as file:
        patterns = [row for row in file]
    return "|".join("(?:%s)" % p.replace("\n","") for p in patterns)

def load_regex():
    """
    Create single compiled regex from the lists of different types.
    """
    # input files have ' so be sure to use " throughout.
    out = ""
    for filename in glob.glob('./identity_lists/*.txt'):
        out += read_patterns(filename) + "|"
    out = out[:-1]
    return re.compile(out)

def get_users(db):
    """
    Take a string.
    Return a set.
    """
    conn = sqlite3.connect(db)
    curr = conn.cursor()
    curr.execute("""SELECT username
                    FROM users
                    """)
    temp_users = curr.fetchall()
    conn.close()

    return [user for user in temp_users]

def remove_quotes(comment):
    # Don't want to attribute gender to users based on quotes
    # All numeric answers are read as float/int, so we need to cast them to
    # string to avoid errors
    quote_stripped_comment = re.sub(r'>.*', '', str(comment).lower())
    # This approach didn't seem to catch nested quotes. seemed easier/more
    # complete to loop if a nested quote is found than making a complex regex
    while '>' in quote_stripped_comment:
        print(quote_stripped_comment)
        quote_stripped_comment = re.sub(r'>.*', '', quote_stripped_comment)

    return quote_stripped_comment

def get_comments(new_redditors):
    # Get comments from the list of users
    # Reddit limits to 1000 comments (probably not worth finding a work around)
    results = {}
    for redditor in new_redditors:
        print('Collecting:', redditor)
        subreddits = set()
        comments = []
        gender = 'unknown'
        orientation = 'unknown'
        age = 0
        for comment in redditor.comments.new(limit=None):
            comments.append([comment.body, comment.score, comment.created_utc, comment.subreddit.display_name])
            subreddits.add(comment.subreddit.display_name)
        author = comment.author.name
        results[author] = [comments, gender, orientation, age, subreddits]
    return results

def add_to_db(db, results):
    conn = sqlite3.connect(db)
    curr = conn.cursor()

    # Just gonna create the table here so I don't have to do it elsewhere
    # Pass if the table already exists
    try:
        curr.execute("""CREATE TABLE
                        users (
                        username string,
                        gender string,
                        orientation string,
                        age int,
                        subreddits string
                        )
                        """)
        curr.execute("""CREATE TABLE
                        comments (
                        user string,
                        body string,
                        score int,
                        date string,
                        subreddit string
                        )
                        """)

    except sqlite3.OperationalError:
        pass

    for key, value in results.items():
        user = (key, value[1], value[2], value[3], ','.join(value[4]))
        curr.execute("""INSERT INTO users
                    (username, gender, orientation, age, subreddits)
                    VALUES (?,?,?,?,?)
                    """, user)
        for comment in value[0]:
            curr.execute("""INSERT INTO comments
                        (user, body, score, date, subreddit)
                        VALUES (?,?,?,?,?)
                        """, (key, comment[0], comment[1], comment[2], comment[3]))

    conn.commit()
    conn.close()
    print('Added to DB!')


if __name__ == '__main__':
    db = '/data/accounts.db'
    bot = 'bot1'
    subs = 'all'
    # Make sure we don't get more from users already in the DB
    new_redditors = set()
    used_redditors = set(get_users(db))

    match_strings = load_regex()
    reddit = praw.Reddit(bot)
    subreddit = reddit.subreddit(subs)
    start = int(time.time())
    i = 0 # Can't enumerate on stream
    for comment in subreddit.stream.comments():
        i += 1
        if i % 300 == 0:
            print('Elapsed time: ', int(time.time()) - start)
        if comment.author in used_redditors:
            continue
        elif match_strings.search(remove_quotes(comment.body)):
            new_redditors.add(comment.author)
            used_redditors.add(comment.author)
            print('================================')
            print(comment.body) # matched comment
            print(match_strings.search(remove_quotes(comment.body))[0]) # matched string
            print('================================')
        if len(new_redditors) > 20:
            # Can't multithread here without a new bot
            # New bot probably against TOS...
            # PRAW didn't seem to wait long enough here before I start requesting user comments
            # So we manually wait the reddit-required 2 seconds between requests
            print(new_redditors)
            time.sleep(2)
            results = get_comments(new_redditors)
            # Could multithread here but this probably takes a couple
            # of ms
            add_to_db(db, results)
            new_redditors = set()
        if time.time() > start + 50000:
            # Did this approach rather than while to save an indent level
            break
