from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.hashers import make_password
from .models import *
from django.http import JsonResponse, HttpResponse
from django.db.models import Sum
from django.db.models import Q, Count
from django.db.models.functions import ExtractYear
from django.core.paginator import Paginator
from django.core.files.storage import default_storage
from django.http import HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from datetime import datetime
from .utils import format_money_thai
from django.utils import timezone
from .forms import *
from django.views.decorators.csrf import csrf_exempt



def researcher_login_required(function):
    def wrap(request, *args, **kwargs):
        profile = get_object_or_404(Researcher, pk=kwargs['id'])
        # Check if the profile's associated user matches the request.user
        # or if the user is a main_admin
        if (request.user.is_authenticated and profile.user == request.user) or \
           (request.user.is_authenticated and request.user.user_type == 'main_admin'):
            return function(request, *args, **kwargs)
        else:
            # Redirect to login page or show forbidden message
            return HttpResponseForbidden("คุณไม่ได้รับอนุญาตให้มาหน้านี้")
    return wrap



def Home(request):
    researcher_count = Researcher.objects.count()
    research_project_count = ResearchProject.objects.count()
    research_count = Research_model.objects.count()
    performance_count = ResearchPerformance.objects.count()
    academic_count = Academic_model.objects.count()
    Mou_count = Mou.objects.count()
    # Sum the money from all ResearchProject instances
    total_money_aggregate = ResearchProject.objects.aggregate(total_money=Sum('money'))
    total_money = total_money_aggregate['total_money']

    if total_money is not None:
        total_money_number, total_money_unit = format_money_thai(total_money)
    else:
        # Handle the case when there's no data (total_money is None)
        total_money_number = 0
        total_money_unit = ""  # or any appropriate default value

    # Now you can use total_money_number and total_money_unit in your context

    # Get the current year
    current_year = timezone.now().year

    # Filter the research projects by year
    chart_data = ResearchProject.objects.values('date_promise__year').annotate(count=Count('id'))

    # Constructing the chart data dictionary
    chart_data_dict = {}
    for entry in chart_data:
        year = entry['date_promise__year']
        count = entry['count']
        chart_data_dict[year] = count

    # If you want to include years with no research projects, you can fill in the missing years with count 0
    for year in range(current_year - 4, current_year + 1):
        if year not in chart_data_dict:
            chart_data_dict[year] = 0

    # Sort the dictionary by keys
    sorted_chart_data = dict(sorted(chart_data_dict.items()))

    context = {
        'researcher_count': researcher_count,
        'research_project_count': research_project_count,
        'research_count': research_count,
        'performance_count': performance_count,
        'academic_count': academic_count,
        'Mou_count': Mou_count,
        'total_money_number': total_money_number,
        'total_money_unit': total_money_unit,
        'chart_data': sorted_chart_data
    }

    return render(request, 'home.html', context)

def Login(request):
    if request.method == 'POST':
        form_data = {
            'username': request.POST.get('username', ''),
            'password': request.POST.get('password', ''),
        }
        user = authenticate(request, username=form_data['username'], password=form_data['password'])
        if user is not None:
            login(request, user)
            return redirect('home')  # Redirect to a home page or dashboard
        else:
            # Check if the username exists in the database
            if User.objects.filter(username=form_data['username']).exists():
                messages.error(request, 'กรุณาใส่รหัสผ่านให้ถูกต้อง')
            else:
                messages.error(request, 'ชื่อผู้ใช้นี้ยังไม่ได้ลงทะเบียน')
            return render(request, 'login/login.html', {'form_data': form_data})
       
    return render(request, 'login/login.html')

def Logout(request):
    # sign user out
    logout(request)

    # Redirect to sign-in page
    return redirect('home')

def Register(request):
    faculties = Faculty.objects.all()

    if request.method == 'POST':
        form_data = {
            'username': request.POST.get('username', ''),
            'password': request.POST.get('password', ''),
            'nameTH': request.POST.get('nameTH', ''),
            'nameEN': request.POST.get('nameEN', ''),
            'position': request.POST.get('position', ''),
            'faculty_id': request.POST.get('faculty', ''),  # Get faculty ID from the form
            'department_id': request.POST.get('department', ''),    # Get department ID from the form
            'email': request.POST.get('email', ''),
            'phonenumber': request.POST.get('phonenumber', ''),
            'position': request.POST.get('position',''),
            'profile': request.FILES.get('imageInput', None),
            'UserType': 'researcher',
        }

        # Check if the username already exists
        if User.objects.filter(username=form_data['username']).exists():
            messages.error(request, 'ชื่อผู้ใช้นี้มีคนใช้งานแล้ว')
            return render(request, 'login/register.html', {'form_data': form_data})

        # Fetch the Faculty and Department objects
        faculty_id = form_data.pop('faculty_id')
        department_id = form_data.pop('department_id')
        faculty = Faculty.objects.get(pk=faculty_id)
        department = Department.objects.get(pk=department_id)

        # Create the User instance
        new_user = User.objects.create_user(
            username=form_data['username'],
            password=form_data['password'],
        )

        # Create the Researcher instance
        new_research = Researcher.objects.create(
            user=new_user,
            name_lastname_en=form_data['nameEN'],
            name_lastname_th=form_data['nameTH'],
            profile_picture=form_data['profile'],
            faculty=faculty,  # Assign the Faculty instance
            department=department,  # Assign the Department instance
            email=form_data['email'],
            telephone_number=form_data['phonenumber'],
            position=form_data['position'],
            usertype=form_data['UserType']
        )

        # Redirect to login page after successful registration
        return redirect('login')
    else:
        # Default form data for GET request
        form_data = {
            'username': '',
            'password': '',
            'nameTH': '',
            'nameEN': '',
            'position': '',
            'email': '',
            'phonenumber': '',
            'profile': None,
            'UserType': 'researcher',
        }

    context = {
        'form_data': form_data,
        'faculties': faculties,
        'position':Researcher.POSITION_CHOICES
    }

    return render(request, 'login/register.html', context)

def Profile(request,id):
    user_profile = get_object_or_404(Researcher, pk=id)

    user_research_projects = ResearchProject.objects.filter(internal_researchers__name=user_profile).order_by('-id')
    paginator_research_projects = Paginator(user_research_projects, 3)  # Show 10 academics per page
    page_number_research_projects = request.GET.get('page')
    page_research_projects = paginator_research_projects.get_page(page_number_research_projects)


    user_projects = Research_model.objects.filter(internal_researchers__name=user_profile).order_by('-id')
    paginator_projects = Paginator(user_projects, 5)  # Show 10 academics per page
    page_number_projects = request.GET.get('page')
    page_projects = paginator_projects.get_page(page_number_projects)


    user_academic = Academic_model.objects.filter(internal_researchers__name=user_profile).order_by('-id')
    paginator_academic = Paginator(user_academic, 5)  # Show 10 academics per page
    page_number_academic = request.GET.get('page')
    page_academic = paginator_academic.get_page(page_number_academic)
    
    user_researchperformance = ResearchPerformance.objects.filter(internal_researchers__name=user_profile).order_by('-id')
    paginator_researchperformance = Paginator(user_researchperformance, 5)  # Show 10 academics per page
    page_number_researchperformance = request.GET.get('page')
    page_researchperformance = paginator_researchperformance.get_page(page_number_researchperformance)


    context = {
        'user_profile': user_profile,
        'page_research_projects':page_research_projects,
        'page_projects': page_projects,
        'page_academic':page_academic,
        'page_researchperformance':page_researchperformance,
        'user': request.user,
    }

    # Render the profile template with the context
    return render(request, 'login/profile.html', context)

@researcher_login_required
def edit_profile(request, id):
    profile = get_object_or_404(Researcher, pk=id)
    faculties = Faculty.objects.all()

    if request.method == 'POST':
        profile.name_lastname_th = request.POST.get('name_lastname_th', profile.name_lastname_th)
        profile.name_lastname_en = request.POST.get('name_lastname_en', profile.name_lastname_en)
        profile.position = request.POST.get('position', profile.position)
        profile.faculty_id = request.POST.get('faculty', profile.faculty_id)
        profile.department_id = request.POST.get('department', profile.department_id)
        profile.email = request.POST.get('email', profile.email)
        profile.telephone_number = request.POST.get('telephone_number', profile.telephone_number)

        if 'profile_picture' in request.FILES:
            profile_picture = request.FILES['profile_picture']
            file_path = default_storage.save('researchers/' + profile_picture.name, profile_picture)
            profile.profile_picture = file_path

        profile.save()
        return redirect('profile', id=profile.id)

    context = {
        'user_profile': profile,
        'faculties': faculties,
        'position': Researcher.POSITION_CHOICES
    }
    return render(request, 'edit/edit_profile.html', context)

def Select (request):
       
    return render(request,'select.html')

def Select_report (request):
       
    return render(request,'select_report.html')

