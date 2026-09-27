# PH2 mekanik kavram

**A3 Lite, M3 (güncel, DD72–DD75):**
- **Gövde:** 300 × 236 × z210 karakter gövdesi; baskı PETG plaka ve kirişler.
- **Tahrik:** gövdenin içinde JGA25 motor kelepçeleri; duvardan geçen göbek boynu ve baskı göbek + TPU lastik; tekerleklerin üstünde çamurluklar.
- **İç düzen:** 3S batarya ve elektronik zarfları, E-stop ve ToF, kargo kutusu ve atma ağzı.
- **Kol:** yan duvardan çıkan 5 eksenli sağ kol (DS3218MG omuz servosu gövde içinde, 6804/6704 rulmanlar) ve pasif sol kol.
- **Doğrulama:** kol duruşları ve duruş grafiğinin geçişleri `manifest.json`'da (`arm_poses`, `arm_edges`, `arm_limp_rest`, `arm_chain`).

Ayrıntı: [Lite mekanik](../../docs/lite_mechanical_A3.md).

**3D inceleme:** [UGV-01-A3-viewer.html](../../docs/renders/UGV-01-A3-viewer.html) tarayıcıda açılır (three.js için internet gerekir). Sunduğu özellikler:
- döndürme ve parça bilgisi;
- duruş düğmeleri (kol, CAD'de denetlenen graf yolundan gider);
- eklem kaydırıcıları ve baş hareketi;
- saydam gövde. CAD değişince `.venv/bin/python tools/build_viewer.py` ile yeniden üretilir. Fusion 360 için `generated/UGV-01-A3-concept.step` doğrudan açılır. Aşağıdaki A2 açıklaması baş ve kapak ayrıntıları için tarihsel kayıttır; kollar M3'te değişti.

`build_concept.py` ve `../../config/vehicle.json` parametrik kaynaklardır; STEP dosyaları düzenlenip kaynakmış gibi kullanılmaz. x ileri, y sol, z yukarı; z0 nominal zemin; mm.

Panel modülleri ön/orta/arka için ayrı sol/sağ parçalar ve kapaklardan oluşur. A2'de ([biçim ve ölçüler](../../docs/exterior_language_A2.md)) kapak üst kenarında 1 mm pah, ön duvarda 8×120×6 mm ışık şeridi penceresi, flanş üstünde pan/tilt boyunlu iki göz kabuğu (Camera Module 3 tahsisi) ve ön köşelerde omuz kuleli iki kol vardır. Sağ kolun −55° çalışma pozu ayrı STEP olarak üretilir; park→çalışma süpürmesi 5° adımla manifestte denetlenir. Servo kornası, rulman tutucu, kablo yolu ve kamera montajı açık. Ø4,5mm M4 taban delikleri ve Ø3,4mm M3 kapak delikleri CAD'de vardır. Insert geometrileri henüz verilmez; geçiş delikleridir. Bazı metal ve son duvar bağlantıları tasarım arayüzüdür, bütün bağlantı elemanları modellenmedi.

Manifest fiziksel solid kesişmelerini ve özellikle **modellenmemiş** öğeleri kaydeder. REF-WHEEL, REF-MOTOR, REF-BATTERY, REF-CM5/PCB, REF-SERVO, REF-BEARING, REF-EYE-CAMERA ve REF-LIGHT-BAR hacimleri komponent detay CAD'i değildir. Teker/göbek işlevli imalat modeli PH4'tedir. STL'ler panelin zemin z0 konumuna taşınmıştır; baskı yönü/slicer/kupon doğrulaması ayrıca gerekir. [A2 CAD önizlemesi](concept_preview.png) STEP katılarından türetilmiştir; [A1 stil görseli](../../docs/renders/UGV-01-A1-exterior-concept.png) ölçü kanıtı değildir.

`generated/` içinde arşiv A0/A1 montajları da tutulur (A1 kaydı: [revisions/A1](../../docs/revisions/A1/README.md)). Güncel parça kümesi yalnız `manifest.json` içindeki `parts` listesidir.

Kavram modeli için [montaj sırası](assembly_sequence.md); genel DFM ve malzeme hesabı [mekanik mimaride](../../docs/mechanical_architecture.md).
