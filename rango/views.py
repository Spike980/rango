from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from rango.models import Category
from rango.models import Page
from rango.forms import CategoryForm
from rango.forms import PageForm
from rango.forms import UserForm, UserProfileForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from datetime import datetime

def index(request):
	category_list = Category.objects.order_by('-likes')[:5]
	pages_list = Page.objects.order_by('-views')[:5]
	context_dict = {'categories': category_list, 'pages': pages_list}
	visits = int(request.COOKIES.get('visits', '0'))
	reset_last_visit_time = False
	response = render(request, 'rango/index.html', context_dict)
	if visits == 0:
		response = HttpResponseRedirect('/rango/')
		response.set_cookie('last_visit', datetime.now())
		response.set_cookie('visits', 1)
		return response


	if 'last_visit' in request.COOKIES:
		last_visit = request.COOKIES['last_visit']
		last_visit_time = datetime.strptime(last_visit[:-7], "%Y-%m-%d %H:%M:%S")

		if (datetime.now() - last_visit_time).seconds > 5:
			visits = visits + 1
			reset_last_visit_time = True
	else:
		# Cookie last_visit doesn't exist, so flag that it should be set
		reset_last_visit = True
	context_dict['visits'] = visits
	response = render(request,'rango/index.html', context_dict)

	if reset_last_visit_time:
		response.set_cookie('last_visit', datetime.now())
		response.set_cookie('visits', visits)

	return response
    	

def about(request):
    return render(request, 'rango/about.html')


def category(request, category_name_slug):
    context_dict = {}

    try:
        category = Category.objects.get(slug=category_name_slug)
        context_dict['category_name'] = category.name

        pages = Page.objects.filter(category=category)
        context_dict['pages'] = pages

        context_dict['category'] = category


    except Category.DoesNotExist:
        pass

    return render(request, 'rango/category.html', context_dict)

@login_required
def add_category(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save(commit=True)
            return index(request)
        else:
            print(form.errors)
    else:
        form = CategoryForm()
    return render(request, 'rango/add_category.html', {'form':form})

@login_required
def add_page(request, category_name_url):
	try:
		cat = Category.objects.get(slug=category_name_url)
	except Category.DoesNotExist:
		cat = None

	if request.method == 'POST':
		form = PageForm(request.POST)
		if form.is_valid():
			if cat:
				page = form.save(commit=False)
				page.category = cat
				page.views = 0
				page.save()
				# probably better to use a redirect here
				return category(request, category_name_url)
		else:
			print(form.errors)
	else:
		form = PageForm()
	context_dict = {'form':form, 'category':cat, 'category_name_url':category_name_url}
	return render(request, 'rango/add_page.html', context_dict)


def register(request):
		registered = False

		if request.method == 'POST':
				user_form = UserForm(data=request.POST)
				profile_form = UserProfileForm(data=request.POST)

				if user_form.is_valid() and profile_form.is_valid():
						user = user_form.save()
						# hash the password before storing using set_password() method
						user.set_password(user.password)
						user.save()

						profile = profile_form.save(commit=False)
						profile.user = user

						# Did the user provide a profile picture, if yes then save it to UserProfile model
						if 'picture' in request.FILES:
								profile.picture = request.FILES['picture']

						profile.save()

						registered = True

				else:
						print('{0} {1}'.format(user_form.errors, profile_form.errors))
		else:
				user_form = UserForm()
				profile_form = UserProfileForm()

		return render(request, 'rango/register.html', {'user_form': user_form, 'profile_form': profile_form, 'registered': registered})


def user_login(request):
		context_dict={}
		if request.method == 'POST':
				username = request.POST['username']
				password = request.POST['password']

				# use Django's machinery to authenticate user, if present a User object 
				user = authenticate(username=username, password=password)

				if user:
						if user.is_active:
								# if the user is valid and active, we can log the user in.
								login(request, user)
								return HttpResponseRedirect('/rango/')
						else:
								# the account is disabled
								context_dict['disabled'] = True
								return render(request, 'rango/login.html', context_dict)
				else:
						print("Invalid login details: {0}, {1}".format(username, password))
						context_dict['bad_details'] = True
						return render(request, 'rango/login.html', context_dict)
		else:
				return render(request, 'rango/login.html', {})


@login_required
def restricted(request):
		return render(request, 'rango/restricted.html', {})


@login_required
def user_logout(request):
		logout(request)
		return HttpResponseRedirect('/rango/')
