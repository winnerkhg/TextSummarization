from django.shortcuts import render
from apps.Summarize import main
from django.shortcuts import redirect
from django.core.files.storage import FileSystemStorage
from apps import views
def index(request):
    return render(request,'apps/index.html')

def ketik(request):
    return render(request,'apps/unggah.html')

def unggah(request):
    return render(request, 'apps/unggah.html')

#process
def file(request):
    if request.method == 'POST':
        myfile = request.FILES['input_file']
        fs = FileSystemStorage()
        filename = fs.save(myfile.name, myfile)
        uploaded_file_url = fs.url(filename)
        summarize, clean, scores = main.main(myfile)
        contex = {'cal': summarize, 'clean': clean, 'scores':scores}
        return render(request, 'apps/unggah.html', contex)
    return render(request, 'apps/unggah.html')

def ketik(request):
    if request.method == 'POST':
        teks = request.POST['input_teks']
        fs = FileSystemStorage()
        f = open('input_teks.txt', 'w+')
        f.write(teks)
        filename = fs.save(f.name, f)
        summarize, clean, scores= main.ketik(filename)
        ori = teks
        #get all the process in main function
        contex = {'cal': summarize, 'clean': clean, 'scores': scores,'ori':ori}
        return render(request, 'apps/ketik.html', contex)
    return render(request, 'apps/ketik.html')