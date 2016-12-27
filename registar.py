from flask import Flask, redirect, url_for, flash, render_template, request
from werkzeug.utils import secure_filename
import requests
import csv
import time
import os #library for uploading/manipulating files
import sys
# import wx

app = Flask(__name__)


first_names = []
last_names = []
companies = []
date = time.strftime("%d/%m/%Y")
today_signed = []


def preload_names(csv_file_name):
    with open(csv_file_name) as csvfile:
        readCSV = csv.DictReader(csvfile, delimiter=',')
        for row in readCSV:
            first_names.append(row['first_name'])
            last_names.append(row['last_name'])
            companies.append(row['company'])

preload_names('names.csv')


@app.route('/event', methods = ['GET'])
def render_main():
    with open('new_signups.csv','r') as new_signups:
        find_new_attendees = csv.DictReader(new_signups, delimiter=',')
        for row in find_new_attendees:
            if row['date'] == time.strftime("%d/%m/%Y"):
                for i in range(len(first_names)):
                    if "".join([row['first_name'],row['last_name']]) == "".join([first_names[i],last_names[i]]):
                        today_signed.append("n")
                    else:
                        today_signed.append("y")
                if "n" in today_signed:
                    pass
                else:
                    first_names.append(row['first_name'])
                    last_names.append(row['last_name'])
                    companies.append(row['company'])

    return render_template("main.html", event="Registar Launch", venue ="Level 39, 1 Canada Square", f_names=first_names, l_names=last_names, companies = companies, date = date)


@app.route('/signup', methods = ['POST'])
def new_signup():
    form_data = request.form
    with open('new_signups.csv','a') as new_signups:
        fieldnames = ['date','first_name','last_name','company','email','newsletter']
        writer = csv.DictWriter(new_signups, fieldnames=fieldnames)
        writer.writerow({'date' : (time.strftime("%d/%m/%Y")) ,'first_name' : form_data['first_name'], 'last_name' : form_data['last_name'], 'company' : form_data['company'], 'email' : form_data['email'], 'newsletter' : form_data['newsletter']})
        first_names.append(form_data['first_name'])
        last_names.append(form_data['last_name'])
        companies.append(form_data['company'])
#NEED NEW API KEY
        requests.post(
            "https://api.mailgun.net/v3/sandbox3e7227e67a8b424891fd4bc2e2126db0.mailgun.org/messages",
            auth=("api", "key-53ed1f7079a97617110a13a0f80b036e"),
            data={"from": "Mailgun Sandbox <postmaster@sandbox3e7227e67a8b424891fd4bc2e2126db0.mailgun.org>",
                  "to": form_data['email'] ,
                  "subject": "Welcome to Registar %s!" % (form_data['first_name']),
                  "html": "Hi %s Thank you for signing up for this event with registar. We hope you've had a great time and we're looking forward to seeing you soon at one of our events." % (form_data['first_name'])})

    return render_template("signup_screen.html")

# @app.route('/register', methods = ['POST'])
# def generate_register():
#     register_data = request.data
#     # print request.json
#     print register_data
#     import pdb; pdb.set_trace()
#     return "string"
#

@app.route('/')
def homepage():
    return render_template("homepage.html")

# @app.route('/register', methods = ["POST"])
# def export_register():
#     # import pdb
#     # pdb.set_trace()
#     print request.form
#     return request.form['attendees']

@app.route('/upload_completed')
def signin():
    return render_template("upload_completed.html")


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] == 'csv'


@app.route('/admin', methods = ['GET','POST'] )
# def check_password(parent=None, message='', default_value=''):
#     dialog_box = wx.TextEntryDialog(parent, message, defaultValue=default_value)
#     dialog_box.ShowModal()
#     password = dialog_box.GetValue()
#     dialog_box.Destroy()
#     return result



def upload():
    password = raw_input("Password")
    if password != "cfg":
        alert = "Your password isn't correct. You do not have permission to view this site."
        return render_template('homepage.html')
    else:
        if request.method == 'POST':
            if 'upload-file' not in request.files:
                flash('No file part')
                return redirect(request.url)
            file = request.files['upload-file']

            if file.filename == '':
                flash('No selected file')
                return redirect(request.url)
            print file
            print allowed_file(file.filename)
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                print filename
                file.save(os.path.join(app.root_path,'registers', secure_filename(request.form['event_name']))+'.csv')

                return redirect(url_for('signin'))
        else:
            return render_template('admin_view.html')


if __name__ == '__main__':
    app.run(debug=True)
