#!/usr/bin/env python
# coding: utf-8

# ======================================================================
# İŞ ZEKÂSI VE KARAR VERME — VİZE ÖDEVİ
# Nike (NKE) Hisse Senedi Karar Destek Dashboard'u
# ----------------------------------------------------------------------
# Bu dashboard, hocanın paylaştığı şablon yapısı takip edilerek
# Nike hisse veri setine uyarlanmıştır. Poliklinik örneği yerine
# son 6 yıl (2020-2025) alternatifler olarak alınmış, her yıl için
# vize ödevinde belirlenen 3 KPI (Volatilite, MA30 Trend, Hacim)
# hesaplanmış ve karar destek sistemi kurulmuştur.
# ======================================================================

# Streamlit arayüzünü oluşturmak için temel kütüphane
import streamlit as st
# Veri tablolarını yönetmek için pandas
import pandas as pd
# Sayısal işlemler ve sıralama için numpy
import numpy as np
# Hızlı ve etkileşimli grafikler için Plotly Express
import plotly.express as px
# İleri seviye grafik özelleştirmeleri için Plotly Graph Objects
import plotly.graph_objects as go

# Sayfa başlığı ve geniş yerleşim ayarı
st.set_page_config(page_title="Nike BI Dashboard — İş Zekâsı ve Karar Verme", layout="wide")

# ----------------------------------------------------------------------
# Yardımcı fonksiyonlar
# ----------------------------------------------------------------------
def normalize_series(series: pd.Series, higher_is_better: bool = True) -> pd.Series:
    """
    Farklı ölçeklerdeki KPI'ları 0-1 aralığına taşır.

    higher_is_better=True ise büyük değer daha iyidir.
    Örn: hacim, pozitif trend, piyasa ilgisi.

    higher_is_better=False ise küçük değer daha iyidir.
    Örn: volatilite, risk, fiyat dalgalanması.
    """
    min_val = series.min()
    max_val = series.max()

    # Tüm değerler aynıysa payda sıfır olur.
    # Bu durumda tüm birimlere 1.0 vererek hesap hatasını önlüyoruz.
    if max_val == min_val:
        norm = pd.Series([1.0] * len(series), index=series.index)
    else:
        norm = (series - min_val) / (max_val - min_val)

    # Küçük değer iyi ise skoru ters çeviriyoruz.
    return norm if higher_is_better else 1 - norm


@st.cache_data
def nike_csv_yukle(yol: str = "NKE.csv") -> pd.DataFrame:
    """
    NKE.csv dosyasını okur ve KPI'ları hesaplar.
    Tarih kolonu M/D/YYYY formatında olduğu için açıkça parse ediyoruz.
    """
    df = pd.read_csv(yol)
    df['Date'] = pd.to_datetime(df['Date'], format='%m/%d/%Y')
    df = df.sort_values('Date').reset_index(drop=True)

    # KPI hesaplamaları (günlük bazda)
    df['Daily_Return'] = df['Close'].pct_change()
    df['Volatility']   = df['Daily_Return'].rolling(window=30).std()
    df['MA30']         = df['Close'].rolling(window=30).mean()
    df['HL_Spread']    = df['High'] - df['Low']
    # Trend gücü: Close/MA30 oranı (>1 yukarı trend, <1 aşağı trend)
    df['Trend_Gucu']   = df['Close'] / df['MA30']

    df['Yıl'] = df['Date'].dt.year
    return df


def yillik_ozet(df: pd.DataFrame, yillar: list) -> pd.DataFrame:
    """
    Seçilen yıllar için ortalama KPI değerlerini hesaplar.
    Her satır bir yılı (alternatifi) temsil eder.
    """
    kayitlar = []
    for y in yillar:
        alt = df[df['Yıl'] == y]
        if len(alt) < 30:
            continue
        kayitlar.append({
            'Dönem': f'{y} Yılı',
            'Ortalama Volatilite':   alt['Volatility'].mean(),
            'Ortalama Trend (Close/MA30)': alt['Trend_Gucu'].mean(),
            'Ortalama Hacim (Milyon)':  alt['Volume'].mean() / 1_000_000,
            'Yıl Sonu Kapanış ($)':    alt['Close'].iloc[-1],
            'Günlük Getiri Ort. (%)':  alt['Daily_Return'].mean() * 100,
        })
    return pd.DataFrame(kayitlar)


