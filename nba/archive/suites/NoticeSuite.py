import smtplib


def sendEmail(user, pwd, recipient, subject, body):

    gmail_user = user
    gmail_pwd = pwd
    FROM = user
    TO = recipient if type(recipient) is list else [recipient]
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
        print ('successfully sent the email')
    except:
        print ('failed to send email')


def createMessage(daily_proj_dict, s3_status, queue_num):
    """
    Takes in daily projection daily_proj_dict
    Loops through entries, checks counts
    Returns message to send in e-mail
    """
    date = daily_proj_dict["game_date"]
    nf = str(daily_proj_dict["number_fire"]["record_count"])
    # nf = "DISABLED"
    rw = str(daily_proj_dict["roto_wire"]["record_count"])
    bm = str(daily_proj_dict["basketball_monster"]["record_count"])
    fp = str(daily_proj_dict["fantasy_pros"]["record_count"])

    body = (date + " - nf: " + nf + " records, rw: " + rw +
            " records, bm: " + bm + " records, fp: " + fp +
            " records. S3 Success: " + str(s3_status) +
            ", Players in Queue: " + str(queue_num))


    return body
