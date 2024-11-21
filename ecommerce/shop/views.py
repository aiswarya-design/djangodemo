from django.shortcuts import render,redirect
from shop.models import Category,Product
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
def allcategories(request):
    c=Category.objects.all()
    context={'cat': c}
    return render(request, 'category.html', context)
def allproducts(request,p): #here p receives the category id 1 usage(1 dynamic)
    c = Category.objects.get(id=p)# reads a particular category objects using id
    p = Product.objects.filter(category=c)# reads all products in category objects
    context = {'cat': c, 'product': p}
    return render(request, 'product.html', context)
def alldetails(request,p):
   d=Product.objects.get(id=p)
   context={'product':d}
   return render(request,'details.html',context)

def register(request):
    if(request.method == "POST"):
        use = request.POST.get('username')
        p = request.POST.get('password')
        c = request.POST.get('c')
        f = request.POST.get('f')
        l = request.POST.get('l')
        e = request.POST.get('e')
        if c==p:
            use = User.objects.create_user(username=use, password=p, first_name=f, last_name=l, email=e)
            use.save()
            return redirect('shop:categories')

    return render(request, 'register.html')
def user_login(request):
    if request.method=="POST":
        use = request.POST.get('u')
        p = request.POST.get('p')
        print(use,p)
        user=authenticate(username=use,password=p)
        if user:
            login(request, user)
            return redirect('shop:categories')
        else:
            messages.error(request,"Invalid credentials")
    return render(request,  'login.html')


@login_required
def user_logout(request):
    logout(request)
    return redirect('shop:categories')

def addcategory(request):
    if(request.method=="POST"):
        n=request.POST['n']
        image=request.FILES['image']
        d=request.POST['d']

        c=Category.objects.create(name=n,image=image,desc=d)
        c.save()
        return redirect('shop:categories')
    return render(request,'addcategory.html')

def addproduct(request):
    if (request.method =="POST"):
        n=request.POST['n']
        image=request.FILES['image']
        d=request.POST['d']
        s=request.POST['s']
        p=request.POST['p']
        c=request.POST['c']
        cat=Category.objects.get(name=c)

        p=Product.objects.create(name=n,image=image,desc=d,stock=s,price=p,category=cat)
        p.save()
        return redirect('shop:categories')
    return render(request,'addproduct.html')

def addstock(request,p):
    product=Product.objects.get(id=p)
    if(request.method=="POST"):
        product.stock=request.POST['n']
        product.save()
        return redirect('shop:categories')
    context={'pro':product}
    return render(request,'addstock.html',context)