def Research_project(request):
    # Retrieve all Funds, Agencies, Faculties, and Researchers
    fund = Fund.objects.all()
    agency = Agency.objects.all()
    faculties = Faculty.objects.all()
    researchers = Researcher.objects.all().order_by('name_lastname_th')
    
    internal_research_position_choices = Internal_researcher.RESEARCH_POSITION_CHOICES
    external_research_position_choices = External_researcher.RESEARCH_POSITION_CHOICES

    inside_outside_choices = ResearchProject.INSIDE_OUTSIDE_CHOICES
    research_type_choices = ResearchProject.RESEARCH_TYPE_CHOICES
    strategic_choices = strategic.objects.all()
    status_choices = ResearchProject.STATUS_CHOICES    
    
    if 'btnaddfund' in request.POST:
        new_fund_from = request.POST.get('addfund')
        Fund.objects.create(fund_from=new_fund_from)
        return redirect('research_project')

    if 'btnaddagency' in request.POST:
        new_agency_from = request.POST.get('addagency')
        Agency.objects.create(agency_from=new_agency_from)
        return redirect('research_project')   

    if 'btn' in request.POST:
        strategic_name = request.POST.get('strategic')
        try:
            # Retrieve the specific strategic instance based on the name
            strategic_instance = strategic.objects.get(name=strategic_name)
        except strategic.DoesNotExist:
            messages.error(request, f"Strategic choice '{strategic_name}' does not exist.")
            return redirect('error_page')  # Redirect to the error page or handle it accordingly

        form_data = {
            'research_code': request.POST.get('research_code', ''),
            'research_nameTH': request.POST.get('research_nameTH', ''),
            'research_nameEN': request.POST.get('research_nameEN', ''),
            'inside_outside': request.POST.get('inside_outside', ''),
            'research_type': request.POST.get('research_type', ''),
            'strategic': strategic_instance,  # Assign the retrieved strategic instance
            'status': request.POST.get('status', ''),
            'file': request.FILES.get('fileInput', None),
            'money': request.POST.get('money', ''),
            'date': request.POST.get('date',''),
            'internal_researchers_ids': request.POST.getlist('name_inside', []),
            'internal_researchers_positions': request.POST.getlist('position_inside', []),
            'external_researchers_names': request.POST.getlist('name_outside', []),
            'external_researchers_positions': request.POST.getlist('position_outside', []),
            'fund_id': request.POST.getlist('fund', []),
            'agency_id': request.POST.getlist('agency', []),
            'faculty_id': request.POST.get('faculty', ''),
            'department_id': request.POST.get('department', ''),
        }    
        departments = Department.objects.filter(faculty_id=form_data['faculty_id']).values('id', 'name')
        existing_project = ResearchProject.objects.filter(research_code=form_data['research_code']).first()

        if existing_project:
            messages.error(request, "รหัสโครงการวิจัยนี้มีอยู่แล้ว")
            context = {
                'researchers': researchers,
                'internal_research_position_choices': internal_research_position_choices,
                'external_research_position_choices': external_research_position_choices,
                'inside_outside_choices': inside_outside_choices,
                'research_type_choices': research_type_choices,
                'strategic_choices': strategic_choices,
                'status_choices': status_choices,
                'fund': fund,
                'agency': agency,
                'faculties': faculties,
                'departments':departments,
                'form_data':form_data,
            }
            return render(request, 'research/research_project.html', context)

        date = datetime.strptime(form_data['date'], '%d-%m-%Y')

        try:
            new_project = ResearchProject(
                research_code=form_data['research_code'],
                research_nameTH=form_data['research_nameTH'],
                research_nameEN=form_data['research_nameEN'],
                inside_outside=form_data['inside_outside'],
                research_type=form_data['research_type'],
                strategic_choice=form_data['strategic'],  # Assign the retrieved strategic instance
                status=form_data['status'],
                file=form_data['file'],
                money=form_data['money'],
                date_promise = date,
                faculty_id=form_data['faculty_id'],
                department_id=form_data['department_id'],
            )
            new_project.save()
            
            for fund_id in form_data['fund_id']:
                try:
                    fund, created = Fund.objects.get_or_create(fund_from=fund_id)
                    new_project.fund.add(fund)
                except Fund.DoesNotExist:
                    pass

            for agency_id in form_data['agency_id']:
                try:
                    agency, created = Agency.objects.get_or_create(agency_from=agency_id)
                    new_project.agency.add(agency)
                except Agency.DoesNotExist:
                    pass

            for researcher_id, position in zip(form_data['internal_researchers_ids'], form_data['internal_researchers_positions']):
                try:
                    researcher = Researcher.objects.get(name_lastname_th=researcher_id)
                    internal_researcher = Internal_researcher.objects.create(name=researcher, research_position=position)
                    new_project.internal_researchers.add(internal_researcher)
                except (Researcher.DoesNotExist, IndexError):
                    pass

            for name, position in zip(form_data['external_researchers_names'], form_data['external_researchers_positions']):
                try:
                    external_researcher = External_researcher.objects.create(name=name, research_position=position)
                    new_project.external_researchers.add(external_researcher)
                except IndexError:
                    pass

            return redirect('home')
        except Fund.DoesNotExist:
            pass
        except Agency.DoesNotExist:
            pass

    context = {
        'researchers': researchers,
        'internal_research_position_choices': internal_research_position_choices,
        'external_research_position_choices': external_research_position_choices,
        'inside_outside_choices': inside_outside_choices,
        'research_type_choices': research_type_choices,
        'strategic_choices': strategic_choices,
        'status_choices': status_choices,
        'fund': fund,
        'agency': agency,
        'faculties': faculties,
    }

    return render(request, 'research/research_project.html', context)


def Research(request):
    researchers = Researcher.objects.all().order_by('name_lastname_th')
    internal_research_position_choices = Internal_researcher.RESEARCH_POSITION_CHOICES
    external_research_position_choices = External_researcher.RESEARCH_POSITION_CHOICES
    research_work_type_choices = Research_model.RESEARCH_WORK_TYPE_CHOICES
    publishing_type_choices = Research_model.PUBLISHING_TYPE_CHOICES
    publishing_level_choices = Research_model.PUBLISHING_LEVEL_CHOICES
    faculties = Faculty.objects.all()

    if request.method == 'POST':
        form_data = {
            'research_nameTH': request.POST.get('research_nameTH', ''),
            'research_nameEN': request.POST.get('research_nameEN', ''),
            'work_type': request.POST.get('work_type', ''),
            # 'publishing_type': request.POST.get('publishing_type', ''),
            'publishing_year': request.POST.get('publishing_year', ''),
            'publishing_level': request.POST.get('publishing_level', ''),
            'url': request.POST.get('url', ''),
            'internal_researchers_ids': request.POST.getlist('name_inside', []),
            'internal_researchers_positions': request.POST.getlist('position_inside', []),
            'external_researchers_names': request.POST.getlist('name_outside', []),
            'external_researchers_positions': request.POST.getlist('position_outside', []),
            'faculty_id': request.POST.get('faculty', ''),  # Change to 'faculty_id'
            'department_id': request.POST.get('department', ''),  # Change to 'department_id'
        }
        
        try:
            if form_data['work_type'] == 'อื่นๆ':
                # สร้าง instance ใหม่ของ ResearchProject
                other_work_type = request.POST.get('other_work_type', '')
                new_project = Research_model(
                    research_nameTH=form_data['research_nameTH'],
                    research_nameEN=form_data['research_nameEN'],
                    faculty_id=form_data['faculty_id'],  # Assign faculty_id
                    department_id=form_data['department_id'],  # Assign department_id
                    work_type=form_data['work_type'],
                    other_work_type=other_work_type,
                    # publishing_type=form_data['publishing_type'],
                    publishing_year=form_data['publishing_year'],
                    publishing_level=form_data['publishing_level'],
                    url=form_data['url'],
                )
            else:
                new_project = Research_model(
                    research_nameTH=form_data['research_nameTH'],
                    research_nameEN=form_data['research_nameEN'],
                    faculty_id=form_data['faculty_id'],  # Assign faculty_id
                    department_id=form_data['department_id'],  # Assign department_id
                    work_type=form_data['work_type'],
                    # publishing_type=form_data['publishing_type'],
                    publishing_year=form_data['publishing_year'],
                    publishing_level=form_data['publishing_level'],
                    url=form_data['url'],
                )

            new_project.save()

            # สำหรับ Internal_researchers
            for researcher_id, position in zip(form_data['internal_researchers_ids'], form_data['internal_researchers_positions']):
                try:
                    researcher = Researcher.objects.get(name_lastname_th=researcher_id)
                    # สร้างอินสแตนซ์ของ Internal_researcher
                    internal_researcher = Internal_researcher.objects.create(name=researcher, research_position=position)
                    # เชื่อม Internal_researcher กับ new_project
                    new_project.internal_researchers.add(internal_researcher)
                except (Researcher.DoesNotExist, IndexError):
                    pass

            # สำหรับ External_researchers
            for name, position in zip(form_data['external_researchers_names'], form_data['external_researchers_positions']):
                try:
                    # สร้างอินสแตนซ์ของ External_researcher
                    external_researcher = External_researcher.objects.create(name=name, research_position=position)
                    # เชื่อม External_researcher กับ new_project
                    new_project.external_researchers.add(external_researcher)
                except IndexError:
                    pass

            return redirect('home')
        except Fund.DoesNotExist:
            # จัดการเมื่อไม่พบ Funds ที่ระบุ
            pass
        except Agency.DoesNotExist:
            # จัดการเมื่อไม่พบ Agencies ที่ระบุ
            pass

    # โหลดหน้าแบบฟอร์มเมื่อเป็น GET request
    context = {
        'researchers': researchers,
        'internal_research_position_choices': internal_research_position_choices,
        'external_research_position_choices': external_research_position_choices,
        'research_work_type_choices': research_work_type_choices,
        'publishing_type_choices': publishing_type_choices,
        'publishing_level_choices': publishing_level_choices,
        'faculties': faculties,
    }
       
    return render(request, 'research/research.html', context)


