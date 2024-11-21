from django.contrib.auth.decorators import login_required
from django.shortcuts import render,redirect
from cart.models import Cart,Payment,Order_details
from django.contrib.auth import login
from django.views.decorators.csrf import csrf_exempt
from shop.models import Product
from django.contrib.auth.models import User
import razorpay
@login_required
def add_to_cart(request,p):
    p=Product.objects.get(id=p)
    username=request.user

    try:

        c=Cart.objects.get(user=username,product=p)#checks the product present in cart table for a particular user
        if(p.stock>0):
            c.quantity +=1                                        #if present it will increment the quantity of product
            c.save()
            p.stock-=1
            p.save()
    except:
        if(p.stock>0):   #if not  present then it will create a new record inside cart table with quantity=1

            c=Cart.objects.create(product=p,user=username,quantity=1)
            c.save()
            p.stock-=1
            p.save()


    return redirect('cart:cartview')

@login_required
def cart_view(request):
    u=request.user
    total=0
    c=Cart.objects.filter(user=u)  #All cart items for a particular user
    for i in c:
        total+=i.quantity*i.product.price #Calculate the sum of each product price*quantity


    context={'cart':c,'total':total}

    return render(request,'cart.html',context)

def cart_remove(request,i):
    p=Product.objects.get(id=i)
    u=request.user

    try:
        c=Cart.objects.get(user=u,product=p)
        if(c.quantity>1):
            c.quantity-=1
            c.save()
            p.stock+=1
            p.save()
        else:
            c.delete()
            p.stock+=1
            p.save()
    except:
        pass
    return redirect('cart:cartview')


@login_required
def cart_delete(request,i):
    u=request.user
    p=Product.objects.get(id=i)
    try:
        c=Cart.objects.get(user=u,product=p)
        c.delete()
        p.stock+=c.quantity
        p.save()
    except:
        pass
    return redirect('cart:cartview')
@login_required
def orderform(request):
    if request.method == 'POST':
        address = request.POST.get('a')
        phone = request.POST.get('p')
        pin = request.POST.get('pi')
        u=request.user
        c=Cart.objects.filter(user=u)
        total=0
        for i in c:
            total+=i.quantity*i.product.price
        total=int(total*100)
        client=razorpay.Client(auth=('rzp_test_dHjisSvcdwnH0r','NbkqlS0sbCMrtF9Avzppv25O'))
        #using razorpay id and secret code

        response_payment=client.order.create(dict(amount=total,currency="INR"))
        #razorpay using razorpay client
        #print(response_payment)
        order_id=response_payment['id'] #Retrieves the order_id from response
        order_status=response_payment['status'] #retrieves status from response
        if(order_status=="created"): #if status is created then store order_id in Payment and Order_details table
            p=Payment.objects.create(name=u.username,amount=total,order_id=order_id)
            p.save()
            for i in c:  #For each item creates a record inside Order_details table
                o=Order_details.objects.create(product=i.product,user=u,no_of_items=i.quantity,address=address,phoneno=phone,pin=pin,order_id=order_id)
                o.save()
        else:
            pass
        response_payment['name']=u.username


        context={'payment':response_payment}
        return render(request, 'payment.html',context)
    return render(request,'orderform.html')



@csrf_exempt
def payment_status(request,u):
    user = User.objects.get(username=u)
    if(not request.user.is_authenticated): #if user is not authenticated
        login(request,user) #allowing request user to login

    if(request.method=="POST"):
        response=request.POST
        print(response)




        param_dict={
            'razorpay_order_id':response['razorpay_order_id'],
            'razorpay_payment_id':response['razorpay_payment_id'],
            'razorpay_signature':response['razorpay_signature']
        }

        client = razorpay.Client(auth=('rzp_test_dHjisSvcdwnH0r','NbkqlS0sbCMrtF9Avzppv25O'))
        print(client)
        try:
            status=client.utility.verify_payment_signature(param_dict)  #to check authenticity of the razorpay signature
            print(status)

            #To retrieve a particular record in Payment table whose order  id matches the response order id
            p=Payment.objects.get(order_id=response['razorpay_order_id'])
            p.razorpay_payment_id=response['razorpay_payment_id'] #adds the payment id after successful payment
            p.paid=True #changes the paid status to True
            p.save()


            print(user.username)
            o=Order_details.objects.filter(user=user,order_id=response['razorpay_order_id']) #retireve the particular record in order_details
            #matching with current user and response order_id

            print(o)
            for i in o:
                i.payment_status="paid"
                i.save()

            #After successful payment deletes the item in cart for a particular user
            c=Cart.objects.filter(user=user)
            c.delete()


        except:
            pass

    return render(request,'payment_status.html',{'status':status})

@login_required
def order_view(request):
    u=request.user
    o=Order_details.objects.filter(user=u,payment_status="paid")
    context={'orders':o}
    return render(request,'order_view.html',context)


