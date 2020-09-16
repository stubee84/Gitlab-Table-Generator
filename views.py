from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from . import csv_table_generator as ctg
from .models import execution
import json, io, django.http.request as request

def home(request: request.HttpRequest):
    context = {}
    return render(request, 'home.html', context)

@csrf_exempt
@require_POST
def generate_table(request: request.HttpRequest):
    try:
        limit = request.POST['limit']
        t = request.POST['type']
    except KeyError:
        return HttpResponse(json.dumps({"failure":"could not generate table"}), content_type="application/json")

    limit = [int(i) for i in limit.split(',')]

    if t == "string":
        csv_data = request.POST['csv']
        result = ctg.csv_to_gitlab_table(string=csv_data,limit=limit)
    elif t == "file":
        csv_data = request.FILES['csv']

        if csv_data.content_type != "text/csv":
            return HttpResponse(json.dumps({"failure":"incorrect file type. must be CSV"}), content_type="application/json")

        if csv_data.size <= 1024:
            csv_data = convert_bytes_string(file_io=csv_data.read())
            result = ctg.csv_to_gitlab_table(file=io.StringIO(csv_data),limit=limit)
        else:
            result = get_file_chunk(file=csv_data, limit=limit)
    elif t == "url":
        url = request.POST.get('url')
        table_name = request.POST.get('table_name')

        result = ctg.csv_to_gitlab_table(url_info=[url,table_name], limit=limit)
    elif t == "query":
        query = request.POST['query']
        conn_string = request.POST['connection']

        result = ctg.csv_to_gitlab_table(query=query, conn_string=conn_string, limit=limit)

        try:
            return HttpResponse(json.dumps({"failure":result.output['failure']}), content_type="application/json")
        except TypeError:
            pass

    save_data(input=result.input, output=result.output, data_type=t, limit=','.join([str(l) for l in limit]))
    
    output = {"success":result.output}
    return HttpResponse(content=json.dumps(output), content_type="application/json")

def convert_bytes_string(file_io: bytes) -> str:
    s = str(file_io,'utf-8')
    return s

def get_file_chunk(file: request.uploadhandler.InMemoryUploadedFile, limit: list = []) -> ctg.csv_to_gitlab_table:
    for chunk in file.chunks():
        chunk = convert_bytes_string(file_io=chunk)
        result = ctg.csv_to_gitlab_table(file=io.StringIO(chunk), limit=limit)
    return result

def save_data(input: str, output: str, data_type: str, limit: str):
    exec = execution()
    exec.input_data = input
    exec.output_data = output
    exec.data_type = data_type
    exec.limit = limit
    exec.save()