from django.test import TestCase

from django.db import IntegrityError
from django.contrib.auth.models import User

import datetime

from django.utils import timezone

from .models import Server, Project, DC_User, Access_Log, EnvtSubtype, SubFunction

from .forms import StorageChangeForm


class ProjectModelTests(TestCase):

    def test_project_id_is_unique(self):
        """
        was_published_recently() returns False for questions whose pub_date
        is in the future.
        """
        
        first_project = Project(dc_prj_id="prj123")
        second_project = Project(dc_prj_id="prj123")
        self.assertEqual(first_project.dc_prj_id, second_project.dc_prj_id)
        
class StorageTestCase(TestCase):
    def setUp(self):
        js = DC_User.objects.create(first_name='John', last_name='Smith', cwid='jos1234')
        jd = DC_User.objects.create(first_name='Jane', last_name='Doe', cwid='jed2001')
        env = EnvtSubtype.objects.create(name='cool_research')
        subfn = SubFunction.objects.create(name='impo_subfn')
        host = Server.objects.create(   status = "ON",
                            function = "PR",
                            machine_type = "VM",
                            vm_size = "MD",
                            backup = "EN",
                            operating_sys = "M2",
                            node = "HPRP010",
                            sub_function = subfn,
                            name_address = "vITS-HPCP02.med.cornell.edu",
                            ip_address = "10.36.217.229",
                            processor_num = 4,
                            ram = 16,
                            disk_storage = 100,
                            other_storage = 100,   
                            connection_date = datetime.date(2014, 6, 30),
                            comments = "This is an awesome test server for unittest",
        )
        Project.objects.create( dc_prj_id = 'prj0006',
                                title = 'test project',
                                nickname = 'testy',
                                fileshare_storage = 100,
                                direct_attach_storage = 100,
                                backup_storage = 0,
                                requested_ram = 16,
                                requested_cpu = 4,
                                pi = js,
                                env_type = 'RE',
                                env_subtype = env,
                                expected_completion = datetime.date(2018, 7, 13),
                                requested_launch = datetime.date(2018, 2, 13),
                                status = 'RU',
                                predata_date = datetime.date(2017, 12, 1),
                                postdata_date = datetime.date(2017, 12, 13),
                                host = host,
                                comments = "This is a test project for unittest",
        )
        Project.objects.create( dc_prj_id = 'prj0007',
                                title = 'minimal test project',
                                nickname = 'minitest',
                                pi = jd,
                                env_type = 'RE',
                                env_subtype = env,
                                expected_completion = datetime.date(2018, 7, 13),
                                requested_launch = datetime.date(2018, 2, 13),
                                status = 'RU',
        )
        StorageCost.objects.create(
            record_author = models.ForeignKey(User, on_delete=models.CASCADE)
    
            storage_type = models.CharField(max_length=64)
            st_cost_per_gb = models.FloatField()
)
        
        
    def test_unique_cwid(self):
        with self.assertRaises(IntegrityError):
            newbie = DC_User.objects.create(first_name='Tim', 
                                            last_name='Taylor', 
                                            cwid='jos1234')
                                            
    def test_init_without_entry(self):
        with self.assertRaises(KeyError):
            StorageChangeForm()
            
    def test_valid_data(self):
        form = StorageChangeForm({
                    'sn_ticket':,
                    'date_changed':,
                    'project':,
                    'storage_amount':200,
                    'storage_type':"",
                    'comments':"random comment"
        }, entry=self.entry)
        self.assertTrue(form.is_valid())
        comment = form.save()
        self.assertEqual(comment.name, "Turanga Leela")
        self.assertEqual(comment.email, "leela@example.com")
        self.assertEqual(comment.body, "Hi there")
        self.assertEqual(comment.entry, self.entry)

    def test_blank_data(self):
        form = CommentForm({}, entry=self.entry)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors, {
            'name': ['required'],
            'email': ['required'],
            'body': ['required'],
        })