def Academic(request):
    faculties = Faculty.objects.all()
    # ดึงข้อมูลทุก Funds และ Agencies
    funds = Fund.objects.all()
    agencies = Agency.objects.all()
    subdistricts = SubDistrict.objects.values_list('name_th', flat=True).distinct()
    districts = District.objects.values_list('name_th', flat=True).distinct()
    provinces = Province.objects.values_list('name_th', flat=True).distinct()

    # ดึงข้อมูลนักวิจัยทั้งหมด
    researchers = Researcher.objects.all().order_by('name_lastname_th')
    
    internal_research_position_choices = Internal_researcher.RESEARCH_POSITION_CHOICES
    external_research_position_choices = External_researcher.RESEARCH_POSITION_CHOICES

    work_type_choices = Academic_model.WORK_CHOICES
    integration_choices = Academic_model.INTERGRATION_CHOICES
    academic_type_choices = Academic_model.ACADEMIC_TYPE

    if 'btnaddfund' in request.POST:
        # Get the value of the new fund from the form
        new_fund_from = request.POST.get('addfund')

        # Create a new Fund object and save it to the database
        Fund.objects.create(fund_from=new_fund_from)

        # Redirect back to the same page after adding the fund
        return redirect('research_project')

    if 'btnaddagency' in request.POST:
        # Get the value of the new fund from the form
        new_agency_from = request.POST.get('addagency')

        # Create a new Fund object and save it to the database
        Agency.objects.create(agency_from=new_agency_from)

        # Redirect back to the same page after adding the fund
        return redirect('research_project')   

    if 'btn' in request.POST:
        form_data = {
            'workTH': request.POST.get('workTH', ''),
            'workEN': request.POST.get('workEN', ''),
            'year': request.POST.get('year', ''),
            'startDate': request.POST.get('startDate', ''),
            'endDate': request.POST.get('endDate', ''),
            'work_type': request.POST.get('work_type', ''),
            'integration': request.POST.get('integration', ''),
            'academic_type':request.POST.get('academic_type',''),
            'faculty_id': request.POST.get('faculty', ''),  # Change to 'faculty_id'
            'department_id': request.POST.get('department', ''),  # Change to 'department_id'
            'address': request.POST.get('address', ''),
            'subdistrict': request.POST.get('subdistrict', ''),
            'district': request.POST.get('district', ''),
            'province': request.POST.get('province', ''),
            'information': request.POST.get('information', ''),
            'money': request.POST.get('money', ''),
            'organizing_agency': request.POST.get('organizing_agency', ''),
            'partner_organize': request.POST.get('partner_organize', ''),
            'internal_researchers_ids': request.POST.getlist('name_inside', []),
            'internal_researchers_positions': request.POST.getlist('position_inside', []),
            'external_researchers_names': request.POST.getlist('name_outside', []),
            'external_researchers_positions': request.POST.getlist('position_outside', []),
            'fund_id': request.POST.getlist('fund', []),
            'agency_id': request.POST.getlist('agency', []),
        }    
        # Parse start date and end date into datetime objects
        start_date = datetime.strptime(form_data['startDate'], '%d-%m-%Y')
        end_date = datetime.strptime(form_data['endDate'], '%d-%m-%Y')
        subdistrict_instance = SubDistrict.objects.filter(name_th=form_data['subdistrict']).first()
        district_instance = District.objects.filter(name_th=form_data['district']).first()
        province_instance = Province.objects.filter(name_th=form_data['province']).first()

        try:
            if form_data['work_type'] == 'อื่นๆ':
                other_work_type = request.POST.get('other_work_type', '')
                new_project = Academic_model(
                    workTH=form_data['workTH'],
                    workEN=form_data['workEN'],
                    year=form_data['year'],
                    startDate=start_date,
                    endDate=end_date,
                    work_type=form_data['work_type'],
                    other_work_type=other_work_type,
                    integration=form_data['integration'],
                    academic_type=form_data['academic_type'],
                    faculty_id=form_data['faculty_id'],  # Assign faculty_id
                    department_id=form_data['department_id'],  # Assign department_id
                    address=form_data['address'],
                    subdistrict=subdistrict_instance,
                    district=district_instance,
                    province=province_instance,
                    money=form_data['money'],
                    information=form_data['information'],
                )
            else:
                new_project = Academic_model(
                    workTH=form_data['workTH'],
                    workEN=form_data['workEN'],
                    year=form_data['year'],
                    startDate=start_date,
                    endDate=end_date,
                    work_type=form_data['work_type'],
                    integration=form_data['integration'],
                    academic_type=form_data['academic_type'],
                    faculty_id=form_data['faculty_id'],  # Assign faculty_id
                    department_id=form_data['department_id'],  # Assign department_id
                    address=form_data['address'],
                    subdistrict=subdistrict_instance,
                    district=district_instance,
                    province=province_instance,
                    money=form_data['money'],
                    information=form_data['information'],
                )

            new_project.save()
            
            for fund_id in form_data['fund_id']:
                try:
                    fund, created = Fund.objects.get_or_create(fund_from=fund_id)
                    new_project.fund.add(fund)
                except Fund.DoesNotExist:
                    pass

            for agency_id in form_data['agency_id']:
                try:
                    agency, created = Agency.objects.get_or_create(agency_from=agency_id)
                    new_project.agency.add(agency)
                except Agency.DoesNotExist:
                    pass

            # สำหรับ Internal_researchers
            for researcher_id, position in zip(form_data['internal_researchers_ids'], form_data['internal_researchers_positions']):
                try:
                    researcher = Researcher.objects.get(name_lastname_th=researcher_id)
                    # สร้างอินสแตนซ์ของ Internal_researcher
                    internal_researcher = Internal_researcher.objects.create(name=researcher, research_position=position)
                    # เชื่อม Internal_researcher กับ new_project
                    new_project.internal_researchers.add(internal_researcher)
                except (Researcher.DoesNotExist, IndexError):
                    pass

            # สำหรับ External_researchers
            for name, position in zip(form_data['external_researchers_names'], form_data['external_researchers_positions']):
                try:
                    # สร้างอินสแตนซ์ของ External_researcher
                    external_researcher = External_researcher.objects.create(name=name, research_position=position)
                    # เชื่อม External_researcher กับ new_project
                    new_project.external_researchers.add(external_researcher)
                except IndexError:
                    pass

            return redirect('home')
        except Fund.DoesNotExist:
            # จัดการเมื่อไม่พบ Funds ที่ระบุ
            pass
        except Agency.DoesNotExist:
            # จัดการเมื่อไม่พบ Agencies ที่ระบุ
            pass

    # โหลดหน้าแบบฟอร์มเมื่อเป็น GET request
    context = {
        'researchers': researchers,
        'internal_research_position_choices': internal_research_position_choices,
        'external_research_position_choices': external_research_position_choices,
        'work_type_choices': work_type_choices,
        'academic_type_choices': academic_type_choices,
        'integration_choices': integration_choices,
        'funds': funds,  # changed variable name to 'funds'
        'agencies': agencies,  # changed variable name to 'agencies'
        'faculties': faculties,
        'subdistricts': subdistricts,
        'districts': districts,
        'provinces': provinces,
    }
       
    return render(request, 'research/academic.html', context)

def Performance(request):
    researchers = Researcher.objects.all().order_by('name_lastname_th')
    internal_research_position_choices = Internal_researcher.RESEARCH_POSITION_CHOICES
    external_research_position_choices = External_researcher.RESEARCH_POSITION_CHOICES
    agency_choices = Department.objects.all()


    if request.method == 'POST':
        form_data = {
            'research_name': request.POST.get('research_name', ''),
            'date': request.POST.get('date', ''),
            'agency': request.POST.get('agency', ''),
            'detail': request.POST.get('detail', ''),
            'file': request.FILES.get('fileInput', None),
            'publishing_level': request.POST.get('publishing_level', ''),
            'url': request.POST.get('url', ''),
            'internal_researchers_ids': request.POST.getlist('name_inside', []),
            'internal_researchers_positions': request.POST.getlist('position_inside', []),
            'external_researchers_names': request.POST.getlist('name_outside', []),
            'external_researchers_positions': request.POST.getlist('position_outside', []),
        }

        date = datetime.strptime(form_data['date'], '%d-%m-%Y')

        agency_id = form_data['agency']
        if agency_id.isdigit():  # Making sure the agency_id is a digit before fetching
            agency_instance = get_object_or_404(Department, id=agency_id)
        else:
            return HttpResponse("Invalid Department ID", status=400)


        try:
            # Create a new instance of ResearchPerformance
            new_project = ResearchPerformance.objects.create(
                research_name=form_data['research_name'],
                date=date,
                agency=agency_instance,
                detail=form_data['detail'],
                file=form_data['file'],
                url=form_data['url'],
            )

           # สำหรับ Internal_researchers
            for researcher_id, position in zip(form_data['internal_researchers_ids'], form_data['internal_researchers_positions']):
                try:
                    researcher = Researcher.objects.get(name_lastname_th=researcher_id)
                    # สร้างอินสแตนซ์ของ Internal_researcher
                    internal_researcher = Internal_researcher.objects.create(name=researcher, research_position=position)
                    # เชื่อม Internal_researcher กับ new_project
                    new_project.internal_researchers.add(internal_researcher)
                except (Researcher.DoesNotExist, IndexError):
                    pass

            # สำหรับ External_researchers
            for name, position in zip(form_data['external_researchers_names'], form_data['external_researchers_positions']):
                try:
                    # สร้างอินสแตนซ์ของ External_researcher
                    external_researcher = External_researcher.objects.create(name=name, research_position=position)
                    # เชื่อม External_researcher กับ new_project
                    new_project.external_researchers.add(external_researcher)
                except IndexError:
                    pass

            return redirect('home')
            
        except Exception as e:
            print(e)
    
    # Context data to be passed to the template
    context = {
        'researchers': researchers,
        'internal_research_position_choices': internal_research_position_choices,
        'external_research_position_choices': external_research_position_choices,
        'agency_choices': agency_choices,  # Add agency choices to the context
    }
      
    return render(request, 'research/performance.html', context)

