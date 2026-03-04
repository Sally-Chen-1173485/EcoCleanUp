"""Script to generate password hashes for one or more user accounts.

You can use this script to generate bcrypt password hashes for all of the
initial user accounts in your database creation script. Remember that each
of your user accounts should have its own unique password.

Before running this script, you'll need to replace the list of user accounts
(the block beginning "users = [") with the actual list of user accounts you
want to generate hashes for.
"""
from collections import namedtuple
from flask import Flask
from flask_bcrypt import Bcrypt

# We use a "named tuple" here to create a simple "User Account" class that can
# store a username and password.
# 
# Don't worry if you haven't seen this before: it's just a simple way of
# storing those two pieces of data together in one variable. It also lets us
# access the username and password by name: for example, if we create a
# UserAccount named "myuser", like this:
# 
# myuser = UserAccount('myusername', 'mypassword')
# 
# We can then access those values via "myuser.username" and "myuser.password",
# instead of having to access myuser[0] and myuser[1] like you would have to
# with a regular tuple.
UserAccount = namedtuple('UserAccount', ['username', 'password'])

app = Flask(__name__)
flask_bcrypt = Bcrypt(app)

# Replace the example UserAccount objects below with the initial user accounts
# for your own web app. You can add as many as you need to the list.
users = [UserAccount('customer1', 'customer1pass'), 
         UserAccount('customer2', 'customer2pass'),
         UserAccount('staff1', 'staff1pass'),
         UserAccount('staff2', 'staff2pass'),
         UserAccount('admin1', 'admin1pass'),
         UserAccount('admin2', 'admin2pass'),
         UserAccount('alice_williams', 'alice_williams_pass'),
         UserAccount('bob_smith', 'bob_smith_pass'),
         UserAccount('carol_jones', 'carol_jones_pass'),
         UserAccount('david_brown', 'david_brown_pass'),
         UserAccount('emma_davis', 'emma_davis_pass'),
         UserAccount('frank_martin', 'frank_martin_pass'),   
         UserAccount('grace_clark', 'grace_clark_pass'),
         UserAccount('hannah_lee', 'hannah_lee_pass'),     
         UserAccount('ian_king', 'ian_king_pass'),
         UserAccount('jack_moore', 'jack_moore_pass'),
         UserAccount('karen_wilson', 'karen_wilson_pass'),
         UserAccount('lucas_taylor', 'lucas_taylor_pass'),
         UserAccount('mona_lee', 'mona_lee_pass'),    
         UserAccount('noah_sanders', 'noah_sanders_pass'),
         UserAccount('olivia_smith', 'olivia_smith_pass'),
         UserAccount('paul_baker', 'paul_baker_pass'),
         UserAccount('queen_carter', 'queen_carter_pass'),
         
         UserAccount('yolanda_garcia', 'yolanda_garcia_pass'),
         UserAccount('zachary_lee', 'zachary_lee_pass'),
         UserAccount('april_walker', 'april_walker_pass'),
         UserAccount('brandon_hall', 'brandon_hall_pass'),
         UserAccount('cynthia_king', 'cynthia_king_pass'),
         UserAccount('derek_wright', 'derek_wright_pass'),
         UserAccount('eric_lopez', 'eric_lopez_pass'),
         UserAccount('fiona_green', 'fiona_green_pass'),
         UserAccount('george_adams', 'george_adams_pass'),
         UserAccount('hannah_baker', 'hannah_baker_pass'),
         UserAccount('ian_nelson', 'ian_nelson_pass')]


print('Username | Password | Hash | Password Matches Hash')

for user in users:
    # Generate a bcrypt hash using the default settings. This function returns
    # the hash as 59-60 bytes (always 60 in the current version of bcrypt).
    password_hash = flask_bcrypt.generate_password_hash(user.password)
    
    # Check whether the hash matches the original password. We don't really
    # need to do this here: this is just to show how your web app would check a
    # password supplied by the user (user.password) against a hash value
    # retrieved from the database (password_hash).
    # 
    # This returns True if the password matches, or False if it doesn't.
    password_matches_hash = flask_bcrypt.check_password_hash(password_hash, user.password)

    # Output username, password, hash, and the result of our verification test.
    # 
    # Note that username is never actually used when generating the hash or
    # checking a password. We only include username here for display purposes,
    # to make it easier for you to copy the right password for each user when
    # creating your database population script.
    #
    # We call password_hash.decode() to translate the series of bytes that make
    # up the hash into a UTF-8 encoded string of characters. Otherwise, when 
    # Python prints out the hash, it will surrounded it with `b''` to indicate
    # that the hash is a binary string. You don't need to do this if you're
    # passing the hash in to MySQL: you can just use password_hash directly, as
    # we do in the Login Example project, and it will accept the binary string.
    print(f'{user.username} | {user.password} | {password_hash.decode()} | {password_matches_hash}')