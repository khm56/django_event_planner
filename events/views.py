from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.views import View
from .forms import UserSignup, UserLogin, ConcertForm
from .models import Concert
from django.contrib import messages

def home(request):
    return render(request, 'home.html')

class Signup(View):
    form_class = UserSignup
    template_name = 'signup.html'

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(user.password)
            user.save()
            messages.success(request, "You have successfully signed up.")
            login(request, user)
            return redirect("home")
        messages.warning(request, form.errors)
        return redirect("signup")


class Login(View):
    form_class = UserLogin
    template_name = 'login.html'

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():

            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            auth_user = authenticate(username=username, password=password)
            if auth_user is not None:
                login(request, auth_user)
                messages.success(request, "Welcome Back!")
                return redirect('concert-dashboard')
            messages.warning(request, "Wrong email/password combination. Please try again.")
            return redirect("login")
        messages.warning(request, form.errors)
        return redirect("login")


class Logout(View):
    def get(self, request, *args, **kwargs):
        logout(request)
        messages.success(request, "You have successfully logged out.")
        return redirect("login")

def concert_list(request):
    concerts = Concert.objects.all()
    query = request.GET.get('q')
    if query:
        concerts = concerts.filter(
            Q(organizer__username__icontains=query)|
            Q(name__icontains=query)|
            Q(description__icontains=query)|
            Q(concert_of__icontains=query)
        ).distinct()

    # favorite_list = []
    # if request.user.is_authenticated:
    #     favorite_list = request.user.favoriteconcert_set.all().values_list('concert', flat=True)

    context = {
       "concerts": concerts,
       # "favorite_list": favorite_list
    }
    return render(request, 'dashboard.html', context)

def concert_detail(request, concert_id):
    concert = Concert.objects.get(id=concert_id)
    # items = Item.objects.filter(concert=concert)
    context = {
        "concert": concert,
        # "items": items,
    }
    return render(request, 'concertdetail.html', context)

def concert_create(request):
    if request.user.is_anonymous:
        return redirect('signin')
    form = ConcertForm()
    if request.method == "POST":
        form = ConcertForm(request.POST, request.FILES)
        if form.is_valid():
            concert = form.save(commit=False)
            concert.organizer = request.user
            concert.save()
            return redirect('concert-dashboard')
    context = {
        "form":form,
    }
    return render(request, 'concertcreate.html', context)

def concert_update(request, concert_id):
    concert_obj = Concert.objects.get(id=concert_id)
    if not (request.user.is_staff or request.user == concert_obj.organizer):
        return redirect('no-access')
    form = ConcertForm(instance=concert_obj)
    if request.method == "POST":
        form = ConcertForm(request.POST, request.FILES, instance=concert_obj)
        if form.is_valid():
            form.save()
            return redirect('concert-dashboard')
    context = {
        "concert_obj": concert_obj,
        "form":form,
    }
    return render(request, 'concertupdate.html', context)

# def concert_delete(request, concert_id):
#     concert_obj = Concert.objects.get(id=concert_id)
#     if not (request.user.is_staff or request.user == concert_obj.organizer ):
#         return redirect('no-access')
#     restaurant_obj.delete()
#     return redirect('rconcert-dashboard')

