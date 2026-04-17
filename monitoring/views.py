import json # Tambahkan ini di paling atas views.py
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Santri, LaporanBacaan
from datetime import date, datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os

def format_spreadsheet(sheet):
    sheet.format("A1:J1", {"backgroundColor": {"red": 0.0, "green": 0.4, "blue": 0.0}, "textFormat": {"foregroundColor": {"red": 1.0, "green": 1.0, "blue": 1.0}, "bold": True}})
    num_rows = len(sheet.get_all_values())
    if num_rows > 0:
        sheet.format(f"A1:J{num_rows}", {"borders": {"top": {"style": "SOLID"}, "bottom": {"style": "SOLID"}, "left": {"style": "SOLID"}, "right": {"style": "SOLID"}}})

def kirim_ke_spreadsheet(data_list):
    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        
        # JURUS SAKTI: Baca dari Vercel Env, kalau tidak ada baru cari file lokal
        if os.getenv('GOOGLE_CREDENTIALS'):
            creds_dict = json.loads(os.getenv('GOOGLE_CREDENTIALS'))
            creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        else:
            # Ini untuk jaga-jaga kalau Bapak running di laptop (local) pakai file
            json_path = os.path.join(os.getcwd(), 'credentials.json')
            creds = ServiceAccountCredentials.from_json_keyfile_name(json_path, scope)
            
        client = gspread.authorize(creds)
        
        # Gunakan ID Spreadsheet Bapak yang baru
        spreadsheet_id = "1Rryo4OiOptMDxtX5c-RNf-fdtrgRZgE67stgcu37YQQ"
        worksheet = client.open_by_key(spreadsheet_id).get_worksheet(0)
        
        worksheet.append_rows(data_list)
        format_spreadsheet(worksheet)
        return True
    except Exception as e:
        print(f"Gagal Sinkron ke Sheets: {e}")
        return False

#@login_required
def riwayat_laporan(request):
    tanggal_str = request.GET.get('tanggal', str(date.today()))
    kelas_selected = request.GET.get('kelas', 'XA')
    santris = Santri.objects.filter(kelas=kelas_selected).order_by('nama')
    laporans_hari_ini = LaporanBacaan.objects.filter(tanggal=tanggal_str)
    data_map = {l.santri_id: l for l in laporans_hari_ini}
    auto_fill_data = {s.id: LaporanBacaan.objects.filter(santri=s).order_by('-tanggal', '-id').first().halaman_akhir if LaporanBacaan.objects.filter(santri=s).exists() else "" for s in santris}

    return render(request, 'monitoring/riwayat.html', {
        'santris': santris, 'data_map': data_map, 'auto_fill_data': auto_fill_data,
        'tanggal_sekarang': tanggal_str, 'kelas_list': Santri.KELAS_CHOICES, 'kelas_selected': kelas_selected,
    })

@login_required
def simpan_laporan(request):
    if request.method == 'POST':
        is_admin = request.user.username.lower() in ['alif', 'nurmawan', 'reza']
        now = datetime.now().time()
        if not is_admin and not (now.replace(hour=7, minute=25) <= now <= now.replace(hour=7, minute=35, second=59)):
            return redirect(f"/?tanggal={request.POST.get('tanggal')}&kelas={request.POST.get('kelas_hidden')}")

        tanggal = request.POST.get('tanggal')
        kelas = request.POST.get('kelas_hidden')
        santri_ids = request.POST.getlist('santri_id')
        kehadiran = request.POST.getlist('status_kehadiran')
        khatam = request.POST.getlist('jumlah_khatam')
        h_awal = request.POST.getlist('hal_awal')
        h_akhir = request.POST.getlist('hal_akhir')
        
        single_save_id = request.POST.get('single_save') # Cek apakah ini edit per santri
        data_sheet = []
        waktu_input = datetime.now().strftime("%d/%m/%Y %H:%M")

        for i in range(len(santri_ids)):
            if single_save_id and santri_ids[i] != single_save_id: continue
            
            awal, akhir = int(h_awal[i] or 0), int(h_akhir[i] or 0)
            jml = akhir - awal + 1 if (akhir >= awal and awal > 0) else 0
            
            LaporanBacaan.objects.update_or_create(
                santri_id=santri_ids[i], tanggal=tanggal,
                defaults={'ustaz': request.user, 'halaman_awal': awal or None, 'halaman_akhir': akhir or None, 'jumlah_khatam': int(khatam[i] or 0), 'status_kehadiran': kehadiran[i]}
            )
            s_nama = Santri.objects.get(id=santri_ids[i]).nama
            data_sheet.append([waktu_input, tanggal, request.user.username, kelas, s_nama, kehadiran[i], khatam[i] or 0, awal, akhir, jml])

        if data_sheet: kirim_ke_spreadsheet(data_sheet)
        return redirect(f"/?tanggal={tanggal}&kelas={kelas}")
