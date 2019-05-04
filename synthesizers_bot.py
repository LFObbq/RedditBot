# -*- coding: utf-8 -*-
import praw
import datetime
import time
import pytz
import os
import daemon
from praw.models import MoreComments

# Domains that are checked
# SHOULD THIS CHECK ALL LINK POSTS INSTEAD OF JUST SPECIFIC LINKS? WHAT IS THE WILDCARD FUNCTION IN THIS CONTEXT?
DOMAINS = ["imgur", "i.redd.it", "v.redd.it", "instagram", "youtube", "youtu.be"]

# Time limits (in minutes)
TIME_WARN = 15
TIME_BOTSLEEP = 1

SUBREDDIT = "synthesizersbottest"
USERNAME = "synthesizers_bot"

def main():
    # Authenticate Reddit bot. Needs API client_id and client_secret
    reddit = praw.Reddit(client_id="",
                        client_secret="",
                        password="",
                        username=USERNAME,
                        user_agent="Synthesizers Bot v0.1")

    # Active Subreddit for the bot
    target_subreddit = reddit.subreddit(SUBREDDIT)

    # Main loop, runs every minute
    while True:
        for submission in target_subreddit.new(limit=100):
            submission_checker(submission, USERNAME)
        time.sleep(TIME_BOTSLEEP * 60)
        
        
def log(submission, message):
    title = (submission.title[:40] + " (...)") if len(submission.title) > 40 else submission.title
    print(datetime.datetime.now(pytz.utc).strftime("%Y-%m-%d %H:%M:%S") + " ## Thread '" + title + "' by /u/" + submission.author.name + ": " + message)

def getSubCommentAuthors(comment, comment_authors):
    if isinstance(comment, MoreComments) == False and comment.author is not None:
        comment_authors.append(comment.author.name)
    
    if not hasattr(comment, "replies"):
        replies = comment.comments()
    else:
        replies = comment.replies
        
    for child in replies:
        getSubCommentAuthors(child, comment_authors)
    
    
# The base function that checks every submission
def submission_checker(submission, USERNAME):      
    to_check = False

    # Create list of all usernames to comment on a submission
    comment_authors=[]

    # Check thread age and convert to minutes
    thread_age = datetime.datetime.now(pytz.utc).timestamp()-submission.created_utc
    thread_age = thread_age/60
    
    # Only process submission that are at max 24 hours old and in list of checkable domains
    if thread_age > (60 * 24):
        return
        
    for domain in DOMAINS:
        if domain in submission.url:
            to_check = True
            
    if to_check == False:
        return
    
    # Add all current commenters to the list
    for top_level_comment in submission.comments:
        getSubCommentAuthors(top_level_comment, comment_authors)

# SEE BELOW. I DON'T KNOW WHETHER THE NESTED IF STATEMENTS ARE VALID. SORRY I'M A BIT RUSTY.
    if submission.author not in comment_authors:
        if thread_age > TIME_WARN:
            # Post warning message after TIME_WARN has passed
            if USERNAME not in comment_authors:
                log(submission, "" + str(TIME_WARN) + " minutes expired -> Reply to submission with warning message!") 
                reply = submission.reply("**Friendly reminder: please leave a thoughtful comment. (rule 5).**  \n\n*I am a bot, and this action was performed automatically. Please [contact the moderators of this subreddit](/message/compose/?to=/r/" + SUBREDDIT + ") if you have any questions or concerns.*")
                reply.mod.distinguish(how='yes', sticky=True)
    else:
        # Remove bot message if OP has replied
        for comment in submission.comments:
            if comment.author is not None and comment.author.name == USERNAME:
                log (submission, "OP replied -> remove warning message!")
                comment.delete()
                
# main loop
if __name__ == "__main__":
    print("*--------------------------*")
    print("* /r/synthesizers BOT v0.1 *")
    print("*--------------------------*")
    print("Starting python daemon...") 
    print("working_directory=" + curr_path)
    print("stdout=synthesizers_bot.log")

    curr_path = os.path.dirname(os.path.abspath(__file__))
    out = open("synthesizers_bot.log", "w+")

    with daemon.DaemonContext(working_directory=curr_path, stdout=out):
        main()
