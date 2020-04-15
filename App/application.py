#!/usr/bin/env python

from flask import Flask
from flask import render_template
from flask import request
from flask import redirect
from flask import url_for
from os import listdir
from os.path import isfile, join

import subprocess

app = Flask(__name__)

modsec_rl_dir       ='/usr/local/nginx/conf/owasp-modsecurity-crs/rules'
listen_port_file    ='/usr/local/nginx/conf/listen_port.conf'
modsec_file			='/usr/local/nginx/conf/modsecurity.conf'
host_config_file	='/etc/hosts'
logs_error_file		= '/var/log/syslog'
logs_access_file	= '/usr/local/nginx/logs/access.log'
nginx_status_file 	= '/usr/local/nginx/logs/nginx_status.log'
config_file 		= '/usr/local/nginx/conf/nginx.conf'
sample_site 		= 'sample.conf'
sample_modsec       = 'sample_modsec.conf'
sample_index		= 'sample_index.html'
sites_dir 			= '/usr/local/nginx/conf/sites-available'
enabled_sites_dir 	=  sites_dir + '/../sites-enabled'

@app.route("/")
def main():
  return redirect('/login')

@app.route("/login",methods=['GET','POST'])
def login():
    error=None
    if request.method == 'POST':
        if request.form['username']!='1' or request.form['password']!='1':
            error = 'Invalid Credentials. Please try again.'
        else:
            return redirect(url_for('index'))
    return render_template('login.html',mis=error)

@app.route('/home')
def index():
    files = [f for f in listdir(sites_dir) if isfile(join(sites_dir, f))]
    sites = []

    for file in files:
        sites.append({'file':file})

    with open(logs_error_file) as f:
        logs_error = f.read()

    with open(nginx_status_file) as f:
        nginx_status = f.read()

    with open(logs_access_file) as f:
        logs_access = f.read()

    with open(listen_port_file) as a:
        listen_port = a.read()

    return render_template('index.html',sites=sites,logs_error=logs_error,nginx_status=nginx_status,logs_access=logs_access,listen_port=listen_port )

@app.route('/nginx-config')
def nginx_config():
    with open(config_file) as f:
        config = f.read()
    return render_template('nginx_config.html', config=config)

@app.route('/host-config')
def host_config():
    with open(host_config_file) as f:
        config = f.read()
    return render_template('host_config.html', config=config)

#------------SAVE-------
@app.route('/save-nginx-config', methods=['POST'])
def save_nginx_config():
    with open(config_file, "w") as f:
        f.write(request.form['conf'])
    return redirect(url_for('index'))

@app.route('/save-host-config', methods=['POST'])
def save_host_config():
    with open(host_config_file, "w") as f:
        f.write(request.form['conf'])
    return redirect(url_for('index'))

@app.route('/save-listen-port', methods=['POST'])
def save_listen_port():
    with open(listen_port_file, "w") as f:
        f.write(request.form['port'])
    return redirect(url_for('index'))

@app.route('/save-site', methods=['POST'])
def save_site():
    name = request.form['name'].replace('.com','.conf')
    folder_site = "/usr/local/nginx/domain/%s" % request.form['name'].replace('.com','')

    #---------Create file /etc/nginx/sites-available
    with open(sample_site, "r") as s:
        sample = s.read()
    new_file = '%s/%s' % (sites_dir, name)

    with open(new_file, "w") as f:
        f.write(sample)

    # ----------Create file /var/www/..
    subprocess.call("mkdir " + folder_site, shell=True)
    with open(sample_index, "r") as s:
        sample_index_file = s.read()
    new_file_index = '%s/index.html' % folder_site

    with open(new_file_index, "w") as f:
        f.write(sample_index_file)

    return redirect(url_for('edit_site', name=name))

@app.route('/create-site')
def create_site():
    return render_template('create_site.html')

@app.route('/edit-site')
def edit_site():
    name = request.args.get('name','')
    with open('%s/%s' % (sites_dir, name)) as f:
        file_site = f.read()
    return render_template('edit_site.html', file_site=file_site, name=name)

@app.route('/update-site', methods=['POST'])
def update_site():
    name = request.args.get('name', '')
    with open('%s/%s' % (sites_dir, name), "w") as f:
        f.write(request.form['file'])
    return redirect(url_for('index'))

