import enquiries, subprocess, shutil, sys
from re import sub
from subprocess import CalledProcessError, check_output, run
from os import listdir, path, sep, remove
from os.path import exists
from zipfile import ZipFile
from urllib.request import urlopen, urlretrieve
from urllib.error import URLError, HTTPError
from bs4 import BeautifulSoup

def list_ovpn_files(directory, extension):
    return [f for f in listdir(directory) if f.endswith('.' + extension)]

url_vpnbook="https://www.vpnbook.com"
url_freevpn = url_vpnbook + '/freevpn'
profile_dir = 'profile'
pass_file = 'pwd.png'
vpn_zip = 'vpn.zip'
login_file = 'login.conf'
openvpn_dir = path.join(path.expanduser('~'), '.OpenVPN')
# remove ovpn-files in openvpn_dir
for file_item in list_ovpn_files(openvpn_dir, 'ovpn'):
    try:
        remove(path.join(openvpn_dir, file_item))
    except:
        pass
# delete directory profile_dir if exists
if exists(profile_dir):
    shutil.rmtree(profile_dir)
try:
    response = urlopen(url_freevpn)
except HTTPError as e:
    print(f'{url_vpnbook}: {e.code}')
    sys.exit(f'{e.code}')
except URLError as e:
    print(f'{url_vpnbook}: {e.reason}')
    sys.exit(f'{e.reason}')
html = BeautifulSoup(response, "lxml")  # "lxml" or "html.parser" but lxml faster
ul_elem = html.body.find('ul', attrs={'class':'disc'})
hrefs = [a['href'] for a in html.body.findAll('a') if a.get('href')]
# список url с архивами ovpn-файлов, которые указаны на сайте
ovpn_files = [url_vpnbook + l for l in hrefs if l.find('free-openvpn-account') == 1]
pwd_url = url_vpnbook + '/' + ul_elem.find('img')['src'].replace(' ', '%20')
try:
    urlretrieve(pwd_url, pass_file)
except BaseException as e:
    print(e.reason)
    sys.exit(e.reason)
except ValueError as e:
    print(f'{pwd_url}: {e.reason}')
    sys.exit(e.reason)
except URLError as e:
    print(f'{pwd_url}: {e.reason}')
    sys.exit(e.reason)

password = check_output(["gocr", pass_file], universal_newlines=True).strip()
username = [u.text for u in ul_elem.findAll('li') if u.text.find('Username:', 0) == 0][0].split(': ')[1]
# create login.conf with credentials
with open(path.join(openvpn_dir, login_file), 'w') as conf_file:
    conf_file.writelines('\n'.join([username, password]))
# show menu with list of VPN-servers
selected_vpn = enquiries.choose('Choose one of these VPN servers: ', ovpn_files)
# get archive with ovpn-files as 'vpn.zip'
urlretrieve(selected_vpn, vpn_zip)
# extract files from zip-archive
with ZipFile(vpn_zip, 'r') as zf:
    zf.extractall(profile_dir)
ovpn_profile = list_ovpn_files(profile_dir, 'ovpn')
# show menu with list of vpn profiles
profile = enquiries.choose('Choose one of these profile in VPN server: ', ovpn_profile)
selected_profile = path.join(profile_dir, profile)
selected_profile_openvpn_dir = path.join(openvpn_dir, profile)
# move file to openvpn_dir
shutil.move( selected_profile, selected_profile_openvpn_dir )
# append to selected ovpn-file username and login from login.conf
lines = ''
with open(selected_profile_openvpn_dir,'r', encoding ='utf-8') as f:
    # lines = '\n'.join([line.strip() + ' ' + path.join(openvpn_dir, login_file) if line.strip() == 'auth-user-pass' else line.strip() for line in f])
    lines = '\n'.join([line.strip() + ' ' + login_file if line.strip() == 'auth-user-pass' else line.strip() for line in f])
with open(selected_profile_openvpn_dir, 'w', encoding ='utf-8') as f:
    f.write(lines)

try:
    # find all vpn connections in table mode with fields NAME,TYPE (add "--active" param if only active)
    process_vpn = run('nmcli -f NAME,TYPE con show|grep vpn', shell=True, check=True, stdout=subprocess.PIPE, universal_newlines=True)
    # replace two or more spaces with one and create list
    con_vpn_list = sub(' +vpn', '', process_vpn.stdout.strip()).split('\n')
    # create list with name vpn
    vpn_names_list = [c.split(' ')[0] for c in con_vpn_list]
    if enquiries.choose('Delete all vpn connections?: ', ['yes', 'no']) == 'yes':
        # delete vpn connections
        for v in vpn_names_list:
            try:
                print(f'Delete vpn connection: {v}')
                run(f'nmcli con del {v}', shell=True, check=True, stdout=subprocess.PIPE, universal_newlines=True)
            except:
                pass
except CalledProcessError as e:
    # print(e.returncode)
    print('No configured vpn connections found. Passed..')

# add profile to connections list
process_add_con_vpn = run(f'nmcli con import type openvpn file {selected_profile_openvpn_dir}', shell=True, check=True, stdout=subprocess.PIPE, universal_newlines=True)
vpn_con = profile.replace('.ovpn', '')
try:
    # Add a password to the vpn connection configuration
    run(f'nmcli con modify {vpn_con} vpn.secrets \"password={password}\"', shell=True, check=True, stdout=subprocess.PIPE, universal_newlines=True)
    # Add a username to the vpn connection configuration
    run(f'nmcli con modify {vpn_con} vpn.user-name \"{username}\"', shell=True, check=True, stdout=subprocess.PIPE, universal_newlines=True)
    # trying to connect
    run(f'nmcli con up {vpn_con}', shell=True, check=True, stdout=subprocess.PIPE, universal_newlines=True)
    print('VPN connection successfully established.')
except:
    print('An unexpected error occurred. VPN connection not established. Check username and password')
