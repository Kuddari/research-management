from django.db import models
from django.contrib.auth.models import User



# Create your models here.

class Faculty(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = "คณะ"


class Department(models.Model):
    name = models.CharField(max_length=100, unique=True)
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE, related_name='departments')

    def __str__(self):
        return f"{self.name}"

    class Meta:
        verbose_name_plural = "สาขา"

class Zone(models.Model):
    name = models.CharField(max_length=50)
    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "ภูมิภาค"


class Province(models.Model):
    code = models.PositiveIntegerField()
    name_th = models.CharField(max_length=100)
    name_en = models.CharField(max_length=100)
    zone = models.ForeignKey(Zone, on_delete=models.CASCADE)

    def __str__(self):
        return self.name_th

    class Meta:
        ordering = ['name_th']
        verbose_name_plural = "จังหวัด"

class District(models.Model):
    code = models.PositiveIntegerField()
    name_th = models.CharField(max_length=100)
    name_en = models.CharField(max_length=100)
    province = models.ForeignKey(Province, on_delete=models.CASCADE)

    def __str__(self):
        return self.name_th

    class Meta:
        ordering = ['name_th']
        verbose_name_plural = "อำเภอ"

class SubDistrict(models.Model):
    zip_code = models.PositiveIntegerField()
    name_th = models.CharField(max_length=100)
    name_en = models.CharField(max_length=100)
    amphure = models.ForeignKey(District, on_delete=models.CASCADE)

    def __str__(self):
        return self.name_th

    class Meta:
        ordering = ['name_th']
        verbose_name_plural = "ตำบล"


