# UGV-01 tanıtım filmi

91 s, 1920×1080, 30 fps. Baştan sona kodla üretilir; tek bir hazır görsel ya da ses örneği yoktur:

- **Görüntü:** robot, projenin gerçek CAD modelidir (`tools/build_viewer.py` ağları, 96 parça, eklem zinciri). `film_template.html` her kareyi `renderAt(t)` ile belirlenimci çizer: robotun sürüşü (tekerler kat edilen yola göre döner), kamera yolları ve müziğin vuruşlarına oturan kesmeler, kol duruş grafiği, patlatılmış görünüm, X-ışını, sesli komut ve AI araç çağrılarını gösteren operatör paneli, ağırlık merkezi, imzalı paketler, E-stop, 36 kontrol ve ampullü tabela. Sayılar projeden gelir; kontrol listesi `tests/README.md`'den okunur.
- **Müzik:** `music.py` numpy ile 60'lar big band swing'i sentezler: kontrbas yürüyüşü, ride ve fırçalar, parmak şıklatma, sürdinli trompet, 4 sesli brass ve saksafon armonileri (fall-off'larla), vibrafon köprüsü; 132 BPM, Fa majör, final chorus Sol majöre çıkar ve button vuruşuyla biter. "Dur" anında orkestra susar. Melodi ve akorlar özgündür, hiçbir şarkıdan alınmamıştır.
- **Ses:** operatörün sesli komutları ("Mavi küpü al, kutuya koy.", "Dur!") ve robotun sözleri ("Merhaba.", "Küp kutuda.", "Hazırım.") macOS `say` Yelda sesinden üretilir; robotunki tizleştirilip hafifçe robotlaştırılır.
- **Şarkılı sürüm:** `vocals.py` (`music.py --vocal`), aşağıdaki Türkçe sözleri bir kadın sesine söyletir. Ses macOS `say` Yelda'dır: her hece ayrı okunur, WORLD vokoderiyle (pyworld) çözümlenir ve notasına bir şarkıcı gibi yerleştirilir. Ünsüzler doğal uzunluğunda kalır ve vuruştan hemen önce gelir; ünlü notayı dolduracak kadar uzar. Perde melodiyi izler: cümle başında küçük bir kayma, notalar arasında hafif aşan geçiş, uzun notalarda geç gelen vibrato. Bütün parça tek bir akış olarak yeniden sentezlendiği için ses kendi tınısını korur, vokoder robotluğu yoktur. Notalar hedefin birkaç cent yakınında ölçüldü. Kıtalar grup ve mühendislik bölümlerinde, köprü güven bölümünde; son "elinde" Sol majöre geçişin üstünde tutulur. Nakarat shout chorus'ta, "küçük robot, büyük iş" kapanışta. AI bölümü operatör komutları duyulsun diye sözsüzdür. Açılış anonsu: "Hanımlar, beyler… karşınızda: küçük robot!". Aranje vokal için değişir: melodiyi çalan trompet ve saksafon, satır aralarında cevap, pedler ve brass vuruşlarına çekilir.
- **Müzik dosyaları:** `audio/UGV-01_swing_enstrumantal.mp3` ve `audio/UGV-01_swing_sarkili.mp3` (91 s, 192 kbps).
- **Senkron:** `timeline.json` tek saattir. Müzik, yazılar, kol, baş ve kamera aynı dosyadan beslenir.

Robot, projenin kuralı gereği özgün tasarım UGV-01 olarak anlatılır. Filmde başka bir karakterin adı, logosu ya da müziği kullanılmaz.

## Üretmek

```sh
zsh media/film/make_film.sh        # müzik (iki sürüm) → film sayfası → 2730 kare (Chrome, GPU) → out/UGV-01_tanitim.mp4 ve out/UGV-01_tanitim_sarkili.mp4
```

Gerekenler: ffmpeg, Node ≥22, Google Chrome, macOS `say` (Yelda), CAD sanal ortamı (`.venv`, cadquery), `uv` (şarkılı sürüm pyworld'ü geçici bir ortamda çalıştırır). Kareler varsayılan olarak `/tmp/ugv-film-frames` altına yazılır (≈1 GB). Yazıyı, zamanlamayı ya da kamerayı değiştirmek için `timeline.json`'u düzenleyip betiği yeniden çalıştırmak yeter.

## Sözler ve isteğe bağlı gerçek şarkıcı sürümü (Suno)

Şarkılı sürümde bu sözleri Yelda sesinden sentezlenen kadın vokal söyler. Gerçek bir insan sesi istenirse aynı sözler ve stil Suno'ya verilebilir. Üretilen şarkı `out/score_vocal.wav` yerine konur (sesli komut ve robot sesleri istenirse üstüne yeniden karıştırılır) ve yalnız son ffmpeg adımı çalıştırılır. Suno ücretli ya da hesaplı bir hizmettir; kullanıcı kendisi üretir. Suno sanatçı adlarını kabul etmeyebilir; stil bu yüzden tarif edilir.

**Stil:** `1960s big band swing, warm female jazz vocalist singing in Turkish, smooth and playful, brassy shout chorus with trumpet fall-offs, walking upright bass, brushed drums and finger snaps, muted trumpet fills, key change up a whole step, button ending, 132 bpm, elegant, witty`

**Sözler (özgün):**

```
[Intro – trampet, brass vuruşu]
(anons) Hanımlar, beyler... karşınızda: küçük robot!

[Kıta 1]
Dört tekerle ağır ağır gelir,
her dönüşünü tek tek bilir,
iki cam gözle odayı okur,
küpü senden önce bulur.

[Kıta 2]
Doksan altı parça, fazlası yok,
her açıya bakılmış, eksiği yok,
kolu yedi yoldan uzanır,
bir kez olsun çarpmaz, sakınır.

[Köprü – güven]
Ama "dur" de, taş gibi durur,
çünkü fren, dostum, senin elinde.

[Nakarat – bir ton yukarı]
Küçük ama ciddi iş,
temelden sağlam iş,
her mesajı imzalı,
her adımı hesaplı,
ağırlığı alçakta, sözünün eri o.

[Kapanış – button]
Küçük robot... büyük iş.
```
