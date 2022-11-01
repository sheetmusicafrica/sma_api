import hashlib,datetime
from django.db import models
from django.db.models import Q

from sheet_music_africa.storage_backends import GameMediaStorage


class Competition(models.Model):
    name = models.CharField(max_length=20)
    pass_phrase = models.CharField(max_length=20)
    date_started = models.DateTimeField(null=True,blank=True)
    span = models.PositiveBigIntegerField(default=0)
    date_ended = models.DateField(null=True,blank=True)
    location = models.CharField(max_length=200,default="Virtual")
    status = models.CharField(
        max_length=3,
        choices=[("PEN", 'PENDING'),("STA", 'STARTED'),("END", 'ENDED'),
    ],
        default="PEN",
    )

    def __str__(self):
        return f"{self.name} {self.status}"

    def get_number_of_contenders(self):
        return GameProfile.objects.filter(Q(competition=self)&Q(can_compete=True)).count()

    
    def get_leader_board(self):
        return self.gameprofile_set.all().order_by("-score")

    def update_state(self):
        if self.status == "STA":
            start = self.date_started.time()
            now = datetime.datetime.now().time()

            if start.timestamp() - now.timestamp() > self.span:
                self.status = "END"
                self.save()

        return self.status != "STA"



class GameProfile(models.Model):    
    full_name = models.CharField(max_length=300)
    nickname = models.CharField(max_length=100,default="",unique=True)
    email = models.EmailField(unique=True)
    pic = models.FileField(null=True,blank=True,storage=GameMediaStorage())
    score = models.PositiveBigIntegerField(default=0)
    competition = models.ManyToManyField(Competition,blank=True)  
    password = models.TextField()  
    state = models.CharField(max_length=30)

    class Meta:
        ordering = ['-score']

    def __str__(self):
        return self.full_name

    def save_password(self,password):
        hash = hashlib.md5(password.encode())
        self.password = hash.hexdigest()
        self.save()

    def check_password(self,password):
        hash = hashlib.md5(password.encode())
        return self.password == hash.hexdigest()


class ScoreLog(models.Model):
    profile = models.ForeignKey(GameProfile,on_delete=models.CASCADE)
    score = models.PositiveBigIntegerField()

    def __str__(self):
        return f"{self.profile.full_name} - {self.score}"