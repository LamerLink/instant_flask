import os
import sys
import re
import shutil
import distutils.dir_util
import subprocess
import pkg_resources
from getpass import getpass


def call_safely(command: list) -> bool:
    try:
        subprocess.check_call(command, stdout=subprocess.DEVNULL)
        return True
    except subprocess.CalledProcessError:
        return False

def pip_install(package_name: str) -> None:
    print(f'Installing {package_name}...', end="", flush=True)
    result = call_safely(['pip', 'install', package_name])
    if result:
        print('success!')
    else:
        print('installation failed!')

def install_virtualenv() -> None:
    install_venv_yn = input('Install now? (y/n): ').lower()
    if install_venv_yn not in ['y', 'n']:
        print('Invalid response, enter y or n.')
        install_virtualenv()
    elif install_venv_yn == 'n':
        sys.exit(0)
    elif install_venv_yn == 'y':
        call_safely([sys.executable, '-m', 'pip', 'install', 'virtualenv'])

def get_dest_dir() -> str:
    dest_dir = input(
        (
            "Directory you'd like to install to "
            "(leave blank for current directory): "
        )
    )
    if not os.path.isdir(dest_dir):
        try:
            os.mkdir(dest_dir)
        except OSError:
            print('Directory cannot be created, try another.')
            dest_dir = get_dest_dir()
    return dest_dir

def get_ip() -> str:
    ip_pattern = re.compile(".*\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}")
    dest_ip = input("IPv4 to bind to (leave blank for 127.0.0.1): ")
    if dest_ip == '':
        dest_ip = '127.0.0.1'
    elif not ip_pattern.match(dest_ip):
        print('Invalid IPv4 address, try again.')
        dest_ip = get_ip()
    return dest_ip

def get_port() -> str:
    dest_port = input("Port to bind to (leave blank for 8080): ")
    if dest_port == '':
        dest_port = '8080'
    try:
        int(dest_port)
        return dest_port
    except ValueError:
        print('Invalid port. Port should be a number between 1 and 65535.')
        dest_port = get_port()

def get_secret_key() -> str:
    key = input("Server security key: ")
    if len(key) == 0:
        print('Key cannot be empty.')
        key = get_secret_key()
    elif len(key) < 12:
        key = key * 2
    return key

def replace_file_text(file_name, original_text, replacement_text) -> None:
    with open(file_name, "r+") as file_io:
        file_text = file_io.read()
        file_text = file_text.replace(original_text, replacement_text)
    with open(file_name, "w") as file_io:
        file_io.write(file_text)

if sys.platform.startswith('linux'):
    os_type = 'l'
elif sys.platform.startswith('win32'):
    os_type = 'w'
elif sys.platform.startswith('darwin'):
    os_type = 'm'
    print('NOTE: MacOS is not yet supported with this script.')
    sys.exit(1)

setup_dir = os.getcwd()

if 'virtualenv' not in {pkg.key for pkg in pkg_resources.working_set}:
    print('Required module virtualenv is not installed.')
    install_virtualenv()

dest_dir = get_dest_dir()
ip = get_ip()
port = get_port()
secret_key = get_secret_key()

template_environment = os.path.join(setup_dir, 'environment')
distutils.dir_util.copy_tree(template_environment, dest_dir)

app_py = os.path.join(dest_dir, 'app.py')
replace_file_text(app_py, 'ph_for_ip', ip)
replace_file_text(app_py, 'ph_for_port', port)
replace_file_text(app_py, 'ph_for_secret', secret_key)
if os_type == 'l':
    vpy_path = os.path.join(dest_dir, 'venv', 'bin', 'python')
elif os_type == 'w':
    vpy_path = vpy_path = os.path.join(
        dest_dir,
        'venv',
        'Scripts',
        'python.exe'
    )
replace_file_text(app_py, 'ph_for_vpy_path', vpy_path)
misc_py = os.path.join(dest_dir, 'functions', 'misc.py')
replace_file_text(misc_py, 'ph_for_parent_dir', dest_dir)

os.mkdir(os.path.join(dest_dir, 'venv'))
os.mkdir(os.path.join(dest_dir, 'uploads'))
os.mkdir(os.path.join(dest_dir, 'files_to_serve'))
os.mkdir(os.path.join(dest_dir, 'logs'))

os.chdir(dest_dir)
print('Creating virtual environment, this takes a minute or so.')
call_safely(['virtualenv', 'venv'])
if os_type == 'l':
    activate_this_py = os.path.join(dest_dir, 'venv/bin/activate_this.py')
elif os_type == 'w':
    activate_this_py = os.path.join(dest_dir, 'venv\\Scripts\\activate_this.py')
exec(open(activate_this_py).read(), dict(__file__=activate_this_py))

print('Installing dependencies...')
pip_install('waitress')
pip_install('flask')
pip_install('flask-login')
pip_install('flask-talisman')
pip_install('flask-mobility')
pip_install('flask-wtf')
pip_install('flask-sqlalchemy')
pip_install('email-validator')
pip_install('openpyxl')
pip_install('python-dateutil')

print('Set up complete. Make sure you set up a database!')
