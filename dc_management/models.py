from django.urls import reverse
from django.db import models

from django.contrib.auth.models import User
from django.utils import timezone

import datetime
from datetime import date

import collections

## Models 

class SN_Ticket(models.Model):
    "deprecated class, not referenced by any other model"
    ticket_id = models.CharField(max_length=11, unique=True)
    date_created = models.DateField(default=date.today)

    def __str__(self):
            return self.ticket_id

    class Meta:
        verbose_name = 'SN Ticket'
        verbose_name_plural = 'SN Tickets'
            
class SubFunction(models.Model):
    name = models.CharField(max_length=16, default="project")

    def __str__(self):
            return self.name
        
class Server(models.Model):
    record_creation = models.DateField(auto_now_add=True)
    record_update = models.DateField(auto_now=True)

    ON = 'ON'
    OFF = 'OF'
    DECOMMISSIONED = 'DE'
    STATUS_CHOICES = (
            (ON, "On"),
            (OFF, "Off"),
            (DECOMMISSIONED, "Decommissioned"),
    )
    status = models.CharField(
                        max_length=2,
                        choices = STATUS_CHOICES,
                        default = ON,
    )

    PRODUCTION = 'PR'
    TEST = 'TE'
    DEVELOPMENT = 'DE'
    FUNCTION_CHOICES = (
            (PRODUCTION, "Production"),
            (TEST, "Test"),
            (DEVELOPMENT, "Development"),
    )
    function = models.CharField(
                            max_length=2,
                            choices = FUNCTION_CHOICES,
                            default = PRODUCTION,
    )

    VM = "VM"
    VDI = "VD"
    MACHINE_TYPE_CHOICES = (
                    (VM, "Virtual Machine (VM)"),
                    (VDI, "Virtual Desktop Infrastructure (VDI)"),
    )
    machine_type = models.CharField(
                            max_length=2,
                            choices = MACHINE_TYPE_CHOICES,
                            default = VM,
    ) 
    
    SMALL = "SM"
    MEDIUM = "MD"
    LARGE = "LG"
    XLARGE = "XL"
    VM_SIZE_CHOICES = (
                (SMALL, "Small (2 CPU, 8GB RAM)"),
                (MEDIUM, "Medium (4 CPU, 16GB RAM)"),
                (LARGE, "Large (8 CPU, 32GB RAM)"),
                (XLARGE, "Extra Large (16 CPU, 64GB RAM)"),
    )
    vm_size = models.CharField(
                            max_length=2,
                            choices = VM_SIZE_CHOICES,
                            default = SMALL,
    ) 

    ENCRYPTED = "EN"
    UNENCRYPTED = "UE"
    BACKUP_CHOICES = (
                (ENCRYPTED, "Encrypted"),
                (UNENCRYPTED, "Unencrypted"),
    )
    backup = models.CharField(
                            max_length=2,
                            choices = BACKUP_CHOICES,
                            default = ENCRYPTED,
    ) 

    MWS2008 = "M8" 
    MWS2012 = "M2" 
    RHEL7 = "R7" 
    WINDOWS7 = "W7" 
    OS_CHOICES = (
            (MWS2008, "Microsoft Windows Server 2008 (64-bit)"),
            (MWS2012, "Microsoft Windows Server 2012 (64-bit)"),
            (RHEL7, "Red Hat Enterprise Linux 7 (64-bit)"),
            (WINDOWS7, "Microsoft Windows 7 (64-bit)"),
    )
    operating_sys = models.CharField(
                            max_length=2,
                            choices = OS_CHOICES,
                            default = MWS2012,
    ) 
    
    node = models.CharField(max_length=16, unique=True) # eg HPRP010
    sub_function = models.ForeignKey(SubFunction, on_delete=models.CASCADE)
    name_address = models.CharField(max_length=32) # eg vITS-HPCP02.med.cornell.edu
    ip_address = models.GenericIPAddressField() # eg 10.36.217.229
    processor_num = models.IntegerField()
    ram = models.IntegerField() # to be entered in GB
    disk_storage = models.IntegerField() # to be entered in GB
    other_storage = models.IntegerField() # to be entered in GB    
    connection_date = models.DateField(default=date.today)
    dns_name = models.CharField(
                        max_length=32, 
                        null=True, 
                        blank=True
                        ) # eg vITS-HPRP02.a.wcmc-ad.net
    host = models.CharField(
                        max_length=32, 
                        null=True, 
                        blank=True
                        ) # eg brbesx10.med.cornell.edu
    comments = models.TextField(null=True, blank=True)

    def __str__(self):
            return self.node

    def duplicate_users(self):
        # pull all users from all projects. Return users/projects when a user
        # is present in more than one project on the node
        mounted_projects = self.projects_set.all()
        users = [ p.dc_users_set.all() for p in mounted_projects ]
        
        return [ item for item, count in collections.Counter(users).items() if count > 1 ]
           
