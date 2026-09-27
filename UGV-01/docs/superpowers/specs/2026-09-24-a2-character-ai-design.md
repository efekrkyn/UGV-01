# UGV-01 A2 — karakter gövde, baş/kol ve denetimli AI kontrolü — tasarım spec'i

24.09.2026 · Kullanıcıyla brainstorming sonucu onaylanan tasarım. **Uygulama güncellemesi:** A2 mekanik sonuçları [DD62](../../design_decisions.md)'dedir ve aşağıdaki ön tahminlerin yerini alır: yük **1,5 kg** (kullanıcı kararı; ≈1,85 kg CG payını 0,7 mm'ye indiriyordu), kol **200 mm**, tilt **−60…+30°**, park 180°, baş 195 g / kollar 187 g CAD taraması. **Üretim, baskı veya sürüş onayı değildir.** Fiziksel T01–T20 testleri NOT_RUN; 3D yazıcı henüz yok.

## Amaç ve kapsam

Kullanıcı UGV-01'in (1) genel tasarım denetiminden geçip hatalarının düzeltilmesini, (2) sevimli animasyon robotlarından **ilham alan ama özgün** bir görünüme kavuşmasını, (3) bir baş/iki kamera göz, işlevsel kol ve kameraları görüp verilen emirleri yerine getiren **denetimli AI kontrolü** kazanmasını ve (4) yazıcı gelene kadar tasarımın tamamlanmasını istiyor. GitHub/LinkedIn paylaşımı **proje tamamlandıktan sonra** yapılacak.

Bu istek birbirinden ayrılabilir alt projelerdir. Sıra:

| # | Alt proje | Çıktı | Bağımlılık |
|---|---|---|---|
| 1 | Genel tasarım denetimi ve hata düzeltme | Denetim raporu, düzeltmeler, karar/faz kaydı | Yok; A2'den önce |
| 2 | A2 dış görünüş ve mekanik | CadQuery baş/boyun/kol/ışık şeridi, güncel montaj, kütle/CG, STL/STEP | 1 |
| 3 | A2 elektrik/elektronik | Servo PWM pinleri, servo ray akım ölçümü, ışık şeridi, iki CSI kamera, ToF; KiCad/pin/bütçe güncellemesi | 1, 2'nin ölçüleri |
| 4 | AI ve yazılım | `ai_bridge`, `skill_executor`, web panel sohbet/ses/AI modu, MCU servo/ışık firmware'i, mock testler | 3'ün arayüzleri |
| 5 | Kalan tasarım | INA228/giriş, regülatörler, dump clamp, MCU kartı, tam kart ERC, firmware, ROS paketleri | 1–4 |
| 6 | Paylaşım paketi | Repo temizliği, lisans, README EN/TR, render'lar, LinkedIn taslağı | Proje tamamlanınca |

Her alt proje ayrı uygulama planıyla yürür; bu spec 1–4'ün tasarımını sabitler, 5'i sıralar, 6'yı erteler.

## Kullanıcı kararları (24.09.2026)

- Yürüyüş: **tekerler kalır** (4× Ø120 skid-steer, D1/D2A tahrik ve hesaplar geçerli); yalnız gövde ve baş karakter tarzı. Palet yok.
- Benzerlik: **ilham alan özgün robot**. Başka bir karakterin adı, logosu veya birebir oranları kullanılmaz; kendi adı olacak.
- Baş: **boyunlu, iki kameralı, pan/tilt servolu**.
- Kollar: **sağ kol işlevsel** (omuz + pençe, 2 servo), **sol kol pasif** ama aynı görünüşte, servo yuvası hazır. Görev: **≤150 g nesneyi tutup taşımak**.
- Kütle: **toplam 8 kg korunur**; kollar yükten düşülür. Kullanıcıya ≈1,5 kg yük olarak sunuldu; denetim R03 başın mevcut kule tahsisine sığdığını gösterdi, gerçek yük kapasitesi ≈1,85 kg.
- AI: **hibrit** — bulutta Claude planlar, araç üstünde refleksler; **insan denetimli AI modu**; komut **yazılı ve sesli**.
- Model: **Claude Sonnet 5** (`claude-sonnet-5`, $2/$10 per MTok; kullanıcı seçimi).

