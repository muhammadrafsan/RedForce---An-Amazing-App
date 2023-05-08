from distutils.command import build
from importlib.metadata import files
import io
from urllib import response
from django.shortcuts import render
from django.http import HttpResponse
from googleapiclient.http import MediaIoBaseDownload
import sys
import cv2
from django.template import RequestContext
from .models import UserInfo, TestUser
import face_recognition
import base64
import os
from django.shortcuts import redirect
from django.contrib.auth import logout as auth_logout
from django.shortcuts import render
from rforce import models
import requests
import json
import google.auth
from google.oauth2.credentials import Credentials
from apiclient import errors
from django.contrib import messages
import os.path
from allauth.socialaccount.models import SocialAccount, SocialApp


import docx2txt
from allauth.socialaccount.models import SocialApp
from allauth.socialaccount.models import SocialAccount, SocialApp
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from googleapiclient.http import MediaFileUpload
from allauth.socialaccount.models import SocialApp
from googleapiclient.errors import HttpError
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.http import MediaFileUpload
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from django.core.files.storage import FileSystemStorage
from cryptography.fernet import Fernet

count = 0
stop = 0
anti="pika"
face_flag=0


from allauth.socialaccount.models import SocialAccount, SocialApp
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from googleapiclient.http import MediaFileUpload
from allauth.socialaccount.models import SocialToken, SocialApp
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseDownload
import io
import os
import docx2txt

# Create your views here.
def login(request):
    auth_logout(request)
    return render(request,'index.html')

def home(request):
    folder_flag=0
    app_google = SocialApp.objects.get(provider="google")
    account = SocialAccount.objects.get(user=request.user)
    user_tokens = account.socialtoken_set.first()
    creds = Credentials(
    token=user_tokens.token,
    refresh_token=user_tokens.token_secret,
    client_id=app_google.client_id,
    client_secret=app_google.secret,
                    )
    service = build('drive', 'v3', credentials=creds)
    page_token = None
    response = service.files().list(q="mimeType='application/vnd.google-apps.folder'",
                                            spaces='drive',
                                            fields='nextPageToken, '
                                                   'files(id, name)',
                                            pageToken=page_token).execute()
    for file in response.get('files', []):
        print(type({file.get("name")}))
        print(str({file.get("name")}))    
        if(str({file.get("name")})=="{'Redforce'}"):
            folder_flag=1
            break
    if(folder_flag==0):
          
        folder = 'Redforce'
                
        file_metadata = {
                'name': folder,
                'mimeType': 'application/vnd.google-apps.folder'
            }
                
        service.files().create(body=file_metadata).execute()
    return render(request,'home.html')

def upload(request):
    try:
        global face_flag
        print("face-flag in upload",face_flag)
        if face_flag!=1:
            face_flag=1
            return redirect(f"/faceRecog/")
        
        if request.method=="POST":
            face_flag=0
            app_google = SocialApp.objects.get(provider="google")
            account = SocialAccount.objects.get(user=request.user)
            user_tokens = account.socialtoken_set.first()
            creds = Credentials(
            token=user_tokens.token,
            refresh_token=user_tokens.token_secret,
            client_id=app_google.client_id,
            client_secret=app_google.secret,
                            )
            service = build('drive', 'v3', credentials=creds)
            
            results = service.files().list(
                pageSize=10, fields="nextPageToken, files(id, name)").execute()
            items = results.get('files', [])
            folder_id=""
            for item in items:
                if item['name']=="Redforce":
                    folder_id=item['id']
                    
            fname=request.FILES['myfile']
            fs = FileSystemStorage()
            filename = fs.save(fname.name, fname)
            uploaded_file_path = fs.path(filename)
            tname= fname.name
            Object=UserInfo.objects.get(user=request.user)
            ftool = Fernet(Object.key)
            
            data=''
            with open(uploaded_file_path,'rb') as reader:
                data=reader.read()
            print(data)
            
            encryptedData=ftool.encrypt(data)
            
            with open(uploaded_file_path,'wb') as writer:
                writer.write(encryptedData)
                writer.close()
            file_metadata={
                'name': tname,
                'parents' : [folder_id],
            }
            mime_Type='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
            media = MediaFileUpload(uploaded_file_path,mimetype=mime_Type)
            service.files().create(
                body=file_metadata,
                media_body=media,
            ).execute() 
            return redirect(f"/home/")  
        return render(request,'upload.html')
    except:
        face_flag=0
        messages.info(request, 'Cannot Upload Empty File')
        return render(request,'home.html')



