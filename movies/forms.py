from django import forms
from .models import Category, TagPost, Person, Movie
from django.core.validators import MinLengthValidator, MaxLengthValidator
from django.core.exceptions import ValidationError
from django.utils.deconstruct import deconstructible

import re


# @deconstructible
# class RussianValidator:
#     ALLOWED_CHARS_PATTERN = r'^[а-яА-ЯёЁ0-9\s\-\'\":,IVXLCDM]+$'
#     code = 'russian'
#
#     def __init__(self, message=None):
#         self.message = message if message else "Название должно содержать только русские буквы и допустимые символы."
#
#     def __call__(self, value):
#         if not re.match(self.ALLOWED_CHARS_PATTERN, value):
#             raise ValidationError(self.message, code=self.code, params={"value": value})
#
#
# class AddPostForm(forms.Form):
#
#     title = forms.CharField(
#         max_length=255,
#         label="Название",
#         widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Введите название'}),
#         error_messages={
#             'required': 'Пожалуйста, введите название.',
#             'max_length': 'Название не должно превышать 255 символов.',
#         },
#         validators=[MinLengthValidator(3, message='Название должно содержать не менее 3 символов.'),
#                     RussianValidator()]
#     )
#
#     title_en = forms.CharField(
#         max_length=255,
#         required=False,
#         label="Английское название",
#         widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Введите название на английском'})
#     )
#
#     slug = forms.SlugField(
#         max_length=255,
#         required=False,
#         label="URL",
#         widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Введите URL'}),
#         validators=[
#             MinLengthValidator(3, message="URL должен содержать не менее 3 символов."),
#             MaxLengthValidator(255, message="URL не должен превышать 255 символов.")
#         ]
#     )
#
#     content = forms.CharField(
#         widget=forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Описание фильма'}),
#         required=False,
#         label="Описание"
#     )
#     release_date = forms.DateField(
#         required=False,
#         label="Дата выхода",
#         widget=forms.DateInput(attrs={'class': 'form-control', 'placeholder': 'Дата выхода', 'type': 'date'})
#     )
#
#     budget = forms.DecimalField(
#         max_digits=12,
#         decimal_places=2,
#         required=False,
#         label="Бюджет",
#         min_value=0,
#         widget=forms.NumberInput(attrs={
#             'class': 'form-control',
#             'placeholder': 'Введите бюджет'
#         }),
#         error_messages={
#             'invalid': 'Введите действительное число.',
#             'min_value': 'Бюджет не может быть отрицательным.',
#         }
#     )
#
#     rating = forms.FloatField(
#         required=False,
#         label="Рейтинг",
#         widget=forms.NumberInput(attrs={
#             'class': 'form-control',
#             'placeholder': 'Рейтинг от 0 до 10',
#             'min': 0,
#             'max': 10
#         }),
#         error_messages={
#             'invalid': 'Введите действительное число.',
#             'min_value': 'Рейтинг не может быть меньше 0.',
#             'max_value': 'Рейтинг не может быть больше 10.',
#         }
#     )
#
#     cat = forms.ModelChoiceField(
#         queryset=Category.objects.all(),
#         label="Категория",
#         empty_label="Категория не выбрана",
#         widget=forms.Select(attrs={'class': 'form-control'})
#     )
#
#     tags = forms.ModelMultipleChoiceField(
#         queryset=TagPost.objects.all(),
#         label="Жанры",
#         widget=forms.SelectMultiple(attrs={'class': 'form-control'})
#     )
#
#     people_roles = forms.ModelMultipleChoiceField(
#         queryset=Person.objects.all(),
#         label="Режиссер",
#         required=False,
#         widget=forms.SelectMultiple(attrs={'class': 'form-control'})
#     )
#
#     is_published = forms.BooleanField(
#         required=False,
#         label="Опубликовать",
#         initial=True,
#         widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
#     )
#
#     def clean_title_en(self):
#         title_en = self.cleaned_data.get('title_en')
#         if title_en and not re.match(r'^[a-zA-Z0-9\s\-\'\":,]+$', title_en):
#             raise forms.ValidationError("Название должно содержать только английские буквы и допустимые символы.")
#         return title_en

class AddPostForm(forms.ModelForm):
    cat = forms.ModelChoiceField(queryset=Category.objects.all(), label="Категория",
                                 empty_label="Категория не выбрана")
    tags = forms.ModelMultipleChoiceField(queryset=TagPost.objects.all(), label="Жанры")
    people_roles = forms.ModelMultipleChoiceField(queryset=Person.objects.all(), label="Режиссер", required=False)

    class Meta:
        model = Movie
        fields = ['title', 'title_en', 'slug', 'cat', 'release_date', 'content',
                  'budget', 'rating', 'tags', 'people_roles', 'poster', 'is_published']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Введите название'}),
            'title_en': forms.TextInput(attrs={'class': 'form-control',
                                               'placeholder': 'Введите название на английском'}),
            'slug': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Введите URL'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Описание фильма'}),
            'release_date': forms.DateInput(format='%Y-%m-%d', attrs={'class': 'form-control',
                                                                      'placeholder': 'Дата выхода', 'type': 'date'}),
            'budget': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Введите бюджет', 'min': 0}),
            'rating': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Рейтинг от 0 до 10',
                                               'min': 0, 'max': 10}),
            'cat': forms.Select(attrs={'class': 'form-control'}),
            'tags': forms.SelectMultiple(attrs={'class': 'form-control'}),
            'people_roles': forms.SelectMultiple(attrs={'class': 'form-control'}),
            'is_published': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'poster': forms.ClearableFileInput(attrs={'class': 'form-control-file'})
        }

    def clean_title(self):
        title = self.cleaned_data['title']
        if len(title) > 50:
            raise ValidationError('Длина превышает 50 символов')

        if title and not re.match(r'^[а-яА-ЯёЁ0-9\s\-\'\":,IVXLCDM]+$', title):
            raise forms.ValidationError("Название должно содержать только русские буквы и допустимые символы.")
        return title

    def clean_title_en(self):
        title_en = self.cleaned_data.get('title_en')
        if len(title_en) > 50:
            raise ValidationError('Длина превышает 50 символов')

        if title_en and not re.match(r'^[a-zA-Z0-9\s\-\'\":,]+$', title_en):
            raise forms.ValidationError("Название должно содержать только английские буквы и допустимые символы.")
        return title_en

    def clean_release_date(self):
        release_date = self.cleaned_data.get('release_date')
        min_year = 1900
        if release_date and release_date.year < min_year:
            raise ValidationError(f"Дата выхода не может быть раньше {min_year} года.")
        return release_date


class UploadFileForm(forms.Form):
    file = forms.ImageField(label="Изображение")
