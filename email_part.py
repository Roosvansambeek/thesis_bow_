from sqlalchemy import create_engine, text
from email.message import EmailMessage
import ssl
import smtplib
import time
import os

db_connection_string = os.environ['DB_CONNECTION_STRING']

engine = create_engine(
  db_connection_string,
  connect_args={
    "ssl": {
      "ssl_ca": "/etc/ssl/cert.pem"
    }
  }
)



def store_email_in_db(email):
  with engine.connect() as conn:
      query = text("INSERT INTO r_participants (email_address) VALUES (:email)")
      conn.execute(query, {'email': email})  


def load_adres_from_db():
    with engine.connect() as conn:
        result = conn.execute(text("SELECT email_address FROM r_participants"))
        new_courses = []
        columns = result.keys()
        for row in result:
            result_dict = {column: value for column, value in zip(columns, row)}
            new_courses.append(result_dict['email_address'])
        return new_courses

def send_email(email_receiver):
    email_sender ='r.a.c.vansambeek@tilburguniversity.edu'
    email_password = 'qgjt tmvh cugp xgox'

    subject = 'Participation-link/Deelname link questionnaire'
    body = """

    Dear participant,


    Here is the participation link for the questionnaire: 
    https://tilburgss.co1.qualtrics.com/jfe/form/SV_9EKn6odofJYddjg 

    * Make sure to open this link on your PC/laptop, 
    as the new application is not compatible for a mobile-phone (yet).


    Thanks for you time!

    Kind regards, 

    Roos van Sambeek 


    ---------------------------------------------------------------------------


    Beste deelnemer,


    Hier is de deelnamelink voor de vragenlijst: 
    https://tilburgss.co1.qualtrics.com/jfe/form/SV_9EKn6odofJYddjg 

    ** Zorg ervoor dat je deze link opent op je pc/laptop, 
    aangezien de nieuwe applicatie (nog) niet beschikbaar is op een mobiele telefoon.


    Bedankt voor je tijd!

    Met vriendelijke groet, 

    Roos van Sambeek



    """

    em = EmailMessage()
    em['From'] = email_sender
    em['To'] = email_receiver
    em['Subject'] = subject
    em.set_content(body)

    context = ssl.create_default_context()

    with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
        smtp.login(email_sender, email_password)
        smtp.send_message(em)

def check_and_send_email(email):
    send_email(email)
        
      



