import re
import MFLibrary as mf
import sqlite3


def read_patterns(filename):
    list = []
    with open(filename) as file:
        for row in file:
            list.append(row)
    return '|'.join('(?:%s)' % p.replace('\n','') for p in list)

male_patterns = re.compile(read_patterns('./identity_lists/male_patterns.txt'))
male_gay = re.compile(read_patterns('./identity_lists/male_gay.txt'))
male_straight = re.compile(read_patterns('./identity_lists/male_straight.txt'))
female_patterns = re.compile(read_patterns('./identity_lists/female_patterns.txt'))
female_gay = re.compile(read_patterns('./identity_lists/female_gay.txt'))
female_straight = re.compile(read_patterns('./identity_lists/female_straight.txt'))

conn = sqlite3.connect('D:\\reddit\\reddit_user_data.sqlite3')
curr = conn.cursor()

# Exclude unused events and corrupted data
curr.execute("""SELECT user, body
                FROM comments
                JOIN users
                ON users.username = comments.user
                WHERE gender='unknown'""")
comments = curr.fetchall()

# Set everything we pulled above to 'NA' so we don't have to search it again as DB increases in size
#
curr.execute("""UPDATE users
                SET gender='NA'
                where gender='unknown'""")

# conn.commit() done at the end
# connection closed at the end

print(len(comments))
quotes = []
user_scores = {}
for comment in comments:
    # Don't want to attribute gender to users based on quotes
    # Numeric answers are read as float/int, so we need to cast them to string
    quote_stripped_comment = re.sub(r'>.*', '', str(comment[1]).lower())
    # This approach didn't seem to catch nested quotes. seemed easier/more complete than making a complex regex
    # to just loop if a quote is found
    while '>' in quote_stripped_comment:
        print(quote_stripped_comment)
        quote_stripped_comment = re.sub(r'>.*', '', quote_stripped_comment)
    if male_patterns.search(quote_stripped_comment):
        try:
            user_scores[comment[0]]['male'] = user_scores[comment[0]]['male'] + 1
        except KeyError:
            user_scores[comment[0]] = {'male': 1}
        quotes.append([comment[1], male_patterns.search(str(comment[1]).lower())])
    elif male_straight.search(quote_stripped_comment):
        try:
            user_scores[comment[0]]['male'] = user_scores[comment[0]]['male'] + 1
        except KeyError:
            user_scores[comment[0]] = {'male': 1}
        quotes.append([comment[1], male_straight.search(str(comment[1]).lower())])
        # Can add straight/gay to dictionary if it becomes relevant
    elif male_gay.search(quote_stripped_comment):
        try:
            user_scores[comment[0]]['gmale'] = user_scores[comment[0]]['gmale'] + 1
        except KeyError:
            user_scores[comment[0]] = {'gmale': 1}
        quotes.append([comment[1], male_gay.search(str(comment[1]).lower())])
    elif female_patterns.search(quote_stripped_comment):
        try:
            user_scores[comment[0]]['female'] = user_scores[comment[0]]['female'] + 1
        except KeyError:
            user_scores[comment[0]] = {'female': 1}
        quotes.append([comment[1], female_patterns.search(str(comment[1]).lower())])
    elif female_straight.search(quote_stripped_comment):
        try:
            user_scores[comment[0]]['female'] = user_scores[comment[0]]['female'] + 1
        except KeyError:
            user_scores[comment[0]] = {'female': 1}
        quotes.append([comment[1], female_straight.search(str(comment[1]).lower())])
    elif female_gay.search(quote_stripped_comment):
        try:
            user_scores[comment[0]]['gfemale'] = user_scores[comment[0]]['gfemale'] + 1
        except KeyError:
            user_scores[comment[0]] = {'gfemale': 1}
        quotes.append([comment[1], female_gay.search(str(comment[1]).lower())])
print(user_scores)
print(len(user_scores))
mf.csv.write_list('quotes.csv', quotes)
mf.csv.write_dict('userdict.csv', user_scores)


for key,entry in user_scores.items():
    try:
        male = entry['male']
    except:
        male = 0
    try:
        female = entry['female']
    except:
        female = 0
    try:
        gmale = entry['gmale']
    except:
        gmale = 0
    try:
        gfemale = entry['gfemale']
    except:
        gfemale = 0
    # In case we get contradictory information, we only take values where they clearly favor one side
    # First ~2000 entries didn't have any contradictions but we want to be safe
    if gmale/(gfemale + gmale + female + male) > 0.1:  # Considerably lower requirements as mentions of male could vastly outnumber mentions of gay male
        curr.execute("""UPDATE users
                        SET gender='male'
                        WHERE username=(?)
                        """, (key,))
    elif gfemale/(gfemale + gmale + female + male) > 0.1:
        curr.execute("""UPDATE users
                        SET gender='female'
                        WHERE username=(?)
                        """, (key,))
    elif (male + gmale)/(gfemale + gmale + female + male) > 0.8:
        curr.execute("""UPDATE users
                        SET gender='male'
                        WHERE username=(?)
                        """, (key,))
    elif (female + gfemale)/(gfemale + gmale + female + male) > 0.8:
        curr.execute("""UPDATE users
                        SET gender='female'
                        WHERE username=(?)
                        """, (key,))
    else:
        print(key, entry)

conn.commit()
conn.close()
