from django.test import TestCase

import datetime

from django.utils import timezone

from .models import Server, Project, DC_User, Access_Log

class ProjectModelTests(TestCase):

    def test_project_id_is_unique(self):
        """
        was_published_recently() returns False for questions whose pub_date
        is in the future.
        """
        
        first_project = Project(dc_prj_id="prj123")
        second_project = Project(dc_prj_id="prj123")
        self.assertEqual(first_project.dc_prj_id, second_project.dc_prj_id)