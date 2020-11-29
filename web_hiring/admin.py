from django.contrib import admin
from django import forms
from web_hiring.models import Post
from crewing.settings import (TITLE_CHOICES, FLEET_CHOICES,
                                VESSEL_CHOICES, ENGLISH_CHOICES)

# Register your models here.
class MyForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
       super(MyForm, self).__init__(*args, **kwargs)
       if self.instance.id:
            self.fields['title'] = forms.ChoiceField(
                choices=[(self.instance.field,)*2] + TITLE_CHOICES
                )
            self.fields['fleet'] = forms.ChoiceField(
                 choices=[(self.instance.field,)*2] + FLEET_CHOICES
                )
            self.fields['vessel'] = forms.ChoiceField(
                 choices=[(self.instance.field,)*2] + VESSEL_CHOICES
                )
            self.fields['english'] = forms.ChoiceField(
                 choices=[(self.instance.field,)*2] + ENGLISH_CHOICES
                )


class MyAdmin(admin.ModelAdmin):
    form = MyForm

class PostAdmin(admin.ModelAdmin):
    list_display = ('title','fleet','vessel','joining_date','salary')
    search_fields = ['title','text','salary']


admin.site.register(Post, PostAdmin)
admin.site.site_header = "Crewing"
admin.site.site_title = "Crewing"
admin.site.index_title = "Панель управления"
