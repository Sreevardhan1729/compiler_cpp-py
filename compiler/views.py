from django.shortcuts import render,redirect,get_object_or_404
import uuid, time,pathlib
from django.conf import settings
from .forms import SubmissionForm
from .models import CodeSubmission
from .executor import run_submissions
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
# Create your views here.

BASE = settings.SUBMISSIONS_DIR
def editor(request):
    return render(request,"compiler/editor.html",{"form":SubmissionForm()})


# @csrf_exempt
def submit(request):
    if request.method != "POST":
        return redirect("editor")

    form = SubmissionForm(request.POST)
    if not form.is_valid():
        return render(request, "compiler/editor.html", {"form": form})

    uid = uuid.uuid4().hex
    lang = form.cleaned_data["language"]
    ts = int(time.time()*1000)

    name = f"{uid}_{ts}"
    code_path = BASE / "codes" / f"{name}.{lang}"
    input_path = BASE / "inputs" / f"{name}.in"
    code_path.parent.mkdir(parents=True, exist_ok=True)
    input_path.parent.mkdir(parents=True, exist_ok=True)

    code_path.write_text(form.cleaned_data["code"])
    input_path.write_text(form.cleaned_data["stdin"] or "")

    sub = CodeSubmission.objects.create(
        language=lang,
        code_path=str(code_path),
        input_path=str(input_path),
    )
    run_submissions(str(sub.id))
    response = redirect("result", pk=sub.id)
    response["HX-Redirect"] = response.url
    return response

def result(request,pk):
    sub = get_object_or_404(CodeSubmission,pk=pk)
    ctx = {
        "sub":sub,
        "output":sub.output,
        "error":pathlib.Path(sub.error_path).read_text() if sub.error_path and pathlib.Path(sub.error_path).exists() else "",
    }
    return render(request,"compiler/result.html",ctx)
    