## 1. Genel tasarım denetimi

Kapsam: sayısal tutarlılık (kütle, ölçü, güç/akım bütçeleri, pin haritası ↔ arayüz sözleşmesi ↔ KiCad ↔ BOM), belgeler arası çelişki, eskimiş ifade, kırık Markdown bağlantısı, test/hesap yeniden üretimi. Gerçek hatalar düzeltilir; her bulgu `docs/design_review_2026-09-24.md` raporunda kaynak dosya/satır, hata, düzeltme ve kanıtla listelenir. Karar gerektirenler `design_decisions.md`, sonuç `phase_reviews.md`. A2'nin zaten değiştireceği öğeler (ör. A1 ön kamera podu) düzeltilmez, raporda "A2'de değişiyor" olarak işaretlenir. Bağlantı denetimi için tek küçük betik eklenir ve test listesine girer.

## 2. A2 dış görünüş ve mekanik

A1 arşive alınır; A2 aynı 330×270 mm zarf, Ø120 teker ve alt metal yük yolu üzerine kurulur.

- **Gövde:** Sarı ASA paneller, koyu TPU tamponlar, üç servis kapağı korunur. Ön kamera podu kaldırılır (A1'deki 3,25 mm x-payı sorunu kapanır).
- **Durum ışık şeridi:** Ön yüzde 8 adreslenebilir LED; batarya yüzdesi + mod rengi (AI modu mavi, ARM sarı, FAULT kırmızı). Hem karakter öğesi hem AI denetçisine görünür güvenlik bilgisi.
- **Baş:** İki yuvarlatılmış-kare göz podu (klasik silindirik dürbün gözden bilerek farklı), üstte eğik "kaş" plakaları. Her gözde Raspberry Pi Camera Module 3; gözler arası ≈60 mm. Tilt servosu başın içinde, pan servosu boyun tabanında; baş yükünü ince kesitli rulman taşır, servo yalnız döndürür. Pan ±90°, tilt −45…+30°. Boyun ≈100 mm; mevcut 40×40 M4 flanşa oturur. Toplam araç yüksekliği ≈290 mm.
- **Kollar:** Omuz pivotları ön yüzün üst köşelerinde, teker izinin içinde (tekerle çakışma yok). Sağ kol: DS3218MG omuz (pitch) + MG90S iki parmaklı pençe, kol boyu ≈160 mm. Sol kol aynı kabuk, sürtünmeli pasif eklem, servo yuvası boş. Park pozunda 330 mm zarf içine katlanır; çalışma pozunda tamponun ≈40–60 mm önünde zemine ulaşır.
- **Kol hesabı:** 150 g yük + pençe + bağlantı ile omuzda statik ≈0,32 N·m (3,3 kg·cm); dinamik ×1,5 ve güvenlik ×2 ile ≈10 kg·cm gereksinim. DS3218MG 6 V'ta ≈19 kg·cm (6,8 V'ta 21,5). Pençe için MG90S ≈2 kg·cm; 150 g tutma için yeterli (sürtünme μ≈0,5 varsayımı test edilir).
- **Kütle/CG (denetim R03 ile düzeltildi):** Baş ≈225 g, işlevsel kol ≈165 g, pasif kol ≈70 g. Baş, 6 kg bütçede zaten ayrılmış 0,30 kg "RGB kamera + gelecek kule" tahsisinin yerine geçer (≈75 g pay kalır); yalnız kollar (≈0,235 kg) yenidir. `config/vehicle.json` gruplarıyla boş kütle ≈6,13–6,16 kg, toplam 8 kg korunursa yük ≈1,85 kg; yüklü CG z≈107–108 mm (≤110 mm sınırı dar). CAD kütlesiyle yeniden hesaplanır; geçmezse baş/kol hafifletilir veya yük CG sınırı daraltılır.
- **Baskı:** Yeni parçalar ≤240 mm tasarım zarfında; kabuk ASA, kol bağlantıları PETG/PAHT-CF, pençe pedleri TPU. Mevcut `tests/check_cad.py` yeni parçaları geçerlilik, zarf ve çakışma için kapsar.