# ----------------------------------------------------------------------
# VERİ SETİ — Nike (NKE) Yıllık Özet
# ----------------------------------------------------------------------
# --------------------------------------------------------------
# VERİ SETİ HAZIRLIĞI
# Bu tablo, Nike hissesinin son 6 yıldaki yıllık özetlerini
# karar alternatifleri olarak temsil eder.
# Her satır bir yıl, her sütun ise bir KPI'dır.
# --------------------------------------------------------------
try:
    ham_df = nike_csv_yukle("NKE.csv")
except FileNotFoundError:
    st.error(
        "❌ `NKE.csv` dosyası bulunamadı. "
        "Lütfen NKE.csv dosyasını `BIDashboard.py` ile aynı klasöre koyun."
    )
    st.stop()

# Son 6 yıl — alternatifler olarak ele alınıyor
SON_YILLAR = [2020, 2021, 2022, 2023, 2024, 2025]
raw_df = yillik_ozet(ham_df, SON_YILLAR)

# Önceki dönem referansı: 2019 yılı ortalamaları (KPI kartlarındaki % değişim için)
onceki = ham_df[ham_df['Yıl'] == 2019]
previous_month = {
    "Ortalama Volatilite":           onceki['Volatility'].mean(),
    "Ortalama Trend (Close/MA30)":   onceki['Trend_Gucu'].mean(),
    "Ortalama Hacim (Milyon)":       onceki['Volume'].mean() / 1_000_000,
    "Yıl Sonu Kapanış ($)":          onceki['Close'].iloc[-1] if len(onceki) else 0,
}

# ----------------------------------------------------------------------
# Ana başlıklar
# ----------------------------------------------------------------------
st.title("📊 Nike (NKE) İş Zekâsı ve Karar Verme Dashboard'u")
st.subheader("Streamlit ile KPI Tabanlı Yatırım Kararı Dashboard'u")

with st.container():
    st.info(
        "**Karar problemi:** Nike (NKE) hisse senedi için son 6 yıl profilleri arasında "
        "hangisi yatırım açısından en uygun görünüm sunuyor? Bu dashboard, vize ödevinde "
        "belirlenen KPI seçimi, ağırlıklandırma, normalizasyon ve toplam skor mantığını "
        "birlikte göstermekte; ayrıca güncel dönem için **AL / BEKLE / RİSK UYARISI** "
        "karar çıktısı üretmektedir."
    )

# ----------------------------------------------------------------------
# Sidebar kontrolleri
# ----------------------------------------------------------------------
# --------------------------------------------------------------
# SIDEBAR: Kullanıcının ağırlıkları değiştirerek karar sonucunu test etmesi
# --------------------------------------------------------------
st.sidebar.header("⚙️ Dashboard Ayarları")

st.sidebar.markdown("### KPI Ağırlıkları")
st.sidebar.caption("(Vize ödevindeki varsayılanlar: 0.40 / 0.35 / 0.25)")

# Volatilite ağırlığı (risk)
w_vol = st.sidebar.slider("Volatilite (Risk)", 0.0, 1.0, 0.40, 0.05)
# MA30 trend ağırlığı
w_ma  = st.sidebar.slider("MA30 Trend",        0.0, 1.0, 0.35, 0.05)
# Hacim ağırlığı (likidite)
w_vlm = st.sidebar.slider("Hacim (Likidite)",  0.0, 1.0, 0.25, 0.05)

