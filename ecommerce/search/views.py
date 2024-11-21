from django.shortcuts import render
from shop.models import Product
from django.db.models import Q

def search_products(request):
    query=""
    p=None
    if(request.method=="POST"):
        query= request.POST['q']
        print(query)
        if(query):
            p = Product.objects.filter(Q(name__icontains=query) | Q(desc__icontains=query)) #Inorder to add AND or OR logic into django queries here

    return render(request,'search.html',{'product':p,'q':query})