class strategic(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = "ยุทธศาสตร์"

class Researcher(models.Model):
    USERTYPE_CHOICES = [
        ('researcher', 'นักวิจัย'),
        ('assistant_admin', 'แอดมินรอง'),
        ('main_admin', 'แอดมินหลัก'),
    ]

    POSITION_CHOICES = [
        ('Manager', 'Manager'),
        ('Developer', 'Developer'),
        ('Designer', 'Designer'),
        # Add more positions as needed
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='researcher_profile')
    name_lastname_th = models.CharField(max_length=100)
    name_lastname_en = models.CharField(max_length=100)
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    email = models.EmailField()
    telephone_number = models.CharField(max_length=15)
    position = models.CharField(max_length=50, choices=POSITION_CHOICES)
    usertype = models.CharField(max_length=50, choices=USERTYPE_CHOICES)
    profile_picture = models.ImageField(upload_to='researchers/', blank=True)


    def __str__(self):
        return f"{self.user.username} ({self.name_lastname_en})"
    
    def save(self, *args, **kwargs):
        # If the usertype is 'main_admin', set the user's is_staff to True
        if self.usertype == 'main_admin' or self.usertype == '' :
            self.user.is_staff = True
        else:
            self.user.is_staff = False
        self.user.save()  # Save the user instance
        super().save(*args, **kwargs)  # Save the Researcher instance
    
    class Meta:
        verbose_name_plural = "นักวิจัย"



class Internal_researcher(models.Model):
    RESEARCH_POSITION_CHOICES = [
        ('นักวิจัยหลัก', 'นักวิจัยหลัก'),
        ('นักวิจัยรอง', 'นักวิจัยรอง'),
        # Add more choices as needed
    ]

    name = models.ForeignKey(Researcher, on_delete=models.CASCADE, related_name='internal_researchers')
    research_position = models.CharField(max_length=50, choices=RESEARCH_POSITION_CHOICES)

    def __str__(self):
        return f"{self.name} ({self.get_research_position_display()})"
    
    def in_clean_name(self):
        # Example logic to clean up the name
        if '(' in self.name and ')' in self.name:
            return self.name.split('(')[-1].split(')')[0].strip()
        return self.name

    class Meta:
        verbose_name_plural = "นักวิจัยภายใน"

class External_researcher(models.Model):
    RESEARCH_POSITION_CHOICES = [
        ('นักวิจัยหลัก', 'นักวิจัยหลัก'),
        ('นักวิจัยรอง', 'นักวิจัยรอง'),
        # Add more choices as needed
    ]

    name = models.CharField(max_length=100)
    research_position = models.CharField(max_length=50, choices=RESEARCH_POSITION_CHOICES)

    def __str__(self):
        return f"{self.name} ({self.get_research_position_display()})"
    
    def ex_clean_name(self):
        # Example logic to clean up the name
        if '(' in self.name and ')' in self.name:
            return self.name.split('(')[-1].split(')')[0].strip()
        return self.name

    class Meta:
        verbose_name_plural = "นักวิจัยภายนอก"

class Fund (models.Model):
    fund_from = models.CharField(max_length=100)
    class Meta:
        verbose_name_plural = "แหล่งเงินทุน"
    
    def __str__(self):
        return self.fund_from

class Agency (models.Model):
    agency_from = models.CharField(max_length=100)
    class Meta:
        verbose_name_plural = "หน่วยงานที่สนับสนุน"
    
    def __str__(self):
        return self.agency_from
    

class ResearchProject(models.Model):
    research_code = models.CharField(max_length=50, unique=True)
    research_nameTH = models.CharField(max_length=255)
    research_nameEN = models.CharField(max_length=255, blank=True)
    faculty = models.ForeignKey('Faculty', on_delete=models.CASCADE)
    department = models.ForeignKey('Department', on_delete=models.CASCADE)
    
    INSIDE_OUTSIDE_CHOICES = [
        ('ภายใน', 'ภายใน'),
        ('ภายนอก', 'ภายนอก'),
    ]
    inside_outside = models.CharField(max_length=50, choices=INSIDE_OUTSIDE_CHOICES)
    
    RESEARCH_TYPE_CHOICES = [
        ('วิจัยพื้นฐาน (Basic Research)', 'วิจัยพื้นฐาน (Basic Research)'),
        ('วิจัยประยุกต์ (Applied Research)', 'วิจัยประยุกต์ (Applied Research)'),
        ('วิจัยเชิงทดลอง (Experimental Research)','วิจัยเชิงทดลอง (Experimental Research)'),
    ]
    research_type = models.CharField(max_length=50, choices=RESEARCH_TYPE_CHOICES)
    
    strategic_choice = models.ForeignKey('strategic', on_delete=models.CASCADE)
    
    STATUS_CHOICES = [
        ('ทำสัญญา', 'ทำสัญญา'),
        ('ระหว่างดำเนินการ', 'ระหว่างดำเนินการ'),
        ('เสร็จสิ้นโครงการ', 'เสร็จสิ้นโครงการ'),
    ]
    status = models.CharField(max_length=50, choices=STATUS_CHOICES)
    
    file = models.FileField(upload_to='research_files/', blank=True)
    
    internal_researchers = models.ManyToManyField(Internal_researcher, related_name='research_projects')
    external_researchers = models.ManyToManyField(External_researcher, related_name='research_projects', blank=True)
    fund = models.ManyToManyField('Fund',related_name='research_projects',blank=True)
    money = models.PositiveIntegerField()
    agency = models.ManyToManyField('Agency',related_name='research_projects',blank=True)
    date_promise = models.DateField()

    def __str__(self):
        return self.research_nameTH

    class Meta:
        verbose_name_plural = "โครงการวิจัย"

class Research_model(models.Model):
    RESEARCH_WORK_TYPE_CHOICES = [
        ('วาสารนานาชาติ', 'วาสารนานาชาติ'),
        ('วารสารระดับชาติ (TCI 1)', 'วารสารระดับชาติ (TCI 1)'),
        ('วารสารระดับชาติ (TCI 2)', 'วารสารระดับชาติ (TCI 2)'),
        ('การประชุมวิชาการระดับชาติ (Proceedings)', 'การประชุมวิชาการระดับชาติ (Proceedings)'),
        ('ตำรา/หนังสือ', 'ตำรา/หนังสือ'),
        ('การแสดงศิลปวัฒนธรรม', 'การแสดงศิลปวัฒนธรรม'),
        ('หนังสือที่มีผู้เขียนหลายคน (Book Chapter)', 'หนังสือที่มีผู้เขียนหลายคน (Book Chapter)'),
        ('สื่ออิเล็กทรอนิกส์', 'สื่ออิเล็กทรอนิกส์'),
        ('อื่นๆ', 'อื่นๆ'),
    ]

    PUBLISHING_TYPE_CHOICES = [
        ('วาสารนานาชาติ', 'วาสารนานาชาติ'),
        ('วารสารระดับชาติ (TCI 1)', 'วารสารระดับชาติ (TCI 1)'),
        ('วารสารระดับชาติ (TCI 2)', 'วารสารระดับชาติ (TCI 2)'),
        ('การประชุมวิชาการระดับชาติ (Proceedings)', 'การประชุมวิชาการระดับชาติ (Proceedings)'),
        ('ตำรา/หนังสือ', 'ตำรา/หนังสือ'),
        ('การแสดงศิลปวัฒนธรรม', 'การแสดงศิลปวัฒนธรรม'),
        ('หนังสือที่มีผู้เขียนหลายคน (Book Chapter)', 'หนังสือที่มีผู้เขียนหลายคน (Book Chapter)'),
        ('สื่ออิเล็กทรอนิกส์', 'สื่ออิเล็กทรอนิกส์'),
        ('อื่นๆ', 'อื่นๆ'),
    ]

    PUBLISHING_LEVEL_CHOICES = [
        ('ระดับนานาชาติ', 'ระดับนานาชาติ'),
        ('ระดับชาติ', 'ระดับชาติ'),
        ('ระดับภูมิภาค', 'ระดับภูมิภาค'),
        ('ระดับจังหวัด', 'ระดับจังหวัด'),
        ('ระดับองค์กร', 'ระดับองค์กร'),

    ]

    research_nameTH = models.CharField(max_length=255)
    research_nameEN = models.CharField(max_length=255 ,blank=True)
    work_type = models.CharField(max_length=50, choices=RESEARCH_WORK_TYPE_CHOICES)
    other_work_type = models.CharField(max_length=50, blank=True)
    # publishing_type = models.CharField(max_length=50, choices=PUBLISHING_TYPE_CHOICES)
    publishing_year = models.PositiveIntegerField()
    publishing_level = models.CharField(max_length=50, choices=PUBLISHING_LEVEL_CHOICES)
    faculty = models.ForeignKey('Faculty', on_delete=models.CASCADE)
    department = models.ForeignKey('Department', on_delete=models.CASCADE)
    url = models.URLField()
    internal_researchers = models.ManyToManyField(Internal_researcher, related_name='research')
    external_researchers = models.ManyToManyField(External_researcher, related_name='research', blank=True)

    def __str__(self):
        return self.research_nameTH
    
    class Meta:
        verbose_name_plural = "ผลงานวิจัย"

class Academic_model(models.Model):
    workTH = models.CharField(max_length=255)
    workEN = models.CharField(max_length=255, blank=True)
    year = models.CharField(max_length=4)
    startDate = models.DateField()
    endDate = models.DateField()
    WORK_CHOICES = [
        ('ความรู้ศาสนา', 'ความรู้ศาสนา'),
        ('หนังสือ/ตำรา', 'หนังสือ/ตำรา'),
        ('ผลิตภัณฑ์อาหาร (Food)','ผลิตภัณฑ์อาหาร (Food)'),
        ('ผลิตภัณฑ์อาหาร (Non Food)','ผลิตภัณฑ์อาหาร (Non Food)'),
        ('สื่ออิเล็กทรอนิกส์','สื่ออิเล็กทรอนิกส์'),
        ('มุสลิมใหม่ (มุอัลลัฟ)','มุสลิมใหม่ (มุอัลลัฟ)'),
        ('อื่นๆ','อื่นๆ'),
        # Add other choices as needed
    ]
    work_type = models.CharField(max_length=50, choices=WORK_CHOICES)
    ACADEMIC_TYPE = [
        ('การให้บริการวิชาการแบบให้เปล่า','การให้บริการวิชาการแบบให้เปล่า'),
        ('การบริการวิชาการแบบไม่แสวงหากำไร','การบริการวิชาการแบบไม่แสวงหากำไร'),
        ('การบริการวิชาการแบบสร้างรายได้','การบริการวิชาการแบบสร้างรายได้')
    ]
    academic_type = models.CharField(max_length=50, choices=ACADEMIC_TYPE)
    other_work_type = models.CharField(max_length=50,blank=True)
    INTERGRATION_CHOICES = [
        ('บูรณาการเรียนการสอน', 'บูรณาการเรียนการสอน'),
        ('บูรณาการวิจัย', 'บูรณาการวิจัย'),
        ('บูรณาการศิลปวัฒนธรรม','บูรณาการศิลปวัฒนธรรม')
        # Add other choices as needed
    ]
    integration = models.CharField(max_length=50, choices=INTERGRATION_CHOICES)
    faculty = models.ForeignKey('Faculty', on_delete=models.CASCADE)
    department = models.ForeignKey('Department', on_delete=models.CASCADE)
    address = models.CharField(max_length=255)
    subdistrict = models.ForeignKey(SubDistrict, on_delete=models.CASCADE)
    district = models.ForeignKey(District, on_delete=models.CASCADE)
    province = models.ForeignKey(Province, on_delete=models.CASCADE)
    information = models.TextField()
    internal_researchers = models.ManyToManyField('Internal_researcher', related_name='academic')
    external_researchers = models.ManyToManyField('External_researcher', related_name='academic',blank=True)
    fund = models.ManyToManyField('Fund',related_name='academic', blank=True)
    money = models.PositiveIntegerField()
    agency = models.ManyToManyField('Agency',related_name='academic', blank=True)
    organizing_agency = models.TextField(blank=True)
    partner_organize = models.TextField(blank=True)


    def __str__(self):
        return f"{self.workTH} ({self.year})"

    class Meta:
        verbose_name_plural = "บริการวิชาการ"

class ResearchPerformance(models.Model):
    research_name = models.CharField(max_length=255)
    date = models.DateField()
    agency = models.ForeignKey('Department', on_delete=models.CASCADE)
    detail = models.TextField()
    file = models.FileField(upload_to='performance_files/', blank=True)
    url = models.URLField(blank=True)
    internal_researchers = models.ManyToManyField(Internal_researcher, related_name='internal_performance_projects')
    external_researchers = models.ManyToManyField(External_researcher, related_name='external_performance_projects',blank=True)

    def __str__(self):
        return self.research_name
    
    class Meta:
        verbose_name_plural = "ผลงานที่โดดเด่น"

class SupportAgency(models.Model):
    organization = models.CharField(max_length=100)
    signatory = models.CharField(max_length=100)
    address = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.organization} - {self.address} - ({self.signatory})"
    class Meta:
        verbose_name_plural = "MOUหน่วยงานที่ร่วมสนับสนุน"

