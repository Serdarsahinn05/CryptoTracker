# Crypto Tracker 🪙

Streamlit ve CoinGecko API kullanılarak geliştirilmiş, anlık kripto para piyasasını takip etmenizi sağlayan web tabanlı bir analiz aracı.

## 🚀 Özellikler

Uygulama 3 ana modülden oluşur:

1.  **🏠 Piyasa Özeti:**
    * Piyasa değerine göre Top 100 coinin anlık verileri.
    * USD, TRY veya EUR bazında listeleme.
    * En değerli coin ve Bitcoin değişim metrikleri.
2.  **🔍 Detaylı Analiz:**
    * Seçilen herhangi bir coinin (Bitcoin, Ethereum vb.) detaylı incelenmesi.
    * Fiyat grafikleri (1 günden 1 yıla kadar).
    * ATH (En yüksek değer), Piyasa Değeri gibi kritik metrikler.
    * Proje hakkında detaylı açıklamalar.
3.  **💱 Çevirici:**
    * Anlık kur verileriyle kripto paraları birbirine veya itibari paraya (Fiyat) çevirme.

## 🛠️ Teknolojiler

* **Python 3.x**
* **Streamlit:** Arayüz geliştirme.
* **Pandas:** Veri manipülasyonu ve tablolar.
* **PyCoinGecko:** CoinGecko API istemcisi.

## 💻 Kurulum ve Çalıştırma

Projeyi bilgisayarınızda çalıştırmak için:

1.  **Projeyi Klonlayın:**
    ```bash
    git clone [https://github.com/KULLANICI_ADIN/CryptoTracker.git](https://github.com/KULLANICI_ADIN/CryptoTracker.git)
    cd CryptoTracker
    ```

2.  **Gerekli Kütüphaneleri Yükleyin:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Uygulamayı Başlatın:**
    ```bash
    streamlit run app.py
    ```

## ⚠️ API Notu
Bu proje ücretsiz **CoinGecko API** kullanmaktadır. Çok sık istek gönderirseniz (örneğin sayfayı saniyede bir yenilerseniz) geçici olarak API engeli yiyebilirsiniz ("Rate Limit"). Veriler `st.cache_data` ile önbelleğe alınarak bu durum minimize edilmiştir.

## 📝 Lisans
Bu proje eğitim amaçlı geliştirilmiştir.

---
**Geliştirici:** [Serdarsahinn05](https://github.com/KULLANICI_ADIN)
