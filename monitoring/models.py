from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator

class Santri(models.Model):
    KELAS_CHOICES = [
        ('XA', 'XA'), ('XB', 'XB'), ('XC', 'XC'), ('XD', 'XD'), ('XE', 'XE'), ('XF', 'XF'),
        ('XIA', 'XIA'), ('XIB', 'XIB'), ('XIC', 'XIC'), ('XID', 'XID'), ('XIE', 'XIE'),
        ('XIIA', 'XIIA'), ('XIIB', 'XIIB'), ('XIIC', 'XIIC'), ('XIID', 'XIID'), ('XIIE', 'XIIE'),
    ]
    nama = models.CharField(max_length=100)
    induk = models.CharField(max_length=20, unique=True)
    kelas = models.CharField(max_length=5, choices=KELAS_CHOICES, default='XA')

    def __str__(self):
        return f"{self.nama} ({self.kelas})"

class LaporanBacaan(models.Model):
    ustaz = models.ForeignKey(User, on_delete=models.CASCADE)
    santri = models.ForeignKey(Santri, on_delete=models.CASCADE)
    tanggal = models.DateField()
    halaman_target = models.PositiveIntegerField(default=8)
    halaman_awal = models.PositiveIntegerField(null=True, blank=True)
    halaman_akhir = models.PositiveIntegerField(null=True, blank=True)
    jumlah_khatam = models.PositiveIntegerField(default=0) # Kolom Baru
    
    HADIR_CHOICES = [('Hadir', 'Hadir'), ('Sakit', 'Sakit'), ('Izin', 'Izin'), ('Alpa', 'Alpa')]
    status_kehadiran = models.CharField(max_length=10, choices=HADIR_CHOICES, default='Hadir')
    
    catatan = models.TextField(blank=True)

    @property
    def jumlah_halaman(self):
        if self.halaman_awal is None or self.halaman_akhir is None: return 0
        return self.halaman_akhir - self.halaman_awal + 1

    @property
    def mencapai_target(self):
        return self.jumlah_halaman >= self.halaman_target

    class Meta:
        unique_together = ('santri', 'tanggal')
