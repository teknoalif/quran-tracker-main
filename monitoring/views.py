import json
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from datetime import date, datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os

# --- DAFTAR SANTRI MANUAL (Agar tidak Error 500) ---
# Tambahkan nama santri Bapak di sini agar muncul di web
DATA_SANTRI = {
    'XA': ['Alif Rezky', 'Abu Uwais', 'Santri Contoh 1'],
    'XB': ['Santri Contoh 2', 'Santri Contoh 3'],
}

KELAS_CHOICES = [('XA', 'Kelas XA'), ('XB', 'Kelas XB')]

def format_spreadsheet(sheet):
    try:
        sheet.format("A1:J1", {"backgroundColor": {"red": 0.0, "green": 0.4, "blue": 0.0}, "textFormat": {"foregroundColor": {"red": 1.0, "green": 1.0, "blue": 1.0}, "bold": True}})
    except:
        pass

def kirim_ke_spreadsheet(data_list):
    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        if os.getenv('GOOGLE_CREDENTIALS'):
            creds_dict = json.loads(os.getenv('GOOGLE_CREDENTIALS'))
            creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        else:
            json_path = os.path.join(os.getcwd(), 'credentials.json')
            creds = ServiceAccountCredentials.from_json_keyfile_name(json_path, scope)
            
        client = gspread.authorize(creds)
        spreadsheet_id = "1Rryo4OiOptMDxtX5c-RNf-fdtrgRZgE67stgcu37YQQ"
        worksheet = client.open_by_key(spreadsheet_id).get_worksheet(0)
        worksheet.append_rows(data_list)
        format_spreadsheet(worksheet)
        return True
    except Exception as e:
        print(f"Gagal Sinkron ke Sheets: {e}")
        return False

# Hapus sementara @login_required agar Bapak bisa tes tanpa database user
def riwayat_laporan(request):
    tanggal_str = request.GET.get('tanggal', str(date.today()))
    kelas_selected = request.GET.get('kelas', 'XA')
    
    # Ambil daftar nama dari variabel DATA_SANTRI di atas, bukan dari database
    nama_santris = DATA_SANTRI.get(kelas_selected, [])
    
    # Buat objek buatan agar template tidak error
    santris = []
    for i, nama in enumerate(nama_santris):
        santris.append({'id': i, 'nama': nama})

    return render(request, 'monitoring/riwayat.html', {
        'santris': santris, 
        'data_map': {}, 
        'auto_fill_data': {},
        'tanggal_sekarang': tanggal_str, 
        'kelas_list': KELAS_CHOICES, 
        'kelas_selected': kelas_selected,
    })

def simpan_laporan(request):
    if request.method == 'POST':
        tanggal = request.POST.get('tanggal')
        kelas = request.POST.get('kelas_hidden')
        santri_names = request.POST.getlist('santri_nama') # Kita pakai nama sekarang
        kehadiran = request.POST.getlist('status_kehadiran')
        khatam = request.POST.getlist('jumlah_khatam')
        h_awal = request.POST.getlist('hal_awal')
        h_akhir = request.POST.getlist('hal_akhir')
        
        data_sheet = []
        waktu_input = datetime.now().strftime("%d/%m/%Y %H:%M")
        user_sekarang = request.user.username if request.user.is_authenticated else "Guest"

        for i in range(len(santri_names)):
            awal = int(h_awal[i] or 0)
            akhir = int(h_akhir[i] or 0)
            jml = akhir - awal + 1 if (akhir >= awal and awal > 0) else 0
            
            # Langsung bungkus untuk Google Sheets (Skip simpan ke SQL karena memory bakal hilang)
            data_sheet.append([
                waktu_input, tanggal, user_sekarang, kelas, 
                santri_names[i], kehadiran[i], khatam[i] or 0, 
                awal, akhir, jml
            ])

        if data_sheet: 
            kirim_ke_spreadsheet(data_sheet)
            
        return redirect(f"/?tanggal={tanggal}&kelas={kelas}")