class EnvtSubtype(models.Model):
    name = models.CharField(max_length=32, unique=True)

    def __str__(self):
            return self.name

class DC_User(models.Model):
    record_creation = models.DateField(auto_now_add=True)
    record_update = models.DateField(auto_now=True)

    sn_ticket = models.CharField(max_length=32, null=True, blank=True)
    cwid = models.CharField(max_length=16, unique=True)
    first_name = models.CharField(max_length=32)
    last_name = models.CharField(max_length=32)
    
    WCM = "WC"
    NYP = "NP"
    ROCKU = "RU"
    MSKCC = "SK"
    COLUMBIA = "CO"
    OTHER = "OT" # note this is also used in ROLE_CHOICES
    AFFILIATION_CHOICES = (
                    (WCM, "Weill Cornell Medicine"),
                    (NYP, "New York Presbyterian"),
                    (ROCKU, "Rockefeller University"),
                    (MSKCC, "Memorial Sloan Kettering"),
                    (COLUMBIA, "Columbia University"),
                    (OTHER, "Other")
    )
    affiliation = models.CharField(
                            max_length=2,
                            choices = AFFILIATION_CHOICES,
                            default = WCM,
    )
    
    FACULTY = 'FC'
    RESEARCHER = 'RE'
    AFFILIATE = 'AF'
    RESEARCH_COORDINATOR = 'RC'
    STUDENT = 'ST'
    STATISTICIAN = 'SN'
    VOLUNTEER = 'VO'
    STAFF = 'SF'
    EXPIRED = 'EX'
    OTHER = 'OT' # note this is also used in AFFILIATION_CHOICES
    ROLE_CHOICES = (
                (FACULTY, 'Faculty'),
                (STATISTICIAN, 'Statistician'),
                (AFFILIATE, 'Affiliate'),
                (RESEARCH_COORDINATOR, 'Research Coordinator'),
                (STAFF, 'Staff'),
                (STUDENT, 'Student'),
                (VOLUNTEER, 'Volunteer'),
                (OTHER, 'Other'),
                (EXPIRED, 'Role Expired'),
    )
    role = models.CharField(
                            max_length=2,
                            choices = ROLE_CHOICES,
                            default = FACULTY,
    )
    
    comments = models.TextField(null=True, blank=True)

    def __str__(self):
            return "{1} {2} ({0})".format(self.cwid, self.first_name, self.last_name)

    class Meta:
        verbose_name = 'Data Core User'
        verbose_name_plural = 'Data Core Users'

    def get_absolute_url(self):
        return reverse('dcuser-detail', kwargs={'pk': self.pk})

#########################
#### Software Models ####
#########################

class Software_License_Type(models.Model):
    sn_ticket = models.CharField(max_length=32, null=True, blank=True)
    name = models.CharField(max_length=32, unique=True)
    user_assigned = models.BooleanField()
    concurrent = models.BooleanField()
    monitored = models.BooleanField()

    def __str__(self):
            return self.name

    class Meta:
        verbose_name = 'Software License Type'
        verbose_name_plural = 'Software License Types'

