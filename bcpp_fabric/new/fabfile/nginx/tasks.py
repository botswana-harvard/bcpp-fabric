import io
import os
import plistlib

from fabric.api import sudo, task, put, cd, run, env
from fabric.contrib.files import exists, contains, sed

from ..env import update_fabric_env
from ..utils import bootstrap_env


@task
def install_nginx(config_path=None, local_fabric_conf=None, bootstrap_branch=None, skip_bootstrap=None):
    if not skip_bootstrap:
        bootstrap_env(
            path=os.path.expanduser(os.path.join(config_path, 'conf')),
            bootstrap_branch=bootstrap_branch)
        update_fabric_env(use_local_fabric_conf=local_fabric_conf)
    result = run('nginx -V', warn_only=True)
    if env.nginx_version not in result:
        run('brew tap homebrew/services')
        run('brew tap homebrew/nginx')
        run('brew install nginx-full --with-upload-module')
    if not exists(env.log_root):
        sudo('mkdir -p {log_root}'.format(log_root=env.log_root))
    with cd(env.log_root):
        run('touch nginx-error.log')
        run('touch nginx-access.log')
    with cd('/usr/local/etc/nginx'):
        sudo('mv nginx.conf nginx.conf.bak', warn_only=True)
    nginx_conf = os.path.expanduser(os.path.join(
        env.fabric_config_root, 'conf', 'nginx', 'nginx.conf'))
    server_conf = os.path.expanduser(os.path.join(
        env.fabric_config_root, 'conf', 'nginx', env.nginx_server_conf))
    put(nginx_conf, '/usr/local/etc/nginx/', use_sudo=True)
    put(server_conf, '/usr/local/etc/nginx/servers/', use_sudo=True)
    remote_server_conf = os.path.join(
        '/usr/local/etc/nginx/servers/', env.nginx_server_conf)
    if contains(remote_server_conf, 'STATIC_ROOT'):
        sed(remote_server_conf, 'STATIC_ROOT',
            env.static_root, use_sudo=True)
    if contains(remote_server_conf, 'MEDIA_ROOT'):
        sed(remote_server_conf, 'MEDIA_ROOT',
            env.media_root, use_sudo=True)
    create_nginx_plist()


def create_nginx_plist():
    options = {
        'Label': 'nginx',
        'Program': '/usr/local/bin/nginx',
        'KeepAlive': True,
        'NetworkState': True,
        'RunAtLoad': True,
        'UserName': 'root'}
    plist = plistlib.dumps(options, fmt=plistlib.FMT_XML)
    put(io.BytesIO(plist), '/Library/LaunchDaemons/nginx.plist', use_sudo=True)
    sudo('chown root:wheel /Library/LaunchDaemons/nginx.plist')