def Mou_form(request):
    if not request.user.is_authenticated or (request.user.is_authenticated and request.user.researcher_profile.usertype not in ['main_admin', 'assistant_admin']):
        return redirect("home")
    
    if request.method == 'POST':
        form_Mou = MouForm(request.POST)
        form_Support = SupportAgencyForm(request.POST)
        form_Support_activity = SupportActivityForm(request.POST)
        
        if 'submitform' in request.POST:
            if form_Mou.is_valid():
                try:
                    form_Mou.save()
                    return redirect('mou_report')
                except Exception as e:
                    # Handle the error (e.g., log it, display a message)
                    print(e)

        elif 'supportAgencyForm' in request.POST:
            if form_Support.is_valid():
                try:
                    form_Support.save()
                    return redirect('mou')
                except Exception as e:
                    # Handle the error (e.g., log it, display a message)
                    print(e)
        
        elif 'supportActivityForm' in request.POST:
            if form_Support_activity.is_valid():
                try:
                    form_Support_activity.save()
                    return redirect('mou')
                except Exception as e:
                    # Handle the error (e.g., log it, display a message)
                    print(e)
    

    else:
        form_Mou = MouForm()
        form_Support = SupportAgencyForm()
        form_Support_activity = SupportActivityForm()

    context = {
        'form_Mou': form_Mou,
        'form_Support': form_Support,
        'form_Support_activity':form_Support_activity,
    }

    return render(request, 'research/mou.html', context)


def Researcher_report(request):
    faculties = Faculty.objects.all()
    departments = Department.objects.all()
    researchers = Researcher.objects.order_by('-id')

    # Initialize variables to None or appropriate default values
    faculty_id = ''
    department_id = ''
    firstname = ''

    if request.method == 'POST':
        # Now, extract form data
        faculty_id = request.POST.get('faculty')
        department_id = request.POST.get('department')
        firstname = request.POST.get('firstname')
        
        query = Q()
        if faculty_id:
            query &= Q(faculty_id=faculty_id)
        if department_id:
            query &= Q(department_id=department_id)
        if firstname:
            query &= Q(name_lastname_th__icontains=firstname)
        researchers = researchers.filter(query)
    

    # Determine chart_data based on whether faculty_id is set
    if faculty_id:
        data = researchers.values('department__name').annotate(total=Count('id')).order_by('department__name')
        departments = Department.objects.filter(faculty_id=faculty_id).values('id', 'name')
    else:
        data = researchers.values('faculty__name').annotate(total=Count('id')).order_by('faculty__name')

    chart_data = [{'category': x['department__name' if faculty_id else 'faculty__name'], 'value': x['total']} for x in data]
    total = sum(item['value'] for item in chart_data)

    # Add percentage to each item in chart_data
    for item in chart_data:
        item['percent'] = (item['value'] / total) * 100 if total > 0 else 0

    # Pagination setup
    paginator = Paginator(researchers, 10)  # Show 10 researchers per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'faculties': faculties,
        'departments': departments,
        'page_obj': page_obj,
        'chart_data': chart_data,
        'total': total,
        'faculty_id': faculty_id,
        'department_id': department_id,
        'firstname': firstname,
    }
    return render(request, 'showdata/researcher_report.html', context)



def Research_project_report(request):
    inside_outside_choices = ResearchProject.INSIDE_OUTSIDE_CHOICES
    research_type_choices = ResearchProject.RESEARCH_TYPE_CHOICES
    status_choices = ResearchProject.STATUS_CHOICES
    faculties = Faculty.objects.all()
    departments = Department.objects.all()
    fund = Fund.objects.all()
    research_projects = ResearchProject.objects.order_by('-id')
    # Initialize variables to None or appropriate default values
    faculty_id = ''
    department_id = ''
    search_query = ''
    # Assuming 'date_promise' is a DateTimeField in your ResearchProject model
    years_queryset = ResearchProject.objects.annotate(year=ExtractYear('date_promise')).values_list('year', flat=True).distinct()
    years = list(years_queryset)
    years.sort(reverse=True)  # Sort years in descending order if needed
    static_value = request.GET.get('static_value')

    if request.method == 'POST':
        query = Q()
        inside_outside = request.POST.get('inside')
        research_type = request.POST.get('type_research')
        status = request.POST.get('status')
        search_query = request.POST.get('search')
        faculty_id = request.POST.get('faculty')
        department_id = request.POST.get('department')
        year = request.POST.get('year')  # New filter for year
        funds = request.POST.get('fund_id')


        # Store selected values in context

        if faculty_id:
            query &= Q(faculty_id=faculty_id)
        if department_id:
            query &= Q(department_id=department_id)
        if inside_outside:
            query &= Q(inside_outside=inside_outside)
        if funds:
            query &= Q(fund__fund_from=funds)
        if research_type:
            query &= Q(research_type=research_type)
        if status:
            query &= Q(status=status)
        if search_query:
            query &= (Q(research_nameTH__icontains=search_query) | 
                    Q(research_nameEN__icontains=search_query) | 
                    Q(internal_researchers__name__name_lastname_en__icontains=search_query) |
                    Q(internal_researchers__name__name_lastname_th__icontains=search_query))
        if year:
            query &= Q(date_promise__year=year)  # Filter by year

        research_projects = research_projects.filter(query)



    # Determine chart_data based on whether faculty_id is set and static_value
    if static_value == 'faculty':
        # Logic for faculty option
        if faculty_id:
            data = research_projects.values('department__name').annotate(total=Count('id')).order_by('department__name')
            departments = Department.objects.filter(faculty_id=faculty_id).values('id', 'name')
        else:
            data = research_projects.values('faculty__name').annotate(total=Count('id')).order_by('faculty__name')

    elif static_value == 'budget':
        if faculty_id:
            # Aggregate money within departments of a specific faculty
            data = research_projects.filter(department__faculty=faculty_id).values('department__name').annotate(total=Sum('money')).order_by('department__name')
        else:
            # Aggregate money within faculties
            data = research_projects.values('faculty__name').annotate(total=Sum('money')).order_by('faculty__name')
    else:
            data = research_projects.values('faculty__name').annotate(total=Count('id')).order_by('faculty__name')

    chart_data = [{'category': x['department__name' if faculty_id else 'faculty__name'], 'value': (x['total'])} for x in data]
    total = sum(item['value'] for item in chart_data)

    # Add percentage to each item in chart_data
    for item in chart_data:
        item['percent'] = (item['value'] / total) * 100 if total > 0 else 0

    paginator = Paginator(research_projects, 3)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'inside_outside_choices': inside_outside_choices,
        'research_type_choices': research_type_choices,
        'status_choices': status_choices,
        'faculties': faculties,
        'departments': departments,
        'fund': fund,
        'chart_data': chart_data,
        'years': years,
        'total': total,
        'search_query':search_query,        
        'static_value':static_value,
    }

    return render(request, 'showdata/research_project_report.html', context)


