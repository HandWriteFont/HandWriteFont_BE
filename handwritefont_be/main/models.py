from django.db import models
from user.models import HWFUser
from django.conf import settings

def user_directory_path(instance, filename):
    return '{0}/{1}/template/{2}'.format(instance.owner.email,instance.name,'Template.jpg')

def status_field():
    return [('Accept','Accept'),('To Do','To Do'),('Doing','Doing'),('Done','Done'),('Canceled','Canceled')]

class preview(models.Model):
    name = models.CharField(max_length=50)
    path = models.URLField(max_length=200, null=True, blank= True)
    
    def __str__(self):
        return self.name


class Font(models.Model):
    name = models.CharField(primary_key=True, max_length=50)
    created_date = models.DateField(auto_now_add=True)
    like_users = models.ManyToManyField(HWFUser, blank=True, related_name='like')
    owner = models.ForeignKey(HWFUser, related_name='fonts', on_delete=models.CASCADE)
    file = models.FileField(upload_to=user_directory_path,null=True,blank=True)
    ttf_file = models.URLField(max_length=200, null=True, blank= True)
    woff_file = models.URLField(max_length=200, null=True, blank= True)
    status = models.CharField(max_length=10, choices=status_field(), default='Canceled')
    public = models.BooleanField(default=True)
    previews = models.ManyToManyField(preview, related_name='preview', blank=True)

    @property
    def like_num(self):
        return self.like_users.count()

    def __str__(self):
        return self.name

