# UGV-01 tasarım ilerleme tahmini — 24.09.2026

Bu oran **mühendislik tasarım işinin** kaba ilerlemesidir; harcanan süre, doğrulanmış performans veya çalışan araç yüzdesi değildir. Kapsam: gereksinim/sistem mimarisi, ayrıntılı mekanik tasarım ve DFM, tahrik boyutlandırması, elektronik şematik/PCB, firmware–ROS–arayüz mimarisi. Satın alma, üretim, baskı, montaj, firmware/uygulama kodlama ve T01–T20 fiziksel testleri bu yüzdenin dışındadır. İş paketlerinin göreli ağırlıkları ön tahmindir; bileşen seçimleri ve test bulguları bunları değiştirebilir.

| Tasarım iş paketi | Göreli ağırlık | Tamamlanma tahmini | Kanıt ve en büyük açık iş |
|---|---:|---:|---|
| SRS ve sistem mimarisi | %15 | %100 | SRS, blok diyagramı, arayüz ve güvenlik mimarisi yazılı; revizyonlar sürecek |
| Mekanik CAD, tolerans ve DFM | %30 | %38 | Kavram ve D1/D2A tahrik STEP'leri var; tam yük yolu, geçmeler, şasi sehim/yorulma, gerçek bölme/servis boşlukları ve tüm teknik resimler açık |
| Tahrik hesap ve seçim tasarımı | %15 | %55 | Tork/hız/akım/statik tarama var; gerçek motor termal/tork doğrulaması, mil yorulması ve lastik/zemin davranışı açık |
| MCU/PWR/compute şematik ve PCB | %30 | %20 | MCU 58 pin ve A2 servo/ışık kısmi sayfası, 16 net kablo, PCA9615 referansı ve kısmi arayüz sayfaları; PWR güç/güvenlik yolu beş sayfalı kısmi hiyerarşide (birleşik ERC 0 hata). INA228/regülatör/dump clamp sayfaları, K1 MPN, MCU kart şematiği, tam kart ERC, layout/DRC ve Gerber yok |
| Firmware, ROS 2 ve web mimarisi | %10 | %40 | Paket/safety durumları ve veri akışı tanımlı; host üzerinde test edilen güvenlik çekirdeği var, STM32 build/ROS düğümleri/web arayüzü yok |
| **Ağırlıklı tasarım toplamı** | **%100** | **yaklaşık %45** | **yaklaşık %55 kaldı** |

Hesap: `15×1,00 + 30×0,38 + 15×0,55 + 30×0,20 + 10×0,40 = 44,65` puan (AI köprüsü, yürütücü, servo/ışık/CAN firmware modülleri ve panel mantığı host testli; sunucu, ROS ve STM32 build yok). A2 (24.09) baş/kol CAD'i ve servo/ışık sayfasını ekledi, ancak kapsamı da büyüttü (servo montajları, AI yazılımı); yazılım satırı bu yüzden %35'ten %30'a indi. Önceki: 42,35 (24.09 sabah), 40,85 (23.09). Bu bir mühendislik kestirimidir; dürüst belirsizlik yaklaşık **±10 puan**. “%45” PHASE 4/5/6/7 kapılarının geçtiği veya çalışan araç anlamına gelmez. Baskı beklerken sıradaki tasarım işi PWR INA228/giriş koruması, regülatör ve ACT dump clamp sayfaları, ardından MCU kart şematiği ve tam kart ERC'dir. Kart/saha testleri yapılmadan üretim serbest bırakılmaz.