weight_sum = w_vol + w_ma + w_vlm
# Kullanıcı toplamı tam 1.00 yapmasa bile, sistem ağırlıkları otomatik normalize edebilir.
normalize_weights = st.sidebar.checkbox("Ağırlıkları otomatik normalize et", value=True)

# Ağırlıkları sözlük yapısında topluyoruz.
weights = {
    "Ortalama Volatilite":         w_vol,
    "Ortalama Trend (Close/MA30)": w_ma,
    "Ortalama Hacim (Milyon)":     w_vlm,
}

if normalize_weights:
    if weight_sum == 0:
        st.sidebar.error("Ağırlık toplamı 0 olamaz.")
        st.stop()

    # Girilen ağırlıkları kendi toplamlarına bölerek 1.00 seviyesine çekiyoruz.
    # Böylece öğrenciler toplam hatası yapsa bile hesaplama devam eder.
    weights = {k: v / weight_sum for k, v in weights.items()}
    weight_sum = sum(weights.values())

st.sidebar.markdown(f"**Ağırlık Toplamı:** {weight_sum:.2f}")

st.sidebar.markdown("---")
selected_units = st.sidebar.multiselect(
    "Gösterilecek dönemler",
    options=raw_df["Dönem"].tolist(),
    default=raw_df["Dönem"].tolist(),
)

if not selected_units:
    st.warning("Lütfen en az bir dönem seçiniz.")
    st.stop()

df = raw_df[raw_df["Dönem"].isin(selected_units)].copy()

# ----------------------------------------------------------------------
# Normalizasyon ve skorlar
# ----------------------------------------------------------------------
# --------------------------------------------------------------
# NORMALİZASYON ADIMI
# Her KPI ortak ölçeğe getiriliyor.
# Volatilite için küçük değer iyi (risk düşük),
# Trend ve Hacim için büyük değer iyi.
# --------------------------------------------------------------
df["N_Volatilite"] = normalize_series(df["Ortalama Volatilite"],          higher_is_better=False)
df["N_Trend"]      = normalize_series(df["Ortalama Trend (Close/MA30)"],  higher_is_better=True)
df["N_Hacim"]      = normalize_series(df["Ortalama Hacim (Milyon)"],      higher_is_better=True)

# --------------------------------------------------------------
# AĞIRLIKLI SKOR HESAPLAMA
# Her normalize KPI, kendi ağırlığı ile çarpılır.
# --------------------------------------------------------------
df["Skor_Volatilite"] = df["N_Volatilite"] * weights["Ortalama Volatilite"]
df["Skor_Trend"]      = df["N_Trend"]      * weights["Ortalama Trend (Close/MA30)"]
df["Skor_Hacim"]      = df["N_Hacim"]      * weights["Ortalama Hacim (Milyon)"]

# Tüm bileşenler toplanarak nihai karar puanı elde edilir.
df["Toplam Skor"] = (
    df["Skor_Volatilite"]
    + df["Skor_Trend"]
    + df["Skor_Hacim"]
)

df = df.sort_values("Toplam Skor", ascending=False).reset_index(drop=True)
df["Sıralama"] = np.arange(1, len(df) + 1)

# İlk satır en iyi, son satır en düşük profilli dönemi temsil eder.
best_unit  = df.iloc[0]
worst_unit = df.iloc[-1]

# ----------------------------------------------------------------------
# Üst KPI kartları
# ----------------------------------------------------------------------
avg_vol = df["Ortalama Volatilite"].mean()
avg_ma  = df["Ortalama Trend (Close/MA30)"].mean()
avg_vlm = df["Ortalama Hacim (Milyon)"].mean()
avg_prc = df["Yıl Sonu Kapanış ($)"].mean()

# --------------------------------------------------------------
# KPI KARTLARI
# Üst kısımda yöneticinin ilk bakışta göreceği özet göstergeler yer alır.
# --------------------------------------------------------------
c1, c2, c3, c4, c5 = st.columns(5)

