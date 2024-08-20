import random
from django.shortcuts import render
from markdown2 import Markdown
from django.http import HttpResponseRedirect

from . import util


def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })

def entry(request, title):
    page = util.get_entry(title.lower())
    if page == None:
        return render(request, "encyclopedia/error.html", {
            "message": "This entry does not exist."
        })
    else:
        markdowncon = Markdown()
        content = markdowncon.convert(page)
        return render(request, "encyclopedia/entry.html", {
            "title": title.capitalize(),
            "content": content
        })
def search(request):
    query = request.GET["q"]
    page = util.get_entry(query.lower())
    if page != None:
        markdowncon = Markdown()
        content = markdowncon.convert(page)
        title = query.lower()
        return HttpResponseRedirect(f"wiki/{title}")
    else:
        entries = util.list_entries()
        displayed = []
        for entry in entries:
            if query.lower() in entry.lower():
                displayed.append(entry)
        return render(request, "encyclopedia/search.html", {
            "entries": displayed
        })

def create(request):
    if request.method == "POST":
        if util.get_entry(request.POST["title"].lower()):
            return render(request, "encyclopedia/error.html", {
                "message": "This entry already exist."
            })
        else:
            util.save_entry(request.POST["title"].lower(), request.POST["content"])
            return HttpResponseRedirect(f"wiki/{request.POST["title"].lower()}")
    else:
        return render(request, "encyclopedia/create.html")

def edit(request, entry):
    if request.method == "POST":
        util.save_entry(entry.lower(), request.POST["content"])
        return HttpResponseRedirect(f"/wiki/{entry.lower()}")
    else:
        page = util.get_entry(entry.lower())
        if page == None:
            return render(request, "encyclopedia/error.html", {
                "message": "This entry does not exist."
            })
        else:
            return render(request, "encyclopedia/edit.html", {
                "title": entry,
                "content": page
            })

def rand(request):
    entries = util.list_entries()
    choice = random.choice(entries)
    return HttpResponseRedirect(f"/wiki/{choice.lower()}")
