#!/usr/bin/python

import sys, os, commands
from docker import Client

def system_command(clicommand, type):
     try:
         status, output = commands.getstatusoutput(clicommand)
     except TypeError:
         error_message = "Problem with command: %s" % (clicommand) 
         print >>sys.stderr, error_message
         send_email(os.environ['EMAIL_TO'], os.environ['EMAIL_FROM'], "PROBLEM: docker backup of '" + sys.argv[1] + "' container", error_message)
         if type == 'output':
             return ""
         else:
             return status
  
     if status == 0:
         if type == 'output':
             return output
         else:
             return status
     else:
         error_message = "Problem with command: %s\nError: %s" % (clicommand, output)
         print >>sys.stderr, error_message
         send_email(os.environ['EMAIL_TO'], os.environ['EMAIL_FROM'], "PROBLEM: docker backup of '" + sys.argv[1] + "' container", error_message)
         if type == 'output':
             return ""
         else:
             return status

def send_email(to, efrom, subject, message):
    if to == "":
       return
    import smtplib
    from email.mime.text import MIMEText
    print "Email: %s - %s" % (subject, message)
    msg = MIMEText(message)
    msg['Subject'] = subject
    msg['From'] = efrom
    msg['To'] = to

    try:
        s = smtplib.SMTP(os.environ['SMTP_SERVER'])
        s.sendmail(efrom, [efrom], msg.as_string())
        s.quit()
    except Exception as e:
        print >>sys.stderr, 'ERROR: Problem with sending of email' + str(e.message)

sprefix = system_command('date +"' + os.environ['PREFIX'] + '"', 'output')
ssuffix = system_command('date +"' + os.environ['SUFFIX'] + '"', 'output')

c = Client(base_url='unix://docker.sock', version='1.18')
try:
    volumes = c.inspect_container(sys.argv[1])['Volumes']
except Exception as e:
    error_message = "Docker API error: " + str(e.message)
    print >>sys.stderr, error_message
    send_email(os.environ['EMAIL_TO'], os.environ['EMAIL_FROM'], "PROBLEM: docker backup of '" + sys.argv[1] + "' container", error_message)
    sys.exit(1)
   
for volume in volumes:

    # host volume workaround -v /:/host
    if volumes[volume] in os.environ['EXCLUDE'].split(','):
        print "Volume " + volumes[volume] + " is excluded, skipping."
        continue
    if os.path.exists(volumes[volume]) != True:
        if os.path.exists("/host" + volumes[volume]) != True:
            error_message = "Path: " + volumes[volume] + " doesn't exist in container, I recommend attach host FS - v /:/host or exclude FS"
            print >>sys.stderr, error_message
            send_email(os.environ['EMAIL_TO'], os.environ['EMAIL_FROM'], "PROBLEM: docker backup of '" + sys.argv[1] + "' container", error_message)
        else:
            volumes[volume] = "/host" + volumes[volume]

    tar_path = os.environ['BACKUPS'] + sprefix + \
                   sys.argv[1] + '_' + volume.replace('/', '-')[1:] + ssuffix + ".tar.gz"
    tar_command = "tar -zvcf " + tar_path + " " + volumes[volume]

    print "BACKUP: %s - volume: %s" % (sys.argv[1], volumes[volume])
    if system_command(tar_command, 'status') != 0:
        continue;

    print "UPLOAD: %s - file: %s" % (sys.argv[1], tar_path)

    system_command('s3cmd --access_key="' + os.environ['ACCESS_KEY'] + '" --secret_key="' + os.environ['SECRET_KEY'] + \
          '" -c /dev/null ' + os.environ['S3CMD_OPTS'] + ' put "' + tar_path + '" ' + \
          os.environ['BUCKET'], 'status')
      
    system_command('rm "'+ tar_path + '"', 'status')
