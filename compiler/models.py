from django.db import models
import uuid,pathlib,datetime
from django.conf import settings
# Create your models here.

class CodeSubmission(models.Model):
    id = models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
    LANGS = [("cpp","C++"),("py","Python")]
    language = models.CharField(max_length=3,choices=LANGS,default="cpp")
    code_path = models.TextField()
    input_path = models.TextField()
    output_path = models.TextField(null=True,blank=True)
    error_path = models.TextField(null=True,blank=True)

    completed_at = models.DateTimeField(null=True,blank=True)
    status = models.CharField(max_length=32,default="QUEUED")
    exec_time_ms = models.IntegerField(null=True,blank=True)

    @property
    def output(self) -> str| None:
        if self.output_path and pathlib.Path(self.output_path).exists():
            return pathlib.Path(self.output_path).read_text()