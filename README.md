# Nike (NKE) BI Dashboard

**Ders:** İş Zekâsı ve Karar Verme — Vize Projesi

Bu dashboard, vize ödevinde tanımlanan karar problemini çözmek için Nike hisse verisini görselleştirir ve otomatik **AL / BEKLE / RİSK UYARISI** kararı üretir.

## 📁 Klasör İçeriği

| Dosya | Görev |
|---|---|
| `BIDashboard.py` | Ana Streamlit dashboard kodu (hocanın şablon yapısına uygun) |
| `NKE.csv` | Nike hisse veri seti (2000–2026, 6559 satır) |
| `requirements.txt` | Gerekli Python paketleri |
| `calistir.bat` | Windows için tek tıkla çalıştırma scripti |
| `OKUBENI.md` | Bu dosya |

## ⚙️ Kurulum

### 1. Python'ın yüklü olduğundan emin ol
```
python --version
```
Eğer "command not found" diyorsa [python.org](https://www.python.org/downloads/) üzerinden yükle. Kurulum sırasında **"Add Python to PATH"** kutusunu işaretle.

### 2. Gerekli paketleri kur
Bu klasörün içinde PowerShell / CMD aç ve:
```
pip install -r requirements.txt
```
Veya tek tek:
```
pip install streamlit pandas numpy plotly
```

### 3. Dashboard'u çalıştır

**Kolay yol (Windows):** `calistir.bat` dosyasına çift tıkla.

**Manuel yol:**
```
streamlit run BIDashboard.py
```

Komut çalışınca tarayıcın otomatik olarak `http://localhost:8501` adresini açacak. Açmazsa bu adresi kendin yaz.

**Kapatmak için:** Terminal penceresinde `Ctrl+C`.

## 🎯 Dashboard'da Neler Var?

Vize Ödevi PDF'indeki tüm gereksinimler dashboard'a yansıtılmıştır:

- **Karar problemi**: Nike hissesi için son 6 yıl profilleri karşılaştırması (hangi yıl yatırım için en uygun?)
- **3 KPI** (ödevde belirlenen, 2'si çıkarılmıştır):
  - **Volatilite** (ağırlık 0.40) — küçük değer iyi
  - **MA30 Trend** (ağırlık 0.35) — büyük değer iyi
  - **Hacim** (ağırlık 0.25) — büyük değer iyi
- **Min-Max Normalizasyon** — 0-1 aralığına ölçekleme
- **Ağırlıklandırma** — sidebar'daki slider'larla dinamik değiştirilebilir
- **Toplam Skor + Sıralama** — en iyi dönem üstte
- **KPI Kartları** — üstte 5 metrik (geçen yılla karşılaştırmalı)
- **Grafikler**:
  - Bar (yıllık volatilite)
  - Line (yıllık trend)
  - Pie (ağırlık dağılımı)
  - Yığılmış Bar (skor bileşenleri)
- **Detaylı tablo** — ara hesapların tamamı
- **Min-Max Analiz Tablosu** — tüm veri seti için
- **Güncel Karar** — son günün AL / BEKLE / RİSK UYARISI çıktısı
- **Yönetici yorumu + Tartışma sorusu**

## 🖼️ Rapor İçin Alacağın Ekran Görüntüleri

1. Dashboard ana ekran (KPI kartları + grafikler görünecek şekilde)
2. Normalizasyon + skor tablosu
3. Yığılmış bar (skor bileşenleri)
4. Güncel karar kutusu (AL / BEKLE / RİSK UYARISI rozetini gösteren)
5. Farklı ağırlık denemesi — sidebar'daki slider'ları değiştirip sıralamanın nasıl değiştiğini göster

## 📝 Hocanın Şablon Yapısı Koruma Durumu

Hocanın orijinal `BIDashboard.py` şablonundaki tüm yapısal öğeler korundu:

| Şablon Öğesi | Korundu mu? |
|---|---|
| `normalize_series()` fonksiyonu (higher_is_better) | ✅ Birebir |
| `raw_df` (alternatifler tablosu) | ✅ Nike yıllık özeti |
| `previous_month` dict (% değişim için) | ✅ 2019 referansı |
| Sidebar KPI ağırlık slider'ları | ✅ 3 slider |
| Otomatik normalize checkbox | ✅ Aynı |
| multiselect (birim/dönem seçimi) | ✅ Yıl seçimi |
| N_* ve Skor_* kolonları | ✅ Aynı yapı |
| Toplam Skor + Sıralama | ✅ Aynı |
| 5 KPI metrik kartı | ✅ Aynı |
| 3'lü grafik (bar, line, pie) | ✅ Aynı |
| Formül açıklama expander | ✅ Aynı |
| Detay tablo | ✅ Aynı |
| Yığılmış bar skor bileşenleri | ✅ Aynı |
| Karar önerisi + tartışma sorusu | ✅ Aynı |

Sadece içerik Nike'a uyarlanmıştır — poliklinik örneği yerine yıllık hisse profilleri.

## ❓ Sorun Giderme

- **`ModuleNotFoundError: No module named 'streamlit'`**
  → `pip install streamlit pandas numpy plotly` çalıştır.

- **`NKE.csv` bulunamadı hatası**
  → NKE.csv'nin `BIDashboard.py` ile **aynı klasörde** olduğundan emin ol.

- **Port 8501 zaten kullanımda**
  → `streamlit run BIDashboard.py --server.port 8502` ile farklı port kullan.

- **Türkçe karakterler bozuk**
  → Dosya UTF-8 olarak kaydedildi, modern Python sürümlerinde sorun olmamalı. Python 3.7+ kullan.