def setUpProfile(request):
    global stop
    if (stop==1):
        return redirect(f"/faceRecog/")
    user = request.user
    print(user)
    alluser =  models.UserInfo.objects.filter()
    print(alluser)
    list = []
    list.append(alluser)
    
    for i in alluser:
        if(user==i.user):
            return redirect(f"/faceRecog/")        
        
    if request.method=="POST":
        user=UserInfo.objects.create(
        img=request.POST.get("img_data"),
        user = request.user,
        key = Fernet.generate_key().decode()
        
        )
        stop = 1
        return redirect(f"/faceRecog/")
      
    return render(request,'setUpProfile.html')

def faceRecog(request):
    if request.method=="POST":
        test=TestUser.objects.create(
        img=request.POST.get("img_data"),
        user = request.user
        )
        global anti 
        anti= request.POST.get("img_data2")
        print(anti)
        global stop
        stop=0   
    
        return redirect(f"/check/")
    return render(request,'faceRecog.html')


def check(request):
    #temp = flag
    global face_flag
    db = UserInfo.objects.get(user=request.user)
    db_img=db.img
    dbu=db.user
    
    
    db1 = TestUser.objects.get(user=request.user)
    db_img1=db1.img
    dbu1=db1.user
    
    
    with open(f"{dbu}.jpg", "wb") as fh:
        fh.write(base64.b64decode(db_img))
    
    try:       
        known_image = face_recognition.load_image_file(f"{dbu}.jpg")
        known_encoding = face_recognition.face_encodings(known_image)[0]
         
        # #Anti-spoofing starts here

        url = "https://liveness-detection1.p.rapidapi.com/api/v1/liveness-detection"

        payload = {
            "imageUrl":anti,
            "isface": True
        }
        headers = {
            "content-type": "application/json",
            "X-RapidAPI-Key": "3edf7b5a71mshb18cb7601af0b1bp15d53ajsnbf3ed97aac62",
            "X-RapidAPI-Host": "liveness-detection1.p.rapidapi.com"
        }

        response = requests.request("POST", url, json=payload, headers=headers)
        data = response.json()
        print(type(data))
        keys = data.keys()
        print(keys)
        print(type(data['predict']))

        print(response.text)
        #Anti-Spoofing ends here
        with open(f"{dbu1}.jpg", "wb") as fk:
            fk.write(base64.b64decode(db_img1))
        unknown_image = face_recognition.load_image_file(f"{dbu1}.jpg")

        
        unknown_encoding = face_recognition.face_encodings(unknown_image)[0]
        
        results = face_recognition.compare_faces([known_encoding], unknown_encoding,tolerance=0.45)
        print(results)

        f = open(f"{dbu}.jpg", 'w')
        f.close()
        os.remove(f.name)
        
        f1 = open(f"{dbu1}.jpg", 'w')
        f1.close()
        os.remove(f1.name)

        #removing test-user
        instance =TestUser.objects.get(user=request.user)
        instance.delete()
        stresult = str(results)
        global count
        
        if (stresult == "[True]" and data['predict']=="real"):
            if face_flag==0:
                return redirect(f"/home/")
            elif face_flag==1:
                return redirect(f"/upload/")
            elif face_flag==2:
                return redirect(f"/viewfile/")         
        else:
            count=count+1
            print(count)
            if(count==3):
                count = 0
                return redirect(f"/logout/")
            else:
                return redirect(f"/faceRecog/")
    except:
        #global count2
        count=count+1
        
        print("An exception occurred")   
        f1 = open(f"{dbu1}.jpg", 'w')
        f1.close()
        os.remove(f1.name)
        instance =TestUser.objects.get(user=request.user)
        instance.delete()
        if(count==3):
            count=0
            return redirect(f"/logout/")
        else:
            return redirect(f"/faceRecog/")    


def logout(request):
    """Logs out user"""
    global face_flag
    face_flag=0
    auth_logout(request)
    #return render('index.html', {}, RequestContext(request))   
    return render(request,'index.html')    
    


def uploadfile(request):
    if request.method=="POST":
        filename = request.POST.get("upfile")
        print(filename)
        app_google = SocialApp.objects.get(provider="google")
        account = SocialAccount.objects.get(user=request.user)
        user_tokens = account.socialtoken_set.first()
        creds = Credentials(
        token=user_tokens.token,
        refresh_token=user_tokens.token_secret,
        client_id=app_google.client_id,
        client_secret=app_google.secret,
                        )
        service = build('drive', 'v3', credentials=creds)

        folder_id='1g-AB1VuLZiR2Y0bTvSWLLgGvCGyoQ_1R'
        file_names=[filename]
        mime_types=['image/jpeg']

        for file_name,mime_type in zip(file_names,mime_types):
            file_metadata={
                'name':file_name,
                'parents':[folder_id]
            }
        media=MediaFileUpload('{0}'.format(file_name), mimetype=mime_type)
        service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id'

        ).execute()
    else:
        print("Else")
    
    return render(request,'home.html')


