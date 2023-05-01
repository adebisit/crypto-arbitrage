from fastapi import BackgroundTasks
from fastapi_mail import MessageSchema
from config import fastmail, mail_env


async def send_email(subject, template, context, receiptents):
    template = mail_env.get_template(template)
    html = template.render(context)
    message = MessageSchema(
        subject=subject,
        recipients=receiptents,
        body=html,
        subtype='html'
    )
    await fastmail.send_message(message)