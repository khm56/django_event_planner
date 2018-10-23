from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.views import View
from .forms import UserSignup, UserLogin, ConcertForm, UserUpdate
from .models import Concert, AttendConcert, FollowedUser
from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse
from datetime import datetime, timedelta, timezone
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.core.mail import EmailMessage

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
    present= datetime.now()
    concerts = Concert.objects.filter(start_date__gte=present)
    users=User.objects.all()
    query = request.GET.get('q')
    if query:
        concerts = concerts.filter(
            Q(organizer__username__icontains=query)|
            Q(name__icontains=query)|
            Q(description__icontains=query)|
            Q(concert_of__icontains=query)
        ).distinct()

    follow_list = []
    if request.user.is_authenticated:
        follow_list = request.user.follower.all().values_list('following', flat=True)
    context = {
       "concerts": concerts,
       "follow_list":follow_list,
       "users":users,
    }
    return render(request, 'list.html', context)



def profiles(request):
    users=User.objects.all()
    contect = {
        "users":users,
    }


def concert_dashboard(request):
    present=datetime.now()

    concerts = Concert.objects.filter(organizer=request.user)
    attending = AttendConcert.objects.filter(user=request.user).filter(Q(concert__start_date__gte=present))
    attended = AttendConcert.objects.filter(user=request.user).filter(Q(concert__start_date__lt=present))

    query = request.GET.get('q')
    if query:
        concerts = concerts.filter(
            Q(organizer__username__icontains=query)|
            Q(name__icontains=query)|
            Q(description__icontains=query)|
            Q(concert_of__icontains=query)
        ).distinct()


    context = {
       "concerts": concerts,
       "attending": attending,
       "attended": attended,
    }
    return render(request, 'dashboard.html', context)

def concert_detail(request, concert_id):
    concerts = Concert.objects.get(id=concert_id)
    booked= AttendConcert.objects.filter(concert=concerts)
    if request.method == "POST":
        quantity=request.POST.get("quantity")
        AttendConcert.objects.create(quantity=quantity, user=request.user, concert=concerts)
        concerts.capacity = int(concerts.capacity) - int(quantity)
        concerts.save()
        email = EmailMessage('Successfully Booked', 'You have succesffully booked for %s' %(concerts.name), to=[request.user.email])
        email.send()
        return redirect('concert-dashboard')

    context = {
        "concert": concerts,
        "booked":booked,
    }
    return render(request, 'concertdetail.html', context)

def concert_create(request):
    invitation=FollowedUser.objects.filter(following=request.user)
    if request.user.is_anonymous:
        return redirect('signin')
    form = ConcertForm()
    if request.method == "POST":
        form = ConcertForm(request.POST)
        if form.is_valid():
            concert = form.save(commit=False)
            concert.organizer = request.user
            concert.save()
            email = EmailMessage('New Concert', 'Dont miss %s book quickly' %(concert.name), to=[user.follower.email for user in invitation])
            email.send()
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

def profile_update(request, profile_id):
    profile = User.objects.get(id=profile_id)
    form = UserUpdate(instance=profile)
    if request.method == "POST":
        form = UserUpdate(request.POST, instance=profile)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(user.password)
            user.save()
            messages.success(request, "You have successfully Updated profile.")
            return redirect('concert-dashboard')
    context = {
        "profile": profile,
        "form":form,
    }
    return render(request, 'profileupdate.html', context)

def unbook(request, attend_id):
    booking_obj = AttendConcert.objects.get(user=request.user, id=attend_id)
    present=datetime.now()
    timeofevent=datetime.combine(booking_obj.concert.start_date, booking_obj.concert.start_time)
    if (timeofevent - timedelta(hours=3)) >= present:
        concert= Concert.objects.get(id=booking_obj.concert.id)
        concert.capacity=int(concert.capacity)+int(booking_obj.quantity)
        concert.save()
        booking_obj.delete()
    else:
        messages.success(request, "It's too late to unbook")
    return redirect('concert-dashboard')

def user_follow(request, user_id):
    user_obj = User.objects.get(id=user_id)
    if request.user.is_anonymous:
        return redirect('login')
    
    followed, created = FollowedUser.objects.get_or_create(follower=request.user, following=user_obj)
    if created:
        action="follow"
    else:
        followed.delete()
        action="unfollow"

    response = {
        "action": action,
    }
    return JsonResponse(response, safe=False)

def followed_users(request):
    if request.user.is_anonymous:
        return redirect('login')
    follow_list = request.user.follower.all().values_list('following', flat=True)
    users = User.objects.filter(id__in=follow_list)
    context = {
        "users": users,
    }
    return render(request, 'followed_users.html', context)

def organizer_detail(request, organizer_id):
    organizer = User.objects.get(id=organizer_id)
    concerts = Concert.objects.filter(organizer=organizer)
    counter=concerts.count()
    context = {
        "organizer": organizer,
        "concerts":concerts,
        "counter":counter,
    }
    return render(request, 'organizerdetail.html', context)

