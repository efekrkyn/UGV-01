# UGV-01 Detay Mühendislik ve Tasarım Gözden Geçirme Raporu (Design Review Findings)

**Tarih:** 23 Eylül 2026  
**Revizyon:** P0 / D2A İncelemesi  
**Kapsam:** Mekanik CAD (D1/D2A), Elektronik Arayüz (PWR-MCU), MCU Pin Eşleme ve Güvenlik Mimarisi  
**Durum:** EYLEM GEREKTİREN KRİTİK BULGULAR (ACTION REQUIRED)

---

## Yönetici Özeti

Son geliştirme adımlarında (23 Eylül 13:29 - 14:49) yapılan teknik düzeltmeler (PB10/PB11 I2C çakışmasının giderilmesi, DRV8874 PH/EN modunun fren yapması nedeniyle 8 kanallı PWM moduna geçilmesi, iki kart arasındaki paralel GND dolaşım akımının tek sokette birleştirilmesi ve 10 mm 42CrMo4+QT mil seçimi) teorik ve test güdümlü olarak çok başarılıdır.

Bununla birlikte, **fiziksel üretim, montaj, sinyal bütünlüğü ve saha testleri** açısından sistemi doğrudan kilitleyecek veya sahada arızaya ("patlamaya") yol açacak **8 kritik tasarımsal zafiyet** tespit edilmiştir. Bu maddeler şematik ve detay CAD dondurulmadan önce çözülmelidir.

---

## 1. Mekanik ve Yerleşim Bulguları

### 1.1. Molex Mega-Fit Dikey Konnektör ve Hacim Çakışması (Kesin Montaj Engeli)
* **İlgili Parça:** `J-PWR` soketi, Molex `768290004` (Vertical 2x2 Header, takılı yükseklik 16.78 mm). Eşleşen housing: Molex `1700010104` + AWG12 krimp.
* **Fiziksel Çakışma:** 
  * `mechanical_architecture.md` belgesinde MCU ve PWR kartları $z=45\dots78\text{ mm}$ hacminde, üstteki CM5 IO rafı ise $z=84\text{ mm}$ seviyesindedir. Kart yüzeyi ile CM5 rafı altı arasındaki net boşluk **yalnızca 5 mm**'dir.
  * 16.78 mm'lik dikey soket, CM5 taşıyıcı tepsisiyle doğrudan çarpışmaktadır.
  * Sokete giren 3 adet AWG12 kablonun dış çapı $\approx 3.5\text{ mm}$, minimum bükülme yarıçapı ise $\approx 25-30\text{ mm}$'dir. 5 mm'lik aralıkta bu kabloları bükmek ve mandal kilidine parmakla ulaşmak imkansızdır.
* **Gereken Düzeltme:**
  1. Dikey header yerine **Dik Açılı (Right-Angle)** Molex Mega-Fit header seçilmeli (Molex `768300004` veya `1720650004`).
  2. Soket kart kenarına, çıkış yönü dış yan kablo kanalına ($y$ eksenine) bakacak şekilde konumlandırılmalıdır.
  3. `config/pwr_mcu_connector.json`, `pwr_mcu_harness.kicad_sch` ve testler Right-Angle footprint'e güncellenmelidir.

### 1.2. Kütle Rezervi Yanılsaması (Kalan Rezerv: Yalnızca 67 Gram)
* **Durum:** D2A hafifletme çalışmasında (jantta 4 delik, lastikte sırt inceltme) hesaplanan boş kütle **5.933 kg** olarak bulunmuş ve 6.000 kg sınırına 67 gram kaldığı belirtilmiştir.
* **Patlama Riski:**
  * Metre başına $\approx 38\text{ g}$ olan AWG12/14/16/26 kablo demetleri, krimp terminalleri, konnektör gövdeleri henüz tartılmamıştır.
  * Şasideki onlarca M3/M4 çelik cıvata, somun, rondela ve pirinç heat-set insert'lerin toplam kütlesi rahatlıkla 100–150 gram tutmaktadır.
  * Slicer doluluk payı (%100 çevre/perimetre) ve lehim/termal pad kütleleri eklendiğinde ilk prototip **6.2 – 6.4 kg** bandına fırlayacak ve 6.00 kg sınırı aşılacaktır.
* **Gereken Düzeltme:**
  1. 101 gramlık Alüminyum motor taşıyıcı bloklarında (`UGV-MECH-040`) yapısal olmayan gövde bölgelerine cep boşaltma (pocketing) yapılarak teker başına en az 25 g (toplam 100 g) kazanılmalıdır.
  2. 6061 alt plakada gerilmesiz bölgelerde delik/cep boşaltmaları değerlendirilmelidir.
  3. Gerçek montajda en az **250 gram** net rezerv kalmadan Phase 4 kapatılmamalıdır.

