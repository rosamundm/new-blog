from django.conf import settings
from mailjet_rest import Client

# renamed as variables to match Mailjet API nomenclature;
# may switch to Django native email handling at some point
api_key = settings.EMAIL_HOST_USER
api_secret = settings.EMAIL_HOST_PASSWORD


def send_email(recipient_address, magic_link):
    mailjet = Client(auth=(api_key, api_secret))

    data = {
        "FromEmail": settings.DEFAULT_FROM_EMAIL,
        "FromName": settings.FROM_NAME,
        "Subject": settings.EMAIL_SUBJECT,
        "Text-part": f"{settings.EMAIL_BODY} {magic_link}",
        "Recipients": [{"Email": recipient_address}]
    }

    # todo: create template for email body

    result = mailjet.send.create(data=data)
    print(result.status_code)  # todo: remove later
