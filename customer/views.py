from django.shortcuts import render, redirect
from django.views import View
from django.shortcuts import render, get_object_or_404
from .models import Category, Car, User, CartItem, Order, OrderItem, Profile
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

# Create your views here.

class Index(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'customer/index.html')

class Garage(View):
    def get(self, request, *args, **kwargs):
        luxury_cars = Car.objects.filter(category__name__contains='Luxury')
        vintage_cars = Car.objects.filter(category__name__contains='Vintage')
        classic_cars = Car.objects.filter(category__name__contains='Classic')

        
        context = {
            'luxury_cars': luxury_cars,
            'vintage_cars': vintage_cars,
            'classic_cars': classic_cars,
        }

        return render(request, 'customer/Garage.html', context)
    
def login_view(request):
    # if request.user.is_authenticated:
    #     return redirect('order')
    if request.method == 'POST':
        username = request.POST.get('uname')
        password = request.POST.get('pass')

        validate_user = authenticate(username=username, password=password)
        if validate_user is not None:
            login(request, validate_user)
            return redirect('index')
        else:
            messages.error(request, 'Wrong user name/password or user does not exist')
            return redirect('login')

    if request.user.is_authenticated:
        return render(request, 'customer/login.html', {"name": request.user.first_name})
    return render(request, 'customer/login.html', {})

def register(request):
    # Redirect to the index page if the user is already authenticated
    if request.user.is_authenticated:
        return redirect('index')
    
    # Process the registration form if the request method is POST
    if request.method == 'POST':
        # Retrieve form data
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        address = request.POST.get('address')

        # Validate password length
        if len(password) < 8:
            messages.error(request, 'Password must be at least 8 characters long')
            return redirect('register')
        
        # Validate password contains only numbers and alphabets
        if not password.isalnum():
            messages.error(request, 'Password must contain only numbers and alphabets')
            return redirect('register')

        # Check if username already exists
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists. Choose another username.')
            return redirect('register')
        
        # Create a new user
        new_user = User.objects.create_user(first_name=first_name, last_name=last_name,
                                             username=username, password=password,
                                             email=email, address=address)
        new_user.save()

        # Display success message and redirect to login page
        messages.success(request, 'User created successfully. Please login now.')
        return redirect('login')
    
    # Render the registration form template for GET requests
    return render(request, 'customer/register.html', {})


def LogoutView(request):
    logout(request)
    return redirect('login')

@login_required
def order_view(request):
    products = Car.objects.all()
    return render(request, 'customer/order.html', {'products': products})

@login_required
def product_list(request):
    products = Car.objects.all()
    return render(request, 'customer/order.html', {'products': products})
    
def add_to_cart(request, product_id):
    product = Car.objects.get(id=product_id)
    cart_item, created = CartItem.objects.get_or_create(product=product, user=request.user)
    
    cart_item.quantity += 1
    cart_item.save()
    return redirect('view_cart')


@login_required
def view_cart(request):
    CartItem.objects.filter(user=request.user.is_superuser).delete()
    cart_items = CartItem.objects.filter(user=request.user)
    total_price = sum(item.product.price * item.quantity for item in cart_items)
    return render(request, 'customer/cart.html', {'cart_items': cart_items, 'total_price': total_price})

def remove_from_cart(request, item_id):
    cart_item = CartItem.objects.get(id=item_id)
    cart_item.delete()
    return redirect('view_cart')

def view_order(request):
    # Delete any existing cart items for superuser
    CartItem.objects.filter(user=request.user.is_superuser).delete()
    
    # Retrieve cart items for the current user
    cart_items_cart = CartItem.objects.filter(user=request.user)
    
    # Redirect to the order page if the cart is empty
    if cart_items_cart.count() == 0:
        return redirect('order')
    
    # Calculate the total price of items in the cart
    total_price = sum(item.product.price * item.quantity for item in cart_items_cart)
    
    # Mark the order as paid
    is_paid = True
    
    # Get the current user
    user = request.user
    
    # Create a new order with the calculated total price
    new_order = Order.objects.create(is_paid=is_paid, user=user, total_price=total_price)
    new_order.save()
    
    # Add each cart item to the order
    for item in cart_items_cart:
        # Print the name of the product (optional)
        print(item.product.name)
        
        # Create an OrderItem for each cart item and add it to the order
        new_order.order_items.add(OrderItem.objects.create(product=item.product,
                                                            user=item.user,
                                                            quantity=item.quantity))
        
        # Retrieve all order items for the new order
        order_items = new_order.order_items.all()
        
        # Save the order
        new_order.save()
    
    # Delete all cart items for the current user
    CartItem.objects.filter(user=request.user).all().delete()    

    # Render the order confirmation page with necessary data
    return render(request, 'customer/order_confirmation.html', {'order_items': order_items,
                                                                 'order_total_price': total_price,
                                                                 'user_address': request.user.address,
                                                                 'user_first_name': request.user.first_name})


@login_required
def user_orders(request):
    user_orders = Order.objects.filter(user=request.user).all()
    return render(request, 'customer/user_orders.html', {'user_orders': user_orders})

def product(request, product_id):
    product = Car.objects.get(pk=product_id)
    recently_viewed_products = None
    # We can pass any dictionary to the session, in this case it is recently_viewed
    if 'recently_viewed' in request.session:
        # If there is a product that's already been viewed, remove it and add it later at the first index as below
        if product_id in request.session['recently_viewed']:
            request.session['recently_viewed'].remove(product_id)

        recently_viewed_products = Car.objects.filter(pk__in=request.session['recently_viewed'])
        recently_viewed_products = sorted(recently_viewed_products, 
            key=lambda x: request.session['recently_viewed'].index(x.id)
            )
        request.session['recently_viewed'].insert(0, product_id)
        # if there are more than 5 itmes in the session, remove the last item
        if len(request.session['recently_viewed']) > 5:
            request.session['recently_viewed'].pop()
    # If there is no intem recently viewed, then current product is added to the recently viewed list
    else:
        request.session['recently_viewed'] = [product_id]
    # update the session every single time 
    request.session.modified = True
    
    context = {'product': product, 'recently_viewed_products': recently_viewed_products}
    return render(request, 'customer/product.html', context)  

@login_required
def view_profile(request):
    # Attempt to retrieve the user's profile
    try:
        profile = request.user.profile
    except Profile.DoesNotExist:
        # If the profile does not exist, create one
        profile = Profile.objects.create(user=request.user)
        # You may want to redirect the user to a profile creation form instead

    return render(request, 'customer/profile.html', {'profile': profile})