class Software(models.Model):
    record_creation = models.DateField(auto_now_add=True)
    record_update = models.DateField(auto_now=True)

    name = models.CharField(max_length=64, unique=False)
    vendor = models.CharField(max_length=64)
    version = models.CharField(max_length=32)
    license_type = models.ForeignKey(
                            Software_License_Type, 
                            on_delete=models.CASCADE
                            )
    purchase_details = models.TextField(null=True, blank=True)
    comments = models.TextField(null=True, blank=True)

    def __str__(self):
            return "{} (version {})".format(self.name, self.version)

    class Meta:
        verbose_name = 'Software'
        verbose_name_plural = 'Software'

class SoftwareUnit(models.Model):
    record_creation = models.DateField(auto_now_add=True)
    record_update = models.DateField(auto_now=True)
    unit = models.CharField(max_length=64)
    
    def __str__(self):
            return self.unit

########################
#### Project Models ####
########################
  
class Project(models.Model):
    record_creation = models.DateField(auto_now_add=True)
    record_update = models.DateField(auto_now=True)

    dc_prj_id = models.CharField(max_length=8, unique=True)
    title = models.CharField(max_length=256)
    nickname = models.CharField(max_length=256, blank=True)
    fileshare_storage = models.IntegerField("Fileshare size (GB)",
                                            null=True, 
                                            blank=True)
    direct_attach_storage = models.IntegerField("Direct attach size (GB)", 
                                                null=True, 
                                                blank=True)
    backup_storage = models.IntegerField("Backup storage size (GB)", 
                                         null=True, 
                                         blank=True)
    requested_ram = models.IntegerField("Requested RAM (GB)", null=True, blank=True)
    requested_cpu = models.IntegerField(null=True, blank=True)
    
    users = models.ManyToManyField(DC_User, blank=True)
    pi = models.ForeignKey(
                    DC_User, 
                    on_delete=models.CASCADE,
                    related_name='project_pi')
    software_installed = models.ManyToManyField(
                                            Software,
                                            related_name='software_installed',
                                            db_table='prj_soft_install_tbl',
                                            blank=True,
                                            )
    software_requested = models.ManyToManyField(
                                            Software,
                                            related_name='software_requested',
                                            db_table='prj_soft_request_tbl',
                                            blank=True,
                                            )
                                            
    THESIS = 'TH'
    RESEARCH = 'RE'
    CLASS = 'CL'
    ENV_TYPE_CHOICES = (
                (THESIS, "Thesis Project"),
                (RESEARCH, "Research Project"),
                (CLASS, "Classroom Project")
    )
    env_type = models.CharField(
                            "Environment type",
                            max_length=2,
                            choices = ENV_TYPE_CHOICES,
                            default = RESEARCH,
    ) 
    
    env_subtype = models.ForeignKey(EnvtSubtype, on_delete=models.CASCADE)
    expected_completion = models.DateField()
    
    RUNNING = "RU"
    COMPLETED = "CO"
    SUSPENDED = "SU"
    STATUS_CHOICES = (
            (RUNNING, "Running"),
            (COMPLETED, "Completed"),
            (SUSPENDED, "Suspended"),
    )
    status = models.CharField(
                            max_length=2,
                            choices = STATUS_CHOICES,
                            default = RUNNING,
    ) 
    
    sn_tickets = models.CharField(max_length=32, null=True, blank=True)
    predata_ticket = models.CharField(max_length=32, null=True, blank=True)
    predata_date = models.DateField(null=True, blank=True)
    postdata_ticket = models.CharField(max_length=32, null=True, blank=True)
    postdata_date = models.DateField(null=True, blank=True)
    completion_ticket = models.CharField(max_length=32, null=True, blank=True)
    completion_date = models.DateField(null=True, blank=True)
    host = models.ForeignKey(Server, on_delete=models.CASCADE, null=True, blank=True)
    db = models.ForeignKey(Server, 
                            on_delete=models.CASCADE, 
                            related_name='db_host',
                            null=True, 
                            blank=True,
                            )
    
    # finance fields
    user_cost = models.FloatField(null=True, blank=True)
    host_cost = models.FloatField(null=True, blank=True)
    db_cost = models.FloatField(null=True, blank=True)
    fileshare_cost = models.FloatField(null=True, blank=True)
    direct_attach_cost = models.FloatField(null=True, blank=True)
    backup_cost = models.FloatField(null=True, blank=True)
    software_cost = models.FloatField(null=True, blank=True)
    project_total_cost = models.FloatField(null=True, blank=True)
    
    comments = models.TextField(null=True, blank=True)
    
    def __str__(self):
            return "{} ({})".format(self.dc_prj_id, self.nickname)
    
    def get_absolute_url(self):
        return reverse('dc_management:project', kwargs={'pk': self.pk})
        
