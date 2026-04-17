import json
import os
import gspread
from django.shortcuts import render, redirect
from datetime import date, datetime
from oauth2client.service_account import ServiceAccountCredentials
# PANGGIL DATA DARI FILE SEBELAH
from .data_santri import DATA_SANTRI

SPREADSHEET_ID = "1gKsf0NS1MkEC5-GtN4eRFhDqWLYEaGFMhAkfEYJ8Fvc"
KELAS_CHOICES = [(k, f"Kelas {k}") for k in DATA_SANTRI.keys()]

def kirim_ke_spreadsheet(data_list):
    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds_json = os.getenv("GOOGLE_CREDENTIALS")
        if creds_json:
            creds_dict = json.loads(creds_json)
            creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
            client = gspread.authorize(creds)
            worksheet = client.open_by_key(SPREADSHEET_ID).get_worksheet(0)
            worksheet.append_rows(data_list)
            return True
    except Exception as e:
        print(f"Error Sheets: {e}")
    return False

def riwayat_laporan(request):
    tanggal_str = request.GET.get("tanggal", str(date.today()))
    kelas_selected = request.GET.get("kelas", "XA")
    nama_list = DATA_SANTRI.get(kelas_selected, [])
    santris = [{"id": i, "nama": nama} for i, nama in enumerate(nama_list)]
    
    return render(request, "monitoring/riwayat.html", {
        "santris": santris,
        "tanggal_sekarang": tanggal_str,
        "kelas_list": KELAS_CHOICES,
        "kelas_selected": kelas_selected,
    })

def simpan_laporan(request):
    if request.method == "POST":
        tanggal = request.POST.get("tanggal")
        kelas = request.POST.get("kelas_hidden")
        names = request.POST.getlist("santri_nama")
        hadir = request.POST.getlist("status_kehadiran")
        khatam = request.POST.getlist("jumlah_khatam")
        h_awal = request.POST.getlist("hal_awal")
        h_akhir = request.POST.getlist("hal_akhir")
        
        data_sheet = []
        waktu = datetime.now().strftime("%d/%m/%Y %H:%M")
        
        for i in range(len(names)):
            awal = h_awal[i] if h_awal[i] else "0"
            akhir = h_akhir[i] if h_akhir[i] else "0"
            try:
                jml = int(akhir) - int(awal) + 1 if (int(akhir) >= int(awal) and int(awal) > 0) else 0
            except: jml = 0
            data_sheet.append([waktu, tanggal, "Guru", kelas, names[i], hadir[i], khatam[i], awal, akhir, jml])
            
        if data_sheet:
            kirim_ke_spreadsheet(data_sheet)
    return redirect(f"/?tanggal={tanggal}&kelas={kelas}")
