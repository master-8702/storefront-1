from django.core.mail import EmailMessage, BadHeaderError
from templated_mail.mail import BaseEmailMessage
from django.shortcuts import render


def say_hello(request):
    try:
        message = BaseEmailMessage(
            template_name='emails/hello.html',
            context={'name': 'Steve'}
        )
        message.send(to=['john@google.com'])
    except BadHeaderError:
        pass
    return render(request, 'hello.html', {'name': 'Mosh'})
