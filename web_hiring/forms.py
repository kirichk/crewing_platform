from django import forms
from django.forms import formset_factory
from web_hiring.models import Post
from crewing.settings import (TITLE_CHOICES, FLEET_CHOICES,
                                VESSEL_CHOICES, ENGLISH_CHOICES)

class PostForm(forms.ModelForm):
    class Meta():
        model = Post
        fields = ('title','fleet','vessel','salary','joining_date','english',
                'crewer','contact','voyage_duration','sailing_area','dwt',
                'years_constructed','crew','text')

        labels = {
            "title":"Должность",
            "fleet":"Флот",
            "vessel":"Тип судна",
            "salary":"Зарплата($)",
            "joining_date":"Дата посадки",
            "crewer":"Крюинг",
            "contact":"Контактная информация"
            "voyage_duration":"Длительность рейса",
            "sailing_area":"Регион работы",
            "dwt":"DWT",
            "years_constructed":"Год постройки судна",
            "crew":"Экипаж",
            "english":"Уровень английского",
            "text":"Дополнительная информация"
        }

        widgets = {
            'title':forms.Select(choices=TITLE_CHOICES,attrs={'class': 'form-control'}),
            'fleet':forms.Select(choices=FLEET_CHOICES,attrs={'class': 'form-control'}),
            'vessel':forms.Select(choices=VESSEL_CHOICES,attrs={'class': 'form-control'}),
            'english':forms.Select(choices=ENGLISH_CHOICES,attrs={'class': 'form-control'}),
            'voyage_duration':forms.TextInput(attrs={'placeholder':'Длительность рейса (не обязательно)'}),
            'sailing_area':forms.TextInput(attrs={'placeholder':'Регион работы (не обязательно)'}),
            'dwt':forms.TextInput(attrs={'placeholder':'DWT (не обязательно)'}),
            'years_constructed':forms.TextInput(attrs={'placeholder':'Год постройки судна (не обязательно)'}),
            'crew':forms.TextInput(attrs={'placeholder':'Экипаж (не обязательно)'}),
            'salary':forms.TextInput(attrs={'placeholder':'Введите месячную зарплату ($)'}),
            'joining_date':forms.DateInput(format=('%d/%m/%Y'), attrs={'class':'form-control', 'placeholder':'Выберите дату', 'type':'date'})
        }
