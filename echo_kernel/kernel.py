import docker

import hashlib
import os

base_image = 'namin/io.livecode.ch'

def init_app_image(img, git_url):
    c = docker.from_env()
    m = c.containers.create(base_image, 'git clone --recursive "%s" /home/runner/code' % git_url, user='runner')
    m.start()
    s = m.wait()
    if s['Error']:
        return 'error cloning repository %s -- %s' % (git_url,s['Error']), s['StatusCode']
    m.commit(img)
    return dkr_run(img, 'livecode-install', img, c=c)

def dkr_run(img, cmd, commit=None, timeout=10, c=None):
    c = c or docker.from_env()
    r = ""
    m = c.containers.create(img,
                            "timeout %d %s" % (timeout, cmd),
                            user='runner',
                            environment={'HOME':'/home/runner'},
                            volumes={'/tmp/snippets': {'bind': '/mnt/snippets', 'mode': 'ro'}},
                            network_disabled=False)
    m.start()
    s = m.wait()['StatusCode']
    if s!=0:
        r += "error: (%d)\n" % s
    if s==137:
        r += "killed!"
    elif s==125:
        r += "timeout!"
    elif s==124:
        r += "inifinite loop!"
    else:
        r += m.logs().decode('utf-8')
    if commit:
        m.commit(commit)
    return r, s

def snippet_cache(txt):
    key = hashlib.md5(txt.encode('utf-8')).hexdigest()
    fn = os.path.join('/tmp/snippets', key)
    if not os.path.isfile(fn):
        with open(fn, 'w') as f:
            f.write(txt)
    return key

def run(app_image, input_main,input_pre='',input_post=''):
    img = app_image
    key_main = snippet_cache(input_main)
    key_pre = snippet_cache(input_pre)
    key_post = snippet_cache(input_post)
    return dkr_run(img, 'livecode-run %s %s %s' % (key_main, key_pre, key_post))

def strip(cmd, code):
    return code[len(cmd):].strip()

from ipykernel.kernelbase import Kernel

class EchoKernel(Kernel):
    implementation = 'Echo'
    implementation_version = '1.0'
    language = 'no-op'
    language_version = '0.1'
    language_info = {
        'name': 'Any text',
        'mimetype': 'text/plain',
        'file_extension': '.txt',
    }
    banner = "Echo kernel - as useful as a parrot"

    def __init__(self, **kwargs):
        Kernel.__init__(self, **kwargs)
        self.set_repo('webyrd/webmk')
        self.pre = ''
        self.post = ''

    def set_repo(self, user_repo):
        self.user_repo = user_repo
        self.app_image = base_image+'/'+self.user_repo
        self.app_git_url = 'https://github.com/%s.git' % self.user_repo

    def do_execute(self, code, silent, store_history=True, user_expressions=None, allow_stdin=False):
        if not silent:
            inp = None
            if code.startswith('@config'):
                self.set_repo(strip('@config', code))
                output, status = init_app_image(self.app_image, self.app_git_url)
            elif code.startswith('@reset'):
                self.pre = ''
                self.post = ''
                output = 'OK'
            elif code.startswith('@lib @norun'):
                self.pre += '\n' + strip('@lib @norun', code)
                output = 'OK'
            elif code.startswith('@lib'):
                inp = strip('@lib', code)
                self.pre += '\n' + inp
                inp = self.pre
            else:
                inp = self.pre + '\n' + code
            if inp:
                output, status = run(self.app_image, inp, input_pre=self.pre)
            stream_content = {'name': 'stdout', 'text': output}
            self.send_response(self.iopub_socket, 'stream', stream_content)

        return {'status': 'ok',
                # The base class increments the execution count
                'execution_count': self.execution_count,
                'payload': [],
                'user_expressions': {},
               }
