from django.db import models

class Chambre(models.Model):
    nom = models.CharField(max_length=50)
    prix = models.IntegerField(default=0)
    description = models.TextField()
    image = models.ImageField(upload_to='media/pics')
    disponibilité = models.BooleanField(default=True)
    capacity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return self.nom

    class Meta:
        verbose_name = "Номер"
        verbose_name_plural = "Номера"