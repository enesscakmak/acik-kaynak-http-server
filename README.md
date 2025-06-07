# HTTP Server

Basit bir HTTP sunucusu uygulaması. TCP socket üzerinden çalışır ve temel HTTP özelliklerini destekler.

## Özellikler

- TCP socket üzerinden GET istekleri
- `/static` dizininden dosya sunumu
- `/api/hello` endpoint'inden JSON döndürme
- MIME type yönetimi

## Kurulum

### Gereksinimler

- Python 3.9 veya üzeri
- pip (Python paket yöneticisi)

### Yerel Kurulum

1. Projeyi klonlayın:
```bash
git clone [repo-url]
cd http-server
```

2. Bağımlılıkları yükleyin:
```bash
pip install -r requirements.txt
```

3. Sunucuyu başlatın:
```bash
python server.py
```

Sunucu varsayılan olarak `http://localhost:8080` adresinde çalışacaktır.

### Docker ile Kurulum

1. Docker image'ını oluşturun:
```bash
docker build -t http-server .
```

2. Container'ı çalıştırın:
```bash
docker run -p 8080:8080 http-server
```

## Kullanım

### Endpoint'ler

1. `/api/hello`
   - HTTP Method: GET
   - Response: JSON formatında "Hello, World!" mesajı
   - Örnek: `curl http://localhost:8080/api/hello`

2. `/static/*`
   - HTTP Method: GET
   - Response: İstenen statik dosya
   - Örnek: `curl http://localhost:8080/static/hello.txt`

## Lisans

Bu proje MIT lisansı altında lisanslanmıştır. Detaylar için [LICENSE](LICENSE) dosyasına bakın.

## Katkıda Bulunma

1. Bu repository'yi fork edin
2. Feature branch'i oluşturun (`git checkout -b feature/amazing-feature`)
3. Değişikliklerinizi commit edin (`git commit -m 'Add some amazing feature'`)
4. Branch'inizi push edin (`git push origin feature/amazing-feature`)
5. Pull Request oluşturun

## Davranış Kuralları

Bu projeye katkıda bulunurken lütfen [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) dosyasındaki kurallara uyun. 