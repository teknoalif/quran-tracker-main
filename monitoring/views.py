import json
import os
import gspread
from django.shortcuts import render, redirect
from datetime import date, datetime
from oauth2client.service_account import ServiceAccountCredentials

# --- KONFIGURASI ---
SPREADSHEET_ID = "1gKsf0NS1MkEC5-GtN4eRFhDqWLYEaGFMhAkfEYJ8Fvc"

DATA_SANTRI = {
    'XA': ['ABDUL HAAMID', 'ALIF WARDHANI SANTOSO', 'ALVARO SYARIF FERYANSYAH', 'ARKAN SYAIBANU SOFYAN', 'ARKANSYAH NAKHLAN ZAKARIA', 'AZKA IRHAM PURWANSYAH', 'AZZAM DZAKWAN AL FARUQ', 'DAVA KEANU PUTRA', 'EL FAYAADH', 'FAIZ HAQIQI', 'GALYZVITO DWIYANDRA', 'HABIBURRAHMAN AL HASYIM', 'HAFIZ KIYOSHI ARIF', 'HASAN', 'HUDZAIFAH AL HUMAIDI', 'LYAS MUSTHAFA AKHYAR', 'IRFANDA ADHA MIRZALI', 'KENNARD DZAKI HERLAMBANG', 'LUQMAN ABDUL HAKIM', 'MOHAMMAD AL KAUTSAR', 'MOHAMMAD ARSYAD NARARYA PRATOMO', 'MUHAMMAD AL - FATIH', 'MUHAMMAD AYYASH GHAZI MIFZAL', 'MUHAMMAD BINTANG PUTRARASYA', 'MUHAMMAD FADHIL AZKARA', 'NOUVAL RASYDAN ENDRI', 'RAQOIS FAWWAZ BAARI\'UL MUMTAAZ', 'RANJANA MUMTAZ ATHALLAH', 'ZIDANE'],
    'XB': ['ABDULLAH MUHAMMAD RAHMAN', 'AFFAN FIRDAUS', 'AHMAD DANI', 'AKHDAN HELMI', 'AMMAAR ZAKKY BATHHEF', 'ANAS WILDAN SOBARI', 'ARIF KHAIRUL AZAM', 'ATILLA DHIYAEL FAJRI', 'BINTANG ALFIANO BRILIANT SAPUTRA', 'DARU AZRI ARMANSYAH', 'FA\'IQ', 'FAKHRY MUHAMMAD RAYYAN', 'FAUZAN HUSEIN BADJRY', 'HAFIDZ KHALFANI HAMISENA', 'HANIF ALFARIZI', 'KEANU AL GHIFARI AHMAD JAEPUTRA', 'LUQMANUL HAKIM ADDATIN', 'MOCH. REYZA SYARIF ABIDIN', 'MUCHAMMAD THORIQ AL MUZACKY', 'MUHAMMAD FATHURRAHMAN', 'MUHAMMAD NATHAN AL FAIQ', 'MUHAMMAD RASYID', 'MUSH\'AB UMAIR ZACHA WERUS', 'RAYZA FIDIANO SIREGAR', 'SAMI RABBANI HARTONO', 'UBAIDAH AS SA\'DY', 'UMAR MUBARAK', 'ZIYAD GHASSAN AZRI SASONO'],
    'XC': ['AHMAD HARIS IKHWAN', 'AHMAD TSABIT', 'ANDRA AIDILLAH', 'ARAFAH ZHILLAN AMIR NASUTION', 'AUFA SAKHA SALMAN', 'AZFAR IRHAM PURWANSYAH', 'DARRELL YUSRAN ILMANY RAFAN', 'FAIZ ABDUL AZIZ', 'FARRAS MUHAMMAD RAMADHAN', 'FATHI RAYA NONCI', 'GAVIN EKISA AQILA FIKRA', 'GHILMAN ADZKA SYUHADA', 'KHALISMAN RAMADHAN', 'LUQMAN HAFIDZ ANNURIL HIDAYAT', 'MIQDAD', 'MUHAMMAD ALIFFATTAH AS-SYIFA\' SUYANTOM', 'MUHAMMAD AMMAR NUFAIL', 'MUHAMMAD FA\'IQ FAYYADH QUSHAYYI', 'MUHAMMAD NABIL MAKARIM', 'MUHAMMAD RAFIIF GATHFAN', 'MUHAMMAD SETYO ABDUN NASTIR', 'MUHAMMAD TEGUH HASAN', 'MUHAMMAD TIFATULLAH ARRASYID ISMAIL', 'RAIKHAN RASHEED DZAKIANSYAH', 'TENGKU MUADZ', 'UWAIS UBAIDILLAH', 'YAVI AL\'FIAN CHRISTIANDY'],
    'XD': ['AHMAD HANIF FAUZAN', 'AHNAF FARRAS JATMIKA', 'ARKAN UMAIR ROFIF', 'ARKANANTA RA\'UUF BAADILLA', 'ATHASYAH REIZKI RAMADHAN', 'AZZAM BAWAZIER', 'BRAMANTYO PURWOKO NURINGDAVIANDRA JULIAN SISWOYO', 'DHEVIN ADELIO TAMAM', 'ELMALIK ANANDYA SOFYAN', 'FAWAAZ KARIIM BENZEMA', 'GHAISAN ALTHAF NAZURAKHADAFI FAHRIANSYAH', 'M YUSUP', 'MAUZA YUSUF RAFFASYA', 'MUHAMMAD BINAR PRAWISENO', 'MUHAMMAD FADHIL KHAIRULLAH', 'MUHAMMAD FAREL ISVIKHRAM', 'MUHAMMAD RASHID RIZWAAN', 'MUHAMMAD RHAMDHANI EL HAQQ', 'NAUFAL FAWWAZ ALFIAN', 'RADEN MIKAIL HAFIZH GOENAWAN', 'RAFA DLAIFURRAHMAN FAHAMSYAH', 'RAFI MUHAMAD RIZQI', 'SALMAN ALI', 'SHAQUILLE MUFTY KASYAFANI', 'SULAEMAN HARUN MAR\'IZIGGY ALVA RADZAVIER'],
    'XE': ['ADKHILNI MUDKHALA SIDQI', 'ARKAAN ABDILLAH PRANAAWALIAH', 'ARKHAREGA RADITHYA NARARYA AGUSTIAN', 'ATHAYA SHABRAZAN ADHSY', 'AZZAM SHIDIQ NURYANTO', 'DAFFA TRISTAN ADINATA KHRISNADIYANTO', 'DAFFI HADI YURIAWAN', 'DASTAN ZAHIR MANAF', 'DZAKY ALMER RAFIF', 'FARZAN FAEYZA RAVIDYATAMA', 'FATHAN ZIDANE ATTAYA', 'HAMDY MOHAMMAD GHOSAN', 'HAZZA IRSA ASWATAMA', 'MUHAMAD ATHADZAKI UKASYAH ZAENAL', 'MUHAMMAD DZUL HABIE MUKTIADIM', 'MUHAMMAD FARIS HUMAM', 'MUHAMMAD MULTAZAM AL GHAZALI', 'PARAMA RAISSA OBADIAH', 'QAISHAR FADHIL DZIHNI', 'R. MUHAMMAD TERZAGHI INDRA HERMAWAN', 'REYHAN FADHLILLAH PANGESTU', 'RHAFAEL FATURAHMAN', 'RYANDRA PUTRA RIFAI', 'SA\'AD ALI', 'SYED AHMAD ZAKY ABDURAHMAN', 'THUFAIL MUHAMMAD KHALIDI', 'THUFEIL TSANI AR-ROYYAN'],
}