### 1.3. Skid-Steer Yanal Zorlamasında TPU Lastiğin Janttan Sıyrılması (Debeading)
* **İlgili Parça:** Jant `UGV-MECH-046-B` (PAHT-CF) ve Lastik `UGV-MECH-047-B` (TPU95A).
* **Fiziksel Mekanizma:**
  * Jant ile lastik arasındaki 8 adet radyal tırnak sürüş/fren torkunu aktarır; ancak 4 teker skid-steer dönüşünde (pivot turn) tekerlekler yanal olarak sürüklenir ($F_{lateral} \approx \mu \cdot N \approx 1.0 \times 40\text{ N} = 40\text{ N}$ teker başına).
  * TPU95A elastik bir malzemedir. Yanal kuvvet lastik yanağını jant omzundan dışarı doğru esneterek sıyırır (axial debeading).
* **Gereken Düzeltme:**
  * Jantın dışına lastiği eksenel olarak hapseden vidalı dış flanş (beadlock ring) eklenmeli veya jant ile lastik arasına kırlangıç kuyruğu (dovetail) / derin iç kilit kanalı tasarlanmalıdır.

### 1.4. Oldham Kaplinin Eksenel Sabitlik Sağlamaması
* **İlgili Parça:** `REF-RULAND-OLDHAM` / `UGV-MECH-044`.
* **Mekanik Risk:**
  * Oldham kaplinler açısal ve radyal kaçıklığı alır ancak eksenel (axial) kilitleme yapmaz (ortadaki disk serbesttir).
  * Şasi burulmasında veya montaj toleransında disk kayabilir; daha kötüsü diskin eksenel sıkışması durumunda Pololu motor redüktörünün iç yataklarına kontrolsüz eksenel baskı biner (bu redüktörler eksenel yüke dayanıklı değildir).
* **Gereken Düzeltme:**
  * 10 mm teker milinin iki 6000 rulman ve segman (`REF-RETAINING-RING-10`) ile taşıyıcı blokta her iki eksenel yönde (+y / -y) kesinlikle sıfır boşlukla kilitlendiği doğrulanmalıdır.
  * Motor milindeki kaplin yarısı ile tekerlek milindeki kaplin yarısı arasında en az 1.0–1.5 mm eksenel çalışma boşluğu bırakılmalıdır.

---

## 2. Elektrik, Sinyal Bütünlüğü ve Donanım Bulguları

