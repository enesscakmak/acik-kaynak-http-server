# HTTP Server

TCP üzerinden çalışan basit bir sunucusu uygulaması.

## Özellikler

- TCP socket üzerinden GET istekleri
- `/static` dizininden dosya sunumu
- `/api/hello` endpoint'inden JSON döndürme

## Kurulum

### Gereksinimler

- Python 3.9 veya üzeri
- pip

### Yerel Kurulum

1. Projeyi klonlayın:
```bash
git clone https://github.com/enesscakmak/acik-kaynak-http-server
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
2. Feature branch'i oluşturun
3. Değişikliklerinizi commit edin 
4. Branch'inizi push edin 
5. Pull Request oluşturun

## Davranış Kuralları

Bu projeye katkıda bulunurken lütfen [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) dosyasındaki kurallara uyun. 
