import random
from django.shortcuts import render, redirect
from markdown2 import Markdown
from django import forms
from django.urls import reverse

from . import util

class SearchPrompt(forms.Form):
    title = forms.CharField(label='', widget=forms.TextInput(attrs={
        "class": "search",
      "placeholder": "Search"}))

class CreatePrompt(forms.Form):
    title = forms.CharField(label='Title', widget=forms.TextInput)
    text = forms.CharField(label='Content', widget=forms.Textarea)

class EditPrompt(forms.Form):
    text = forms.CharField(label='', widget=forms.Textarea(attrs={
        "placeholder": "Enter page content"
    }))

def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries(),
        "form": SearchPrompt()
    })

def title_search(request, title):
    entry_md = util.get_entry(title)

    # if entry exists, render the appropiate page
    if entry_md != None:
        entry_html = Markdown().convert(entry_md)
        return render(request, "encyclopedia/title.html", {
            "title": title,
            "entry": entry_html,
            "form": SearchPrompt()
        })
    else:
        return render(request, "encyclopedia/error.html", {
            "title": title,
            "form": SearchPrompt()
        })

def search(request):
    if request.method == "POST":
        form = SearchPrompt(request.POST)

        if form.is_valid():
            query = form.cleaned_data["title"]

            if query != None:
                entry_md = util.get_entry(query)

                # if entry exists
                if entry_md:
                    return redirect(reverse('title_search', args=[query]))
                # if entry doesn't exist
                else: 
                    related_titles = []

                    for title in util.list_entries():
                        if query.lower() in title.lower() or title.lower() in query.lower():
                            related_titles.append(title)

                    if related_titles:
                        return render(request, "encyclopedia/search.html", {
                        "related_titles": related_titles,
                        "form": SearchPrompt()
                        })
                    else:
                        return render(request, "encyclopedia/error.html", {
                            "title": query,
                            "form": SearchPrompt()
                        })

        return redirect(reverse('index'))
                
def create(request):

    if request.method == "GET":
        return render(request, "encyclopedia/create.html", {
        "create_form": CreatePrompt(),
        "form": SearchPrompt()
    })

    else:
        form = CreatePrompt(request.POST)

        if form.is_valid():
            title = form.cleaned_data["title"]
            text = form.cleaned_data["text"]
        else:
            return render(request, "encyclopedia/create.html", {
                "create_form": form,
                "form": SearchPrompt()
            })

        # if entry exists already
        if util.get_entry(title):
            return render(request, "encyclopedia/exists.html", {
                "form": SearchPrompt()
            })

        else:
            util.save_entry(title, text)
            return redirect(reverse('title_search', args=[title]))

def edit(request, title):
    if request.method == "GET":
        text = util.get_entry(title)

        return render(request, "encyclopedia/edit.html", {
            "title": title,
            "edit_form": EditPrompt(initial={'text':text}),
            "form": SearchPrompt()
        })
    if request.method == "POST":

        form = EditPrompt(request.POST)

        if form.is_valid():
            text = form.cleaned_data["text"]
            util.save_entry(title, bytes(request.POST['text'], 'utf8'))

            return redirect(reverse('title_search', args=[title]))

    # errors occured if this line is reached
    return render(request, "encyclopedia/error.html", {
        "form": SearchPrompt()
    })

def random_title(request):
    list = util.list_entries()
    title = random.randrange(0, len(list))

    return redirect(reverse('title_search', args=[list[title]]))