def Research_report(request):
    # Common data for all requests
    research_work_type_choices = Research_model.RESEARCH_WORK_TYPE_CHOICES
    publishing_type_choices = Research_model.PUBLISHING_TYPE_CHOICES
    publishing_level_choices = Research_model.PUBLISHING_LEVEL_CHOICES
    publication_years = Research_model.objects.values_list('publishing_year', flat=True).distinct().order_by('publishing_year')
    
    # Initialize with all research data for default display
    researchs = Research_model.objects.order_by('-id')
    faculties = Faculty.objects.all()
    departments = Department.objects.all()

    faculty_id = ''
    department_id = ''
    search_query = ''

    years = Research_model.objects.values_list('publishing_year', flat=True).distinct()

    if request.method == 'POST':
        # Initialize an empty Q object
        query = Q()

        # Extract form data
        work_type = request.POST.get('type')
        # publishing_type = request.POST.get('publishing_type')
        publish_year = request.POST.get('publice_year')
        publish_level = request.POST.get('publice_level')
        search_query = request.POST.get('search')
        faculty_id = request.POST.get('faculty')
        department_id = request.POST.get('department')

        # Add conditions to the query based on form data
        if work_type:
            query &= Q(work_type=work_type)
        if faculty_id:
            query &= Q(faculty_id=faculty_id)
        if department_id:
            query &= Q(department_id=department_id)
        # if publishing_type:
        #     query &= Q(publishing_type=publishing_type)
        if publish_year:
            query &= Q(publishing_year=publish_year)
        if publish_level:
            query &= Q(publishing_level=publish_level)
        if search_query:
            query &= (Q(research_nameTH__icontains=search_query) | 
                    Q(research_nameEN__icontains=search_query) | 
                    Q(internal_researchers__name__name_lastname_en__icontains=search_query) |
                    Q(internal_researchers__name__name_lastname_th__icontains=search_query))

        # Apply the constructed Q object to filter the queryset
        researchs = researchs.filter(query)

     # Determine chart_data based on whether faculty_id is set
    if faculty_id:
        data = researchs.values('department__name').annotate(total=Count('id')).order_by('department__name')
        departments = Department.objects.filter(faculty_id=faculty_id).values('id', 'name')
    else:
        data = researchs.values('faculty__name').annotate(total=Count('id')).order_by('faculty__name')

    chart_data = [{'category': x['department__name' if faculty_id else 'faculty__name'], 'value': x['total']} for x in data]
    total = sum(item['value'] for item in chart_data)

     # Add percentage to each item in chart_data
    for item in chart_data:
        item['percent'] = (item['value'] / total) * 100 if total > 0 else 0
    # Re-initialize paginator and page_obj based on filtered query
    paginator = Paginator(researchs, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Context for both POST and GET requests
    context = {
        'page_obj': page_obj,
        'publication_years': publication_years,
        'research_work_type_choices': research_work_type_choices,
        'publishing_type_choices': publishing_type_choices,
        'publishing_level_choices': publishing_level_choices,
        'years': years,
        'total': total,
        'search_query':search_query,
        'faculties': faculties,
        'departments': departments,
        'chart_data': chart_data,
    }
    return render(request, 'showdata/research_report.html', context)


def Performance_report(request):
    performances = ResearchPerformance.objects.order_by('-id')
    faculties = Faculty.objects.all()
    departments = Department.objects.all()
    faculty_id = ''
    department_id = ''
    search_query = ''


    # Retrieve distinct years from the date field
    years = ResearchPerformance.objects.annotate(year=ExtractYear('date')).values_list('year', flat=True).distinct()
    
    query = Q()
    if 'filterbtn' in request.POST:
        faculty_id = request.POST.get('faculty', '')
        department_id = request.POST.get('department', '')
        year = request.POST.get('year', '')
        search_query = request.POST.get('search', '')

        if faculty_id:
            departments = Department.objects.filter(faculty_id=faculty_id)  # Filter departments based on selected faculty

        if department_id:
            query &= Q(agency_id=department_id)  # Filter by department

        if year:
            query &= Q(date__year=int(year))  # Filter by year

        if search_query:
            query &= Q(research_name__icontains=search_query)

        performances = performances.filter(query)

    if faculty_id:
        data = performances.values('agency__name').annotate(total=Count('id')).order_by('agency__name')
        departments = Department.objects.filter(faculty_id=faculty_id).values('id', 'name')
    else:
        data = performances.values('agency__faculty__name').annotate(total=Count('id')).order_by('agency__faculty__name')

    chart_data = [{'category': x['agency__name' if faculty_id else 'agency__faculty__name'], 'value': x['total']} for x in data]
    total = sum(item['value'] for item in chart_data)

     # Add percentage to each item in chart_data
    for item in chart_data:
        item['percent'] = (item['value'] / total) * 100 if total > 0 else 0

    paginator = Paginator(performances, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'faculties': faculties,
        'departments': departments,
        'page_obj': page_obj,
        'years': years,
        'chart_data': chart_data,
        'search_query': search_query,
        'total': total,
    }

    return render(request, 'showdata/performance_report.html', context)

def Academic_report(request):
    publication_years = Academic_model.objects.values_list('year', flat=True).distinct().order_by('year')
    work_choices = Academic_model.WORK_CHOICES
    integration_choices = Academic_model.INTERGRATION_CHOICES
    zone = Zone.objects.all()
    province = Province.objects.all() 
    district = District.objects.all()

    # Initialize academics with all AcademicWorks regardless of request type
    academics = Academic_model.objects.order_by('-id')
    faculties = Faculty.objects.all()
    departments = Department.objects.all()
    static_value = request.GET.get('static_value')
    faculty_id = ''
    department_id = ''
    search_query = ''
    province_id = ''
    district_id = ''
    chart_data = ''
    zones = ''
    if request.method == 'POST':
        query = Q()
        if static_value == 'zone':
            zones = request.POST.get('zone')
            province_id = request.POST.get('province')
            district_id = request.POST.get('district')
            year = request.POST.get('year')

            if province_id:
                query &= Q(province=province_id)  
            if district_id:
                query &= Q(district=district_id)
            if year:
                query &= Q(year=year)

            academics = academics.filter(query)

          
        else:
            year = request.POST.get('year')
            project_type = request.POST.get('project_type')
            integration_type = request.POST.get('integration_type')
            faculty_id = request.POST.get('faculty')
            department_id = request.POST.get('department')
            start_date = request.POST.get('startDate')
            end_date = request.POST.get('endDate')
            search_query = request.POST.get('search')

            if year:
                query &= Q(year=year)

            if project_type:
                query &= Q(work_type=project_type)
            
            if start_date and end_date:
                start_date = datetime.strptime(start_date, '%d-%m-%Y')
                end_date = datetime.strptime(end_date, '%d-%m-%Y')
                # query &= Q(startDate__gte=start_date, endDate__lte=end_date)
                query &= Q(startDate__range=(start_date, end_date)) | Q(endDate__range=(start_date, end_date))
            
            if integration_type:
                query &= Q(integration=integration_type)

            if faculty_id:
                query &= Q(faculty_id=faculty_id)

            if department_id:
                query &= Q(department_id=department_id)

            # Search query
            if search_query:
                academics = academics.filter(
                    Q(workTH__icontains=search_query) | 
                    Q(workEN__icontains=search_query)
                )
            # Apply the filter using the constructed Q object
            academics = academics.filter(query)

    # Determine chart_data based on whether faculty_id is set and static_value
    if static_value == 'faculty':
        # Logic for faculty option
        if faculty_id:
            data = academics.values('department__name').annotate(total=Count('id')).order_by('department__name')
            departments = Department.objects.filter(faculty_id=faculty_id).values('id', 'name')
            chart_data = [{'category': x['department__name' if faculty_id else 'faculty__name'], 'value': (x['total'])} for x in data]
        else:
            data = academics.values('faculty__name').annotate(total=Count('id')).order_by('faculty__name')
            chart_data = [{'category': x['department__name' if faculty_id else 'faculty__name'], 'value': (x['total'])} for x in data]

    elif static_value == 'budget':
        if faculty_id:
            # Aggregate money within departments of a specific faculty
            data = academics.filter(department__faculty=faculty_id).values('department__name').annotate(total=Sum('money')).order_by('department__name')
            chart_data = [{'category': x['department__name' if faculty_id else 'faculty__name'], 'value': (x['total'])} for x in data]

        else:
            # Aggregate money within faculties
            data = academics.values('faculty__name').annotate(total=Sum('money')).order_by('faculty__name')
            chart_data = [{'category': x['department__name' if faculty_id else 'faculty__name'], 'value': (x['total'])} for x in data]

    elif static_value == 'zone':
        if zones:
            data = academics.filter(province__zone=zones).values('province__name_th').annotate(total=Count('id')).order_by('province__name_th')
            province = Province.objects.filter(zone_id=zones).values('id', 'name_th')
            chart_data = [{'category': x['province__name_th'], 'value': x['total']} for x in data]
            if province_id:
                # Filter by selected province
                data = academics.filter(province__id=province_id).values('district__name_th').annotate(total=Count('id')).order_by('district__name_th')
                district = District.objects.filter(province_id=province_id).values('id', 'name_th')
                chart_data = [{'category': x['district__name_th'], 'value': x['total']} for x in data]
                if district_id:
                    # Filter by selected province
                    data = academics.filter(district_id=district_id).values('subdistrict__name_th').annotate(total=Count('id')).order_by('subdistrict__name_th')
                    chart_data = [{'category': x['subdistrict__name_th'], 'value': x['total']} for x in data]
        else:
            # No specific zone or province selected, show all zones
            data = academics.values('province__zone__name').annotate(total=Count('id')).order_by('province__zone__name')
            chart_data = [{'category': x['province__zone__name'], 'value': x['total']} for x in data]


    else:
        data = academics.values('faculty__name').annotate(total=Count('id')).order_by('faculty__name')
        chart_data = [{'category': x['department__name' if faculty_id else 'faculty__name'], 'value': (x['total'])} for x in data]

    total = sum(item['value'] for item in chart_data)

    # Add percentage to each item in chart_data
    for item in chart_data:
        item['percent'] = (item['value'] / total) * 100 if total > 0 else 0

    paginator = Paginator(academics, 10)  # Show 10 academics per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)


    context = {
        'page_obj': page_obj,
        'publication_years': publication_years,
        'work_choices': work_choices,
        'integration_choices': integration_choices,
        'faculties': faculties,
        'departments': departments,
        'chart_data': chart_data,
        'search_query':search_query,
        'total': total,
        'static_value':static_value,
        'zone':zone,
        'province':province,
        'district':district
    }

    return render(request, 'showdata/academic_report.html', context)

def Mou_report(request):
    faculties = Faculty.objects.all()
    mou_query = Mou.objects.order_by('-id')
    support_type = Mou.SUPPORT_TYPE
    search_query = ''
    if request.method == 'POST':
        query = Q()
        search_query = request.POST.get('search')
        faculty_id = request.POST.get('faculty')
        support_types = request.POST.get('support_type')
        start_date = request.POST.get('startDate')
        end_date = request.POST.get('endDate')
        
        if start_date and end_date:
            start_date = datetime.strptime(start_date, '%d-%m-%Y')
            end_date = datetime.strptime(end_date, '%d-%m-%Y')
            query &= Q(promise_start_date__range=(start_date, end_date))
        
        if support_types:
            query &= Q(support_type=support_types)

        if faculty_id:
            query &= Q(faculty_id=faculty_id)
            
        # Search query
        if search_query:
            mou_query = mou_query.filter(
                Q(project__icontains=search_query)
            )
        # Apply the filter using the constructed Q object
        mou_query = mou_query.filter(query)
    
    paginator = Paginator(mou_query, 15)  # Show 10 academics per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj':page_obj,
        'support_type':support_type,
        'faculties': faculties,
        'search_query':search_query,
        'mou_query':mou_query,
    }

    return render(request, 'showdata/mou_report.html', context)

