# UGV-01 A3 Lite baskı rehberi (M3)

`tools/print_plan.py` tarafından üretilir, elle düzenlenmez. STL'ler `cad/assembly/generated/` içinde, bu tablodaki yönde ve tablaya oturmuş halde. **Baskı ya da üretim onayı değildir;** hiçbir parça basılmadı.

## Genel ayarlar

- Makine: 256 × 256 × 256 mm tabla; parçalar ≤240 mm tasarım zarfında. 0,4 mm meme, 0,2 mm katman.
- PETG: 235–245 °C, tabla 75–80 °C. Dolgu gyroid. "Duvar / dolgu" sütunu çevre duvarı sayısı ve dolgu yüzdesidir.
- TPU 95A: 220–230 °C, ≤25 mm/s, geri çekme kısa. Lastik ve tamponlar yumuşak kalmalı.
- Isıl insert (M3, Ø4,0 × 6 delik): 220–230 °C havya ucuyla, yüzeye dik.
- Kütle sütunu, kütle taramasının baskı tahminidir (1,2 mm kabuk + %20 dolgu; tablodaki dolgu farklıysa değişir).

## Sıra

0. **Deneme parçaları (önce):** M3 insert deliği; motor mili D deliği ve set vidası; 6804 (Ø32), 6704 (Ø27) ve 624 (Ø13) rulman yuvaları; göz kapağı geçmesi (CAD yan başına 0,15 mm boşluk, sıkı geçme değil: kupon elle çekmede tutmazsa bir damla yapıştırıcı ya da bant; servis için sökülebilir kalmalı); TPU lastik–jant oturması. Ölçü tutmazsa config düzeltilir, CAD yeniden üretilir.
1. Şasi → 2. Tekerler (motorla sökülüp takılarak denenir) → 3. Gövde → 4. İç düzen → 5. Dış parçalar → 6. Baş → 7. Kollar.
- Bütün parçalar basılmaya hazır (DD82).
- Baş (DD82, DD83): pan servosu tabanın altından girer; boyun Ø20 mili 6804'e oturur; tilt servosu boyun bloğunda gizli, sol gözü Ø1,5 mm itme çubuğuyla sürer; iki göz altıgen aksla birbirine bağlıdır.
- Kollar (DD81): twist MG996R'nin kulakları gövde hizasında kesilir; dirsek ve bilek servoları kulaklarıyla takılır. Korna ve 624 deliği için önce deneme parçası basılır.

## Parçalar