class AccessPermission(models.Model):
    name = models.CharField(max_length=32)
    description = models.TextField()    

    def __str__(self):
            return self.name
    
def project_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/prj<id>/<filename>
    return '{0}/{1}'.format(instance.project.dc_prj_id, filename)

###########################
#### Governance Models ####
###########################

class Governance_Doc(models.Model):
    record_creation = models.DateField(auto_now_add=True)
    record_update = models.DateField(auto_now=True)
    record_author = models.ForeignKey(User, on_delete=models.CASCADE)
    
    sn_ticket = models.CharField(max_length=32, null=True, blank=True)
    doc_id = models.CharField(max_length=64)
    date_issued = models.DateField()
    expiry_date = models.DateField()
    users_permitted = models.ManyToManyField(DC_User, blank=True)
    access_allowed = models.ForeignKey(AccessPermission, on_delete=models.CASCADE)
    
    IRB = 'IR'
    IRB_EXEMPTION = 'IX'
    DUA = 'DU'
    DCA = 'DC'
    ONBOARDING = 'ON'
    GOVERNANCE_TYPE_CHOICES = (
                    (IRB, "IRB"),
                    (IRB_EXEMPTION, "IRB Exemption"),
                    (DUA, "DUA"),
                    (DCA, "Data Core User Agreement"),
                    (ONBOARDING, "Onboarding Form"),
    )
    governance_type = models.CharField(
                            max_length=2,
                            choices = GOVERNANCE_TYPE_CHOICES,
                            default = DCA,
    )
    
    defers_to_doc = models.ForeignKey('self', 
                                        on_delete=models.CASCADE, 
                                        null=True, 
                                        blank=True,
                                        related_name='overrules')
    supersedes_doc = models.ForeignKey('self', 
                                        on_delete=models.CASCADE, 
                                        null=True, 
                                        blank=True,
                                        related_name='superseded_by')

    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    
    documentation = models.FileField(
                            upload_to=project_directory_path, 
                            null=True,
                            blank=True,
    )

    comments = models.TextField(null=True, blank=True)

    def __str__(self):
            return "{0}_{2}_{1}".format(self.governance_type, self.doc_id, self.project)

    def allowed_user_string(self):
        return  ", ".join([u.cwid for u in self.users_permitted.all()])

    def attention_required(self):
        td = self.expiry_date - datetime.date.today() 
        print(self, len(Governance_Doc.objects.filter(supersedes_doc=self)))
        if td.days >  90:
            status = "safe"
        
        # DCUA always defers to other agreements, and has a soft end date
        elif self.governance_type == "DC":
            status = "safe"
        
        # if doc defers to another doc, then we need not pay attention to this one:
        elif self.defers_to_doc:
            status = "safe"
        elif len(Governance_Doc.objects.filter(supersedes_doc=self)) > 0:
            status = "safe"
        
        # if not deferring, not DCUA:
        elif td.days <= 0:
            status = "danger"
        elif td.days <= 10:
            status = "warning"
        elif td.days <= 90:
            status = "primary"
        
        return status
        
        
    class Meta:
        verbose_name = 'Governance Document'
        verbose_name_plural = 'Governance Documents'

