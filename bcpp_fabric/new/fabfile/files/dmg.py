from fabric.api import cd, env, run

from fabric.colors import red


def dismount_dmg(volume_name=None):
    """Dismounts a dmg file on the remote host.
    """
    result = run('diskutil unmount {}'.format(volume_name))
    if result.failed:
        print(red('{host} Dismount failed for {volume_name}'.format(
            host=env.host, volume_name=volume_name)))


def mount_dmg(dmg_path=None, dmg_filename=None, dmg_passphrase=None):
    """Mounts a dmg file on the remote host.
    """
    env.prompts.update({'Enter disk image passphrase:': dmg_passphrase})
    dmg_path = dmg_path or env.dmg_path
    dmg_filename = dmg_filename or env.dmg_filename
    run('diskutil unmount {}'.format(env.key_volume), warn_only=True)
    with cd(dmg_path):
        run('hdiutil attach -stdinpass {}'.format(dmg_filename))