@app.route('/delete-site')
def delete_site():
    name = request.args.get('name')
    file = '%s/%s' % (sites_dir, name)
    subprocess.call("rm " + file, shell=True)
    return redirect(url_for('index'))

@app.route('/enable-site')
def enable_site():
    name = request.args.get('name', '')
    file = '%s/%s' % (sites_dir, name)
    link = '%s/%s' % (enabled_sites_dir, name)
    print("ln -s %s %s" % (file, link))
    subprocess.call("ln -s %s %s" % (file, link), shell=True)
    return redirect(url_for('index'))

@app.route('/disable-site')
def disable_site():
    name = request.args.get('name')
    file = '%s/%s' % (enabled_sites_dir,name)
    subprocess.call("rm -rf" + file, shell=True)
    return redirect(url_for('index'))

@app.route('/start')
def start_nginx():
    subprocess.call('service nginx start', shell=True)
    subprocess.call('sudo service nginx status | head -n 3 | tail -n 1 >> /usr/local/nginx/logs/nginx_status.log', shell=True)
    return render_template('status_nginx.html')

@app.route('/stop')
def stop_nginx():
    subprocess.call('service nginx stop', shell=True)
    subprocess.call('sudo service nginx status | head -n 3 | tail -n 1 >> /usr/local/nginx/logs/nginx_status.log', shell=True)
    return render_template('status_nginx.html')

@app.route('/reload')
def reload_nginx():
    subprocess.call('service nginx restart', shell=True)
    subprocess.call('sudo service nginx status | head -n 3 | tail -n 1 >> /usr/local/nginx/logs/nginx_status.log', shell=True)
    return render_template('status_nginx.html')


#-------------------------En Modsec
@app.route('/en_modsec')
def en_modsec():
    subprocess.call('sed -i "s/SecRuleEngine DetectionOnly/SecRuleEngine On/" /usr/local/nginx/conf/modsecurity.conf', shell=True)
    return render_template('status_nginx.html')

#-------------------------Dis Modsec
@app.route('/dis_modsec')
def dis_modsec():
    subprocess.call('sed -i "s/SecRuleEngine On/SecRuleEngine DetectionOnly/" /usr/local/nginx/conf/modsecurity.conf', shell=True)
    return render_template('status_nginx.html')
#------------------------Modsec Rules Lists
@app.route('/modsec_rules_lists')
def modsec_rules_lists():
    files = [fl for fl in listdir(modsec_rl_dir) if isfile(join(modsec_rl_dir, fl))]
    sites = []
    for file in files:
        sites.append({'file': file})
    return render_template('modsec_rules_lists.html',sites=sites)
#-------------------------ModSec Edit
@app.route('/edit-modsec')
def edit_modsec():
    name = request.args.get('name','')
    with open('%s/%s' % (modsec_rl_dir, name)) as f:
        file_site = f.read()
    return render_template('edit_modsec.html', file_site=file_site, name=name)

@app.route('/save-modsec', methods=['POST'])
def save_modsec():
    name = request.args.get('name','')
    with open('%s/%s' % (modsec_rl_dir, name), "w") as f:
        f.write(request.form['file'])
    return redirect(url_for('modsec_rules_lists'))

#----------------------Modsec Delete
@app.route('/delete-modsec')
def delete_modsec():
    name = request.args.get('name')
    file = '%s/%s' % (modsec_rl_dir, name)
    subprocess.call("rm " + file, shell=True)
    return redirect(url_for('modsec_rules_lists'))
#---------------------Create modsec
@app.route('/create-modsec')
def create_modsec():
    return render_template('create_modsec.html')

#-------------------update
@app.route('/update-modsec', methods=['POST'])
def update_modsec():
    name = request.form['name']

    with open(sample_modsec, "r") as s:
        sample = s.read()
    new_file = '%s/%s' % (modsec_rl_dir, name)

    with open(new_file, "w") as f:
        f.write(sample)
    return redirect(url_for('edit_modsec', name=name))

if __name__ == '__main__':
    app.run(host='127.0.0.1',port=5555,debug=True)
