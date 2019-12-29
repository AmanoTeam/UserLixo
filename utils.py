import time
import os
import zipfile

def backup_sources(output_file=None):
    ctime = int(time.time())

    if output_file is not None and isinstance(output_file, str) and not output_file.lower().endswith('.zip'):
        output_file += '.zip'

    fname = output_file or 'backup-{}.zip'.format(ctime)

    with zipfile.ZipFile(fname, 'w', zipfile.ZIP_DEFLATED) as backup:
        for folder, _, files in os.walk('.'):
            for file in files:
                if file != fname and not file.endswith('.pyc') and '.heroku' not in folder.split('/') and 'dls' not in folder.split('/'):
                    backup.write(os.path.join(folder, file))

    return fname