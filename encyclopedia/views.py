from django.shortcuts import render, redirect
from django.urls import reverse
import random
import markdown2
from . import util

def index(request):
    """
    Homepage: lists all encyclopedia entries.
    """
    entries = util.list_entries()
    return render(request, "encyclopedia/index.html", {
        "entries": entries
    })

def entry(request, title):
    """
    Entry page: displays the content of the entry with the given 'title'.
    If the entry does not exist, shows an error page.
    """
    content_md = util.get_entry(title)  # get Markdown content

    if content_md is None:
        # Entry does not exist
        return render(request, "encyclopedia/error.html", {
            "message": f"The page '{title}' was not found."
        })

    # Convert Markdown to HTML
    content_html = markdown2.markdown(content_md)

    # Render the page with content
    return render(request, "encyclopedia/entry.html", {
        "title": title,
        "content": content_html
    })


def search(request):
    """
    Handles the search form in the sidebar.
    """
    if request.method != "GET":
        # For security, redirect to index if not GET
        return redirect("encyclopedia:index")

    query = request.GET.get("q", "").strip()  # get search query

    if not query:
        return redirect("encyclopedia:index")  # if empty, go to index

    entries = util.list_entries()

    # Exact match (case-insensitive)
    for entry in entries:
        if entry.lower() == query.lower():
            return redirect("encyclopedia:entry", title=entry)

    # Partial match → search substring
    results = [entry for entry in entries if query.lower() in entry.lower()]

    return render(request, "encyclopedia/search.html", {
        "query": query,
        "results": results
    })


def new_entry(request):
    """
    Create a new encyclopedia entry.
    """
    if request.method == "POST":
        title = request.POST.get("title", "").strip()
        content = request.POST.get("content", "").strip()

        if not title:
            return render(request, "encyclopedia/new.html", {
                "error": "Title cannot be empty.",
                "title": title,
                "content": content
            })

        # Check if entry already exists (case-insensitive)
        entries = util.list_entries()
        for e in entries:
            if e.lower() == title.lower():
                return render(request, "encyclopedia/error.html", {
                    "message": "An entry with this title already exists."
                })

        # Save and redirect to the new page
        util.save_entry(title, content)
        return redirect("encyclopedia:entry", title=title)

    # GET request → show form
    return render(request, "encyclopedia/new.html")


def edit_entry(request, title):
    """
    Edit an existing entry.
    GET -> show form with current content.
    POST -> save changes and redirect to the entry page.
    """
    if request.method == "GET":
        content = util.get_entry(title)
        if content is None:
            return render(request, "encyclopedia/error.html", {
                "message": f"The page '{title}' was not found."
            })
        return render(request, "encyclopedia/edit.html", {
            "title": title,
            "content": content
        })

    # POST -> save changes
    content = request.POST.get("content", "").strip()
    util.save_entry(title, content)  # overwrite existing content
    return redirect("encyclopedia:entry", title=title)


def random_entry(request):
    """
    Redirects to a random encyclopedia entry.
    """
    entries = util.list_entries()
    if not entries:
        return render(request, "encyclopedia/error.html", {
            "message": "No entries available."
        })
    
    title = random.choice(entries)  # choose a random title
    return redirect("encyclopedia:entry", title=title)
