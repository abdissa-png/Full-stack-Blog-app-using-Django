from django import forms
from .models import Comment
class EmailPostForm(forms.Form):
    name=forms.CharField(max_length=25)
    email=forms.EmailField()
    to=forms.EmailField()
    comment=forms.CharField(required=False,widget=forms.Textarea)

#we use forms.ModelForm to create a form from Model
class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields=['name','email','body']
class SearchForm(forms.Form):
    query = forms.CharField()