with c1:
    st.metric(
        "Ortalama Volatilite",
        f"{avg_vol:.4f}",
        delta=f"{((avg_vol - previous_month['Ortalama Volatilite']) / previous_month['Ortalama Volatilite']) * 100:+.1f}%",
        delta_color="inverse",   # volatilitede düşüş iyidir
    )

with c2:
    st.metric(
        "Ortalama Trend (Close/MA30)",
        f"{avg_ma:.3f}",
        delta=f"{((avg_ma - previous_month['Ortalama Trend (Close/MA30)']) / previous_month['Ortalama Trend (Close/MA30)']) * 100:+.1f}%",
    )

with c3:
    st.metric(
        "Ortalama Hacim",
        f"{avg_vlm:.1f} M",
        delta=f"{((avg_vlm - previous_month['Ortalama Hacim (Milyon)']) / previous_month['Ortalama Hacim (Milyon)']) * 100:+.1f}%",
    )

with c4:
    st.metric(
        "Ortalama Yıl Sonu Kapanış",
        f"${avg_prc:.2f}",
        delta=f"{((avg_prc - previous_month['Yıl Sonu Kapanış ($)']) / previous_month['Yıl Sonu Kapanış ($)']) * 100:+.1f}%",
    )

with c5:
    st.metric("En Yüksek Toplam Skor",
              f"{best_unit['Toplam Skor']:.3f}",
              f"{best_unit['Dönem']}")

# ----------------------------------------------------------------------
# Grafikler
# ----------------------------------------------------------------------
# --------------------------------------------------------------
# GRAFİK ALANI
# Farklı grafik türleriyle aynı karar problemini farklı açılardan gösteriyoruz.
# --------------------------------------------------------------
left, mid, right = st.columns((1.15, 1.15, 1))

with left:
    fig_vol = px.bar(
        df,
        x="Dönem",
        y="Ortalama Volatilite",
        title="Yıllık Ortalama Volatilite (Risk)",
        text_auto='.4f',
        color="Ortalama Volatilite",
        color_continuous_scale="Reds",
    )
    fig_vol.update_layout(height=350, showlegend=False, coloraxis_showscale=False)
    st.plotly_chart(fig_vol, use_container_width=True)

with mid:
    fig_trend = px.line(
        df.sort_values("Dönem"),
        x="Dönem",
        y="Ortalama Trend (Close/MA30)",
        markers=True,
        title="Yıllık Ortalama Trend (Close/MA30)",
    )
    fig_trend.add_hline(y=1.0, line_dash="dash", line_color="gray",
                        annotation_text="MA30 eşiği", annotation_position="bottom right")
    fig_trend.update_layout(height=350)
    st.plotly_chart(fig_trend, use_container_width=True)

with right:
    weight_df = pd.DataFrame(
        {
            "Kriter": ["Volatilite", "MA30 Trend", "Hacim"],
            "Ağırlık": list(weights.values()),
        }
    )
    fig_pie = px.pie(
        weight_df,
        values="Ağırlık",
        names="Kriter",
        hole=0.55,
        title="KPI Ağırlık Dağılımı",
        color_discrete_sequence=["#c53030", "#2c5282", "#38a169"],
    )
    fig_pie.update_layout(height=350)
    st.plotly_chart(fig_pie, use_container_width=True)

# ----------------------------------------------------------------------
# Normalizasyon mantığını göster
# ----------------------------------------------------------------------
st.markdown("### 📐 Normalizasyon ve Ağırlıklı Skor Tablosu")
show_math = st.expander("Formül ve açıklamayı göster")
with show_math:
    st.markdown(
        """
**Min-Max normalizasyonu:**

- Büyük değer iyiyse (örn. Trend, Hacim):
  `normalize = (x - min) / (max - min)`
- Küçük değer iyiyse (örn. Volatilite):
  `normalize = 1 - ((x - min) / (max - min))`

**Toplam skor:**

`Toplam Skor = (N_Volatilite × 0.40) + (N_Trend × 0.35) + (N_Hacim × 0.25)`

**Çıkarılan KPI'lar (vize ödevinde gerekçelendirilmiştir):**
- *High-Low Spread*: Volatilite ile bilgi tekrarı yapar.
- *Average Daily Return*: Çok dalgalı, tek başına yanıltıcıdır.
        """
    )

