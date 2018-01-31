import requests
import time
import os.path
import tempfile
import validators
import json
import pandas as pd
from amb_sdk.config import Config as cfg


class DarwinSdk:

    auth_string = ''
    api_key = ''
    password = ''
    username = ''
    user_password = ''
    token_start_time = 0
    token_time_limit = 3500
    cfg = cfg

    s = requests.Session()
    server_url = cfg.server_url
    version = 'v1'
    routes = {'auth_login': 'auth/login',
              'auth_login_user': 'auth/login/user',
              'auth_register': 'auth/register',
              'auth_register_user': 'auth/register/user',
              'lookup_job_status': 'job/status',
              'lookup_job_status_name': 'job/status/',
              'lookup_artifact': 'lookup/artifact',
              'lookup_artifact_name': 'lookup/artifact/',
              'lookup_client': 'lookup/client',
              'lookup_dataset': 'lookup/dataset',
              'lookup_dataset_name': 'lookup/dataset/',
              'lookup_model': 'lookup/model',
              'lookup_model_name': 'lookup/model/',
              'lookup_tier': 'lookup/tier',
              'lookup_tier_num': 'lookup/tier/',
              'create_model': 'train/model',
              'delete_model': 'train/model/',
              'resume_training_model': 'train/model/',
              'upload_dataset': 'upload/',
              'delete_dataset': 'upload/',
              'download_artifact': 'download/artifacts/',
              'delete_artifact': 'download/artifacts/',
              'analyze_data': 'analyze/data/',
              'analyze_model': 'analyze/model/',
              'create_risk_info': 'risk/',
              'run_model': 'run/model/',
              'set_url': '',
              'get_url': '',
              'delete_all_datasets': '',
              'delete_all_models': ''}

    # Set URL
    def set_url(self, url, version='v1'):
        if validators.url(url):
            self.server_url = url
            self.version = version
            return True, self.server_url
        else:
            return False, 'invalid url'

    def get_url(self):
        return True, self.server_url

    # Authentication and Registration
    def auth_login(self, password, api_key):
        self.username = ''
        self.api_key = api_key
        self.password = password
        url = self.server_url + self.routes['auth_login']
        payload = {'api_key': str(api_key), 'pass1': str(password)}
        r = self.s.post(url, data=payload)
        if r.ok:
            self.auth_string = 'Bearer ' + r.json()['access_token']
            self.token_start_time = time.time()
            return True, self.auth_string
        else:
            return False, '{}: {} - {}'.format(r.status_code, r.reason, r.text[0:1024])

    def auth_login_user(self, username, password):
        self.username = username
        self.password = password
        url = self.server_url + self.routes['auth_login_user']
        payload = {'username': str(username), 'pass1': str(password)}
        r = self.s.post(url, data=payload)
        if r.ok:
            self.auth_string = 'Bearer ' + r.json()['access_token']
            self.token_start_time = time.time()
            return True, self.auth_string
        else:
            return False, '{}: {} - {}'.format(r.status_code, r.reason, r.text[0:1024])

    def auth_register(self, password, api_key):
        self.username = ''
        self.password = password
        self.api_key = api_key
        url = self.server_url + self.routes['auth_register']
        headers = {'Authorization': self.auth_string}
        payload = {'api_key': str(api_key), 'pass1': str(password), 'pass2': str(password)}
        r = self.s.post(url, headers=headers, data=payload)
        if r.ok:
            self.auth_string = 'Bearer ' + r.json()['access_token']
            self.token_start_time = time.time()
            return True, self.auth_string
        else:
            return False, '{}: {} - {}'.format(r.status_code, r.reason, r.text[0:1024])

    def auth_register_user(self, username, password):
        self.username = username
        self.password = password
        url = self.server_url + self.routes['auth_register_user']
        headers = {'Authorization': self.auth_string}
        payload = {'username': str(username), 'pass1': str(password), 'pass2': str(password)}
        r = self.s.post(url, headers=headers, data=payload)
        if r.ok:
            self.auth_string = 'Bearer ' + r.json()['access_token']
            self.token_start_time = time.time()
            return True, self.auth_string
        else:
            return False, '{}: {} - {}'.format(r.status_code, r.reason, r.text[0:1024])

    # Conveniences
    def get_auth_header(self):
        if not self.username and not self.api_key:
            # Either api_key or username must be set.
            return None
        if time.time() - self.token_start_time > self.token_time_limit:
            if self.username:
                self.auth_login_user(self.username, self.password)
            else:
                self.auth_login(self.password, self.api_key)
        return {'Authorization': self.auth_string}

    def get_return_info(self, r):
        if r.ok:
            if not r.text:
                return True, None
            else:
                return True, r.json()
        else:
            return False, '{}: {} - {}'.format(r.status_code, r.reason, r.text[0:1024])

    # Get job information
    def lookup_job_status(self, age=None, status=None):
        url = self.server_url + self.routes['lookup_job_status']
        headers = self.get_auth_header()
        if headers is None:
            return False, "Cannot get Auth token. Please log in."
        payload = {'age': age, 'status': status}
        r = self.s.get(url, headers=headers, params=payload)
        return self.get_return_info(r)

    def lookup_job_status_name(self, job_name):
        url = self.server_url + self.routes['lookup_job_status_name']
        headers = self.get_auth_header()
        if headers is None:
            return False, "Cannot get Auth token. Please log in."
        r = self.s.get(url + str(job_name), headers=headers)
        return self.get_return_info(r)

    # Get model or dataset metadata
    def lookup_artifact(self, type=None):
        url = self.server_url + self.routes['lookup_artifact']
        headers = self.get_auth_header()
        if headers is None:
            return False, "Cannot get Auth token. Please log in."
        print(url)
        payload = {'type': type}
        r = self.s.get(url, headers=headers, params=payload)
        return self.get_return_info(r)

    def lookup_artifact_name(self, artifact_name):
        url = self.server_url + self.routes['lookup_artifact_name']
        headers = self.get_auth_header()
        if headers is None:
            return False, "Cannot get Auth token. Please log in."
        r = self.s.get(url + str(artifact_name), headers=headers)
        return self.get_return_info(r)

    def lookup_client(self):
        url = self.server_url + self.routes['lookup_client']
        headers = self.get_auth_header()
        if headers is None:
            return False, "Cannot get Auth token. Please log in."
        r = self.s.get(url, headers=headers)
        return self.get_return_info(r)

    def lookup_dataset(self):
        url = self.server_url + self.routes['lookup_dataset']
        headers = self.get_auth_header()
        if headers is None:
            return False, "Cannot get Auth token. Please log in."
        r = self.s.get(url, headers=headers)
        return self.get_return_info(r)

    def lookup_dataset_name(self, dataset_name):
        url = self.server_url + self.routes['lookup_dataset_name']
        headers = self.get_auth_header()
        if headers is None:
            return False, "Cannot get Auth token. Please log in."
        r = self.s.get(url + dataset_name, headers=headers)
        return self.get_return_info(r)

    def lookup_model(self):
        url = self.server_url + self.routes['lookup_model']
        headers = self.get_auth_header()
        if headers is None:
            return False, "Cannot get Auth token. Please log in."
        r = self.s.get(url, headers=headers)
        return self.get_return_info(r)

    def lookup_model_name(self, model_name):
        url = self.server_url + self.routes['lookup_model_name'] + str(model_name)
        headers = self.get_auth_header()
        if headers is None:
            return False, "Cannot get Auth token. Please log in."
        r = self.s.get(url, headers=headers)
        return self.get_return_info(r)

    def lookup_tier(self):
        url = self.server_url + self.routes['lookup_tier']
        headers = self.get_auth_header()
        if headers is None:
            return False, "Cannot get Auth token. Please log in."
        r = self.s.get(url, headers=headers)
        return self.get_return_info(r)

    def lookup_tier_num(self, tier_num):
        url = self.server_url + self.routes['lookup_tier_num'] + str(tier_num)
        headers = self.get_auth_header()
        if headers is None:
            return False, "Cannot get Auth token. Please log in."
        r = self.s.get(url, headers=headers)
        return self.get_return_info(r)

    # Train a model
    def create_model(self, dataset_names, **kwargs):
        url = self.server_url + self.routes['create_model']
        headers = self.get_auth_header()
        if headers is None:
            return False, "Cannot get Auth token. Please log in."
        parameters = kwargs
        if 'dataset_names' not in parameters:
            if isinstance(dataset_names, str):
                parameters['dataset_names'] = [dataset_names]
            else:
                parameters['dataset_names'] = dataset_names
        r = self.s.post(url, headers=headers, json=parameters)
        return self.get_return_info(r)

    def delete_model(self, model_name):
        url = self.server_url + self.routes['delete_model'] + str(model_name)
        headers = self.get_auth_header()
        if headers is None:
            return False, "Cannot get Auth token. Please log in."
        r = self.s.delete(url, headers=headers)
        return self.get_return_info(r)

    def resume_training_model(self, model_name, dataset_names, **kwargs):
        url = self.server_url + self.routes['resume_training_model'] + model_name
        headers = self.get_auth_header()
        if headers is None:
            return False, "Cannot get Auth token. Please log in."
        parameters = kwargs
        if 'model_name' not in parameters:
            parameters['model_name'] = model_name
        if 'dataset_names' not in parameters:
            if isinstance(dataset_names, str):
                parameters['dataset_names'] = [dataset_names]
            else:
                parameters['dataset_names'] = dataset_names
        r = self.s.patch(url, headers=headers, json=parameters)
        return self.get_return_info(r)

    # Upload or delete a dataset
    def upload_dataset(self, dataset_path, dataset_name=None):
        if dataset_name is None:
            head, tail = os.path.split(dataset_path)
            dataset_name = tail
            # dataset_name = dataset_path.split('/')[-1]
        url = self.server_url + self.routes['upload_dataset']
        headers = self.get_auth_header()
        if headers is None:
            return False, None
        payload = {'dataset_name': str(dataset_name)}
        files = {'dataset': (str(dataset_path), open(str(dataset_path), 'rb'), 'text/csv/h5')}
        r = self.s.post(url, headers=headers, data=payload, files=files)
        return self.get_return_info(r)

    def delete_dataset(self, dataset_name):
        url = self.server_url + self.routes['delete_dataset'] + str(dataset_name)
        headers = self.get_auth_header()
        if headers is None:
            return False, "Cannot get Auth token. Please log in."
        r = self.s.delete(url, headers=headers)
        return self.get_return_info(r)

    # Upload or delete a generated artifact
    def download_artifact(self, artifact_name):
        headers = self.get_auth_header()
        if headers is None:
            return False, "Cannot get Auth token. Please log in."
        artifact_type = None
        (code, response) = self.lookup_artifact_name(artifact_name)
        if code is True:
            artifact_type = response['type']
        url = self.server_url + self.routes['download_artifact'] + str(artifact_name)

        r = self.s.get(url, headers=headers)
        (code, response) = self.get_return_info(r)
        if code is True:
            artifact = response['artifact']
            if artifact_type == 'Model':
                if artifact[1:4] == 'PNG':
                    with tempfile.NamedTemporaryFile(prefix='artifact-', suffix='.png', delete=False) as png_file:
                        png_filename = png_file.name
                        png_file.write(artifact.encode('latin-1'))
                        return True,  {"filename": png_filename}
                else:
                    return False, "Unknown Model artifact type"
            if artifact_type == 'Test':
                data = json.loads(response['artifact'])
                if 'index' in data:
                    if len(data["index"]) == len(data['actual']):
                        df = pd.DataFrame({'index': data['index'], 'actual': data['actual'],
                                           'predicted': data['predicted']})
                    else:
                        df = pd.DataFrame({'actual': data['actual'], 'predicted': data['predicted']})
                    return True, df
                elif 'x' in data:
                    if len(data["x"]) == len(data['actual']):
                        df = pd.DataFrame({'index': data['x'], 'actual': data['actual'],
                                           'predicted': data['predicted']})
                    else:
                        df = pd.DataFrame({'actual': data['actual'], 'predicted': data['predicted']})
                    return True, df
                else:
                    return False, "Cannot interpret Test artifact"
            if (artifact_type == 'Risk'):
                return True, response
            if (artifact_type == 'Run'):
                if 'png' in artifact[0:100]:
                    with tempfile.NamedTemporaryFile(prefix='artifact-', suffix='.zip', delete=False) as zip_file:
                        zip_filename = zip_file.name
                        zip_file.write(artifact.encode('latin-1'))
                        return True,  {"filename": zip_filename}
                if 'anomaly' in artifact[0:50]:
                    with tempfile.NamedTemporaryFile(prefix='artifact-', suffix='.csv', delete=False) as csv_file:
                        csv_filename = csv_file.name
                        csv_file.write(artifact.encode('latin-1'))
                        return True,  {"filename": csv_filename}
                if DarwinSdk.is_json(response['artifact']):
                    data = json.loads(response['artifact'])
                    if 'index' in data:
                        if len(data["index"]) == len(data['actual']):
                            df = pd.DataFrame({'index': data['index'], 'actual': data['actual'],
                                               'predicted': data['predicted']})
                        else:
                            df = pd.DataFrame({'actual': data['actual'], 'predicted': data['predicted']})
                            return True, df
                else:
                    data = response['artifact'].split('\n')
                    col_name = data[0]
                    del data[0]
                    df = pd.DataFrame(data, columns=[col_name])
                    if DarwinSdk.is_number(df[col_name][0]):
                        df[col_name] = pd.to_numeric(df[col_name], errors='coerce')
                    return True, df
            if (artifact_type == 'Dataset'):
                data = json.loads(response['artifact'])
                df = pd.DataFrame(data=data[0], index=[0])
                for x in range(1, len(data)):
                    df = df.append(data[x], ignore_index=True)
                return True, df
            return False, "Unknown artifact type"
        else:
            return False, response

    def delete_artifact(self, artifact_name):
        url = self.server_url + self.routes['delete_artifact'] + str(artifact_name)
        headers = self.get_auth_header()
        if headers is None:
            return False, "Cannot get Auth token. Please log in."
        r = self.s.delete(url, headers=headers)
        return self.get_return_info(r)

    # Analyze a model or data set
    def analyze_data(self, dataset_name, **kwargs):
        url = self.server_url + self.routes['analyze_data'] + str(dataset_name)
        headers = self.get_auth_header()
        parameters = kwargs
        if headers is None:
            return False, "Cannot get Auth token. Please log in."
        r = self.s.post(url, headers=headers, json=parameters)
        return self.get_return_info(r)

    def analyze_model(self, model_name, job_name=None, artifact_name=None):
        url = self.server_url + self.routes['analyze_model'] + str(model_name)
        headers = self.get_auth_header()
        if headers is None:
            return False, "Cannot get Auth token. Please log in."
        payload = {'job_name': job_name, 'artifact_name': artifact_name}
        r = self.s.post(url, headers=headers, data=payload)
        return self.get_return_info(r)

    # Create risk information for a datatset
    def create_risk_info(self, failure_data, timeseries_data, job_name=None, artifact_name=None, **kwargs):
        url = self.server_url + self.routes['create_risk_info'] + failure_data + '/' + timeseries_data
        headers = self.get_auth_header()
        if headers is None:
            return False, "Cannot get Auth token. Please log in."
        parameters = kwargs
        if 'job_name' not in parameters and job_name is not None:
            parameters['job_name'] = job_name
        if 'artifact_name' not in parameters and artifact_name is not None:
            parameters['artifact_name'] = artifact_name
        r = self.s.post(url, headers=headers, json=parameters)
        return self.get_return_info(r)

    # Run a model on some dataset
    def run_model(self, dataset_name, model_name, supervised=True, job_name=None, artifact_name=None):
        url = self.server_url + self.routes['run_model'] + model_name + '/' + dataset_name
        headers = self.get_auth_header()
        if headers is None:
            return False, "Cannot get Auth token. Please log in."
        payload = {'job_name': job_name, 'artifact_name': artifact_name, 'supervised': supervised}
        r = self.s.post(url, headers=headers, data=payload)
        return self.get_return_info(r)

    # Interactive help
    def help(self):
        import inspect
        for key, value in sorted(DarwinSdk.routes.items()):
            print("   ", key, inspect.signature(getattr(DarwinSdk, str(key))))

    # User convenience
    def delete_all_models(self):
        (code, response) = self.lookup_model()
        if code:
            for model in response:
                model_name = model['name']
                (c, r) = self.delete_model(model_name)
                if not c:
                    return False, 'problems removing {}'.format(model_name)
            return True, None
        else:
            return False, None

    def delete_all_datasets(self):
        (code, response) = self.lookup_dataset()
        if code:
            for dataset in response:
                dataset_name = dataset['name']
                (c, r) = self.delete_dataset(dataset_name)
                if not c:
                    return False, 'problems removing {}'.format(dataset_name)
            return True, None
        else:
            return False, None

    def wait_for_job(self, job_name, time_limit=600):
        start_time = time.time()
        (code, response) = self.lookup_job_status_name(str(job_name))
        print(response)
        while (response['percent_complete'] != 100):
            if (time.time() - start_time > time_limit):
                break
            time.sleep(15.0)
            (code, response) = self.lookup_job_status_name(str(job_name))
            print(response)
        if response['percent_complete'] < 100:
            return(False, "Waited for " + time_limit / 60 + "minutes. Re-run wait_for_job to wait longer.")
        if response['percent_complete'] == 100 and response['status'] != 'Failed':
            return (True, "Job completed")
        return False, response

    # private
    @staticmethod
    def is_json(myjson):
        try:
            json.loads(myjson)
        except ValueError as e:
            return False
        return True

    @staticmethod
    def is_number(s):
        try:
            float(s)
            return True
        except ValueError:
            return False