### 2.1. Kartlar Arası Kablo ile $I^2C$ Taşınması (Kritik Güvenilirlik Riski)
* **İlgili Hatlar:** `J-SIG` Pin 9 (`I2C2_SCL`, PA9) ve Pin 10 (`I2C2_SDA`, PA8) $\rightarrow$ PWR kartındaki INA228 akım sensörü.
* **Fiziksel Mekanizma:**
  * $I^2C$, açık kolektörlü (pull-up dirençli) kart-içi kısa mesafe protokolüdür.
  * 15 A motor akımının anahtarlandığı (20 kHz PWM), endüktif kabloların bulunduğu bir gövdede 300–400 mm harici kablo demetiyle $I^2C$ taşımak yüksek EMI/gürültüye maruz kalır.
  * Gürültü darbeleri $I^2C$ hattını kilitler (SDA hattının Low'da asılı kalması); STM32 donanımı `BUSY` durumuna geçer. Telemetri kesildiği için güvenlik durum makinesi aracı FAULT moduna sokar.
* **Gereken Düzeltme:**
  1. *Tercih Edilen:* INA228 sensörü doğrudan MCU kartı üzerine yerleştirilmeli; PWR kartından sadece şönt potansiyeli Kelvin hatlarıyla (veya analog filtreli hatla) alınmalıdır.
  2. *Alternatif:* Eğer $I^2C$ kabloyla taşınacaksa NXP `PCA9615` gibi diferansiyel $I^2C$ tamponu kullanılmalı; firmware'e 9-clock bus-recovery mekanizması eklenmelidir.

### 2.2. Ortak PGND Üzerinde Sinyal Referans Kayması (Ground Bounce)
* **İlgili Hatlar:** `J-PWR` Pin 2/3 (`PGND_A`, `PGND_B`), `J-SIG` sinyal demeti.
* **Fiziksel Mekanizma:**
  * Paralel toprak akımını önlemek için J-SIG soketinden GND kaldırılmış, tüm referans J-PWR'daki AWG12 PGND hatlarına verilmiştir.
  * 4 motor aniden ivmelendiğinde (15 A transient), Molex kontak direnci ve kablo direnci üzerinde anlık gerilim düşümü ($\Delta V = I \cdot R \approx 50-150\text{ mV}$) ve endüktif darbe ($L \frac{di}{dt}$) oluşur.
  * Bu durum MCU toprağı ile PWR toprağı arasında zıplama (ground bounce) yaratarak 3.3V mantık sinyallerinde (özellikle `MCU_WDI` ve `PWR_ACT_EN`) sahte lojik geçişlerine yol açabilir.
* **Gereken Düzeltme:**
  * `MCU_WDI` ve `PWR_ACT_EN` gibi kritik güvenlik sinyallerine donanımsal RC alçak geçiren filtreler konulmalı veya optik/sayısal izolatörlerle kartlar birbirinden galvanik olarak ayrılmalıdır.

### 2.3. Parazitik Besleme (Parasitic Backfeeding)
* **İlgili Durum:** PWR kartı canlıyken MCU kartının beslemesinin kapalı veya gecikmeli olması.
* **Fiziksel Mekanizma:**
  * PWR kartından gelen 3.3V durum sinyalleri (`ESTOP_A_CLOSED`, `PWR_K1_FB`, `PWR_K2_FB` vb.), enerjisiz STM32'nin GPIO dahili ESD diyotları üzerinden MCU'nun $V_{DD}$ rayını beslemeye çalışır.
  * Bu durum STM32 pinlerinde maksimum enjeksiyon akımını ($I_{INJ} \le 5\text{ mA}$) aşabilir ve mikroyu yakabilir ya da brownout kilitlenmesine sokabilir.
* **Gereken Düzeltme:**
  * MCU tarafında tüm gelen GPIO hatlarına seri akım sınırlama dirençleri ($1\text{ k}\Omega - 4.7\text{ k}\Omega$) eklenmelidir.
  * Ya da PWR tarafındaki çıkışlar açık-kollektör (open-drain) yapılmalı ve pull-up dirençleri MCU tarafındaki 3.3V rayına bağlanmalıdır.

---

## 3. Kontrol ve Güvenlik Bulguları

### 3.1. E-Stop Sonrası Eğimde Kaçış (Runaway on Incline)
* **İlgili Durum:** E-stop anında DRV8874'ün `00` (Coast) moduna geçmesi ve K1/K2 kesicilerinin açılması.
* **Fiziksel Risk:**
  * Robot 15° eğimde tırmanırken E-stop'a basılırsa; mekanik park freni bulunmadığından ve motorlar serbest dönmeye (coast) geçtiğinden araç yerçekimi kuvvetiyle ($F_{g} \approx 20\text{ N}$) yokuş aşağı serbestçe hızlanıp devrilecektir.
* **Gereken Düzeltme:**
  * Bu durum resmi bir operasyonel kısıt olarak tescillenmeli; açık alanda eğim testlerinde bağımsız güvenlik halatı (tether) zorunlu tutulmalıdır.
  * DRV8874'ün donanımsal alt-frenleme (`11` Brake) modunun kontrollü bir durdurma aşaması olarak kullanılıp kullanılamayacağı (rejenerasyon sınırları gözetilerek) incelenmelidir.

### 3.2. Çift Timer (TIM1 + TIM8) Senkronizasyon Kayması
* **İlgili Yapı:** 4 motor için TIM1 (4 kanal IN2) ve TIM8 (4 kanal IN1).
* **Kontrol Riski:**
  * `00` Coast ve `10`/`01` sürüş durumlarında, TIM1 ve TIM8 sayaçları faz senkronizasyonlu çalışmazsa veya yazılımda atomik güncellenmezse, geçiş anlarında mikrosaniye mertebesinde istenmeyen `11` (Brake) durumları oluşabilir; bu da sürücülerde ani akım darbelerine ve sarsıntıya yol açar.
* **Gereken Düzeltme:**
  * STM32 CubeMX / firmware tasarımında TIM1 ve TIM8 timer'ları Master-Slave modunda donanımsal olarak kilitlenmeli (hardware synchronized trigger) ve güncellemeler tek bir DMA transferi veya atomik register yazımıyla yapılmalıdır.

---

## 4. Aksiyon Tablosu

| No | Konu | Öncelik | Hedef Faz | Eylem |
|---|---|:---:|:---:|---|
| **A1** | Molex Güç Konnektörü | **P0 - Bloke Edici** | Faz 5/6 | Dikey 76829-0004 yerine Dik Açılı (Right-Angle) 76830-0004 seçilmeli, CAD ve footprint güncellenmeli. |
| **A2** | Kartlar Arası $I^2C$ | **P0 - Bloke Edici** | Faz 5/6 | INA228 MCU kartına taşınmalı veya J-SIG yerine diferansiyel arayüz / CAN düşünülmeli. |
| **A3** | GPIO Parazitik Besleme | **P1 - Yüksek** | Faz 5 | Gelen sinyal hatlarına seri $1-4.7\text{ k}\Omega$ direnç veya açık-kollektör arayüz eklenmeli. |
| **A4** | Kütle Rezervi | **P1 - Yüksek** | Faz 4 | `UGV-MECH-040` taşıyıcı bloklarında cep boşaltma (pocketing) yapılarak en az 150-200 g kazanılmalı. |
| **A5** | Jant-Lastik Yanal Kilidi | **P2 - Orta** | Faz 4 | Skid-steer yanal sıyrılmasını engellemek için beadlock veya kırlangıç kuyruğu kilit eklenmeli. |
| **A6** | E-Stop Eğim Kaçışı | **P2 - Orta** | Faz 11/12 | Park freni yokluğu operasyonel prosedüre ve test güvenlik kurallarına işlenmeli. |
| **A7** | Timer Eşzamanlaması | **P2 - Orta** | Faz 8 | TIM1 ve TIM8 Master-Slave donanımsal senkronizasyonu firmware mimarisine eklenmeli. |