## 3. A2 elektrik ve elektronik

- **Servo PWM:** 4 servo MCU'dan sürülür. Pan/tilt mevcut TIM15_CH1/CH2 (PA2/PA3). Omuz ve pençe için 2 yeni kanal; aday TIM17_CH1/PB9 ve bir TIM20 kanalı. PB8 (BOOT0) kullanılmaz. `tools/check_mcu_pinmap.py` KiCad LQFP100 sembolüyle doğrular; CubeMX teyidi açık kalır. Açı/hız sınırları ve komut tazeliği MCU hakeminde.
- **Servo rayı:** 6 V/4 A regülatör korunur (en kötü eşzamanlı sıkışma ≈4,1 A). Ray akımı ölçülür; eşik aşımında kol gevşer, FAULT kaydı. Aynı anda en fazla bir büyük servo hızlanır.
- **E-stop:** Servo regülatörü K2 sonrası aktüatör barasında; E-stop servoları fiziksel olarak keser. Enerji kesilince kol yerçekimiyle düşer (≈165 g); T13'e eklenir.
- **Kameralar:** İki CSI Camera Module 3 → CM5 IO CAM0/CAM1; USB ön kamera kalkar. ≈0,6 W, önceki 2 W UVC payı içinde; 5,1 V/30,6 W compute rayı aşılmaz.
- **Işık şeridi:** 5V_CONTROL beslemeli, MCU verisi 74AHCT1G125 seviye çeviriciyle; firmware parlaklık tavanı ≤0,5 W.
- **ToF:** Ön tamponda 2 × VL53L1X sınıfı mesafe sensörü (MPN açık), CM5 I²C; `skill_executor` refleks durdurma girdisi.
- **Bütçe:** Servo satırı 2/3 W → 3/8 W (tipik/ağır); ağır görev bütçesi ≈107 → ≈113 W. BOM: B15 servo 2→4, ikinci kamera, rulman, ışık şeridi, seviye çevirici, 2 ToF.
- **Ağ ve gizli bilgi:** CM5 Wi-Fi ile internete çıkar; web panel yerel kalır. API anahtarı yalnız araçtaki gizli dosyada, `.gitignore` ile repodan dışlanır.

## 4. AI ve yazılım

Mevcut DD19/V5 kuralı korunur: dil modeli yalnız doğrulanmış görev şeması üretir; ARM, watchdog, akım sınırı veya fiziksel E-stop'u değiştiremez.