| Aşama | Parça | Malzeme | Yön | Destek | Duvar / dolgu | Kütle g | Not |
|---|---|---|---|---|---|---:|---|
| 1 Şasi | `UGV-MECH-001-F` | PETG | Montaj yönünde, alt yüz tablada | yok | 5 / %40 | 165 | iki yarı; ek yeri x=−35 |
| 1 Şasi | `UGV-MECH-001-R` | PETG | Montaj yönünde, alt yüz tablada | yok | 5 / %40 | 103 | iki yarı; ek yeri x=−35 |
| 1 Şasi | `UGV-MECH-002-+1` | PETG | Montaj yönünde, alt yüz tablada | yok | 5 / %40 | 17 | ek kirişi, iki yarıyı üstten bağlar |
| 1 Şasi | `UGV-MECH-002--1` | PETG | Montaj yönünde, alt yüz tablada | yok | 5 / %40 | 17 | ek kirişi, iki yarıyı üstten bağlar |
| 1 Şasi | `UGV-MECH-003-FL` | PETG | Montaj yönünde, alt yüz tablada | yok | 5 / %40 | 10 | motor kelepçesi alt yuvası |
| 1 Şasi | `UGV-MECH-003-FR` | PETG | Montaj yönünde, alt yüz tablada | yok | 5 / %40 | 10 | motor kelepçesi alt yuvası |
| 1 Şasi | `UGV-MECH-003-RL` | PETG | Montaj yönünde, alt yüz tablada | yok | 5 / %40 | 10 | motor kelepçesi alt yuvası |
| 1 Şasi | `UGV-MECH-003-RR` | PETG | Montaj yönünde, alt yüz tablada | yok | 5 / %40 | 10 | motor kelepçesi alt yuvası |
| 1 Şasi | `UGV-MECH-004-FL` | PETG | Ters çevrili: düz üst yüz tablada, yarım silindir yuvası yukarı | yok | 5 / %40 | 9 |  |
| 1 Şasi | `UGV-MECH-004-FR` | PETG | Ters çevrili: düz üst yüz tablada, yarım silindir yuvası yukarı | yok | 5 / %40 | 9 |  |
| 1 Şasi | `UGV-MECH-004-RL` | PETG | Ters çevrili: düz üst yüz tablada, yarım silindir yuvası yukarı | yok | 5 / %40 | 9 |  |
| 1 Şasi | `UGV-MECH-004-RR` | PETG | Ters çevrili: düz üst yüz tablada, yarım silindir yuvası yukarı | yok | 5 / %40 | 9 |  |
| 2 Tekerler | `UGV-MECH-060-FL` | PETG | Dış yüz (jant göbeği) tablada | yok | 5 / %40 | 65 | önce D delik deneme parçası |
| 2 Tekerler | `UGV-MECH-060-FR` | PETG | Dış yüz (jant göbeği) tablada | yok | 5 / %40 | 65 |  |
| 2 Tekerler | `UGV-MECH-060-RL` | PETG | Dış yüz (jant göbeği) tablada | yok | 5 / %40 | 65 |  |
| 2 Tekerler | `UGV-MECH-060-RR` | PETG | Dış yüz (jant göbeği) tablada | yok | 5 / %40 | 65 |  |
| 2 Tekerler | `UGV-MECH-061-FL` | TPU | Yan yüz tablada (eksen dik) | yok | 3 / %20 | 45 | TPU 95A, yavaş (≤25 mm/s) |
| 2 Tekerler | `UGV-MECH-061-FR` | TPU | Yan yüz tablada (eksen dik) | yok | 3 / %20 | 45 | TPU 95A, yavaş (≤25 mm/s) |
| 2 Tekerler | `UGV-MECH-061-RL` | TPU | Yan yüz tablada (eksen dik) | yok | 3 / %20 | 45 | TPU 95A, yavaş (≤25 mm/s) |
| 2 Tekerler | `UGV-MECH-061-RR` | TPU | Yan yüz tablada (eksen dik) | yok | 3 / %20 | 45 | TPU 95A, yavaş (≤25 mm/s) |
| 3 Gövde | `UGV-MECH-010-+1` | PETG | Dış yüz tablada | yok | 4 / %25 | 57 |  |
| 3 Gövde | `UGV-MECH-010--1` | PETG | Dış yüz tablada | yok | 4 / %25 | 57 |  |
| 3 Gövde | `UGV-MECH-011-+1` | PETG | Dış yüz tablada | yok | 4 / %25 | 57 |  |
| 3 Gövde | `UGV-MECH-011--1` | PETG | Dış yüz tablada | yok | 4 / %25 | 57 |  |
| 3 Gövde | `UGV-MECH-012-+1` | PETG | Dış yüz tablada; rulman yuvası tablaya açılır | yok | 5 / %40 | 59 | omuz boss'u: önce 6804 yuva deneme parçası |
| 3 Gövde | `UGV-MECH-012--1` | PETG | Dış yüz tablada; rulman yuvası tablaya açılır | yok | 5 / %40 | 59 | omuz boss'u ve servo çerçevesi vidaları |
| 3 Gövde | `UGV-MECH-013-1` | PETG | Üst yüz yukarı; pah son katmanlarda | yok | 4 / %25 | 76 | ön kapakta kargo ağzı |
| 3 Gövde | `UGV-MECH-013-2` | PETG | Üst yüz yukarı; pah son katmanlarda | yok | 4 / %25 | 77 | ön kapakta kargo ağzı |
| 3 Gövde | `UGV-MECH-013-3` | PETG | Üst yüz yukarı; pah son katmanlarda | yok | 4 / %25 | 71 | ön kapakta kargo ağzı |
| 3 Gövde | `UGV-MECH-022-+1` | PETG | Dış yüz tablada | yok | 4 / %25 | 123 |  |
| 3 Gövde | `UGV-MECH-022--1` | PETG | Dış yüz tablada | yok | 4 / %25 | 125 |  |
| 3 Gövde | `UGV-MECH-030` | PETG | Montaj yönünde, alt yüz tablada | yok | 5 / %40 | 11 |  |
| 3 Gövde | `UGV-MECH-031` | PETG | Montaj yönünde, alt yüz tablada; havşalar tablaya açılır | yok | 5 / %40 | 30 |  |
| 4 İç düzen | `UGV-MECH-056--1` | PETG | Servo plakası tablada, kollar yukarı | yok | 5 / %40 | 16 |  |
| 4 İç düzen | `UGV-MECH-057-+1` | PETG | Halka yüzü tablada | yok | 5 / %40 | 3 |  |
| 4 İç düzen | `UGV-MECH-070` | PETG | Montaj yönünde, alt yüz tablada | yok | 4 / %25 | 12 |  |
| 4 İç düzen | `UGV-MECH-071` | PETG | Montaj yönünde, alt yüz tablada | yok | 4 / %25 | 22 |  |
| 4 İç düzen | `UGV-MECH-072` | PETG | Montaj yönünde, alt yüz tablada | yok | 4 / %25 | 28 | direnç rafı: PETG ısıya ≈70 °C'ye kadar dayanır; TL1'de ölçülür |
| 4 İç düzen | `UGV-MECH-073` | PETG | Arka duvar tablada; taban dikey, köprü yok | yalnız yatay ayakların altına | 4 / %25 | 122 |  |
| 5 Dış parçalar | `UGV-MECH-015-FL` | PETG | Flanşın gövdeye bakan yüzü tablada | yok | 4 / %25 | 26 |  |
| 5 Dış parçalar | `UGV-MECH-015-FR` | PETG | Flanşın gövdeye bakan yüzü tablada | yok | 4 / %25 | 26 |  |
| 5 Dış parçalar | `UGV-MECH-015-RL` | PETG | Flanşın gövdeye bakan yüzü tablada | yok | 4 / %25 | 26 |  |
| 5 Dış parçalar | `UGV-MECH-015-RR` | PETG | Flanşın gövdeye bakan yüzü tablada | yok | 4 / %25 | 26 |  |
| 5 Dış parçalar | `UGV-MECH-017-+1` | TPU | İç yüz tablada | yok | 3 / %15 | 48 | TPU 95A |
| 5 Dış parçalar | `UGV-MECH-017--1` | TPU | İç yüz tablada | yok | 3 / %15 | 49 | TPU 95A |
| 5 Dış parçalar | `UGV-MECH-018` | TPU | Montaj yönünde, alt yüz tablada | yok | 2 / %100 | 5 | TPU 95A; yarıklar dilimleyicide açık kalmalı; kapağa yapıştırılır |
| 6 Baş | `UGV-MECH-040` | PETG | Açık alt tablada | yok | 5 / %40 | 36 | pan MG90S alttan girer; kulak çıkıntısı köprüyle basılır; 6804 yuvası üstte, önce deneme |
| 6 Baş | `UGV-MECH-041` | PETG | Bloğun açık üstü tablada, mil yukarı | yok | 5 / %40 | 19 | Ø20 mil dik; blok tabanı 38 mm köprü (yavaş köprü hızı); servo plakası olukları |
| 6 Baş | `UGV-MECH-042` | PETG | Kapak plakası tablada, bıçak yukarı | yok | 5 / %40 | 11 | itme çubuğu kanalı; aks göbeği deliği Ø9,4 yatay, gerekirse raybalanır |
| 6 Baş | `UGV-MECH-043-+1` | PETG | Ön yüz tablada, açık arka yukarı | dört ön tırnak ve sol gözdeki krank göbeği için ağaç destek | 4 / %25 | 28 | altıgen aks deliği iç duvarda |
| 6 Baş | `UGV-MECH-043--1` | PETG | Ön yüz tablada, açık arka yukarı | dört ön tırnak ve sol gözdeki krank göbeği için ağaç destek | 4 / %25 | 28 | altıgen aks deliği iç duvarda |
| 6 Baş | `UGV-MECH-044-+1` | PETG | Kapak plakası tablada, çerçeve yukarı | yok | 4 / %25 | 12 | sıkı geçme; önce deneme |
| 6 Baş | `UGV-MECH-044--1` | PETG | Kapak plakası tablada, çerçeve yukarı | yok | 4 / %25 | 12 | sıkı geçme; önce deneme |
| 6 Baş | `UGV-MECH-045` | PETG | Dik (altıgen uç tablada) | yok | 6 / %100 | 1 | göz aksı; %100 dolgu |
| 6 Baş | `UGV-MECH-046` | PETG | Montaj yönünde, alt yüz tablada | yok | 4 / %60 | 3 | tilt servo plakası |
| 7 Kollar | `UGV-MECH-050-+1` | PETG | Omuz kabuğunun düz yüzü tablada (park yönü) | 6704 yuvası, korna boşluğu ve twist cebinin altına ağaç destek | 5 / %40 | 46 | twist cebi: kapak 4 × M2 |
| 7 Kollar | `UGV-MECH-050--1` | PETG | Omuz kabuğunun düz yüzü tablada (park yönü) | 6704 yuvası, korna boşluğu ve twist cebinin altına ağaç destek | 5 / %40 | 47 | twist cebi: kapak 4 × M2 |
| 7 Kollar | `UGV-MECH-051-+1` | PETG | Yan yüz tablada | yok | 5 / %40 | 21 | dirsek MG996R: 4 × M3 insert, M4 somun cebi; iki M3 cepten adaptöre |
| 7 Kollar | `UGV-MECH-051--1` | PETG | Yan yüz tablada | yok | 5 / %40 | 21 | dirsek MG996R: 4 × M3 insert, M4 somun cebi; iki M3 cepten adaptöre |
| 7 Kollar | `UGV-MECH-052-+1` | PETG | Yan yüz tablada | yok | 5 / %40 | 40 | dirsek çatalı (624 yuvası yatay: önce deneme) + bilek MG996R yuvası |
| 7 Kollar | `UGV-MECH-052--1` | PETG | Yan yüz tablada | yok | 5 / %40 | 40 | dirsek çatalı (624 yuvası yatay: önce deneme) + bilek MG996R yuvası |
| 7 Kollar | `UGV-MECH-053-+1` | PETG | Yan yüz tablada | yok | 5 / %40 | 21 | bilek çatalı + MG90S dönüş yuvası |
| 7 Kollar | `UGV-MECH-053--1` | PETG | Yan yüz tablada | yok | 5 / %40 | 21 | bilek çatalı + MG90S dönüş yuvası |
| 7 Kollar | `UGV-MECH-054-+1` | PETG | Dış yüz tablada, kulak yüzü yukarı | yalnız çenelerin altına | 5 / %40 | 12 | pençe MG90S kulakları ve dönüş kornası M2 ile |
| 7 Kollar | `UGV-MECH-054--1` | PETG | Dış yüz tablada, kulak yüzü yukarı | yalnız çenelerin altına | 5 / %40 | 12 | pençe MG90S kulakları ve dönüş kornası M2 ile |
| 7 Kollar | `UGV-MECH-058--1` | PETG | Düz | yok | 3 / %40 | 5 | twist servo kapağı |
| 7 Kollar | `UGV-MECH-059--1` | PETG | Flanş tablada | yok | 6 / %100 | 3 | twist adaptörü: 25T korna ↔ 6704 iç bileziği; %100 dolgu, istenirse alüminyumdan tornalanır |