class DC_Administrator(models.Model):
    record_creation = models.DateField(auto_now_add=True)
    record_update = models.DateField(auto_now=True)
    record_author = models.ForeignKey(User, on_delete=models.CASCADE)
    
    sn_ticket = models.CharField(max_length=32, null=True, blank=True)
    cwid = models.CharField(max_length=32)
    first_name = models.CharField(max_length=32)
    last_name = models.CharField(max_length=32)
    role = models.CharField(max_length=32)
    date_started = models.DateField()
    date_finished = models.DateField(null=True, blank=True)

    def __str__(self):
        return "{} {}({})".format(self.first_name, self.last_name, self.cwid)

    class Meta:
        verbose_name = 'Data Core Administrator'
        verbose_name_plural = 'Data Core Administrators'

class DCUAGenerator(models.Model):
    record_creation = models.DateField(auto_now_add=True)
    record_update = models.DateField(auto_now=True)

    project = models.ForeignKey(Project, on_delete=models.CASCADE, blank=True, null=True)

    ticket = models.CharField("SN Ticket", blank=True,null=True,max_length=12,)
    startdate = models.CharField("Start Date", 
                                blank=False, 
                                max_length=32,
                                default=datetime.datetime.now().strftime("%m/%d/%Y"),
                                )
    enddate = models.CharField(  "End Date",
                                blank=False, 
                                max_length=32,
                                default=(datetime.datetime.now() + 
                                         datetime.timedelta(days=365)
                                        ).strftime("%m/%d/%Y"),
                             )
    folder1 = models.CharField("Folder 1", blank=False, 
                              max_length=128,
                              default="dcore-prj00XX-SOURCE",
                              )
    folder2 = models.CharField("Folder 2", blank=True,null=True, 
                              default="dcore-prj00XX-SHARE",
                              max_length=128,
                              )
    folder3 = models.CharField("Folder 3", blank=True,null=True, 
                              default="WorkArea-<user CWID>",
                              max_length=128,
                              )
    folder4 = models.CharField("Folder 4", blank=True,null=True, max_length=128,)
    folder5 = models.CharField("Folder 5", blank=True,null=True, max_length=128,)
    folder6 = models.CharField("Folder 6", blank=True,null=True, max_length=128,)
    folder7 = models.CharField("Folder 7", blank=True,null=True, max_length=128,)
    url = models.CharField("Qualtrics URL", blank=True,null=True, max_length=512,)

    def __str__(self):
        return "{} - {} {}".format(self.startdate, self.enddate, self.folder1)
    
    def get_absolute_url(self):
        return reverse('dc_management:url_result', kwargs={'pk': self.pk})

########################
#### Finance Models ####
########################
                          
class SoftwareCost(models.Model):
    record_creation = models.DateField(auto_now_add=True)
    record_update = models.DateField(auto_now=True)
    record_author = models.ForeignKey(User, on_delete=models.CASCADE)
    
    software = models.ForeignKey(Software, on_delete=models.CASCADE)
    software_cost = models.FloatField("Regular cost (per person)", 
                                        null=True, 
                                        blank=True,
                                        )
    cost_classroom = models.FloatField("Cost for classrooms (per student)", 
                                        null=True, 
                                        blank=True,
                                        )
    cost_student = models.FloatField("Cost for classrooms (per class)", 
                                        null=True, 
                                        blank=True,
                                        )
    
class UserCost(models.Model):
    record_creation = models.DateField(auto_now_add=True)
    record_update = models.DateField(auto_now=True)
    record_author = models.ForeignKey(User, on_delete=models.CASCADE)
 
    user_quantity = models.IntegerField()
    user_cost     = models.FloatField()
    
class StorageCost(models.Model):
    record_creation = models.DateField(auto_now_add=True)
    record_update = models.DateField(auto_now=True)
    record_author = models.ForeignKey(User, on_delete=models.CASCADE)
    
    storage_type = models.CharField(max_length=64)
    st_cost_per_gb = models.FloatField()

    def __str__(self):
        return "{} (${}/GB)".format( self.storage_type, self.st_cost_per_gb)

############################
#### Log / Audit Models ####
############################    

