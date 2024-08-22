from django.contrib import admin
from .models import *
from django.contrib.admin import AdminSite
from import_export.admin import ImportExportModelAdmin, ImportExportActionModelAdmin
from django_select2.forms import ModelSelect2Widget


class ResearchAppAdminSite(AdminSite):
    site_header = 'RESEARCHAPP Administration'
    site_title = 'RESEARCHAPP Admin'

researchapp_admin_site = ResearchAppAdminSite(name='researchapp_admin')
# กำหนด inline สำหรับ Department
class DepartmentInline(admin.TabularInline):
    model = Department
    extra = 1

class strategicAdmin(ImportExportModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

# แอดมิน Faculty ที่รวมการใช้งาน inlines
class FacultyAdmin(ImportExportModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    inlines = [DepartmentInline]

# แอดมิน Department
class DepartmentAdmin(ImportExportModelAdmin):
    list_display = ('name', 'faculty')
    list_filter = ('faculty',)
    search_fields = ('name', 'faculty__name')

class FundAdmin(ImportExportModelAdmin):
    list_display = ('fund_from',)  # Note the comma to make it a tuple
    search_fields = ('fund_from',)  # Note the comma to make it a tuple

class AgencyAdmin(ImportExportModelAdmin):
    list_display = ('agency_from',)  # Note the comma to make it a tuple
    search_fields = ('agency_from',)  # Note the comma to make it a tuple


# Register the Fund model with the custom admin site

class InternalResearcherAdmin(ImportExportModelAdmin):
    list_display = ('get_researcher_name', 'research_position')
    search_fields = ('name__name_lastname_th', 'research_position')

    def get_researcher_name(self, obj):
        return obj.name.name_lastname_th
    get_researcher_name.short_description = 'Researcher Name'  # Sets column header

class ExternalResearcherAdmin(ImportExportModelAdmin):
    list_display = ('name', 'research_position')
    search_fields = ('name', 'research_position')

# แอดมิน Researcher
class ResearcherAdmin(ImportExportModelAdmin):
    list_display = ('user', 'name_lastname_th', 'faculty', 'department')
    list_filter = ('faculty', 'department')
    search_fields = ('user__username', 'name_lastname_th', 'faculty__name', 'department__name')

class ResearchProjectAdmin(ImportExportModelAdmin):
    list_display = ('research_code', 'research_nameTH', 'research_nameEN', 'inside_outside', 'research_type', 'status')  # เพิ่มฟิลด์ที่ต้องการแสดง
    list_filter = ('inside_outside', 'research_type', 'status')  # ตั้งค่าฟิลเตอร์
    search_fields = ('research_code', 'research_nameTH', 'research_nameEN')  # ตั้งค่าการค้นหา
    filter_horizontal = ('internal_researchers', 'external_researchers', 'fund', 'agency')  # ตั้งค่าฟิลเตอร์แบบแนวนอน


class ResearchAdmin(ImportExportModelAdmin):
    list_display = ('research_nameTH', 'research_nameEN', 'work_type', 'publishing_year', 'publishing_level')
    list_filter = ('work_type', 'publishing_level')
    search_fields = ('research_nameTH', 'research_nameEN')
    filter_horizontal = ('internal_researchers', 'external_researchers')

# Ensure your model admins are defined
class DistrictAdmin(admin.ModelAdmin):
    search_fields = ['name_th']

class ProvinceAdmin(admin.ModelAdmin):
    search_fields = ['name_th']

class SubDistrictAdmin(admin.ModelAdmin):
    search_fields = ['name_th']

class AcademicAdmin(ImportExportModelAdmin):
    list_display = ('workTH', 'year', 'work_type', 'integration', 'faculty', 'department')
    list_filter = ('work_type', 'integration', 'faculty', 'department')
    search_fields = ('workTH', 'workEN', 'subdistrict','district','province')
    filter_horizontal = ('internal_researchers', 'external_researchers', 'fund','agency')
    raw_id_fields = ('subdistrict', 'district', 'province')
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'subdistrict':
            kwargs['widget'] = ModelSelect2Widget(
                queryset=SubDistrict.objects.order_by('name_th'),
                search_fields=['name_th__icontains']
            )
        elif db_field.name == 'district':
            kwargs['widget'] = ModelSelect2Widget(
                queryset=District.objects.order_by('name_th'),
                search_fields=['name_th__icontains']
            )
        elif db_field.name == 'province':
            kwargs['widget'] = ModelSelect2Widget(
                queryset=Province.objects.order_by('name_th'),
                search_fields=['name_th__icontains']
            )
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

class ResearchPerformanceAdmin(admin.ModelAdmin):
    list_display = ('research_name', 'date', 'agency')  # Customize the fields displayed in the list view
    search_fields = ('research_name', 'agency')  # Enable searching by these fields
    list_filter = ('date', 'agency')  # Add filters for these fields
    filter_horizontal = ('internal_researchers', 'external_researchers')


class ZoneAdmin(ImportExportModelAdmin):
    list_display = ('id','name')

class ProvinceAdmin(ImportExportModelAdmin):
    list_display = ('code', 'name_th', 'name_en', 'zone')
    search_fields = ('name_th', 'name_en')

class DistrictAdmin(ImportExportModelAdmin):
    list_display = ('code', 'name_th', 'name_en', 'province')
    list_filter = ('province',)
    search_fields = ('name_th', 'name_en')
    raw_id_fields = ('province',)

class SubDistrictAdmin(ImportExportModelAdmin):
    list_display = ('zip_code', 'name_th', 'name_en', 'amphure')
    list_filter = ('amphure',)
    search_fields = ('name_th', 'name_en')
    raw_id_fields = ('amphure',)

class SupportAgencyAdmin(admin.ModelAdmin):
    list_display = ('organization', 'signatory', 'address')
    search_fields = ['organization', 'signatory', 'address']

class SupportActivityAdmin(admin.ModelAdmin):
    list_display = ('activity', 'start_time', 'end_time', 'success_level')
    list_filter = ('success_level',)

class MouAdmin(admin.ModelAdmin):
    list_display = ('project', 'promise_start_date', 'project_start_date', 'project_end_date', 'success_level')
    list_filter = ('success_level',)
    search_fields = ['project', 'objectives', 'goals']
    filter_horizontal = ('organizations', 'supporting_activities')  # Allows adding pass to the ManyToManyField


# Register the ResearchProject model with the custom admin site
admin.site.register(Researcher, ResearcherAdmin)
admin.site.register(ResearchProject, ResearchProjectAdmin)
admin.site.register(Research_model, ResearchAdmin)
admin.site.register(Academic_model, AcademicAdmin)
admin.site.register(ResearchPerformance, ResearchPerformanceAdmin)
admin.site.register(Mou, MouAdmin)



# ลงทะเบียนโมเดลกับ Django admin ครั้งเดียว
researchapp_admin_site.register(SupportAgency, SupportAgencyAdmin)
researchapp_admin_site.register(SupportActivity, SupportActivityAdmin)

researchapp_admin_site.register(strategic, strategicAdmin)
researchapp_admin_site.register(Faculty, FacultyAdmin)
researchapp_admin_site.register(Department, DepartmentAdmin)
researchapp_admin_site.register(Fund, FundAdmin)
researchapp_admin_site.register(Agency, AgencyAdmin)
researchapp_admin_site.register(Internal_researcher, InternalResearcherAdmin)
researchapp_admin_site.register(External_researcher, ExternalResearcherAdmin)

researchapp_admin_site.register(Zone, ZoneAdmin)
researchapp_admin_site.register(District, DistrictAdmin)
researchapp_admin_site.register(Province, ProvinceAdmin)
researchapp_admin_site.register(SubDistrict, SubDistrictAdmin)