Basılmaya hazır parçaların baskı tahmini: PETG ≈2249 g, TPU ≈281 g (bekleyenler hariç; tamamı için [Lite mekanik](lite_mechanical_A3.md)).

## Vida, insert ve rulman

| Kalem | Adet |
|---|---:|
| M3 ısıl insert (Ø4,0 × 6 delik) | 34 |
| M3 × 10: kapaklar → panel insertleri | 12 |
| M3 × 25: boyun köprüsü → kapak → flanş → pan tabanı insertleri | 4 |
| M2 × 6 kendinden kılavuzlu: pan ve tilt MG90S kulakları 4, pan kornası → boyun 2, sütun kapağı → blok 4 | 10 |
| M4 × 30 + somun: göz aksı (iki gözü aksa sıkar) | 1 |
| M3 × 45 + somun: motor kelepçeleri | 8 |
| M4 × 12 + somun: panel ayakları → plaka | 10 |
| M3 × 12 + somun: batarya beşiği, tepsi, balast rafı, kargo ayakları → plaka | 12 |
| M3 × 8: pertinaks → tepsi insertleri | 4 |
| M3 × 10 + somun: çamurluklar → yan paneller | 12 |
| M3 × 10: omuz servo çerçevesi → insertler (duvardan) | 4 |
| M3 × 16 + somun: DS3218 kulakları → çerçeve | 4 |
| M3 × 8: korna → omuz mili (kılavuz) | 4 |
| M3 × 10: kargo kutusu flanşı → insertler (ön duvardan) | 2 |
| M3 × 10: MG996R kulakları → insertler (dirsek, bilek) | 8 |
| M3 × 8: 25T alüminyum korna → çatal iç yanağı (dirsek, bilek) | 8 |
| M3 × 8: 25T alüminyum korna → twist adaptörü (baş yuvada) | 4 |
| M3 × 12: üst kol B → twist adaptörü (B'nin servo cebinden) | 2 |
| M4 × 12 + somun + 0,5 mm pul: 624 boşta yatakları (dirsek, bilek) | 2 |
| M2 × 8 kendinden kılavuzlu: twist kapağı 4, MG90S kulakları 4, dönüş kornası → pençe 2 | 10 |
| Rulman 6804-2RS (boyun + iki omuz) | 3 |
| Rulman 6704-2RS (üst kol dönüşü) | 1 |
| Rulman 624ZZ (dirsek, bilek) | 2 |
| 25T alüminyum disk korna (twist, dirsek, bilek) | 3 |

Ek kirişlerin plakaya bağlanması (yapıştırma ya da vida) ve göz kapaklarının yapıştırılması montajda karar verilir.