class External_Access_Log(models.Model):
    record_creation = models.DateField(auto_now_add=True)
    record_update = models.DateField(auto_now=True)
    record_author = models.ForeignKey(User, on_delete=models.CASCADE)
    
    sn_ticket = models.CharField(max_length=32, null=True, blank=True)
    date_connected = models.DateField()
    date_disconnected = models.DateField()
    user_requesting = models.ForeignKey(DC_User, on_delete=models.CASCADE)
    project_connected = models.ForeignKey(Project, on_delete=models.CASCADE)
    setup_charge = models.BooleanField()
    hosting_charge = models.BooleanField()

    def __str__(self):
        return self.date_connected

    class Meta:
        verbose_name = 'External Access Log'
        verbose_name_plural = 'External Access Logs'
        
class Software_Log(models.Model):
    sn_ticket = models.CharField(max_length=32, null=True, blank=True)
    change_date = models.DateField(default=timezone.now)
    record_author = models.ForeignKey(User, on_delete=models.CASCADE)
    
    applied_to_prj = models.ForeignKey(Project, 
                                        on_delete=models.CASCADE,
                                        null=True,
                                        blank=True
                                        )
    applied_to_node = models.ForeignKey(Server, 
                                        on_delete=models.CASCADE,
                                        null=True,
                                        blank=True,
                                        )
    applied_to_user = models.ForeignKey(DC_User, 
                                        on_delete=models.CASCADE,
                                        null=True,
                                        blank=True,
                                        )
    software_changed = models.ForeignKey(Software, on_delete=models.CASCADE, null=True)

    comments = models.TextField(null=True, blank=True)

    ADD_ACCESS = 'AA'
    REMOVE_ACCESS = 'RA'
    CHANGE_TYPE_CHOICES = (
                    (ADD_ACCESS, "Add access"),
                    (REMOVE_ACCESS, "Remove access"),
    )  
    change_type  = models.CharField(
                            max_length=2,
                            choices = CHANGE_TYPE_CHOICES,
                            default = ADD_ACCESS,
    )

    
    def __str__(self):
        return "{} on {} ".format( self.change_type, self.change_date)

    class Meta:
        verbose_name = 'Software Log'
        verbose_name_plural = 'Software Logs'
    
class Software_Purchase(models.Model):
    record_creation = models.DateField(auto_now_add=True)
    record_update = models.DateField(auto_now=True)
    record_author = models.ForeignKey(User, on_delete=models.CASCADE)
    
    sn_ticket = models.CharField(max_length=32, null=True, blank=True)
    date_purchased = models.DateField()
    software = models.ForeignKey(Software, on_delete=models.CASCADE)
    num_units_purchased = models.IntegerField()
    unit_type = models.ForeignKey(SoftwareUnit, on_delete=models.CASCADE)  
    expiration = models.DateField()
    invoice_number = models.CharField(max_length=64)
    
    MAINTENANCE = 'MN'
    ADDITIONAL = 'AD'
    PURPOSE_CHOICES = (
                    (MAINTENANCE, "Maintenance/Renewal"),
                    (ADDITIONAL, "Additional/Expanding"),
    )  
    purpose  = models.CharField(
                            max_length=2,
                            choices = PURPOSE_CHOICES,
                            default = MAINTENANCE,
    )
    
    cost = models.FloatField()
    documentation = models.FileField(
                            upload_to='procurement/%Y/%m/%d/', 
                            null=True,
                            blank=True,
    )
    comments = models.TextField(null=True, blank=True)

    def __str__(self):
        return "{} units on {} ({})".format(
                        self.num_units_purchased, 
                        self.date_purchased,
                        self.invoice_number,
                        )

    class Meta:
        verbose_name = 'Software Purchase'
        verbose_name_plural = 'Software Purchases'

    def cost_per_unit(self):
        return self.cost / self.num_units_purchased

