from django.db import models

class State(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class City(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class CityState(models.Model):
    city = models.ForeignKey(City, on_delete=models.CASCADE, related_name='city_states')
    state = models.ForeignKey(State, on_delete=models.CASCADE, related_name='city_states')

    class Meta:
        unique_together = ['city', 'state']

    def __str__(self):
        return f"{self.city.name} - {self.state.name}"

class College(models.Model):
    name = models.CharField(max_length=500,default=None)
    short_name = models.CharField(max_length=255,default=None)

    class Meta:
        unique_together = ['name', 'short_name']
        db_table = 'college'

    def __str__(self):
        return self.name

class Branch(models.Model):
    name = models.CharField(max_length=255,default=None)
    short_name = models.CharField(max_length=255,default=None)

    def __str__(self):
        return self.name
