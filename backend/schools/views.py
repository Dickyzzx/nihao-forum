from django.shortcuts import render

# Create your views here.
from django.http import JsonResponse
from .models import School

def school_list_view(request):
    schools = School.objects.all()
    data = [{"name": s.name, "slug": s.slug} for s in schools]
    return JsonResponse(data, safe=False)
