# Labelit
### Data labelling platform for small teams
## Description
Labelit is a data labelling platform based on open source tool [Label Studio](https://labelstud.io/). We want to help small teams (having 3 to 5 annotators) who use [Label Studio](https://labelstud.io/) to manage multiple projects.

## How it works
Labelit creates a [Label Studio](https://labelstud.io/) server for each project in multi-session mode so that it works for multiple users. So, if you have N projects, there will be N Label Studio servers running. Labelit then routes user requests to these servers based on project using reverse-proxy technique. Labelit takes care of managing projects, user authentication and assigning annotators to projects.

## Features
- Create and manage multiple data labelling projects.
- Label data using the familiar Label Studio tool.
- Access control using Admin, Manager and Annotators roles.
- Support for datasets from remote storage such as AWS S3.
- Export labelled data automatically at regular intervals.

## How to Setup
1. Download latest release from [releases page](https://github.com/verloop/labelit/releases) using `Source code` option and decompress the downloaded file.
3. Create a conda environment (recommended) : `conda create -n label-studio python=3.7`
4. Switch to conda env (recommended) : `conda activate label-studio`
5. Install requirements for Labelit : `pip install -r requirements.txt`
6. Enter Django app directory : `cd labelit`
7. Set secret key for Django as Environment variable (You can generate secret key using https://gist.github.com/ndarville/3452907 or https://djecrety.ir): `export DJANGO_SECRET_KEY='<generated_key>'`
8. Perform database migration (By default, it uses local SQLite database. If you want to connect to another database, check Django documentation) : `python manage.py migrate`
9. Create admin user : `python manage.py createsuperuser`
10. Run the server using gunicorn : `gunicorn --worker-class=gevent --worker-connections=500 --workers=1 -b '0.0.0.0:8000' labelit.wsgi`

## Development Setup
1. Clone the repo : `git clone git@github.com:verloop/labelit.git; cd labelit`
2. Create a conda environment (recommended) : `conda create -n label-studio python=3.7`
3. Switch to conda env (recommended) : `conda activate label-studio`
4. Install requirements for Labelit : `pip install -r requirements.txt`
5. Enter Django app directory : `cd labelit`
6. Set secret key for Django as Environment variable (You can generate secret key using https://gist.github.com/ndarville/3452907 or https://djecrety.ir): `export DJANGO_SECRET_KEY="<generated_key>"`
7. Perform database migration (By default, it uses local SQLite database. If you want to connect to another database, check Django documentation) : `python manage.py migrate`
8. Create admin user : `python manage.py createsuperuser`
9. Run the development server : `python manage.py runserver --noreload`

## How to use
After you perform setup, you can use Labelit as follows:
### Admins
1. Go to `http://127.0.0.1:8000/` and login using your credentials.
2. You can see projects created by all managers in projects list page.
3. You can create new users by going to admin panel at `http://127.0.0.1:8000/admin`.
4. While creating users, make sure you assign the correct access role using `Staff type` field.

### Managers
- Go to `http://127.0.0.1:8000/` and login using your credentials.
- Listing projects
  - You will be shown all the projects you created after successful login. You can also go to `http://127.0.0.1:8000/projects/list` for the same.
- Creating new project
  - You can create new projects using create project page at `http://127.0.0.1:8000/projects/create` and following instructions give there.
  - You can provide local directory or remote storage directory in the dataset path. We currently support AWS S3 and Google storage (plugin needs to be installed and the server needs to have access to the bucket)
  - You need to give labelling configuration as Label Studio XML config. You can test the config first on [Label Studio Playground](https://labelstud.io/playground/).
  - Select export option if needed and we'll automatically export the labelled data in format selected.
- Assigning annotators
  - From the project listing page, click `Manage annotators` to add or remove annotators for the project.
  - Once you are in the annotator managing page, you can select annotators to be assigned and click `Save` once done to apply the changes.
- Deleting projects
  - From the project listing page, click `Delete` button for the project you want to delete.
  - Confirm deleting the project from the popup when its shown.

### Annotators
- Go to `http://127.0.0.1:8000/` and login using your credentials.
- You can view all projects assigned in the homepage.
- Click the `Tasks UI` button to view all the tasks that needs to be labelled for the project
- Click the `Labelling UI` button to go to labelling page.

## Remote storage support
Labelit now supports datasets that are stored remotely.
We have right now added plugins for the following storage :
- AWS S3
- Google storage

Since this is optional, Labelit by default doesn't install the packages needed for accessing data from these storages. Install package for the storage you need:  
For AWS S3 support : `pip install boto3`  
For Google storage support : `pip install google-cloud-storage`  

Make sure the instance/machine is configured with access to the remote storage and check Django settings (`./labelit/labelit/settings.py`) for few additional settings.  
And that's it! Labelit automatically detects the storage type when you give it while creating project, just make sure you use the right prefix (eg. `s3://` for AWS s3 storage).
Currently, Labelit only supports downloading dataset from remote storage. This is performed <b>only one time</b> after project is created. So, in case the data in remote storage is modified later, it won't reflect here.
We will be adding support for remote upload soon to automatically upload labelled data to remote storage.

### Using other remote storages
If you are using any other remote storage type, you can easily write a plugin. Check our `Storage` module for this. Once plugin is created, you need to modify `Jobs` module for using it.

## Deploying to Production
We strongly advise not to use Labelit on production as it's still under development. In case you want to try, you need to run Django using a proper server such as [Gunicorn](https://labelstud.io/playground/). Here's an example of how to run it:  
`gunicorn --worker-class=gevent --worker-connections=500 --workers=1 -b '0.0.0.0:8080' labelit.wsgi`

The above command starts a Gunicorn server on port 8080. Make sure you don't run multiple worker processes as it will start duplicate Label Studio servers, hence we are using `gevent` in the above example. We will be fixing this in a future release.