def viewfile(request):
    global face_flag
    print("face-flag in viewfile",face_flag)
    if face_flag!=2:
        face_flag=2
        print("face-flag in viewfile2",face_flag)
        return redirect(f"/faceRecog/")
    else:
        face_flag=0
        app_google = SocialApp.objects.get(provider="google")
        account = SocialAccount.objects.get(user=request.user)
        user_tokens = account.socialtoken_set.first()
        
        creds = Credentials(
        token=user_tokens.token,
        refresh_token=user_tokens.token_secret,
        client_id=app_google.client_id,
        client_secret=app_google.secret,
        )
        try:
            service = build('drive', 'v3', credentials=creds)
            results = service.files().list(
                pageSize=10, fields="nextPageToken, files(id, name)").execute()
        
            
        
            results = service.files().list(
                pageSize=10, fields="nextPageToken, files(id, name)").execute()
            items = results.get('files', [])
            if items:
                folder_id=""
                for item in items:
                    if item['name']=="Redforce":
                        folder_id=item['id']
                page_token = None
                response = service.files().list(q=f"parents in '{folder_id}'",
                                                    spaces='drive',
                                                    fields='nextPageToken, files(id, name)',
                                                    pageToken=page_token).execute()
                flist= response.get('files', [])
                if flist:
                    folder_name=[]
                    folder_ids=[]
                    for item in flist:
                            folder_name.append(item['name'])
                            folder_ids.append(item['id'])
                            page_token = response.get('nextPageToken', None) 
                            
                    mylist = zip(folder_name, folder_ids)
                    context ={
                        "object_list": mylist,
                        }   
                    return render(request, "viewfiles.html", context)       
        except HttpError as error:
            print(f'An error occurred: {error}')
        
        return render(request, "viewfiles.html")

def openfile(request, id):
    if request.method == 'GET':
        app_google = SocialApp.objects.get(provider="google")
        account = SocialAccount.objects.get(user=request.user)
        user_tokens = account.socialtoken_set.first()
    
        creds = Credentials(
        token=user_tokens.token,
        refresh_token=user_tokens.token_secret,
        client_id=app_google.client_id,
        client_secret=app_google.secret,
        )
        service = build('drive', 'v3', credentials=creds) 
        # file_id = "1570R_MMQksne3GOppaW4IwsRkZXThqdJ"
        file_id = id
        # pylint: disable=maybe-no-member
        request1 = service.files().get_media(fileId=file_id)
        dfile = io.BytesIO()
        
        downloader = MediaIoBaseDownload(dfile, request1)
        done = False
        while done is False:
            
            status, done = downloader.next_chunk()
            print(F'Download {int(status.progress() * 100)}.')
        fs = FileSystemStorage()
        filename = fs.save("test.docx", dfile)
        
        downloaded_file_path = fs.path(filename)
        Object=UserInfo.objects.get(user=account.user_id)
        ftool = Fernet(Object.key)
        
        with open(downloaded_file_path,'rb') as reader1:
            data1=reader1.read()
        
        decryptedData=ftool.decrypt(data1)
        
        with open(downloaded_file_path,'wb') as writer1:
            writer1.write(decryptedData)
            
        my_text = docx2txt.process(downloaded_file_path)
        
        text=my_text.splitlines()
        context ={
            "object_list": text,
            }  
        
        if os.path.exists(downloaded_file_path):
            os.remove(downloaded_file_path)
        
        return render(request, "fileviewer.html", context) 
        
def deletefile(request, id):
    """Permanently delete a file, skipping the trash.

    Args:
        service: Drive API service instance.
        file_id: ID of the file to delete.
    """
    try:
        app_google = SocialApp.objects.get(provider="google")
        account = SocialAccount.objects.get(user=request.user)
        user_tokens = account.socialtoken_set.first()
        creds = Credentials(
        token=user_tokens.token,
        refresh_token=user_tokens.token_secret,
        client_id=app_google.client_id,
        client_secret=app_google.secret,
        )
        service = build('drive', 'v3', credentials=creds)
    
        service.files().delete(fileId=id).execute()
        
    except errors.HttpError:
        print('An error occurred')

    return render(request, "home.html") 
