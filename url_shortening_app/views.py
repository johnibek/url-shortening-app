from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from django.http import HttpResponse, JsonResponse, Http404
from .forms import UrlModelForm
from api.models import UrlModel
from django.urls import reverse
from django import forms
import re
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.conf import settings


class GetShortenedURL(View):
    def get(self, request, short_code):
        domain_name = request.get_host()
        try:
            short_url = UrlModel.objects.get(short_code=short_code)
        except UrlModel.DoesNotExist:
            raise Http404("This short code does not exist")

        return render(request, 'shortened_url.html', {'short_url': short_url, 'domain_name': domain_name, 'debug': settings.DEBUG})

class RedirectShortUrl(View):
    def get(self, request, short_code):
        short_url = get_object_or_404(UrlModel, short_code=short_code)
        short_url.access_count += 1
        short_url.save(update_fields=['access_count'])
        return redirect(short_url.url)

class CreateShortUrl(View):
    def get(self, request):
        form = UrlModelForm()
        return render(request, 'index.html', {'form': form})

    def post(self, request):
        form = UrlModelForm(data=request.POST)
        if form.is_valid():
            url_instance = form.save(commit=False)
            if UrlModel.objects.filter(url=url_instance.url).exists():
                existent_url_obj = UrlModel.objects.get(url=url_instance.url)
                return redirect(reverse('url:get_short_url', kwargs={'short_code': existent_url_obj.short_code}))

            url_instance.save()
            return redirect(reverse('url:get_short_url', kwargs={'short_code': url_instance.short_code}))

        return render(request, 'index.html', {'form': form})


class UrlAccessCount(View):
    def get(self, request, short_code):
        domain_name = request.get_host()
        url_obj = get_object_or_404(UrlModel, short_code=short_code)
        return render(request, 'count_clicks.html', {'url_obj': url_obj, 'domain_name': domain_name})


class TrackShortUrl(View):
    def get(self, request):
        domain_name = request.get_host()
        form = UrlModelForm()
        form.fields['url'].widget = forms.URLInput(attrs={'placeholder': 'Enter here your shortened URL'})
        return render(request, 'track_url.html', {'form': form, 'domain_name': domain_name, 'debug': settings.DEBUG})

    def post(self, request):
        form = UrlModelForm(data=request.POST)
        if not form.is_valid():
            raise ValidationError('Invalid Url')
        short_url = form.cleaned_data['url']  # http://127.0.0.1:8000/abc123
        domain_name = request.get_host()
        if settings.DEBUG:
            match = re.search(rf"^http://{re.escape(domain_name)}/(.+)$", short_url)
        else:
            match = re.search(rf"^https://{re.escape(domain_name)}/(.+)$", short_url)
        if not match:
            messages.error(request, "The input url does not match the pattern given in an example.")
            return render(request, 'track_url.html', {'form': form})
        short_code = match.group(1)
        if not UrlModel.objects.filter(short_code=short_code).exists():
            raise Http404("There is no shortened url found with this short code.")
        return redirect(reverse('url:url_access_count', kwargs={'short_code': short_code}))



class UnshortenUrl(View):
    def get(self, request):
        domain_name = request.get_host
        form = UrlModelForm()
        form.fields['url'].widget = forms.URLInput(attrs={'placeholder': 'Enter the shortened url'})
        return render(request, 'unshorten_url.html', {'form': form, 'domain_name': domain_name, 'debug': settings.DEBUG})
    
    def post(self, request):
        form = UrlModelForm(data=request.POST)
        
        if not form.is_valid():
            return ValidationError("Invalid Url")
            
        domain_name = request.get_host()
        short_url = form.cleaned_data['url']
        if settings.DEBUG:
            match = re.search(rf"^http://{re.escape(domain_name)}/(.+)$", short_url)
        else:
            match = re.search(rf"^https://{re.escape(domain_name)}/(.+)$", short_url)

        if not match:
            messages.error(request, "The input url does not match the pattern given in an example.")
            return render(request, 'unshorten_url.html', {'form': form})  # I rendered the html file to keep input url as is.

        short_code = match.group(1)
        if not UrlModel.objects.filter(short_code=short_code).exists():
            raise Http404("There is no shortened url found with this short code.")
        
        url_obj = UrlModel.objects.get(short_code=short_code)
        return render(request, 'result_unshorten_url.html', {'url_obj': url_obj, 'domain_name': domain_name})
    
            
        
            
        