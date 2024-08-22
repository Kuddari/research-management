from django import forms
from .models import *

class MouForm(forms.ModelForm):


    class Meta:
        model = Mou
        fields = '__all__'
        widgets = {
            'project': forms.TextInput(attrs={'class': 'py-2 rounded-lg border border-gray-300 focus:border-blue-500 focus:ring-blue-500 focus:ring-opacity-50 focus:outline-none','placeholder': 'ชื่อโครงการ'}),
            'faculty': forms.Select(attrs={'class': 'py-2 rounded-lg border border-gray-300 focus:border-blue-500 focus:ring-blue-500 focus:ring-opacity-50 focus:outline-none'}),
            'support_type': forms.Select(attrs={'class': 'py-2 rounded-lg border border-gray-300 focus:border-blue-500 focus:ring-blue-500 focus:ring-opacity-50 focus:outline-none'}),
            'promise_start_date': forms.DateInput(format='%d/%m/%Y', attrs={'class': 'py-2 rounded-lg border border-gray-300 focus:border-blue-500 focus:ring-blue-500 focus:ring-opacity-50 focus:outline-none', 'data-input': "",'placeholder': 'วันที่ทำสัญญา'}),
            'project_start_date': forms.DateInput(format='%d/%m/%Y', attrs={'class': 'py-2 rounded-lg border border-gray-300 focus:border-blue-500 focus:ring-blue-500 focus:ring-opacity-50 focus:outline-none', 'data-input': "", 'placeholder': 'วันที่เริ่มต้นโครงการ'}),
            'project_end_date': forms.DateInput(format='%d/%m/%Y', attrs={'class': 'py-2 rounded-lg border border-gray-300 focus:border-blue-500 focus:ring-blue-500 focus:ring-opacity-50 focus:outline-none', 'data-input': "", 'placeholder': 'วันที่สิ้นสุดโครงการ'}),
            'success_level': forms.Select(attrs={'class': 'py-2 rounded-lg border border-gray-300 focus:border-blue-500 focus:ring-blue-500 focus:ring-opacity-50 focus:outline-none'}),
            'objectives': forms.Textarea(attrs={'class': 'py-2 rounded-lg border border-gray-300 focus:border-blue-500 focus:ring-blue-500 focus:ring-opacity-50 focus:outline-none','placeholder': 'วัตถุประสงค์'}),
            'goals': forms.Textarea(attrs={'class': 'py-2 rounded-lg border border-gray-300 focus:border-blue-500 focus:ring-blue-500 focus:ring-opacity-50 focus:outline-none','placeholder': 'เป้าหมายของ'}),
            'organizations': forms.SelectMultiple(attrs={'class': 'py-2 rounded-lg border border-gray-300 focus:border-blue-500 focus:ring-blue-500 focus:ring-opacity-50 focus:outline-none'}),
            'supporting_activities': forms.SelectMultiple(attrs={'class': 'py-2 rounded-lg border border-gray-300 focus:border-blue-500 focus:ring-blue-500 focus:ring-opacity-50 focus:outline-none'}),
            # เพิ่มคลาสสำหรับฟิลด์อื่น ๆ ตามต้องการ
        }

    def __init__(self, *args, **kwargs):
        super(MouForm, self).__init__(*args, **kwargs)
        # Retrieve the latest organizations and supporting activities
        latest_organizations = SupportAgency.objects.all().order_by('-id')  # Sort in reverse order based on id
        latest_supporting_activities = SupportActivity.objects.all().order_by('-id')  # Sort in reverse order based on id

        # Set choices for the 'organizations' field
        self.fields['organizations'].widget.choices = [(-org.id, f"{org.organization} - {org.signatory} - ({org.address})") for org in latest_organizations]

        # Set choices for the 'supporting_activities' field
        self.fields['supporting_activities'].widget.choices = [(-activity.id, f"{activity.activity} - {activity.start_time} - {activity.end_time}") for activity in latest_supporting_activities]

        for field_name in self.fields:
            self.fields[field_name].widget.attrs.update({'autocomplete': 'off'})
            self.fields[field_name].required = False


class SupportAgencyForm(forms.ModelForm):
    class Meta:
        model = SupportAgency  # Use the correct model
        fields = '__all__'  # You can specify specific fields here if you don't want all fields
        widgets = {
            'organization': forms.TextInput(attrs={'class': 'py-2 rounded-lg border border-gray-300 focus:border-blue-500 focus:ring-blue-500 focus:ring-opacity-50 focus:outline-none'}),
            'signatory': forms.TextInput(attrs={'class': 'py-2 rounded-lg border border-gray-300 focus:border-blue-500 focus:ring-blue-500 focus:ring-opacity-50 focus:outline-none'}),
            'address': forms.TextInput(attrs={'class': 'py-2 rounded-lg border border-gray-300 focus:border-blue-500 focus:ring-blue-500 focus:ring-opacity-50 focus:outline-none'}),
        }

    def __init__(self, *args, **kwargs):
        super(SupportAgencyForm, self).__init__(*args, **kwargs)  # Use SupportAgencyForm instead of MouForm

class SupportActivityForm(forms.ModelForm):
    class Meta:
        model = SupportActivity  # Use the correct model
        fields = '__all__'  # You can specify specific fields here if you don't want all fields
        widgets = {
            'activity': forms.TextInput(attrs={'class': 'py-2 rounded-lg border border-gray-300 focus:border-blue-500 focus:ring-blue-500 focus:ring-opacity-50 focus:outline-none'}),
            'start_time': forms.DateInput(format='%d/%m/%Y', attrs={'class': 'py-2 rounded-lg border border-gray-300 focus:border-blue-500 focus:ring-blue-500 focus:ring-opacity-50 focus:outline-none', 'data-input': ""}),
            'end_time': forms.DateInput(format='%d/%m/%Y', attrs={'class': 'py-2 rounded-lg border border-gray-300 focus:border-blue-500 focus:ring-blue-500 focus:ring-opacity-50 focus:outline-none', 'data-input': ""}),
            'success_level': forms.Select(attrs={'class': 'py-2 rounded-lg border border-gray-300 focus:border-blue-500 focus:ring-blue-500 focus:ring-opacity-50 focus:outline-none'}),
        }

    def __init__(self, *args, **kwargs):
        super(SupportActivityForm, self).__init__(*args, **kwargs)  # Use SupportAgencyForm instead of MouForm

        