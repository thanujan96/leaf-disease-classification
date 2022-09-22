from pickle import NONE
import threading
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.conf import settings
from django.core.mail import EmailMessage
from django.http import JsonResponse
import os
import subprocess

from . import models
from project.settings import BASE_DIR
import json

# Create your views here.
def index(request):
    path = settings.MEDIA_ROOT
    img_list = os.listdir(path + '/final')
    context = {'images' : img_list}
    return render(request, "index.html", context)
    
# index.html file and the upload form
def dashboard(request):
    if request.POST and request.FILES:
        try:
            file = request.FILES['file']
            email = str(request.POST.get('email'))
            data = models.PeptideStructureData(email=email, file=file, status="SUBMITTED")
            data.save()
            dataset_object = models.PeptideStructureData.objects.get(id=data.id)
            runback = ThreadingExample()
            thread = threading.Thread(target=runback.run, args=(dataset_object, "file"))
            thread.daemon = True
            thread.start()
            uploadstatus = True
            jobID = data.id
            return render(request, "index.html", {'uploadstatus': uploadstatus, 'jobID': jobID})
        except Exception as e:
            print(e)
            uploadstatus = False
            return render(request, "index.html", {'uploadstatus': uploadstatus, })
    else:
        return render(request, "index.html")


# job status check using ajax
def checkStatus(request):
    if request.POST:
        jobid = request.POST['jobid']
        try:
            database_object = models.PeptideStructureData.objects.get(id=jobid)
            print(database_object.status)
            if(database_object.status == "COMPLETED"):
                try:
                    with open("media/final/" + str(jobid) + "/result.json", 'r') as f:
                        print("hi")

                        data = json.load(f)
                        response_data = {
                        'response': 'success',
                        'result_id': jobid,
                        'result_status': database_object.status,
                        'result_log': json.dumps(data)}
                        print(data)
                        # print("media/final/" + str(jobid) + "/result.json")
                        return  JsonResponse(response_data, status=201, safe=False)
                except FileNotFoundError:
                    print("file not found")
                    pass
            elif(database_object.status == "FAILED"):
                fp = open("media/final/" + str(jobid) + "/log.txt", 'r')
                text = ""
                for i in fp:
                    text = text + "<br/>" + str(i)
                response_data = {
                    'response': 'fail',
                    'result_id': jobid,
                    'result_status': database_object.status,
                    'result_log': text}
                return JsonResponse(response_data, status=201,safe=False)
            else:
                fp = open("media/final/" + str(jobid) + "/log.txt", 'r')
                text = ""
                for i in fp:
                    text = text + "<br/>" + str(i)
                response_data = {
                    'response': 'wait',
                    'result_id': jobid,
                    'result_status': database_object.status,
                    'result_log': text}
                return JsonResponse(response_data, status=201,safe=False)

            
        except Exception as e:
            print("some error " + str(e))
            return HttpResponse("error")
    else:
        return redirect('/')


# ajax call to send message to admin from frontend
def contact(request):
    if request.POST:
        cname = str(request.POST.get('cname'))
        cemail = str(request.POST.get('cemail'))
        csubject = str(request.POST.get('csubject'))
        cmessage = str(request.POST.get('cmessage'))
        # send email to admin and the customer
        try:
            from_email = settings.EMAIL_HOST_USER
            to_list = [str(cemail),]
            sendemail = EmailMessage("Message received!!!", "Hello " + cname + ",\n\nThank you for contacting us. "
                                                                               "We will get back to you soon."
                                                                               "\n\nYour have provided,\nName : "
                                     + cname + "\nSubject : " + csubject +
                                     "\nMessage : " + cmessage +
                                                                               "\n\nRegards,"
                                                                               "\nAdmin"
                                     , str(from_email), to_list)
            sendemail.send()
        except Exception as e:
            print("Error in contact form." + str(e))
            return HttpResponse("error")
        return HttpResponse("success")
    else:
        return redirect("/")