KELAS_CHOICES = [(k, f'Kelas {k}') for k in DATA_SANTRI.keys()]

def kirim_ke_spreadsheet(data_list):
    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        if os.getenv('GOOGLE_CREDENTIALS'):
            creds_dict = json.loads(os.getenv('GOOGLE_CREDENTIALS'))
            creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
            client = gspread.authorize(creds)
            worksheet = client.open_by_key(SPREADSHEET_ID).get_worksheet(0)
            worksheet.append_rows(data_list)
            return True
    except Exception as e:
        print(f"Error Sheets: {e}")
    return False

def riwayat_laporan(request):
    tanggal_str = request.GET.get('tanggal', str(date.today()))
    kelas_selected = request.GET.get('kelas', 'XA')
    nama_list = DATA_SANTRI.get(kelas_selected, [])
    santris = [{'id': i, 'nama': nama} for i, nama in enumerate(nama_list)]
    
    return render(request, 'monitoring/riwayat.html', {
        'santris': santris,
        'tanggal_sekarang': tanggal_str,
        'kelas_list': KELAS_CHOICES,
        'kelas_selected': kelas_selected,
    })

def simpan_laporan(request):
    if request.method == 'POST':
        tanggal = request.POST.get('tanggal')
        kelas = request.POST.get('kelas_hidden')
        names = request.POST.getlist('santri_nama')
        hadir = request.POST.getlist('status_kehadiran')
        khatam = request.POST.getlist('jumlah_khatam')
        h_awal = request.POST.getlist('hal_awal')
        h_akhir = request.POST.getlist('hal_akhir')
        
        data_sheet = []
        waktu = datetime.now().strftime("%d/%m/%Y %H:%M")
        
        for i in range(len(names)):
            awal = h_awal[i] if h_awal[i] else "0"
            akhir = h_akhir[i] if h_akhir[i] else "0"
            jml = int(akhir) - int(awal) + 1 if (int(akhir) >= int(awal) and int(awal) > 0) else 0
            data_sheet.append([waktu, tanggal, "User", kelas, names[i], hadir[i], khatam[i], awal, akhir, jml])
            
        if data_sheet:
            kirim_ke_spreadsheet(data_sheet)
    return redirect(f"/?tanggal={tanggal}&kelas={kelas}")
