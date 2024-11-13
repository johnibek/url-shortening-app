from django import forms
from api.models import UrlModel

class UrlModelForm(forms.ModelForm):
    class Meta:
        model = UrlModel
        fields = ['url']
        widgets = {
            'url': forms.URLInput(attrs={'placeholder': "Enter the link here", 'autocomplete': 'off'})
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['url'].label = ""