# Kullanıcının tüm ara hesapları görebilmesi için ayrıntılı tablo
score_view = df[
    [
        "Dönem",
        "Ortalama Volatilite",
        "Ortalama Trend (Close/MA30)",
        "Ortalama Hacim (Milyon)",
        "N_Volatilite",
        "N_Trend",
        "N_Hacim",
        "Skor_Volatilite",
        "Skor_Trend",
        "Skor_Hacim",
        "Toplam Skor",
        "Sıralama",
    ]
].copy()

for col in [
    "Ortalama Volatilite",
    "N_Volatilite",
    "N_Trend",
    "N_Hacim",
    "Skor_Volatilite",
    "Skor_Trend",
    "Skor_Hacim",
    "Toplam Skor",
]:
    score_view[col] = score_view[col].round(4)

score_view["Ortalama Trend (Close/MA30)"] = score_view["Ortalama Trend (Close/MA30)"].round(3)
score_view["Ortalama Hacim (Milyon)"]     = score_view["Ortalama Hacim (Milyon)"].round(2)

st.dataframe(score_view, use_container_width=True, hide_index=True)

# ----------------------------------------------------------------------
# Ağırlıklı skor kırılımı
# ----------------------------------------------------------------------
st.markdown("### 📊 Alternatiflerin Ağırlıklı Skor Kırılımı")
# Toplam skorun hangi bileşenlerden oluştuğunu göstermek için uzun formata çeviriyoruz.
stack_df = df[["Dönem", "Skor_Volatilite", "Skor_Trend", "Skor_Hacim"]].copy()
stack_df = stack_df.melt(id_vars="Dönem", var_name="Skor Türü", value_name="Değer")
label_map = {
    "Skor_Volatilite": "Volatilite (Risk)",
    "Skor_Trend":      "MA30 Trend",
    "Skor_Hacim":      "Hacim (Likidite)",
}
stack_df["Skor Türü"] = stack_df["Skor Türü"].map(label_map)
fig_stack = px.bar(
    stack_df,
    x="Dönem",
    y="Değer",
    color="Skor Türü",
    title="Toplam Skoru Oluşturan Bileşenler",
    color_discrete_map={
        "Volatilite (Risk)": "#c53030",
        "MA30 Trend":        "#2c5282",
        "Hacim (Likidite)":  "#38a169",
    },
)
fig_stack.update_layout(height=420)
st.plotly_chart(fig_stack, use_container_width=True)

# ----------------------------------------------------------------------
# Min-Max Analizi Tablosu (vize ödevinde istenen)
# ----------------------------------------------------------------------
st.markdown("### 📐 Min-Max Analizi (Tüm Veri Seti)")
st.caption(" ")

min_max = pd.DataFrame({
    "KPI": ["Volatilite", "Volume", "Moving Average (MA30)", "High-Low Spread (çıkarıldı)", "Günlük Getiri (çıkarıldı)"],
    "Min Değer": [
        f"{ham_df['Volatility'].min():.4f}",
        f"{ham_df['Volume'].min():,.0f}",
        f"{ham_df['MA30'].min():.2f}",
        f"{ham_df['HL_Spread'].min():.4f}",
        f"{ham_df['Daily_Return'].min():.4f}",
    ],
    "Max Değer": [
        f"{ham_df['Volatility'].max():.4f}",
        f"{ham_df['Volume'].max():,.0f}",
        f"{ham_df['MA30'].max():.2f}",
        f"{ham_df['HL_Spread'].max():.4f}",
        f"{ham_df['Daily_Return'].max():.4f}",
    ],
})
st.dataframe(min_max, use_container_width=True, hide_index=True)

