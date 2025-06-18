import pathlib, subprocess, shlex, time, resource,datetime,platform
from django.conf import settings
from .models import CodeSubmission

TIME_LIMIT = 2
MEM_LIMIT = 256 *1024 * 1024 

def set_limits():
    if platform.system() == "Darwin":
        resource.setrlimit(resource.RLIMIT_CPU, (TIME_LIMIT, TIME_LIMIT))
    else:
        resource.setrlimit(resource.RLIMIT_AS, (MEM_LIMIT, MEM_LIMIT))
        resource.setrlimit(resource.RLIMIT_CPU, (TIME_LIMIT, TIME_LIMIT))
def run_submissions(sub_id: str):
    sub = CodeSubmission.objects.get(pk=sub_id)
    code_path = pathlib.Path(sub.code_path)
    input_path = pathlib.Path(sub.input_path)
    base_id = code_path.stem
    output_path = pathlib.Path(settings.SUBMISSIONS_DIR /"outputs"/f"{base_id}.out")
    error_path = pathlib.Path(settings.SUBMISSIONS_DIR / "errors" / f"{base_id}.err")

    output_path.parent.mkdir(parents=True,exist_ok=True)
    error_path.parent.mkdir(parents=True,exist_ok=True)

    t0 = time.perf_counter()
    try:
        if sub.language =="cpp":
            exe_path = code_path.with_suffix("")
            compile_cmd = f"g++-14 {code_path} -o {exe_path}"
            compiler = subprocess.run(
                shlex.split(compile_cmd),
                stderr=subprocess.PIPE,
                timeout=TIME_LIMIT,
            )
            if compiler.returncode != 0:
                error_path.write_bytes(compiler.stderr)
                sub.status = "Compilation Error"
                sub.error_path = str(error_path)
                sub.completed_at = datetime.datetime.now(datetime.timezone.utc)
                sub.save()
                return sub
            run_cmd = f"timeout {TIME_LIMIT}s {exe_path}"
        elif sub.language == "py":
            run_cmd = f"timeout {TIME_LIMIT}s python3 {code_path}"
        
        with open(input_path,"rb") as fin, \
                open(output_path,"wb") as fout,\
                open(error_path,"wb") as ferr:
            proc = subprocess.Popen(
                shlex.split(run_cmd),
                stdin=fin,stdout=fout,stderr=ferr,
                preexec_fn=set_limits,
            )
            try:
                proc.wait(TIME_LIMIT + 1)
            except subprocess.TimeoutExpired:
                proc.kill()
                sub.status = "Time Limit Exceeded"
            else:
                if proc.returncode ==0:
                    sub.status="Accepted"
                else:
                    sub.status = "Runtime Error"
        sub.output_path = str(output_path)
        sub.error_path = str(error_path)
    except Exception as e:
        error_path.write_text(str(e))
        sub.error_path = str(error_path)
        sub.status = "SYSTEM_ERROR"
    finally:
        sub.exec_time_ms = int((time.perf_counter()-t0)*1000)
        sub.completed_at = datetime.datetime.now(datetime.timezone.utc)
        sub.save()
        return sub
