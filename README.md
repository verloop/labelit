# labelit
### Data labelling platform for small teams
## Description
Labelit is a data labelling platform based on open source tool [Label Studio](https://labelstud.io/). We want to help small teams (having 3 to 5 annotators) who use [Label Studio](https://labelstud.io/) to manage multiple projects. We run a [Label Studio](https://labelstud.io/) server for each project in multi-session mode to make it work for multiple users. So, if you have N projects, there will be N Label Studio servers running. Labelit then helps to route request to each of these servers based on project ID by using reverse-proxy technique.

Note : Labelit is still in it's initial development phase and not intended for production use. 

## Features
- Create and manage multiple data labelling projects.
- Label data using the familiar Label Studio tool.
- Managers can assign annotators to different projects.

## Development Setup
1. Clone the repo : `git clone git@github.com:verloop/labelit.git; cd labelit`
2. Create a conda environment (recommended) : `conda create -n label-studio python=3.7`
3. Switch to conda env (recommended) : `conda activate label-studio`
4. Clone Label Studio [repo](https://github.com/heartexlabs/label-studio) (There was a bug in Label Studio's code that was fixed recently hence its not there in the release) : `git clone git@github.com:heartexlabs/label-studio.git`
5. Enter Label Studio directory : `cd label-studio`
6. Install Label Studio : `python setup.py install`
7. Go back to Labelit : `cd ..`
8. Install requirements for Labelit : `pip install -r requirements.txt`
9. Enter Django app directory : `cd labelit`
10. Create temp directories : `mkdir projects; mkdir tmp`
11. Set secret key for Django as Environment variable (You can generate secret key using https://gist.github.com/ndarville/3452907 or https://djecrety.ir): `export DJANGO_SECRET_KEY=<generated_key>`
11. Perform database migration (By default, it uses local SQLite database. If you want to connect to another database, check Django documentation) : `python manage.py migrate`
12. Create admin user : `python manage.py createsuperuser`
13. Run the development server : `python manage.py runserver --noreload`

## How to use
After you perform development setup, you can use Labelit as follows:
1. Go to `http://127.0.0.1:8000/admin`
2. Click on `Projects` and then `Create Project`
3. Give a project name (without space)
4. Give path to your dataset (supports text files now). (eg. `dataset-text.txt`)
5. In the Config field, give your Label Studio's XML config. You can test the config first on [Label Studio Playground](https://labelstud.io/playground/).
6. Set yourself as Manager, leave all other fields empty
7. Click on save

You can list projects at `http://127.0.0.1:8000/projects/list`.  
Also, you can go to `http://127.0.0.1:8000/label/<project_name>/labelit` for labeling page and `http://127.0.0.1:8000/label/<project_name>/labelit-tasks` for tasks page

## Deploying to Production
We strongly advise not to use Labelit on production as it's still under development. In case you want to try, you need to run Django using a proper server such as [Gunicorn](https://labelstud.io/playground/). Here's an example of how to run it:  
`gunicorn --worker-class=gevent --worker-connections=500 --workers=1 -b '0.0.0.0:8080' labelit.wsgi`

The above command starts a Gunicorn server on port 8080. Make sure you don't run multiple worker processes as it will start duplicate Label Studio servers, hence we are using `gevent` in the above example. This will go away once we start managing Label Studio instances using cron jobs.
