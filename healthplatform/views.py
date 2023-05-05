from django.contrib import messages
from django.template import loader
from django.shortcuts import redirect, render
from django.http import HttpResponse
from django.contrib.auth import login, logout, authenticate

from healthplatform.forms import AppointmentForm
from .models import CustomUser, Doctor, Patient, Review
from django.contrib.auth.decorators import login_required


# Create your views here.

def home(request):
    template = loader.get_template('index.html')
    return HttpResponse(template.render())


def register_doctor(request):
    if request.method == 'POST':
        email = request.POST['email']
        phone = request.POST['phone']
        password = request.POST['password']
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        specialty = request.POST['specialty']
        dob = request.POST['dob']
        address = request.POST['address']
        user = CustomUser.objects.create_user(email=email, password=password, first_name=first_name,
                                              last_name=last_name, dob=dob, phone=phone, address=address)
        doctor = Doctor.objects.create(user=user, specialty=specialty)

        template = loader.get_template('index.html')
        return HttpResponse(template.render())
    else:
        template = loader.get_template('register_doctor.html')
        return HttpResponse(template.render())


def register_patient(request):
    if request.method == 'POST':
        email = request.POST['email']
        phone = request.POST['phone']
        password = request.POST['password']
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        dob = request.POST['dob']
        address = request.POST['address']
        user = CustomUser.objects.create_user(email=email, password=password, first_name=first_name,
                                              last_name=last_name, dob=dob, phone=phone, address=address)
        patient = Patient.objects.create(user=user)

        template = loader.get_template('index.html')
        return HttpResponse(template.render())
    else:
        template = loader.get_template('register_patient.html')
        return HttpResponse(template.render())


@login_required
def make_appointment(request, doctor_id):
    doctor = Doctor.objects.get(id=doctor_id)
    if request.method == 'POST':
        form = AppointmentForm(request.POST)
        if form.is_valid():
            # Create a new Appointment object based on the form data
            appointment = form.save(commit=False)
            appointment.patient = request.user
            appointment.doctor = doctor
            appointment.save()
            return redirect('home')
    else:
        form = AppointmentForm()
        return render(request, 'make_appointment.html', {'doctor': doctor, 'form': form})


def write_review(request, doctor_id):
    if request.method == 'POST':
        star = request.POST['star']
        comment = request.POST['comment']
        patient = request.user.patient  # assuming you have a user model and patient model
        doctor = Doctor.objects.get(id=doctor_id)
        review = Review.objects.create(patient=patient, doctor=doctor, star=star, comment=comment)
        messages.success(request, 'Your review has been submitted!')
        return redirect('doctor_detail', doctor_id=doctor_id)

    return render(request, 'add_review.html', {'doctor_id': doctor_id})


@login_required(login_url="login")
def deleteReview(request, pk):
    review = Review.objects.get(id=pk)

    if request.user != review.user:
        return HttpResponse('You are not owner of this review!!')

    if request.method == 'POST':
        review.delete()
        return redirect('home')
    context = {'obj': review}
    return render(request, 'delete.html', context)


def logoutUser(request):
    logout(request)
    return redirect('home')


def login(request):
    page = 'login'

    # if request.user.is_authenticated:
    #     return redirect('home')

    if request.method == 'POST':
        print("Hello!!")
        email = request.POST.get('email')
        password = request.POST.get('password')

        # try:
        #     user = CustomUser.objects.get(email=email)
        # except:
        #     messages.error(request, "Incorrect username or password combination")

        user = authenticate(request, email=email, password=password)

        if user is not None:
            return redirect('home')
        else:
            messages.error(request, "Incorrect email or password combination")
            return redirect('login')

    context = {'page': page}
    return render(request, 'login.html', context)
