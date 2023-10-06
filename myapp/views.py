from django.shortcuts import render
from .models import *
import razorpay
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string

# Create your views here.

def index(request):
    if request.method == 'POST':
       name = request.POST.get('name')
       amount = int(request.POST.get('amount'))*100
       email = request.POST.get('email')

       client = razorpay.Client(auth = ("rzp_test_pj8LAwuK1ujv2V","yKEV23EZG8gA9lF3VvIcxgBv"))
       payment = client.order.create({'amount':amount,'currency':'INR','payment_capture':"1"})

       cof = Coffee(name=name,email=email,amount=amount,payment_id = payment['id'])
       cof.save()
       

       return render(request,'index.html',{'payment':payment})
    return render(request,'index.html')

from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
def done(request):
    if request.method == 'POST':
        a = request.POST
        order_id = ""
        data={}
        for key,val in a.items():
            if key == "razorpay_order_id":
                data['razorpay_order_id']=val
                order_id = val
            elif key == 'razorpay_payment_id':
                data['razorpay_payment_id']=val
            elif key == 'razorpay_signature':
                data['razorpay_signature']=val
        user = Coffee.objects.filter(payment_id=order_id).first()
        user.paid = True
        user.save()
        
    msg_plain = render_to_string('email.txt')
    msg_html = render_to_string('email.html')

    send_mail("Your Donation has been received" , msg_plain , settings.EMAIL_HOST_USER,
              [user.email], html_message=msg_html)

    return render(request,'done.html')