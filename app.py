import streamlit as st
import pandas as pd
import data_manager as dm

# --- 1. SAYFA AYARLARI (En başta olmalı) ---
st.set_page_config(
    page_title="Kripto Takipçisi",
    page_icon="🪙",
    layout="wide",  # Geniş ekran modu
    initial_sidebar_state="expanded"
)

# --- 2. CSS İLE GÖRSEL DÜZENLEMELER (Opsiyonel Süsleme) ---
st.markdown("""
<style>
    .big-font { font-size:30px !important; font-weight: bold; }
    .metric-card { background-color: #f0f2f6; padding: 15px; border-radius: 10px; margin-bottom: 10px; }
</style>
""", unsafe_allow_html=True)

# --- 3. KENAR ÇUBUĞU (SIDEBAR) ---
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/4/46/Bitcoin.svg/1200px-Bitcoin.svg.png", width=50)
    st.title("Crypto Tracker")
    st.markdown("---")

    # Menü Seçimi
    menu = st.radio(
        "Menü",
        ["🏠 Piyasa Özeti", "🔍 Detaylı Analiz", "💱 Çevirici"]
    )

    st.markdown("---")

    # Para Birimi Seçimi
    st.subheader("Ayarlar")
    currency = st.selectbox("Para Birimi", ["usd", "try", "eur"], index=0)

    st.info(f"Seçilen Kur: {currency.upper()}")

# --- 4. SAYFA YÖNETİMİ ---

# ==========================================
# 🏠 SAYFA 1: PİYASA ÖZETİ (MARKET OVERVIEW)
# ==========================================
if menu == "🏠 Piyasa Özeti":
    st.title("📈 Canlı Piyasa Verileri")
    st.markdown(f"Piyasadaki **Top 100** coinin **{currency.upper()}** bazındaki anlık durumudur.")

    # Veriyi çek (Cache sayesinde hızlı gelir)
    with st.spinner('Veriler yükleniyor...'):
        df = dm.get_top_coins(currency=currency, limit=100)

    if not df.empty:
        # Metrikler (En tepede genel bakış)
        col1, col2, col3 = st.columns(3)
        top_coin = df.iloc[0]  # Bitcoin

        col1.metric("En Değerli Coin", top_coin['Coin'], f"{top_coin['Fiyat']} {currency.upper()}")

        # 24s Değişim rengini ayarlayalım
        degisim = top_coin['24s Değişim (%)']
        col2.metric("Bitcoin 24s Değişim", f"%{degisim:.2f}", delta=f"{degisim:.2f}")

        # Tabloyu Göster
        # use_container_width=True -> Tabloyu ekran genişliğine yayar
        st.dataframe(df, use_container_width=True, height=800)
    else:
        st.error("Veri çekilemedi. Lütfen internet bağlantınızı kontrol edin.")

