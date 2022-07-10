from django.core.mail import send_mail
from sheet_music_africa.settings import FROM_EMAIL, MAIN_ADDRESS

# import os
# from sendgrid import SendGridAPIClient
# from sendgrid.helpers.mail import Mail




def send_reset_password_email(token,recipent):
    token = "https://%s?token=%s"%(MAIN_ADDRESS,token)
    message = "your reset password Link <br> <p><a href='%s'> Reset password </a></p>"%token
    send_email("Sheet Music Africa Password Reset",message,recipent)

def send_email(subject,message,recipient):

    print("to : ",recipient)
    send_mail(
    subject,
    "hello world",
    FROM_EMAIL,
    [recipient],
    fail_silently=False,
    html_message=message,
    )

    # message = Mail(
    # from_email=FROM_EMAIL,
    # to_emails=recipient,
    # subject=subject,
    # html_content=message)


    # try:
    #     sg = SendGridAPIClient('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')
    #     response = sg.send(message)
    #     print(response.status_code)
    #     print(response.body)
    #     print(response.headers)

    # except Exception as e:
    #     print(e)
