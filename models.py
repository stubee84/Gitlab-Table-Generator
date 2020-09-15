from django.db import models

# Create your models here.
class execution(models.Model):
    input_data = models.TextField()
    output_data = models.TextField()
    data_type = models.CharField(max_length=20, default=None)
    limit = models.CharField(max_length=20, default=None)
    executed_at = models.DateTimeField(verbose_name='executed_at',auto_now=True)