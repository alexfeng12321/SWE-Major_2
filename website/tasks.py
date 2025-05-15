import os, requests
from celery import Celery
from . import create_app, db
from .models import Submission

celery = Celery(__name__, broker=os.getenv('CELERY_BROKER_URL'))
celery.conf.update(result_backend=os.getenv('CELERY_RESULT_BACKEND'))


JD_URL    = "https://api.jdoodle.com/v1/execute"
JD_CLIENT = os.getenv('JD_CLIENT_ID')
JD_SECRET = os.getenv('JD_CLIENT_SECRET')

def run_code_jdoodle(code, stdin=""):
    payload = {
        "clientId":     JD_CLIENT,
        "clientSecret": JD_SECRET,
        "script":       code,
        "stdin":        stdin,
        "language":     "python3",
        "versionIndex": "3"
    }
    r = requests.post(JD_URL, json=payload, timeout=10)
    r.raise_for_status()
    return r.json()

@celery.task
def grade_submission(sub_id):
    app = create_app()
    with app.app_context():
        sub = Submission.query.get(sub_id)
        print("JD CLIENT ID:", os.getenv('JD_CLIENT_ID'))
        print("JD SECRET   :", os.getenv('JD_CLIENT_SECRET'))
        print("Payload     :", {
        "clientId": os.getenv('JD_CLIENT_ID'),
        "clientSecret": os.getenv('JD_CLIENT_SECRET'),
        "script": "print(2)",
        "stdin": "",
        "language": "python3",
        "versionIndex": "3"
        })
        if not sub: return
        
        # load code from disk
        path = os.path.join(app.config['UPLOAD_FOLDER'], sub.code_filename)
        code = open(path).read()
        
        try:
            result = run_code_jdoodle(code, stdin=sub.input_data or "")
            output = result.get('output','').strip()
            sub.output_data = output
            sub.status = 'Passed' if result.get('statusCode')==200 else 'Failed'
        except Exception as e:
            sub.status = 'Error'
            sub.output_data = str(e)

        db.session.commit()
        