from label_studio import server
from label_studio.utils.io import find_editor_files
from flask import session, request, render_template, redirect
import os
from sys import exit
from label_studio.utils.argparser import parse_input_args
import label_studio.utils.functions
import logging

logger = logging.getLogger(__name__)

app = server.app

APP_PATH = os.path.dirname(os.path.abspath(__file__))

# Set template path to use our custom templates
TEMPLATE_PATH = os.path.join(APP_PATH, 'templates/')
app.template_folder = TEMPLATE_PATH


def set_user_data(username, project_name):
    """Set session data for user"""
    session['user'] = username
    session['project'] = project_name

def set_details_from_headers(headers):
    """Setup user details from headers"""
    return set_user_data(headers['LABELIT_USER'], headers['LABELIT_PROJECT'])

# Labeling home for Labelit
@app.route('/labelit')
def labelit_labeling_page():
    """ Label studio frontend: task labeling
    This is a modification of labeling page view provided by label studio.
    Our modifications make sure we call the right API URLs as label studio is
    running behind labelit/django.
    """
    set_details_from_headers(request.headers)

    project = server.project_get_or_create()
    if len(project.tasks) == 0:
        return redirect('/welcome') # need to fix this. not sure if this is needed

    # task data: load task or task with completions if it exists
    task_data = None
    task_id = request.args.get('task_id', None)

    if task_id is not None:
        task_data = project.get_task_with_completions(task_id) or project.get_task(task_id)
        """
        # Disabling ML backend for now
        if project.ml_backend:
            task_data = deepcopy(task_data)
            task_data['predictions'] = project.ml_backend.make_predictions(task_data, project.project_obj)
        """
    # Get project name from session
    project_name = session['project']

    return render_template(
        'label_home.html',
        project=project_name,
        config=project.config,
        label_config_line=project.label_config_line,
        task_id=task_id,
        task_data=task_data,
        **find_editor_files()
    )

# Labeling tasks page for Labelit
@app.route('/labelit-tasks')
def labelit_tasks_page():
    """ Tasks and completions page
    Modification of label studio's default tasks page for using proper URLs
    """
    set_details_from_headers(request.headers)

    project = server.project_get_or_create()

    proxy_prefix = "/label/" + session['project']

    label_config = open(project.config['label_config']).read()  # load editor config from XML
    task_ids = project.get_tasks().keys()
    completed_at = project.get_completed_at(task_ids)

    # sort by completed time
    task_ids = sorted([(i, completed_at[i] if i in completed_at else '9') for i in task_ids], key=lambda x: x[1])
    task_ids = [i[0] for i in task_ids]  # take only id back
    return render_template(
        'tasks_home.html',
        show_paths=False,
        config=project.config,
        label_config=label_config,
        task_ids=task_ids,
        completions=project.get_completions_ids(),
        completed_at=completed_at,
        proxy_prefix=proxy_prefix,
    )




def main():
    """Runs label studio server using given config.""""
    global input_args

    input_args = parse_input_args()
    server.input_args = input_args

    # setup logging level
    if input_args.log_level:
        print(f"log level is {input_args.log_level}")
        logging.root.setLevel(input_args.log_level)

    label_studio.utils.functions.HOSTNAME = 'http://localhost:' + str(input_args.port)

    if input_args.command != 'start-multi-session':
        exit("Only multi user session is supported!")
    # Lets start the server
    app.run(host='0.0.0.0', port=input_args.port, debug=input_args.debug)


if __name__ == "__main__":
    main()
