import sys
import os
import re

old_os_path = os.environ['PATH']
os.environ['PATH'] = os.path.dirname(os.path.abspath(__file__)) + os.pathsep + old_os_path
base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
site_packages = os.path.join(base, 'lib', 'python%s' % sys.version[:3], 'site-packages')
prev_sys_path = list(sys.path)
import site
site.addsitedir(site_packages)
sys.real_prefix = sys.prefix
sys.prefix = base
# Move the added items to the front of the path
new_sys_path = []
for item in list(sys.path):
    if item not in prev_sys_path:
        new_sys_path.append(item)
        sys.path.remove(item)
sys.path[:0] = new_sys_path
# set env variables
#env_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
env_dir = '/software/anaconda3/envs/server'
dir_to_activate = os.path.join(env_dir, 'etc/conda/activate.d')
for filename in os.listdir(dir_to_activate):
    with open(os.path.join(dir_to_activate,filename), 'r') as f:
        for line in f:
            if line[0] == '#':
                continue
            m = re.search('export (?P<key>[^=]+)=\'(?P<value>.+)\'$', line)
            if m:
                os.environ[m.group('key')] = m.group('value')