class SupportActivity(models.Model):
    activity = models.CharField(max_length=100)
    start_time = models.DateField()
    end_time = models.DateField()
    choices = [
        (1, '1'),
        (2, '2'),
        (3, '3'),
        (4, '4'),
        (5, '5')
    ]
    success_level = models.IntegerField(choices=choices)
    def __str__(self):
        return f"{self.activity} - {self.start_time} - {self.end_time}"
    class Meta:
        verbose_name_plural = "MOUกิจกรรมในเครือข่ายสนับสนุน"

class Mou(models.Model):
    project = models.CharField(max_length=50)
    faculty = models.ForeignKey('Faculty', on_delete=models.CASCADE)
    SUPPORT_TYPE = [
        ('บริการวิชาการ', 'บริการวิชาการ'),
        ('วิจัย', 'วิจัย'),
    ]
    support_type = models.CharField(max_length=50, choices=SUPPORT_TYPE)
    promise_start_date = models.DateField()
    project_start_date = models.DateField()
    project_end_date = models.DateField()
    choices = [
        (1, '1'),
        (2, '2'),
        (3, '3'),
        (4, '4'),
        (5, '5'),
    ]
    success_level = models.IntegerField(choices=choices)
    objectives = models.TextField()
    goals = models.TextField(blank=True)
    organizations = models.ManyToManyField(SupportAgency)
    supporting_activities = models.ManyToManyField(SupportActivity, blank=True)
    
    def __str__(self):
        return self.project
    
    class Meta:
        verbose_name_plural = "เครือข่ายMOU"