class Access_Log(models.Model):
    record_creation = models.DateField(auto_now_add=True)
    record_update = models.DateField(auto_now=True)
    record_author = models.ForeignKey(User, on_delete=models.CASCADE)

    sn_ticket = models.CharField(max_length=32, null=True, blank=True)
    date_changed = models.DateField()
    dc_user = models.ForeignKey(DC_User, on_delete=models.CASCADE)
    prj_affected = models.ForeignKey(Project, on_delete=models.CASCADE)
    ADD_ACCESS = 'AA'
    REMOVE_ACCESS = 'RA'
    CHANGE_TYPE_CHOICES = (
                    (ADD_ACCESS, "Add access"),
                    (REMOVE_ACCESS, "Remove access"),
    )  
    change_type  = models.CharField(
                            max_length=2,
                            choices = CHANGE_TYPE_CHOICES,
                            default = ADD_ACCESS,
    )

    def __str__(self):
        return "{} on {}".format(self.change_type, self.date_changed)

    class Meta:
        verbose_name = 'Access Log'
        verbose_name_plural = 'Access Logs'

class Audit_Log(models.Model):
    record_creation = models.DateField(auto_now_add=True)
    record_update = models.DateField(auto_now=True)
    record_author = models.ForeignKey(User, on_delete=models.CASCADE)
    
    performed_by = models.ForeignKey(DC_Administrator, on_delete=models.CASCADE)
    sn_ticket = models.CharField(max_length=32, null=True, blank=True)
    audit_date = models.DateField()
    dc_user = models.ForeignKey(
                        DC_User, 
                        null=True, 
                        blank=True, 
                        on_delete=models.CASCADE,
                        )
    project = models.ForeignKey(
                        Project, 
                        null=True, 
                        blank=True, 
                        on_delete=models.CASCADE,
                        )
    node = models.ForeignKey(
                        Server, 
                        null=True, 
                        blank=True, 
                        on_delete=models.CASCADE,
                        )
    governance_docs = models.ForeignKey(
                            Governance_Doc, 
                            null=True, 
                            blank=True, 
                            on_delete=models.CASCADE,
                            )
    comments = models.TextField(null=True, blank=True)

    def __str__(self):
        return "{}_{}".format(self.audit_date, self.comments[:10])

    class Meta:
        verbose_name = 'Audit Log'
        verbose_name_plural = 'Audit Logs'

class Storage_Log(models.Model):
    record_creation = models.DateField(auto_now_add=True)
    record_update = models.DateField(auto_now=True)
    record_author = models.ForeignKey(User, on_delete=models.CASCADE)
    
    sn_ticket = models.CharField(max_length=32, null=True, blank=True)
    date_changed = models.DateField()
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    storage_amount = models.IntegerField(null=True, blank=True)
    storage_type = models.ForeignKey(StorageCost, on_delete=models.CASCADE)
    comments = models.TextField(null=True, blank=True)

    def __str__(self):
        return "{} {}".format( self.storage_amount, self.date_changed)

    class Meta:
        verbose_name = 'Storage Log'
        verbose_name_plural = 'Storage Logs'

class Data_Log(models.Model):
    record_creation = models.DateField(auto_now_add=True)
    record_update = models.DateField(auto_now=True)
    record_author = models.ForeignKey(User, on_delete=models.CASCADE)
    
    change_date = models.DateField()

    IMPORT = 'IM'
    EXPORT = 'EX'
    DIRECTION_TYPE_CHOICES = (
                    (IMPORT, "Import data"),
                    (EXPORT, "Export data"),
    )  
    direction  = models.CharField(
                            max_length=2,
                            choices = DIRECTION_TYPE_CHOICES,
                            default = EXPORT,
    )

    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    request_ticket = models.CharField(max_length=32, null=True, blank=True)
    transfer_ticket = models.CharField(max_length=32, null=True, blank=True)
    authorized_by = models.ForeignKey(
                            DC_Administrator, 
                            on_delete=models.CASCADE,
                            related_name='authorizing_administrator',
                            )
    reviewed_by = models.ForeignKey(
                            DC_Administrator, 
                            on_delete=models.CASCADE,
                            related_name='reviewing_administrator',
                            )
    file_description = models.TextField()

    TRANSFERMED = 'TM'
    PHYSICAL = 'PH'
    EMAIL = 'EM'
    SFTP = 'SF'
    POPMED = 'PM'
    TRANSFER_METHOD_CHOICES = (
                    (TRANSFERMED, "Transfer.med.cornell.edu"),
                    (PHYSICAL, "Physical media"),
                    (EMAIL, "Email"),
                    (SFTP, "SFTP"),
                    (POPMED, "PopMedNet"),
    )  
    transfer_method  = models.CharField(
                            max_length=2,
                            choices = TRANSFER_METHOD_CHOICES,
                            default = TRANSFERMED,
    )

    def __str__(self):
        return "{} {}".format(self.direction, self.change_date)

    class Meta:
        verbose_name = 'Data Log'
        verbose_name_plural = 'Data Logs'

