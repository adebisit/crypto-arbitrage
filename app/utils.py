import smtplib


def send_email(to, activation_token):
    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.ehlo()
    server.starttls()
    server.login("adebisijosephh@gmail.com", "TaYeLoLu123")
    message = f"Subject: Activate your profile\n\nPlease activate your profile by clicking on the following link: http://localhost:8000/activate?token={activation_token}"
    server.sendmail("adebisijosephh@gmail.com", to, message)
    server.quit()