# Data Core Manager
_A django app for managing institutional data cores_

**NB: This repository has been deprecated, and is being held for archival purposes only. For the latest development on this project, please look at [Datacore Web Manager](https://github.com/oxpeter/datacore_web_manager)**

```
Peter Oxley
Weill Cornell Medicine
Samuel J. Wood Library and C.V. Starr Biomedical Information Center
1300 York Ave
New York, NY 10065
```

## Scope
This app is for the collection, logging and auditing of infrastructure, project environments, users, software and data governance that are part of a data core. This app is not being developed as a general-purpose app, but as a specific tool for use at the Samuel J. Wood library. The basic data structure should nevertheless be amenable to use in other data core projects. 

## Setup
This app will need to be installed into an existing Django project.

1. Copy `dc_management` directory into the project directory
2. Add `dc_management.apps.DcManagementConfig` to INSTALLED_APPS in settings.py
3. From the project directory, run `python manage.py makemigrations dc_management`
4. run `python manage.py migrate`

## Dependencies
django==2.0
python>=3.6
django-autocomplete-light==3.3.0rc1
django-bootstrap3==9.1.0
django-crispy-forms==1.7.0