- **Komut girişi:** Web panel sohbet kutusu + mikrofon düğmesi (tarayıcı tr-TR konuşma tanıma → metin, ekranda gösterilir). "Dur/stop" yerelde, AI'a gitmeden anında durdurur.
- **AI modu izni:** Paneldeki açık "AI modu" anahtarı + sayfa görünür/odaklı + mevcut ≤100 ms lease/heartbeat. Biri düşerse normal durma ve AI döngüsü duraklar. Operatör joystick'i AI modunu anında düşürür. Öncelik: fiziksel E-stop > yazılımsal STOP > operatör > AI yürütücüsü.
- **`ai_bridge` (CM5, Python, resmî Anthropic SDK):** Her turda iki göz görüntüsü (küçültülmüş JPEG), araç durumu JSON'u (baş/kol açıları, batarya, ToF mesafeleri, son eylem sonucu) ve talimat. `claude-sonnet-5`, uyarlamalı düşünme; `stop_reason` (refusal, max_tokens) her turda kontrol edilir; sistem istemi ve araç tanımları prompt cache'te; görev başına adım ve dolar tavanı; her adım görüntüleriyle kaydedilir. Kesin SDK çağrıları uygulama planında skill belgelerinden alınır.
- **Claude araçları (katı şema):** `look(pan_deg, tilt_deg)`, `drive(distance_m ≤1,0, speed ≤0,2)`, `turn(angle_deg)`, `arm(pose: stow|ready|reach_low|reach_mid)`, `gripper(open|close)`, `wait(s)`, `say(text)` (web panelde gösterilir; araç üstü hoparlör yok), `ask_operator(question)`, `finish(summary)`. İkinci TIM20 servo kanalının kesin pini alt proje 3'te pin testiyle seçilir.
- **`skill_executor` (araç üstü, internetsiz):** Her aracı sınırlar ve yerelde yürütür; AI modunda hız ≤0,2 m/s; ToF eşiğinde refleks durdurma; ağ/Claude gecikmesinde araç durmuş bekler. CM5 çökerse MCU 100 ms tazelik sınırıyla keser.
- **MCU firmware:** Servo hedef/sınır/rampa, sıkışma algılama, ışık şeridi, yeni CAN çerçeveleri (servo hedefleri, AI modu bayrağı).
- **Maliyet:** Sonnet 5 ile adım başına ≈0,01–0,02 USD, 15 adımlık görev ≈0,2–0,3 USD (tahmin; ölçülecek).
- **Gizlilik:** Kamera görüntüleri Anthropic API'ye gönderilir; README ve panelde belirtilir.
- **Test:** Yürütücü sınırları, AI modu düşüşleri, stop kelimesi ve şema doğrulaması mock Claude ile ücretsiz testlerde. Gerçek API duman testi para harcar; yalnız kullanıcı onayıyla ve düşük tavanla.

## 5. Kalan tasarım (sıralama)

INA228/giriş koruması ve STAR/`MOTOR_FEED` sayfası, regülatörler (servo rayı akım ölçümü dahil), ACT TVS/dump clamp, MCU kart şematiği (servo/ışık/CAN), tam kart ERC; ardından STM32 firmware iskeleti ve ROS 2 paketleri. Her biri kendi plan/spec döngüsünde.

## 6. Paylaşım (ertelendi)

Proje tamamlanınca: `.DS_Store`/`__pycache__`/`.venv` temizliği, gizli bilgi taraması, büyük dosya politikası, UGV-01 için ayrı git deposu (bugünkü kök üst klasör `ika`), lisans önerisi (kod MIT, donanım CERN-OHL-S-2.0, belgeler CC BY 4.0 — kullanıcı kararı), robotun kendi adı, "resmî olmayan, ilham alınmış, ticari değil" ifadesi, EN/TR README ve render'lar, LinkedIn taslağı. Commit/push yalnız kullanıcı onayıyla.

## Kapsam dışı

Palet/yürüyüş değişikliği, motorlu sol kol, araç üstü mikrofon/hoparlör, araç üstü dil modeli, gözetimsiz otonom AI, LiDAR/SLAM (V3), paylaşım içeriğinin yayımlanması.

## Başarı ölçütleri

- Denetim raporu: her bulgu kanıtlı; bütün mevcut testler yeşil.
- A2 CAD: yeni katılar geçerli, ≤240 mm, sıfır izinsiz çakışma, park pozunda 330×270 zarf; kütle/CG hesabı raporlu.
- Elektronik: pin testi yeşil; ilgili KiCad sayfaları netlist testi + ERC; güç bütçesi yeniden üretildi.
- Yazılım: mock testlerinde AI hiçbir yoldan hız/açı sınırını, E-stop'u veya AI modu iznini aşamaz; stop kelimesi ağ olmadan çalışır.
- Fiziksel testler NOT_RUN olarak kalır; hiçbir çıktı üretim/sürüş onayı iddia etmez.
