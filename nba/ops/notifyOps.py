import smtplib
import json
import time
from nba.ops.config import APP_CONFIG

config = APP_CONFIG["NOTIFY"]

def sendEmail(subject, body):

    gmail_user = config["MAIL_FROM"]
    gmail_pwd = config["MAIL_PW"]
    FROM = config["MAIL_FROM"]
    TO = config["MAIL_TO"] if type(config["MAIL_TO"]) is list else [config["MAIL_TO"]]
    SUBJECT = subject
    TEXT = body

    # Prepare actual message
    message = """\From: %s\nTo: %s\nSubject: %s\n\n%s
    """ % (FROM, ", ".join(TO), SUBJECT, TEXT)

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.ehlo()
        server.starttls()
        server.login(gmail_user, gmail_pwd)
        server.sendmail(FROM, TO, message)
        server.close()
        print ('successfully sent the email with subject:', subject)
    except:
        print ('failed to send email with subject:', subject)


def createProjectionScrapeMessage(scrapeStats, scrapeTime):
    """
    Takes in daily projection daily_proj_dict
    Loops through entries, checks counts
    Returns message to send in e-mail
    """
    today = time.strftime('%Y-%m-%d')

    body = ("GAME DATE: " + str(today) + " - STATS: " + json.dumps(scrapeStats) + " - TIME (s): " + str(scrapeTime))

    return body

# projection scrape
def notifyProjectionScrapeSuccess(scrapeStats, scrapeTime):
    subject = "PROJECTION SCRAPE SUCCESSFUL"
    message = createProjectionScrapeMessage(scrapeStats, scrapeTime)
    sendEmail(subject, message)

def notifyProjectionScrapeError(errorMessage):
    subject = "PROJECTION SCRAPE FAILED"
    sendEmail(subject, errorMessage)

def sendTestEmail():
    subject = "TEST MESSAGE"
    message = "This is a test."
    sendEmail(subject, message)

def notifyFirstOfDayUpdateTaskSuccess(pendingUpdates):
    '''
    pendingUpdates is a dict of pending manual updates required
    '''
    subject = "Morning Update Successful"
    message = "Initial morning update successful. Depth charts & source ids updated. Pending manual updates: " + str(pendingUpdates)
    sendEmail(subject, message)

def notifyFirstDayOfUpdateError(error):
    '''
    error is error/exception thrown from script failing
    '''
    subject = "Morning Update Successful"
    message = ("Initial morning update failed with error: " + str(error))
    sendEmail(subject, message)

# new source ids update
def notifySourceIdsUpdateSuccess(scrapeStats, scrapeTime):
    subject = "SOURCE IDS AUTO UPDATE SUCCESSFUL"
    message = createProjectionScrapeMessage(scrapeStats, scrapeTime)
    sendEmail(subject, message)

def notifySourceIdsUpdateError(errorMessage):
    subject = "SOURCE IDS AUTO UPDATE SUCCESSFUL"
    sendEmail(subject, errorMessage)

# salary scrape
def notifySalaryScrapeSuccess(numSalaries):
    subject = "Salary scrape successful"
    message = ("Number of salaries: " + str(numSalaries))
    sendEmail(subject, message)

def notifySalaryScrapeError(error):
    '''
    error is error/exception thrown from script failing
    '''
    subject = "Salary scrape failed"
    message = ("Salary scrape failed with error " + str(error))
    sendEmail(subject, message)

# game spreads
def notifySpreadsScrapeSuccess(spreads):
    subject = "Spreads scrape successful"
    message = ("Game totals & spreads scraped for games.")
    sendEmail(subject, message)

def notifySpreadsScrapeError(error):
    '''
    error is error/exception thrown from script failing
    '''
    subject = "Spreads scrape failed"
    message = ("Game spreads scrape failed with error " + str(error))
    sendEmail(subject, message)