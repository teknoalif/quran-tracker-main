from django.contrib import admin # Mengambil alat admin dari Django
from .models import Santri, LaporanBacaan # Mengambil tabel yang baru kita buat tadi

@admin.register(Santri) # Mendaftarkan tabel Santri ke halaman Admin
class SantriAdmin(admin.ModelAdmin):
    list_display = ('nama', 'induk') # Menampilkan kolom Nama dan Induk di daftar tabel

@admin.register(LaporanBacaan) # Mendaftarkan tabel Laporan ke halaman Admin
class LaporanAdmin(admin.ModelAdmin):
    # Menentukan kolom apa saja yang muncul di daftar laporan
    list_display = ('santri', 'tanggal', 'halaman_awal', 'halaman_akhir', 'jumlah_halaman', 'mencapai_target')
    list_filter = ('tanggal', 'santri') # Menambahkan menu filter di samping berdasarkan tanggal dan santri
