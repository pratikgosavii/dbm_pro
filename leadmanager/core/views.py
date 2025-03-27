from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect

@login_required
def home(request):
    """Redirect to dashboard"""
    return HttpResponseRedirect('/dashboard/')