def Mou_detail(request, id):
    mou_query = get_object_or_404(Mou, id=id)
    objectives_lines = mou_query.objectives.split('\n')
    goals_lines = mou_query.goals.split('\n')
    
    # Fetching related organizations and supporting activities
    organizations = mou_query.organizations.all()
    supporting_activities = mou_query.supporting_activities.all()

    context = {
        'mou_query': mou_query,
        'objectives_lines': objectives_lines,
        'goals_lines': goals_lines,
        'organizations': organizations,
        'supporting_activities': supporting_activities,
    }

    return render(request, 'detail/mou_detail.html', context)


def Research_project_detail(request, id):
    research_project = get_object_or_404(ResearchProject, id=id)

    # Combine internal and external researchers, tagging each with their type
    combined_researchers = [
        {'type': 'internal', 'researcher': researcher} 
        for researcher in research_project.internal_researchers.all()
    ] + [
        {'type': 'external', 'researcher': researcher} 
        for researcher in research_project.external_researchers.all()
    ]

    context = {
        'research_project': research_project,
        'combined_researchers': combined_researchers,
    }
       
    return render(request, 'detail/research_project_detail.html', context)


def Research_detail(request, id):
    research_project = get_object_or_404(Research_model, id=id)

    combined_researchers = [
        {'type': 'internal', 'researcher': researcher} 
        for researcher in research_project.internal_researchers.all()
    ] + [
        {'type': 'external', 'researcher': researcher} 
        for researcher in research_project.external_researchers.all()
    ]

    # Directly pass the instance to your context
    context = {
        'research_project': research_project,
        'combined_researchers': combined_researchers,
    }
       
    return render(request, 'detail/research_detail.html', context)

def Performance_detail (request,id):
    researchperformance = get_object_or_404(ResearchPerformance, id=id)

    # Directly pass the instance to your context
    context = {
        'researchperformance': researchperformance,
    }
       
    return render(request,'detail/performance_detail.html',context)


def Academic_detail(request, id):
    # Fetch the Academic_model instance by id
    academic = get_object_or_404(Academic_model, id=id)

    # Split the 'organizing_agency' text into lines
    if academic.organizing_agency:
        organizing_agency_lines = academic.organizing_agency.split('\n')
    else:
        organizing_agency_lines = ['-']

    # Split the 'partner_organize' text into lines
    if academic.partner_organize:
        partner_organize_lines = academic.partner_organize.split('\n')
    else:
        partner_organize_lines = ['-']
        
    combined_researchers = [
        {'type': 'internal', 'researcher': researcher} 
        for researcher in academic.internal_researchers.all()
    ] + [
        {'type': 'external', 'researcher': researcher} 
        for researcher in academic.external_researchers.all()
    ]

    # Pass the lines along with the academic instance to your context
    context = {
        'academic': academic,
        'organizing_agency_lines': organizing_agency_lines,
        'partner_organize_lines': partner_organize_lines,
        'combined_researchers': combined_researchers,
    }

    return render(request, 'detail/academic_detail.html', context)


def get_departments(request):
    selected_faculty_id = request.GET.get('faculty_id')
    departments = Department.objects.filter(faculty_id=selected_faculty_id).values('id', 'name')
    return JsonResponse(list(departments), safe=False)

