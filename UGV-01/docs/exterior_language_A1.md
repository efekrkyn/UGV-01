# UGV-01 A1 dış görünüş ve kamera revizyonu

> **A2 ile yerini aldı (24.09.2026):** ön tek kamera kaldırıldı; iki göz kamerası boyunlu başa taşındı. Güncel sınırlar: [A2 karakter revizyonu](exterior_language_A2.md). Bu belge A1 kaydı olarak korunur.

24.09.2026 · PH4 kavram revizyonu. [Görsel konsept](renders/UGV-01-A1-exterior-concept.png) yalnız biçim iletişimidir; resimdeki vida, ışık, lastik dişi, kablo ve kamera ölçüleri **CAD/tedarik kanıtı değildir**. Üretim dosyası olarak kullanılmaz.

Kullanıcı yönü: UGV-01, sıcak sarı gövde ve koyu koruyucu köşelerle sevimli/çalışkan endüstriyel bir karakter taşıyacak. Dört **ayrı tekerli** skid-steer mimari, üç sökülebilir kapak, alt metal yük yolu ve sensör genişleme arayüzü korunur. Çift yuvarlak “kameralı göz” modülü **sonraki revizyona ertelendi**; ilk sürümde tek öne bakan RGB kamera için ayrılabilir ön ara yüz ve üstte 50×50 mm / 40×40 M4 kule flanşı kalır. Gövdede karakter görünümü işlevsiz çıkıntılarla değil, servis panellerinin ek yerleri, darbe koruyucular ve kamera/sensör açıklığıyla oluşturulur.

| Bölge | A1 biçim kararı | Mühendislik sınırı |
|---|---|---|
| Ön/orta/arka kapak ve yan muhafaza | Mat okra/sarı ASA; ayrı modüller, kenar pahı ve okunur bağlantı noktaları | Her kapak tek baskıda ≤240 mm tasarım zarfı; montaj yüzeyi, conta/kapak açılımı ve kablo erişimi korunur. |
| Köşeler/tampon | Koyu antrasit değiştirilebilir TPU | Enerji emme ve teker koruması test gerektirir; teker x=±165 mm dış zarfını aşmamalı. |
| Ön RGB | Tek küçük kamera, ön duvar üst bölgesinde değiştirilebilir dış pod | [Camera Module 3 Standard](front_camera_A1.md) boyutu geçici mekanik referanstır; UVC/CSI seçimi, delik/vida/optik eksen, su/toz yolu ve ısıl sınır açık. Kavram CAD yalnız ayrılan hacmi gösterir. |
| Gelecek çift göz/kule | Mevcut 40×40 M4 flanş ve ayrılmış kablo kanalı | A1'de motorlu başlık yok. Servo, titreşim, optik eksen ve kütle/CG sonraki revizyonda yeniden hesaplanır. |

A1 geometrisinin kontrol sınırları: x ileri; 330×270 mm A0 dış zarfı aşılmaz; teker-gövde yanal nominal 5 mm boşluk azaltılmaz; ön açıklık y±12,z122…138 mm, üst duvar ligamenti 5 mm; dış kamera tahsisi x150,25…161,75,y±12,5,z120…144 mm, tamponun z90…120 mm alanına katı olarak girmez. Bu açıklık **kamera kartı montaj deliği değildir**; yalnız kablo/pencere arayüzü kavramıdır. Dış pod, lens penceresi, FFC bükülmesi ve darbe koruması açık P0 mekanik tasarım işidir. Batarya ve CM5 için üstten çıkarma yolu kapatılmaz. Sarı pigmentin güneş altında yüzey sıcaklığı, ASA gerçek TDS'si, UV dayanımı ve TPU/ASA bağlantı torku test edilmeden malzeme onayı verilmez. Kapak pahı ve ön kamera yeri hesap/kesişme testinden geçse bile baskı/kurulum/optik görüş testi **NOT_RUN** kalır.
