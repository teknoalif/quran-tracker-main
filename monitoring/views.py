import json
import os
import gspread
from django.shortcuts import render, redirect
from datetime import date, datetime
from oauth2client.service_account import ServiceAccountCredentials

try:
    from .data_santri import DATA_SANTRI
except ImportError:
    DATA_SANTRI = {}

# --- ID SPREADSHEET BARU BAPAK ---
SPREADSHEET_ID = "18knwd2i4FR0XOX0Bb22No66venosWUsma5DbTZ6u9_s"
KELAS_CHOICES = [(k, f"Kelas {k}") for k in DATA_SANTRI.keys()] if DATA_SANTRI else []

def kirim_ke_spreadsheet(data_list):
    try:
        scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        creds_json = os.getenv("GOOGLE_CREDENTIALS")
        
        if not creds_json:
            print("LOG: GOOGLE_CREDENTIALS tidak terbaca di Vercel!")
            return False
            
        creds_dict = json.loads(creds_json)
        
        # PERBAIKAN KRUSIAL: Menangani karakter kunci rahasia yang sering rusak di Vercel
        if 'private_key' in creds_dict:
            # Mengganti karakter literal \n menjadi baris baru yang asli
            raw_key = creds_dict['private_key']
            creds_dict['private_key'] = raw_key.replace('\\n', '\n').replace('\n\n', '\n').strip()
            
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        client = gspread.authorize(creds)
        
        # Target Spreadsheet Baru
        sheet = client.open_by_key("18knwd2i4FR0XOX0Bb22No66venosWUsma5DbTZ6u9_s")
        worksheet = sheet.get_worksheet(0) 
        
        # Kirim Data
        worksheet.append_rows(data_list, value_input_option='RAW')
        print(f"LOG: Berhasil kirim {len(data_list)} data!")
        return True
    except Exception as e:
        print(f"LOG ERROR: {str(e)}")
        return False

def riwayat_laporan(request):
    tanggal_str = request.GET.get("tanggal", str(date.today()))
    kelas_selected = request.GET.get("kelas", "XA")
    
    nama_list = DATA_SANTRI.get(kelas_selected, [])
    # Santris diubah menjadi list of dict untuk looping di template
    santris = [{"id": i, "nama": nama} for i, nama in enumerate(nama_list)]
    
    return render(request, "monitoring/riwayat.html", {
        "santris": santris,
        "tanggal_sekarang": tanggal_str,
        "kelas_list": KELAS_CHOICES,
        "kelas_selected": kelas_selected,
    })

def simpan_laporan(request):
    # Default redirect jika ada data yang hilang
    tanggal = str(date.today())
    kelas = "XA"
    
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
        
        # Looping berdasarkan jumlah nama yang dikirim
        for i in range(len(names)):
            try:
                # Pastikan input halaman adalah angka, jika kosong set ke 0
                val_awal = h_awal[i] if (i < len(h_awal) and h_awal[i]) else "0"
                val_akhir = h_akhir[i] if (i < len(h_akhir) and h_akhir[i]) else "0"
                
                # Hitung jumlah halaman (Logic: Akhir - Awal + 1)
                awal_int = int(val_awal)
                akhir_int = int(val_akhir)
                jml = akhir_int - awal_int + 1 if (akhir_int >= awal_int and awal_int > 0) else 0
                
                # Susun baris untuk Google Sheets
                data_sheet.append([
                    waktu, 
                    tanggal, 
                    "Ustaz/Guru", # Nama penginput (Bisa request.user.username jika login aktif)
                    kelas, 
                    names[i], 
                    hadir[i] if i < len(hadir) else "Hadir", 
                    khatam[i] if i < len(khatam) else "0", 
                    val_awal, 
                    val_akhir, 
                    jml
                ])
            except (ValueError, IndexError):
                continue
            
        if data_sheet:
            kirim_ke_spreadsheet(data_sheet)
            
    # Kembalikan ke halaman utama dengan parameter filter yang sama
    return redirect(f"/?tanggal={tanggal}&kelas={kelas}")