class Server_Change_Log(models.Model):
    sn_ticket = models.CharField(max_length=32, null=True, blank=True)
    change_date = models.DateField()
    record_author = models.ForeignKey(User, on_delete=models.CASCADE)
    
    node_changed = models.ForeignKey(Server, on_delete=models.CASCADE, null=True)
    CONNECTED = 'CO'
    DISCONNECTED = 'DC'
    STATE_CHANGE_CHOICES = (
                    (CONNECTED, "Connected"),
                    (DISCONNECTED, "Disconnected"),
    )  
    state_change  = models.CharField(
                            max_length=2,
                            choices = STATE_CHANGE_CHOICES,
                            null=True,
                            blank=True,
    )    

    ADD_STORAGE = 'AS'
    REM_STORAGE = 'RS'
    STORAGE_CHANGE_CHOICES = (
                    (ADD_STORAGE, "Add storage"),
                    (REM_STORAGE, "Remove storage"),
    )  
    state_change  = models.CharField(
                            max_length=2,
                            choices = STORAGE_CHANGE_CHOICES,
                            null=True,
                            blank=True,
    )    

    change_amount = models.IntegerField(null=True, blank=True)
    comments = models.TextField(null=True, blank=True)
    
    def __str__(self):
        return "{}".format(self.change_date)

    class Meta:
        verbose_name = 'Server Change Log'
        verbose_name_plural = 'Server Change Logs'

class AlertTagType(models.Model):
    name = models.CharField(max_length=64)
    description = models.TextField(null=True, blank=True)

class AlertTag(models.Model):
    record_creation = models.DateField(auto_now_add=True)
    record_update = models.DateField(auto_now=True)
    record_author = models.ForeignKey(User, on_delete=models.CASCADE)
    
    name = models.CharField(max_length=64, null=True, blank=True)   
    type = models.ForeignKey(AlertTagType, 
                            on_delete=models.CASCADE, 
                            related_name="tagtype"
                            )
                            
    description = models.TextField(null=True, blank=True)                   
    affected_prj = models.ForeignKey(Project, 
                            on_delete=models.CASCADE, 
                            related_name="tagtype",
                            null=True,
                            blank=True,
                            )
    affected_dcuser = models.ForeignKey(DC_User, 
                            on_delete=models.CASCADE, 
                            related_name="tagtype",
                            null=True,
                            blank=True,
                            )
    affected_software = models.ForeignKey(Software, 
                            on_delete=models.CASCADE, 
                            related_name="tagtype",
                            null=True,
                            blank=True,
                            )
    affected_server = models.ForeignKey(Server, 
                            on_delete=models.CASCADE, 
                            related_name="tagtype",
                            null=True,
                            blank=True,
                            )
    affected_admin = models.ForeignKey(DC_Administrator, 
                            on_delete=models.CASCADE, 
                            related_name="tagtype",
                            null=True,
                            blank=True,
                            )
    affected_govdoc = models.ForeignKey(Governance_Doc, 
                            on_delete=models.CASCADE, 
                            related_name="tagtype",
                            null=True,
                            blank=True,
                            )
    affected_softwarelicensetype = models.ForeignKey(Software_License_Type, 
                            on_delete=models.CASCADE, 
                            related_name="tagtype",
                            null=True,
                            blank=True,
                            )
  


    