# ----------------------------------------------------------------------
# Yönetici yorumu ve güncel karar (AL / BEKLE / RİSK UYARISI)
# ----------------------------------------------------------------------
st.markdown("---")
st.markdown("### 🎯 Karar Destek Sistemi — Güncel Durum")

# Son 30 günlük veriye göre karar üret
son = ham_df.iloc[-1]
vol_raw     = son['Volatility']
ma_raw      = son['MA30']
close_raw   = son['Close']
ort_hacim   = ham_df['Volume'].tail(30).mean()
hacim_orani = son['Volume'] / ort_hacim if ort_hacim else 1.0

# Vize ödevindeki karar kurallarını uygula
if pd.notna(vol_raw) and vol_raw > 0.03:
    guncel_karar = "RİSK UYARISI"
    karar_renk   = "🔴"
    karar_msg    = f"Volatilite ({vol_raw:.4f}) risk eşiğini (0.03) aşıyor. Mevcut koşullarda yatırım risklidir."
elif pd.notna(ma_raw) and close_raw <= ma_raw:
    guncel_karar = "BEKLE"
    karar_renk   = "🟡"
    karar_msg    = f"Kapanış (${close_raw:.2f}) MA30'un (${ma_raw:.2f}) altında — trend zayıf."
elif hacim_orani < 1.0:
    guncel_karar = "BEKLE"
    karar_renk   = "🟡"
    karar_msg    = f"Hacim oranı ({hacim_orani:.2f}) ortalamanın altında — likidite desteği yetersiz."
else:
    guncel_karar = "AL"
    karar_renk   = "🟢"
    karar_msg    = "Trend güçlü, risk kontrol altında, hacim yeterli — yatırım için uygun görünüm."

col_a, col_b = st.columns((1.3, 1))
with col_a:
    # Yöneticiye doğrudan sunulabilecek kısa karar çıktısı
    st.success(
        f"**Karar önerisi (En iyi dönem profili):** Mevcut ağırlıklandırmaya göre en yüksek "
        f"toplam skora sahip dönem **{best_unit['Dönem']}** görünmektedir. "
        f"Bu dönem {best_unit['Toplam Skor']:.3f} puan ile ilk sıradadır."
    )

    st.markdown(
        f"""
**Güncel Gün Kararı:** {karar_renk} **{guncel_karar}**

{karar_msg}

---

**Yönetici yorumu:**
- En güçlü alternatif dönem: **{best_unit['Dönem']}**
- En düşük profilli dönem: **{worst_unit['Dönem']}**
- Bu sonuç, seçilen ağırlıkların mevcut öncelikleri nasıl yansıttığını göstermektedir.
- Volatilite ağırlığı artırılırsa düşük riskli dönemler, trend ağırlığı artırılırsa yükseliş
  gösteren dönemler öne çıkar.
        """
    )

with col_b:
    st.warning(
        "**Tartışma sorusu:**  \n"
        "Ağırlıklar değişse karar değişir mi?  \n"
        "Özellikle Volatilite ağırlığını azaltıp Hacim ağırlığını yükselttiğinizde "
        "sıralamayı yeniden inceleyiniz. Ayrıca sidebar'daki dönem seçimini tek yıl "
        "bırakıp güncel karar motoruyla karşılaştırınız."
    )

    # Güncel KPI özet kutusu
    st.markdown("**📍 Son Gün KPI'ları:**")
    st.caption(f"Tarih: {son['Date'].strftime('%Y-%m-%d')}")
    st.caption(f"Volatilite: **{vol_raw:.4f}** (eşik: 0.03)")
    st.caption(f"Close/MA30: **{close_raw:.2f} / {ma_raw:.2f}**")
    st.caption(f"Hacim oranı: **{hacim_orani:.2f}** (eşik: 1.00)")

st.markdown("---")
st.caption(""
)