@csrf_exempt
def delete_fund(request, fund_id):
    if request.method == 'DELETE':
        try:
            # Delete the Fund object from the database
            fund = Fund.objects.get(pk=fund_id)
            fund.delete()

            return JsonResponse({'message': 'Fund deleted successfully'}, status=200)
        except Fund.DoesNotExist:
            return JsonResponse({'error': 'Fund not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    else:
        return JsonResponse({'error': 'Invalid method'}, status=405)

@csrf_exempt
def delete_agency(request, agency_id):
    if request.method == 'DELETE':
        try:
            # Delete the Agency object from the database
            agency = Agency.objects.get(pk=agency_id)
            agency.delete()

            return JsonResponse({'message': 'Agency deleted successfully'}, status=200)
        except Agency.DoesNotExist:
            return JsonResponse({'error': 'Agency not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    else:
        return JsonResponse({'error': 'Invalid method'}, status=405)
    
@login_required
def edit_research_project(request, id):
    research_project = get_object_or_404(ResearchProject, id=id)
    user_researcher = Researcher.objects.filter(user=request.user).first()

    # Check if the user is an admin
    if user_researcher and user_researcher.usertype in 'main_admin':
        # Admins can edit any project
        pass
    else:
        # Check if the user is listed as an internal or external researcher for the project
        if not user_researcher:
            return HttpResponseForbidden("นี้ไม่ใช่โครงการวิจัยของคุณไม่สามารถแก้ไขได้")

        internal_researchers = research_project.internal_researchers.filter(name=user_researcher)
        external_researchers = research_project.external_researchers.filter(name=user_researcher.user)

        if not internal_researchers.exists() and not external_researchers.exists():
            return HttpResponseForbidden("นี้ไม่ใช่โครงการวิจัยของคุณไม่สามารถแก้ไขได้")

    if 'btnaddfund' in request.POST:
        # Get the value of the new fund from the form
        new_fund_from = request.POST.get('addfund')
        # Create a new Fund object and save it to the database
        Fund.objects.create(fund_from=new_fund_from)
        return redirect('edit_research_project', id=research_project.id)

    if 'btnaddagency' in request.POST:
        # Get the value of the new agency from the form
        new_agency_from = request.POST.get('addagency')
        # Create a new Agency object and save it to the database
        Agency.objects.create(agency_from=new_agency_from)
        return redirect('edit_research_project', id=research_project.id)

    if request.method == 'POST':
        faculty_name = request.POST.get('faculty')
        department_name = request.POST.get('department')
        strategic_name = request.POST.get('strategic')
        faculty_instance, created = Faculty.objects.get_or_create(name=faculty_name)
        department_instance = Department.objects.filter(name=department_name, faculty=faculty_instance).first()
        strategic_instance = strategic.objects.filter(name=strategic_name).first()

        if not department_instance:
            department_instance = Department.objects.create(name=department_name, faculty=faculty_instance)

        research_project.research_code = request.POST.get('research_code', research_project.research_code)
        research_project.research_nameTH = request.POST.get('research_nameTH', research_project.research_nameTH)
        research_project.research_nameEN = request.POST.get('research_nameEN', research_project.research_nameEN)
        research_project.faculty = faculty_instance
        research_project.department = department_instance
        research_project.inside_outside = request.POST.get('inside_outside', research_project.inside_outside)
        research_project.research_type = request.POST.get('research_type', research_project.research_type)
        research_project.strategic_choice = strategic_instance
        research_project.status = request.POST.get('status', research_project.status)
        research_project.money = request.POST.get('money', research_project.money)

        date_time = request.POST.get('date')
        research_project.date_promise = datetime.strptime(date_time, '%d-%m-%Y')

        if 'fileInput' in request.FILES:
            research_project.file = request.FILES['fileInput']

        # Update internal researchers
        current_internal_researchers = research_project.internal_researchers.all()
        updated_internal_ids = request.POST.getlist('name_inside')
        updated_internal_positions = request.POST.getlist('position_inside')
        updated_internal_ids = [int(id) for id in updated_internal_ids]

        for current_researcher in current_internal_researchers:
            if current_researcher.id not in updated_internal_ids:
                research_project.internal_researchers.remove(current_researcher)
            else:
                index = updated_internal_ids.index(current_researcher.id)
                current_researcher.research_position = updated_internal_positions[index]
                current_researcher.save()

        for id, position in zip(updated_internal_ids, updated_internal_positions):
            if not Internal_researcher.objects.filter(id=id).exists():
                researcher_instance = Researcher.objects.get(id=id)
                new_internal_researcher = Internal_researcher.objects.create(
                    name=researcher_instance, 
                    research_position=position
                )
                research_project.internal_researchers.add(new_internal_researcher)

        research_project.external_researchers.clear()
        updated_external_names = request.POST.getlist('name_outside')
        updated_external_positions = request.POST.getlist('position_outside')

        for name, position in zip(updated_external_names, updated_external_positions):
            researcher = External_researcher.objects.filter(name=name, research_position=position).first()
            if researcher:
                research_project.external_researchers.add(researcher)
            else:
                new_researcher = External_researcher.objects.create(name=name, research_position=position)
                research_project.external_researchers.add(new_researcher)

        research_project.save()

        fund_ids = request.POST.getlist('fund', [])
        if fund_ids:
            research_project.fund.set(Fund.objects.filter(id__in=fund_ids))

        agency_ids = request.POST.getlist('agency', [])
        if agency_ids:
            research_project.agency.set(Agency.objects.filter(id__in=agency_ids))

        return redirect('home')

    else:
        context = {
            'research_project': research_project,
            'researchers': Researcher.objects.all(),
            'current_internal_researchers': research_project.internal_researchers.all(),
            'current_external_researchers': research_project.external_researchers.all(),
            'internal_research_position_choices': Internal_researcher.RESEARCH_POSITION_CHOICES,
            'external_research_position_choices': External_researcher.RESEARCH_POSITION_CHOICES,
            'inside_outside_choices': ResearchProject.INSIDE_OUTSIDE_CHOICES,
            'research_type_choices': ResearchProject.RESEARCH_TYPE_CHOICES,
            'strategic_choices': strategic.objects.all(),
            'status_choices': ResearchProject.STATUS_CHOICES,
            'fund': Fund.objects.all(),
            'agency': Agency.objects.all(),
        }

        return render(request, 'edit/edit_research_project.html', context)

def edit_research(request, id):
    research_project = get_object_or_404(Research_model, id=id)
    user_researcher = Researcher.objects.filter(user=request.user).first()

    if user_researcher and user_researcher.usertype in 'main_admin':
        # Admins can edit any project
        pass
    else:
        # Check if the user is listed as an internal or external researcher for the project
        if not user_researcher:
            return HttpResponseForbidden("นี้ไม่ใช่โครงการวิจัยของคุณไม่สามารถแก้ไขได้")

    # Check if the user is listed as an internal or external researcher for the project
    internal_researchers = research_project.internal_researchers.filter(name=user_researcher)
    external_researchers = research_project.external_researchers.filter(name=user_researcher.user)

    if not internal_researchers.exists() and not external_researchers.exists():
        return HttpResponseForbidden("นี้ไม่ใช่ผลงานวิจัยของคุณไม่สามารถแก้ไขได้")

    if request.method == 'POST':
        faculty_name = request.POST.get('faculty')
        department_name = request.POST.get('department')


        # Get or create Faculty instance
        faculty_instance, created = Faculty.objects.get_or_create(name=faculty_name)

        # Try to get the Department instance by name
        department_instance = Department.objects.filter(name=department_name, faculty=faculty_instance).first()

        if department_instance:
            # Department with the same name and faculty already exists, update its fields if needed
            # Update department fields if necessary
            # For example:
            # department_instance.some_field = request.POST.get('some_field', department_instance.some_field)
            department_instance.save()
        else:
            # Create new Department instance if it doesn't exist
            department_instance = Department.objects.create(name=department_name, faculty=faculty_instance)        

        research_project.research_nameTH = request.POST.get('research_nameTH', research_project.research_nameTH)
        research_project.research_nameEN = request.POST.get('research_nameEN', research_project.research_nameEN)
        # กำหนดค่าให้กับฟิลด์ "faculty" ใน Research_model
        research_project.faculty = faculty_instance
        research_project.department = department_instance
        research_project.work_type = request.POST.get('work_type', research_project.work_type)
        research_project.other_work_type = request.POST.get('other_work_type', research_project.other_work_type)
        # research_project.publishing_type = request.POST.get('publishing_type', research_project.publishing_type)
        research_project.publishing_year = request.POST.get('publishing_year', research_project.publishing_year)
        research_project.publishing_level = request.POST.get('publishing_level', research_project.publishing_level)
        research_project.url = request.POST.get('url', research_project.url)
        
        research_project.save()
        
        # Fetch current internal researcher relationships
        current_internal_researchers = research_project.internal_researchers.all()

        # Lists from the form submission
        updated_internal_ids = request.POST.getlist('name_inside')
        updated_internal_positions = request.POST.getlist('position_inside')

        # Convert IDs from strings to integers
        updated_internal_ids = [int(id) for id in updated_internal_ids]

        # Update and Remove Logic for Internal Researchers
        for current_researcher in current_internal_researchers:
            if current_researcher.id not in updated_internal_ids:
                # Remove researchers not in the updated list
                research_project.internal_researchers.remove(current_researcher)
            else:
                # Update existing researchers
                index = updated_internal_ids.index(current_researcher.id)
                current_researcher.research_position = updated_internal_positions[index]
                current_researcher.save()

        # Adding New Researchers
        for id, position in zip(updated_internal_ids, updated_internal_positions):
            if not Internal_researcher.objects.filter(id=id).exists():
                # Fetch the Researcher instance
                researcher_instance = Researcher.objects.get(id=id)
                # Create a new Internal_researcher instance and add to the project
                new_internal_researcher = Internal_researcher.objects.create(
                    name=researcher_instance, 
                    research_position=position
                )
                research_project.internal_researchers.add(new_internal_researcher)
        
        # Clear the existing many-to-many relationships for external_researchers
        research_project.external_researchers.clear()

        # Assuming 'name_outside' and 'position_outside' are the correct form field names
        updated_external_names = request.POST.getlist('name_outside')
        updated_external_positions = request.POST.getlist('position_outside')

        for name, position in zip(updated_external_names, updated_external_positions):
            # Instead of get_or_create, use filter().first() to safely handle duplicates
            researcher = External_researcher.objects.filter(name=name, research_position=position).first()

            if researcher:
                # If a matching researcher is found, use it
                research_project.external_researchers.add(researcher)
            else:
                # If no matching researcher, create a new one
                new_researcher = External_researcher.objects.create(name=name, research_position=position)
                research_project.external_researchers.add(new_researcher)

        research_project.save()

        return redirect('home')  # Make sure to replace 'home' with your actual URL name

    else:
        # Preparing context for GET request, including all necessary objects
        context = {
            'research_project': research_project,
            'researchers': Researcher.objects.all(),
            'current_internal_researchers': research_project.internal_researchers.all(),
            'current_external_researchers': research_project.external_researchers.all(),
            'internal_research_position_choices': Internal_researcher.RESEARCH_POSITION_CHOICES,
            'external_research_position_choices': External_researcher.RESEARCH_POSITION_CHOICES,
            'research_work_type_choices': Research_model.RESEARCH_WORK_TYPE_CHOICES,
            'publishing_type_choices': Research_model.PUBLISHING_TYPE_CHOICES,
            'publishing_level_choices': Research_model.PUBLISHING_LEVEL_CHOICES,
        }    

        return render(request, 'edit/edit_research.html', context)
    

def edit_researchperformance(request, id):
    research_project = get_object_or_404(ResearchPerformance, id=id)

    if request.method == 'POST':
        # Basic project information update
        research_project.research_name = request.POST.get('research_name', research_project.research_name)        
        # Retrieve the agency name from the POST data
        agency_name = request.POST.get('agency')

        # Get the Department instance corresponding to the agency name
        department_instance = Department.objects.filter(name=agency_name).first()

        # Assign the Department instance to the agency field
        research_project.agency = department_instance
        
        research_project.detail = request.POST.get('detail', research_project.detail)
        research_project.url = request.POST.get('url', research_project.url)
        # Get the date string from the POST data
        date_time = request.POST.get('date')
        date = datetime.strptime(date_time, '%d-%m-%Y')
        research_project.date_promise = date

        # File handling
        file = request.FILES.get('fileInput')
        if file:
            research_project.file = file

        research_project.save()
        # Fetch current internal researcher relationships
        current_internal_researchers = research_project.internal_researchers.all()

        # Lists from the form submission
        updated_internal_ids = request.POST.getlist('name_inside')
        updated_internal_positions = request.POST.getlist('position_inside')

        # Convert IDs from strings to integers
        updated_internal_ids = [int(id) for id in updated_internal_ids]

        # Update and Remove Logic for Internal Researchers
        for current_researcher in current_internal_researchers:
            if current_researcher.id not in updated_internal_ids:
                # Remove researchers not in the updated list
                research_project.internal_researchers.remove(current_researcher)
            else:
                # Update existing researchers
                index = updated_internal_ids.index(current_researcher.id)
                current_researcher.research_position = updated_internal_positions[index]
                current_researcher.save()

        # Adding New Researchers
        for id, position in zip(updated_internal_ids, updated_internal_positions):
            if not Internal_researcher.objects.filter(id=id).exists():
                # Fetch the Researcher instance
                researcher_instance = Researcher.objects.get(id=id)
                # Create a new Internal_researcher instance and add to the project
                new_internal_researcher = Internal_researcher.objects.create(
                    name=researcher_instance, 
                    research_position=position
                )
                research_project.internal_researchers.add(new_internal_researcher)
        
     # Clear the existing many-to-many relationships for external_researchers
        research_project.external_researchers.clear()

        # Assuming 'name_outside' and 'position_outside' are the correct form field names
        updated_external_names = request.POST.getlist('name_outside')
        updated_external_positions = request.POST.getlist('position_outside')

        for name, position in zip(updated_external_names, updated_external_positions):
            # Instead of get_or_create, use filter().first() to safely handle duplicates
            researcher = External_researcher.objects.filter(name=name, research_position=position).first()

            if researcher:
                # If a matching researcher is found, use it
                research_project.external_researchers.add(researcher)
            else:
                # If no matching researcher, create a new one
                new_researcher = External_researcher.objects.create(name=name, research_position=position)
                research_project.external_researchers.add(new_researcher)

        research_project.save()

        return redirect('home')  # Make sure to replace 'some_success_url' with your actual URL name

    else:
        # Preparing context for GET request, including all necessary objects
        context = {
            'research_project': research_project,
            'researchers': Researcher.objects.all(),
            'current_internal_researchers': research_project.internal_researchers.all(),
            'current_external_researchers': research_project.external_researchers.all(),
            'internal_research_position_choices': Internal_researcher.RESEARCH_POSITION_CHOICES,
            'external_research_position_choices': External_researcher.RESEARCH_POSITION_CHOICES,
        }    

        return render(request, 'edit/edit_performance.html', context)

def edit_academic(request, id):
    academic_project = get_object_or_404(Academic_model, id=id)
    user_researcher = Researcher.objects.filter(user=request.user).first()
    subdistricts = SubDistrict.objects.values_list('name_th', flat=True).distinct()
    districts = District.objects.values_list('name_th', flat=True).distinct()
    provinces = Province.objects.values_list('name_th', flat=True).distinct()

    if user_researcher and user_researcher.usertype in 'main_admin':
        # Admins can edit any project
        pass
    else:
        # Check if the user is listed as an internal or external researcher for the project
        if not user_researcher:
            return HttpResponseForbidden("นี้ไม่ใช่โครงการวิจัยของคุณไม่สามารถแก้ไขได้")

    # Check if the user is listed as an internal or external researcher for the project
    internal_researchers = academic_project.internal_researchers.filter(name=user_researcher)
    external_researchers = academic_project.external_researchers.filter(name=user_researcher.user)

    if not internal_researchers.exists() and not external_researchers.exists():
        return HttpResponseForbidden("นี้ไม่ใช่งานบริการวิชาของคุณไม่สามารถแก้ไขได้")
    
    if 'btnaddfund' in request.POST:
        # Get the value of the new fund from the form
        new_fund_from = request.POST.get('addfund')

        # Create a new Fund object and save it to the database
        Fund.objects.create(fund_from=new_fund_from)

        # Redirect back to the same page after adding the fund
        return redirect('edit_academic', id=academic_project.id)
    if 'btnaddagency' in request.POST:
        # Get the value of the new fund from the form
        new_agency_from = request.POST.get('addagency')

        # Create a new Fund object and save it to the database
        Agency.objects.create(agency_from=new_agency_from)

        # Redirect back to the same page after adding the fund
        return redirect('edit_academic', id=academic_project.id)

    if request.method == 'POST':
        faculty_name = request.POST.get('faculty')
        department_name = request.POST.get('department')
        subdistrict_name = request.POST.get('subdistrict')
        district_name = request.POST.get('district')
        province_name = request.POST.get('province')

        # Get or create Faculty instance
        faculty_instance, created = Faculty.objects.get_or_create(name=faculty_name)

        # Try to get the Department instance by name
        department_instance = Department.objects.filter(name=department_name, faculty=faculty_instance).first()

        if department_instance:
            # Department with the same name and faculty already exists, update its fields if needed
            # Update department fields if necessary
            # For example:
            # department_instance.some_field = request.POST.get('some_field', department_instance.some_field)
            department_instance.save()
        else:
            # Create new Department instance if it doesn't exist
            department_instance = Department.objects.create(name=department_name, faculty=faculty_instance)   
            
        try:
            subdistrict_instance = SubDistrict.objects.get(name_th=subdistrict_name)
            district_instance = District.objects.get(name_th=district_name)
            province_instance = Province.objects.get(name_th=province_name)
        except SubDistrict.MultipleObjectsReturned:
            # Handle the case where multiple SubDistrict objects have the same name
            # For example, you could choose one of the objects or prompt the user to resolve the conflict
            # Here, we're just selecting the first object found
            subdistrict_instance = SubDistrict.objects.filter(name_th=subdistrict_name).first()
            district_instance = District.objects.filter(name_th=district_name).first()
            province_instance = Province.objects.filter(name_th=province_name).first()
        except SubDistrict.DoesNotExist:
            # Handle the case where no SubDistrict object with the given name is found
            # For example, you could create a new SubDistrict object
            subdistrict_instance = SubDistrict.objects.create(name_th=subdistrict_name)
            district_instance = District.objects.create(name_th=district_name)
            province_instance = Province.objects.create(name_th=province_name)


        academic_project.workTH = request.POST.get('workTH', academic_project.workTH)
        academic_project.workEN = request.POST.get('workEN', academic_project.workEN)
        academic_project.year = request.POST.get('year', academic_project.year)
        academic_project.work_type = request.POST.get('work_type', academic_project.work_type)
        academic_project.other_work_type = request.POST.get('other_work_type', academic_project.other_work_type)
        academic_project.academic_type = request.POST.get('academic_type',academic_project.academic_type)
        academic_project.integration = request.POST.get('integration', academic_project.integration)
        academic_project.faculty = faculty_instance
        academic_project.department = department_instance
        academic_project.address = request.POST.get('address', academic_project.address)
        academic_project.subdistrict = subdistrict_instance
        academic_project.districtInput = district_instance
        academic_project.province = province_instance
        academic_project.information = request.POST.get('information', academic_project.information)
        academic_project.organizing_agency = request.POST.get('organizing_agency', academic_project.organizing_agency)
        academic_project.partner_organize = request.POST.get('partner_organize', academic_project.partner_organize)
        academic_project.money = request.POST.get('money', academic_project.money)
        startDate = request.POST.get('startDate')
        endDate = request.POST.get('endDate')
        startDate_clean = datetime.strptime(startDate, '%d-%m-%Y')
        endDate_clean = datetime.strptime(endDate, '%d-%m-%Y')
        academic_project.startDate = startDate_clean
        academic_project.endDate = endDate_clean

        academic_project.save()

        # Fetch current internal researcher relationships
        current_internal_researchers = academic_project.internal_researchers.all()

        # Lists from the form submission
        updated_internal_ids = request.POST.getlist('name_inside')
        updated_internal_positions = request.POST.getlist('position_inside')

        # Convert IDs from strings to integers
        updated_internal_ids = [int(id) for id in updated_internal_ids]

        # Update and Remove Logic for Internal Researchers
        for current_researcher in current_internal_researchers:
            if current_researcher.id not in updated_internal_ids:
                # Remove researchers not in the updated list
                academic_project.internal_researchers.remove(current_researcher)
            else:
                # Update existing researchers
                index = updated_internal_ids.index(current_researcher.id)
                current_researcher.research_position = updated_internal_positions[index]
                current_researcher.save()

        # Adding New Researchers
        for id, position in zip(updated_internal_ids, updated_internal_positions):
            if not Internal_researcher.objects.filter(id=id).exists():
                # Fetch the Researcher instance
                researcher_instance = Researcher.objects.get(id=id)
                # Create a new Internal_researcher instance and add to the project
                new_internal_researcher = Internal_researcher.objects.create(
                    name=researcher_instance, 
                    research_position=position
                )
                academic_project.internal_researchers.add(new_internal_researcher)
        
     # Clear the existing many-to-many relationships for external_researchers
        academic_project.external_researchers.clear()

        # Assuming 'name_outside' and 'position_outside' are the correct form field names
        updated_external_names = request.POST.getlist('name_outside')
        updated_external_positions = request.POST.getlist('position_outside')

        for name, position in zip(updated_external_names, updated_external_positions):
            # Instead of get_or_create, use filter().first() to safely handle duplicates
            researcher = External_researcher.objects.filter(name=name, research_position=position).first()

            if researcher:
                # If a matching researcher is found, use it
                academic_project.external_researchers.add(researcher)
            else:
                # If no matching researcher, create a new one
                new_researcher = External_researcher.objects.create(name=name, research_position=position)
                academic_project.external_researchers.add(new_researcher)

        academic_project.save()

        # Update ManyToMany fields for funds and agencies
        fund_ids = request.POST.getlist('fund', [])
        if fund_ids:
            academic_project.fund.set(Fund.objects.filter(id__in=fund_ids))

        agency_ids = request.POST.getlist('agency', [])
        if agency_ids:
            academic_project.agency.set(Agency.objects.filter(id__in=agency_ids))

        # Example of handling internal researchers (simplified, see note below)
        # You would do similar for external researchers, funds, and agencies

        # Redirect to a success page, or back to the form with a success message
        return redirect('home')  # Make sure to replace 'some_success_url' with your actual URL name

    else:
        # Preparing context for GET request, including all necessary objects
        context = {
            'academic_project': academic_project,
            'faculties': Faculty.objects.all(),
            'departments': Department.objects.all(),
            'current_internal_researchers': academic_project.internal_researchers.all(),
            'current_external_researchers': academic_project.external_researchers.all(),
            'academic_type_choices': Academic_model.ACADEMIC_TYPE,
            'internal_research_position_choices': Internal_researcher.RESEARCH_POSITION_CHOICES,
            'external_research_position_choices': External_researcher.RESEARCH_POSITION_CHOICES,
            'work_type_choices': Academic_model.WORK_CHOICES,
            'integration_choices': Academic_model.INTERGRATION_CHOICES,
            'fund': Fund.objects.all(),
            'agency': Agency.objects.all(),
            'subdistricts': subdistricts,
            'districts': districts,
            'provinces': provinces,
        }

        return render(request, 'edit/edit_academic.html', context)

def get_provinces(request):
    zone_id = request.GET.get('zone_id')
    provinces = Province.objects.filter(zone_id=zone_id).values('id', 'name_th')
    return JsonResponse(list(provinces), safe=False)

def get_districts(request):
    province_id = request.GET.get('province_id')
    districts = District.objects.filter(province_id=province_id).values('id', 'name_th')
    return JsonResponse(list(districts), safe=False)

def districts_by_subdistrict(request):
    subdistrict_id = request.GET.get('subdistrict_id')
    if subdistrict_id is not None:
        districts = list(District.objects.filter(subdistrict__id=subdistrict_id).values('id', 'name_th'))
        return JsonResponse(districts, safe=False)
    else:
        return JsonResponse({'error': 'Subdistrict ID is missing'}, status=400)

def provinces_by_district(request):
    district_id = request.GET.get('district_id')
    if district_id is not None:
        provinces = list(Province.objects.filter(district__id=district_id).values('id', 'name_th'))
        return JsonResponse(provinces, safe=False)
    else:
        return JsonResponse({'error': 'District ID is missing'}, status=400)