# thread for prediction
class ThreadingExample(object,):
    def __init__(self, interval=1):
        self.interval = interval

    def run(self, database_object, type):
        try:
            working_dir = str(BASE_DIR) + "/media/modelData/"
            # get the info from database
            result_path = str(BASE_DIR) + "/media/final/" + str(database_object.id) + "/"
            # create drectory for result file
            if not os.path.exists(result_path):
                os.makedirs(result_path)
            email = database_object.email
            models.PeptideStructureData.objects.filter(id=database_object.id).update(status='THREAD STARTED')
            from_email = settings.EMAIL_HOST_USER
            to_list = [email, ]
            send_email_started = EmailMessage("ML Tool - Job " + str(database_object.id) + " started!!!", "Hello Sir/Ma'am,\n\nWe have received "
                                                                               "your file "
                                                                               "and we are processing it.\n"
                                                                               "Have patience.\n\nJob ID : " + str(database_object.id) +
                                                                               "\n\nRegards,\nAdmin\nTLtool",
                                      str(from_email), to_list)
            send_email_started.send()

            
            
            models.PeptideStructureData.objects.filter(id=database_object.id).update(status='UNDER PROCESS')
            command = []
            # run the scripts
            if type == "file":
                print("processing")
                file_path = str(BASE_DIR) + "/" + str(database_object.file)
                print(file_path)
                command = ["python", working_dir + "mainFile.py", working_dir, file_path, result_path]
            # else:
            #     sequence = str(database_object.sequence)
            #     command = ["python", working_dir + "mainSequence.py", working_dir, sequence, result_path]
            status = 0
            try:
                print(subprocess.call(command))
                models.PeptideStructureData.objects.filter(id=database_object.id).update(status='COMPLETED')
            except OSError:
                status = 1
                print("Error in command")
                models.PeptideStructureData.objects.filter(id=database_object.id).update(status='FAILED')
            # mail the result
            print(str(status))
            # try:
            result_f = open(result_path + "result.json", 'r')
            result_json = json.load(result_f)
            result = json.dumps(result_json)

                # serialized_data
            # except e:
            #     result = e
            if int(status) == 0:
                # if completed successfully
                from_email = settings.EMAIL_HOST_USER
                to_list = [email, ]
                send_email = EmailMessage("ML Tool - Process Completed!!!", "Hello Sir/Ma'am,\n\nCheck the attached "
                                                                             "files.\n\nRegards,\nAdmin\nTLtool",
                                          str(from_email), to_list)
                fp = open(result_path + "log.txt", 'r')
                send_email.attach('log.txt', fp.read(), 'text/plain')
                fp.close()
                fp = open(result_path + "result.json", 'r')
                if(fp!=NONE):
                    data = json.load(fp)
                    send_email.attach('result.json', json.dumps(data), 'application/json')
                else: 
                    send_email.attach('result.txt', "Files are not generated. There could be some erros try again", 'text/plain')
                fp.close()
                send_email.send()
            else:
                # if anything failed
                from_email = settings.EMAIL_HOST_USER
                to_list = [email, ]
                send_email = EmailMessage("ML Tool - Some error!!!", "Hello Sir/Ma'am,\n\nCheck the attached "
                                                                      "file.\n\n"
                                                                      "You can contact us for more details.\n\n"
                                                                      "Regards,\nAdmin\nTLtool",
                                          str(from_email), to_list)
                fp = open(result_path + "log.txt", 'r')
                send_email.attach('log.txt', fp.read(), 'text/plain')
                fp.close()
                send_email.send()
            
            return JsonResponse(result, status=201, safe=False)
        except Exception as e:
            print(e)
            return JsonResponse(e, status=201,  safe=False)
            # from_email = settings.EMAIL_HOST_USER
            # to_list = [email, ]
            # send_email = EmailMessage("ML Tool - Some error!!!", "Hello Sir/Ma'am,\n\n"
            #                                                       "We apologize for the inconvenience.\n"
            #                                                       "You can submit it again.\n\n"
            #                                                       "Regards,\nAdmin\nTLtool",
            #                           str(from_email), to_list)
            # send_email.send()


