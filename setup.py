REPLACEMENTS = {
    '%COLLECTION_PHYS_ROOT%': '/mnt/dysk/01_ZDJĘCIA',           # path containing original images
    '%STATIC_PHYS_ROOT%': '/mnt/dysk/01_ZDJĘCIA/.thumbnails',   # path where thumbnails and previews will be created
    '%PROJECT_ROOT%': '/mnt/dysk/homesite',
    '%VIRTUALENV%': '/mnt/dysk/homesite/virtualenvs/uwsgi',     # virtualenv used by uwsgi
    '%HOST_NAME%': 'majki.mooo.com',
    '%NGINX_PORT%': '80',
    '%UWSGI_PYTHON_PLUGIN%': 'python32',
}

templates = [
    'homesite_uwsgi_template.ini',
    'homesite_nginx_template.conf',
    'mysite/gallery/locations_template.py',
]

import os, re

if __name__ == '__main__':
    PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

    for template in templates:
        template_match = re.match(r'(.*)_template\.([^.]*)', template)
        if template_match:
            original_path = os.path.join(PROJECT_ROOT, template)
            new_path = os.path.join(PROJECT_ROOT, '{0[0]}.{0[1]}'.format(template_match.groups()))

            print("Transforming file: {0} -> {1}".format(original_path, new_path))

            with open(new_path, 'w') as new_file:
                for line in open(original_path).readlines():
                    for (key, value) in REPLACEMENTS.items():
                        line = line.replace(key, value)
                    new_file.write(line)
