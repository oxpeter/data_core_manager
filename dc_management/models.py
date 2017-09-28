from django.urls import reverse
from django.db import models
from datetime import date


## Models 
class SN_Ticket(models.Model):
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
    STATUS_CHOICES = (
            (ON, "On"),
            (OFF, "Off"),
    )
    status = models.CharField(
                        max_length=2,
                        choices = STATUS_CHOICES,
                        default = ON,
    )

    PRODUCTION = 'PR'
    TEST = 'TE'
    FUNCTION_CHOICES = (
            (PRODUCTION, "Production"),
            (TEST, "Test"),
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
                (SMALL, "Small ()"),
                (MEDIUM, "Medium ()"),
                (LARGE, "Large ()"),
                (XLARGE, "Extra Large ()"),
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

    
class EnvtSubtype(models.Model):
    name = models.CharField(max_length=32, unique=True)

    def __str__(self):
            return self.name

class DC_User(models.Model):
    record_creation = models.DateField(auto_now_add=True)
    record_update = models.DateField(auto_now=True)

    sn_ticket = models.ForeignKey(SN_Ticket, on_delete=models.CASCADE, null=True, blank=True)
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
    OTHER = 'OT' # note this is also used in AFFILIATION_CHOICES
    ROLE_CHOICES = (
                (FACULTY, 'Faculty'),
                (STATISTICIAN, 'Statistician'),
                (AFFILIATE, 'Affiliate'),
                (RESEARCH_COORDINATOR, 'Research Coordinator'),
                (STUDENT, 'Student'),
                (VOLUNTEER, 'Volunteer'),
                (OTHER, 'Other'),
    )
    role = models.CharField(
                            max_length=2,
                            choices = ROLE_CHOICES,
                            default = FACULTY,
    )
    
    comments = models.TextField(null=True, blank=True)

    def __str__(self):
            return "{1} {2}({0})".format(self.cwid, self.first_name, self.last_name)

    class Meta:
        verbose_name = 'Data Core User'
        verbose_name_plural = 'Data Core Users'

    def get_absolute_url(self):
        return reverse('dcuser-detail', kwargs={'pk': self.pk})


class Software_License_Type(models.Model):
    sn_ticket = models.ForeignKey(SN_Ticket, on_delete=models.CASCADE, null=True, blank=True)
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

    name = models.CharField(max_length=64, unique=True)
    vendor = models.CharField(max_length=64)
    version = models.CharField(max_length=16)
    license_type = models.ForeignKey(
                            Software_License_Type, 
                            on_delete=models.CASCADE
                            )
    purchase_details = models.TextField(null=True, blank=True)
    comments = models.TextField(null=True, blank=True)

    def __str__(self):
            return self.name

    class Meta:
        verbose_name = 'Software'
        verbose_name_plural = 'Software'


class SoftwareUnit(models.Model):
    record_creation = models.DateField(auto_now_add=True)
    record_update = models.DateField(auto_now=True)
    unit = models.CharField(max_length=64)
    
    def __str__(self):
            return self.unit
    

class SoftwarePurchase(models.Model):
    record_creation = models.DateField(auto_now_add=True)
    record_update = models.DateField(auto_now=True)
    
    date_purchased = models.DateField(auto_now=True)
    sn_ticket = models.ForeignKey(
                            SN_Ticket, 
                            on_delete=models.CASCADE, 
                            null=True, 
                            blank=True,
                            )
    sw_purchased = models.ForeignKey(Software, on_delete=models.CASCADE)                        
    units_purchased = models.IntegerField()
    cost_per_unit = models.FloatField()
    unit = models.ForeignKey(SoftwareUnit, on_delete=models.CASCADE)  
    invoice_number = models.CharField(max_length=64)
    
    def __str__(self):
            return "{} units on {} ({})".format( 
                                self.date_purchased, 
                                self.units_purchased,
                                self.invoice_number,
                                )
        
class Project(models.Model):
    record_creation = models.DateField(auto_now_add=True)
    record_update = models.DateField(auto_now=True)

    dc_prj_id = models.CharField(max_length=8, unique=True)
    title = models.CharField(max_length=256)
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
    
    sn_tickets = models.ManyToManyField(SN_Ticket, blank=True)
    predata_ticket = models.ForeignKey(
                                SN_Ticket, 
                                on_delete=models.CASCADE,
                                related_name="predata_tickets",
                                null=True,
                                blank=True,
    )
    predata_date = models.DateField(null=True, blank=True)
    postdata_ticket = models.ForeignKey(
                                SN_Ticket, 
                                on_delete=models.CASCADE,
                                related_name="postdata_tickets",
                                null=True,
                                blank=True,
    )
    postdata_date = models.DateField(null=True, blank=True)
    completion_ticket = models.ForeignKey(
                                SN_Ticket, 
                                on_delete=models.CASCADE,
                                related_name="completion_tickets",
                                null=True,
                                blank=True,
    )
    completion_date = models.DateField(null=True, blank=True)
    host = models.ForeignKey(Server, on_delete=models.CASCADE, null=True, blank=True)
    comments = models.TextField(null=True, blank=True)
    
    def __str__(self):
            return self.dc_prj_id
    
class AccessPermission(models.Model):
    name = models.CharField(max_length=32)
    description = models.TextField()    

    def __str__(self):
            return self.name
    
def project_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/prj<id>/<filename>
    return '{0}/{1}'.format(instance.project.dc_prj_id, filename)

class Governance_Doc(models.Model):
    record_creation = models.DateField(auto_now_add=True)
    record_update = models.DateField(auto_now=True)

    sn_ticket = models.ForeignKey(SN_Ticket, on_delete=models.CASCADE, null=True, blank=True)
    doc_id = models.CharField(max_length=64)
    date_issued = models.DateField()
    expiry_date = models.DateField()
    users_permitted = models.ManyToManyField(DC_User, blank=True)
    access_allowed = models.ForeignKey(AccessPermission, on_delete=models.CASCADE)
    
    IRB = 'IR'
    DUA = 'DU'
    DCA = 'DC'
    ONBOARDING = 'ON'
    GOVERNANCE_TYPE_CHOICES = (
                    (IRB, "IRB"),
                    (DUA, "DUA"),
                    (DCA, "Data Core User Agreement"),
                    (ONBOARDING, "Onboarding Form"),
    )
    governance_type = models.CharField(
                            max_length=2,
                            choices = GOVERNANCE_TYPE_CHOICES,
                            default = DCA,
    )
    
    defers_to_doc = models.ForeignKey('self', on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    
    documentation = models.FileField(
                            upload_to=project_directory_path, 
                            null=True,
                            blank=True,
    )

    comments = models.TextField(null=True, blank=True)

    def __str__(self):
            return "{}_{}".format(self.governance_type, self.doc_id)

    class Meta:
        verbose_name = 'Governance Document'
        verbose_name_plural = 'Governance Documents'
   
class DC_Administrator(models.Model):
    record_creation = models.DateField(auto_now_add=True)
    record_update = models.DateField(auto_now=True)

    sn_ticket = models.ForeignKey(SN_Ticket, on_delete=models.CASCADE, null=True, blank=True)
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
    
class External_Access_Log(models.Model):
    record_creation = models.DateField(auto_now_add=True)
    record_update = models.DateField(auto_now=True)

    sn_ticket = models.ForeignKey(SN_Ticket, on_delete=models.CASCADE, null=True, blank=True)
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
    sn_ticket = models.ForeignKey(SN_Ticket, on_delete=models.CASCADE, null=True, blank=True)
    change_date = models.DateField()
    applied_to_prj = models.ForeignKey(Project, on_delete=models.CASCADE)
    applied_to_node = models.ForeignKey(Server, on_delete=models.CASCADE)
    applied_to_user = models.ForeignKey(DC_User, on_delete=models.CASCADE)
    software_changed = models.ForeignKey(Software, on_delete=models.CASCADE, null=True)

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

    sn_ticket = models.ForeignKey(SN_Ticket, on_delete=models.CASCADE, null=True, blank=True)
    date_purchased = models.DateField()
    software = models.ForeignKey(Software, on_delete=models.CASCADE)
    num_licenses_purchased = models.IntegerField()
    expiration = models.DateField()
    
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
        return "{} licenses on {}".format(
                        self.num_licenses_purchased, 
                        self.date_purchased
                        )

    class Meta:
        verbose_name = 'Software Purchase'
        verbose_name_plural = 'Software Purchases'

    
class Access_Log(models.Model):
    record_creation = models.DateField(auto_now_add=True)
    record_update = models.DateField(auto_now=True)

    sn_ticket = models.ForeignKey(SN_Ticket, on_delete=models.CASCADE, null=True, blank=True)
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
    
    performed_by = models.ForeignKey(DC_Administrator, on_delete=models.CASCADE)
    sn_ticket = models.ForeignKey(SN_Ticket, on_delete=models.CASCADE, null=True, blank=True)
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

    sn_ticket = models.ForeignKey(SN_Ticket, on_delete=models.CASCADE, null=True, blank=True)
    date_changed = models.DateField()
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    storage_amount = models.IntegerField(null=True, blank=True)
    comments = models.TextField(null=True, blank=True)

    def __str__(self):
        return "{} {}".format( self.storage_amount, self.date_changed)

    class Meta:
        verbose_name = 'Storage Log'
        verbose_name_plural = 'Storage Logs'

    
class Data_Log(models.Model):
    record_creation = models.DateField(auto_now_add=True)
    record_update = models.DateField(auto_now=True)

    sn_ticket = models.ForeignKey(SN_Ticket, on_delete=models.CASCADE, null=True, blank=True)
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
    request_ticket = models.ForeignKey(
                            SN_Ticket, 
                            on_delete=models.CASCADE,
                            related_name='request_ticket',
                            )
    transfer_ticket = models.ForeignKey(
                            SN_Ticket, 
                            on_delete=models.CASCADE,
                            related_name='transfer_ticket',
                            )
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
    sn_ticket = models.ForeignKey(SN_Ticket, on_delete=models.CASCADE, null=True, blank=True)
    change_date = models.DateField()

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
