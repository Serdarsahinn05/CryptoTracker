import streamlit as st
import pandas as pd
from pycoingecko import CoinGeckoAPI

# 1. API nesnesini başlat (Global olarak bir kere çalışır)
cg = CoinGeckoAPI()


# --- YARDIMCI FONKSİYONLAR ---

@st.cache_data(ttl=300)  # 5 Dakika boyunca hafızada tut
def get_top_coins(currency='usd', limit=100):
    """
    Ana Sayfa için piyasadaki en popüler coinleri getirir.

    Parametreler:
    - currency (str): Para birimi (örn: 'usd', 'try').
    - limit (int): Kaç coin getirilsin (örn: 100).

    Döndürür:
    - pd.DataFrame: Sıralama, İsim, Fiyat, Değişim vb. içeren tablo.
    """
    try:

        # 1. API'den veriyi çekiyoruz
        # vs_currency: Hangi para birimi (usd, try)
        # order: Piyasa değerine göre sırala (market_cap_desc)
        data = cg.get_coins_markets(
            vs_currency=currency,
            order='market_cap_desc',
            per_page=limit,
            page=1,
            sparkline=False
        )

        # 2. Gelen listeyi Pandas Tablosuna çeviriyoruz
        df = pd.DataFrame(data)

        # 3. Bize lazım olan sütunları seçiyoruz (API çok fazla gereksiz bilgi dönüyor)
        # 'image' sütununu da aldık, ileride logo göstermek istersen diye.
        selected_columns = [
            'market_cap_rank',
            'name',
            'symbol',
            'current_price',
            'price_change_percentage_24h',
            'market_cap'
        ]
        df = df[selected_columns]

        # 4. Sütun isimlerini daha şık/Türkçe hale getiriyoruz
        df.columns = [
            'Sıralama',
            'Coin',
            'Sembol',
            'Fiyat',
            '24s Değişim (%)',
            'Piyasa Değeri'
        ]
        # 5. Kozmetik Düzeltmeler
        # Sembolleri büyük harf yap (btc -> BTC)
        df['Sembol'] = df['Sembol'].str.upper()

        # Sıralama sütununu index (başlık) yapıyoruz ki sol tarafta 0,1,2 diye python indexi çıkmasın
        df.set_index('Sıralama', inplace=True)

        return df  # Şimdilik boş dönüyor

    except Exception as e:
        st.error(f"Veri çekilirken hata oluştu: {e}")
        return pd.DataFrame()


@st.cache_data(ttl=600)  # 10 Dakika boyunca değişmez (Listeler sık değişmez)
def get_coin_list():
    """
    Selectbox (Açılır kutu) için sadece Coin İsimlerini ve ID'lerini getirir.

    Döndürür:
    - list: Coin ID'lerinin listesi (örn: ['bitcoin', 'ethereum', ...])
    """
    try:

        all_coins = cg.get_coins_list()

        coin_ids = [coin['id'] for coin in all_coins]

        coin_ids.sort()

        return coin_ids
    except Exception as e:
        print(e)
        return []


@st.cache_data(ttl=60)  # 1 Dakika cache (Fiyat grafiği taze olsun)
def get_coin_history(coin_id, days, currency='usd'):
    """
    Seçilen coinin geçmiş fiyat verilerini grafiğe dökmek için çeker.

    Parametreler:
    - coin_id (str): Coinin ID'si (örn: 'bitcoin').
    - days (str/int): Kaç günlük veri (örn: '7', '30', 'max').

    Döndürür:
    - pd.DataFrame: Tarih ve Fiyat sütunları olan temiz tablo.
    """
    try:

        # 1. API'den veriyi çekiyoruz
        # chart_data şuna benzer bir sözlük döner:
        # {'prices': [[1600000000000, 35000], [1600000300000, 35100]], ...}
        chart_data = cg.get_coin_market_chart_by_id(
            id=coin_id,
            vs_currency=currency,
            days=days
        )

        # 2. Sadece 'prices' (fiyatlar) listesini alıp DataFrame yapıyoruz
        # Sütunlar: Zaman Damgası (TimeStamp) ve Fiyat
        df = pd.DataFrame(chart_data['prices'], columns=['TimeStamp', 'Fiyat'])

        # 3. ZAMAN DÖNÜŞÜMÜ (En Kritik Adım) 🕒
        # API zamanı milisaniye (ms) olarak verir. Bunu tarihe çeviriyoruz.
        df['Tarih'] = pd.to_datetime(df['TimeStamp'], unit='ms')

        # 4. Tabloyu Düzenleme
        # Zaman damgası artık gereksiz, siliyoruz veya index yapıyoruz.
        # Grafikler genelde index'teki tarihi kullanır.
        df.set_index('Tarih', inplace=True)

        # Gereksiz ham sütunu atalım
        df.drop(columns=['TimeStamp'], inplace=True)

        return df
    except Exception as e:
        st.error(f"Grafik verisi alınamadı: {e}")
        return pd.DataFrame()


@st.cache_data(ttl=60)
def get_coin_details(coin_id):
    """
    Coin Analiz sayfası için detaylı bilgileri (Logo, Açıklama, ATH) getirir.

    Parametreler:
    - coin_id (str): Coinin ID'si.

    Döndürür:
    - dict: İhtiyacımız olan tüm detaylar (description, image, market_data vb.)
    """
    try:

        # 1. API İsteği (Optimizasyonlu)
        # localization=false -> Sadece İngilizce yeterli (hız kazandırır)
        # tickers=false -> Hangi borsada kaç para olduğu bilgisi gereksiz (çok yer kaplar)
        data = cg.get_coin_by_id(
            id=coin_id,
            localization='false',
            tickers=False,
            community_data=False,
            developer_data=False,
            sparkline=False
        )

        # 2. Ham veriyi temiz bir sözlüğe (dictionary) çeviriyoruz.
        # .get() kullanıyoruz ki eğer veri yoksa program patlamasın, None dönsün.
        details = {
            'name': data.get('name'),
            'symbol': data.get('symbol', '').upper(),
            'image': data.get('image', {}).get('large'),  # Büyük boy logo
            'description': data.get('description', {}).get('en'),  # İngilizce açıklama
            'homepage': data.get('links', {}).get('homepage', [''])[0],  # Resmi Web Sitesi

            # Piyasa Verileri (Varsayılan olarak USD çekiyoruz)
            # data['market_data'] içinde fiyatlar durur
            'current_price': data['market_data']['current_price'].get('usd'),
            'market_cap': data['market_data']['market_cap'].get('usd'),

            # ATH = All Time High (Tüm Zamanların En Yükseği)
            'ath': data['market_data']['ath'].get('usd'),
            'ath_date': data['market_data']['ath_date'].get('usd'),

            # 24 Saatlik En Yüksek / En Düşük
            'high_24h': data['market_data']['high_24h'].get('usd'),
            'low_24h': data['market_data']['low_24h'].get('usd')
        }

        return details
    except Exception as e:
        st.error(f"Detaylar alınamadı: {e}")
        return None