# ==========================================
# 🔍 SAYFA 2: DETAYLI ANALİZ (DEEP DIVE)
# ==========================================
elif menu == "🔍 Detaylı Analiz":
    st.title("🔍 Detaylı Coin Analizi")

    # Coin Listesini Getir (Selectbox için)
    coin_list = dm.get_coin_list()

    # Varsayılan olarak Bitcoin seçili gelsin
    default_index = coin_list.index('bitcoin') if 'bitcoin' in coin_list else 0

    # Seçim Kutusu
    col1, col2 = st.columns([3, 1])
    with col1:
        selected_coin_id = st.selectbox("İncelemek istediğiniz coini seçin:", coin_list, index=default_index)
    with col2:
        days = st.selectbox("Zaman Aralığı", ["1", "7", "30", "90", "365"], index=2)

    # Detayları Çek
    if selected_coin_id:
        with st.spinner(f'{selected_coin_id} verileri getiriliyor...'):
            details = dm.get_coin_details(selected_coin_id)
            history_df = dm.get_coin_history(selected_coin_id, days, currency)

        if details:
            # --- Üst Bilgi Kartı (Header) ---
            head_col1, head_col2 = st.columns([1, 6])
            with head_col1:
                if details['image']:
                    st.image(details['image'], width=100)
            with head_col2:
                st.header(f"{details['name']} ({details['symbol']})")
                st.markdown(f"[Resmi Web Sitesi]({details['homepage']})")

            st.divider()

            # --- İstatistikler (Metrics) ---
            m1, m2, m3, m4 = st.columns(4)

            curr_sym = currency.upper()  # USD, TRY vb.

            m1.metric("Anlık Fiyat", f"{details['current_price']:,} {curr_sym}")
            m2.metric("Piyasa Değeri", f"{details['market_cap']:,} {curr_sym}")
            m3.metric("Rekor (ATH)", f"{details['ath']:,} {curr_sym}")
            m4.metric("ATH Tarihi", str(details['ath_date'])[:10])  # Sadece tarihi al (saati at)

            st.divider()

            # --- Grafik Bölümü ---
            st.subheader(f"Fiyat Grafiği ({days} Günlük)")
            if not history_df.empty:
                # Area chart, line chart'tan daha dolgun durur
                st.line_chart(history_df, color="#7FFF00")
            else:
                st.warning("Grafik verisi bulunamadı.")

            # --- Hakkında Bölümü ---
            st.subheader(f"{details['name']} Hakkında")
            with st.expander("Detaylı Açıklamayı Oku", expanded=False):
                if details['description']:
                    # HTML içeriğini render etmek için
                    st.markdown(details['description'], unsafe_allow_html=True)
                else:
                    st.info("Açıklama bulunamadı.")
        else:
            st.error("Coin detayları alınamadı.")

# ==========================================
# 💱 SAYFA 3: ÇEVİRİCİ (CONVERTER)
# ==========================================
elif menu == "💱 Çevirici":
    st.title("💱 Kripto Para Çevirici")
    st.markdown("Anlık piyasa verilerini kullanarak dönüşüm yapın.")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Elimdeki Coin")
        coin_list = dm.get_coin_list()
        # Varsayılan BTC
        idx_btc = coin_list.index('bitcoin') if 'bitcoin' in coin_list else 0
        src_coin = st.selectbox("Coin Seç", coin_list, index=idx_btc, key="src_coin")

        amount = st.number_input("Miktar Girin", min_value=0.0, value=1.0, step=0.1, format="%.4f")

    with col2:
        st.subheader("Hedef Para Birimi")
        target_currency = st.selectbox("Para Birimi Seç", ["usd", "try", "eur"], key="target_curr")

        # Hesapla Butonu
        if st.button("Hesapla", type="primary"):
            # Fiyatı çekmek için detay fonksiyonunu kullanabiliriz veya basit price fonksiyonu
            # Burada pratik olsun diye CoinGecko'nun basit get_price fonksiyonunu kullanacağız
            # Ancak data_manager içinde buna özel bir fonksiyon yazmadıysak,
            # DataManager'a gidip basit bir fiyat fonksiyonu ekleyebilirsin.
            # Şimdilik burada direkt çağıralım:

            try:
                # Anlık fiyatı alalım
                cg = dm.cg  # data_manager içindeki cg nesnesine eriştik
                price_data = cg.get_price(ids=src_coin, vs_currencies=target_currency)

                if src_coin in price_data:
                    unit_price = price_data[src_coin][target_currency]
                    total = unit_price * amount

                    st.success("Hesaplama Başarılı!")
                    st.metric(
                        label=f"{amount} {src_coin.upper()} eşittir:",
                        value=f"{total:,.2f} {target_currency.upper()}",
                        delta=f"1 {src_coin.upper()} = {unit_price} {target_currency.upper()}"
                    )
                else:
                    st.error("Fiyat bilgisi alınamadı.")
            except Exception as e:
                st.error(f"Hata: {e}")

# --- Alt Bilgi ---
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: gray;'>
    Veriler <b>CoinGecko API</b> tarafından sağlanmaktadır. | Developed with ❤️ via Streamlit
    </div>
    """,
    unsafe_allow_html=True
)
