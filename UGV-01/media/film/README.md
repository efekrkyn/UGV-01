# UGV-01 tanıtım filmi

91 s, 1920×1080, 30 fps. Baştan sona kodla üretilir; tek bir hazır görsel ya da ses örneği yoktur:

- **Görüntü:** robot, projenin gerçek CAD modelidir (`tools/build_viewer.py` ağları, 96 parça, eklem zinciri). `film_template.html` her kareyi `renderAt(t)` ile belirlenimci çizer: robotun sürüşü (tekerler kat edilen yola göre döner), kamera yolları ve müziğin vuruşlarına oturan kesmeler, kol duruş grafiği, patlatılmış görünüm, X-ışını, sesli komut ve AI araç çağrılarını gösteren operatör paneli, ağırlık merkezi, imzalı paketler, E-stop, 36 kontrol ve ampullü tabela. Sayılar projeden gelir; kontrol listesi `tests/README.md`'den okunur.
- **Müzik:** `music.py` numpy ile 60'lar big band swing'i sentezler: kontrbas yürüyüşü, ride ve fırçalar, parmak şıklatma, sürdinli trompet, 4 sesli brass ve saksafon armonileri (fall-off'larla), vibrafon köprüsü; 132 BPM, Fa majör, final chorus Sol majöre çıkar ve button vuruşuyla biter. "Dur" anında orkestra susar. Melodi ve akorlar özgündür, hiçbir şarkıdan alınmamıştır.
- **Ses:** operatörün sesli komutları ("Mavi küpü al, kutuya koy.", "Dur!") ve robotun sözleri ("Merhaba.", "Küp kutuda.", "Hazırım.") macOS `say` Yelda sesinden üretilir; robotunki tizleştirilip hafifçe robotlaştırılır.
- **Senkron:** `timeline.json` tek saattir. Müzik, yazılar, kol, baş ve kamera aynı dosyadan beslenir.

Robot, projenin kuralı gereği özgün tasarım UGV-01 olarak anlatılır. Filmde başka bir karakterin adı, logosu ya da müziği kullanılmaz.

## Üretmek

```sh
zsh media/film/make_film.sh        # müzik → film sayfası → 2730 kare (Chrome, GPU) → out/UGV-01_tanitim.mp4
```

Gerekenler: ffmpeg, Node ≥22, Google Chrome, macOS `say` (Yelda), CAD sanal ortamı (`.venv`, cadquery). Kareler varsayılan olarak `/tmp/ugv-film-frames` altına yazılır (≈1 GB). Yazıyı, zamanlamayı ya da kamerayı değiştirmek için `timeline.json`'u düzenleyip betiği yeniden çalıştırmak yeter.

## İsteğe bağlı: şarkılı sürüm (Suno)

Film enstrümantal swing ile gelir. Sözlü bir crooner sürümü istenirse aşağıdaki özgün sözler ve stil Suno'ya verilebilir. Üretilen şarkı `out/score.wav` yerine konur (sesli komut ve robot sesleri istenirse üstüne yeniden karıştırılır) ve yalnız son ffmpeg adımı çalıştırılır. Suno ücretli ya da hesaplı bir hizmettir; kullanıcı kendisi üretir. Suno sanatçı adlarını kabul etmeyebilir; stil bu yüzden tarif edilir.

**Stil:** `1960s Las Vegas big band swing, smooth baritone crooner, brassy shout chorus with trumpet fall-offs, walking upright bass, brushed drums and finger snaps, muted trumpet fills, vibraphone bridge, key change up a whole step, button ending, 132 bpm, confident, witty, cool`

**Sözler (özgün):**

```
[Intro – drum roll, brass hit]
(spoken) Ladies and gentlemen... the little machine.

[A]
Four wheels rolling, nice and slow,
every turn counted, top to toe,
two glass eyes that read the room —
well, I clock the cube before you do.

[A]
Ninety-six parts, not one to spare,
swept every angle with the greatest care,
seven roads my arm can take,
and not one bump, for goodness' sake.

[Bridge – vibes, finger snaps]
You say "pick it up", I say "consider it done",
I look, I roll, I reach — one, two, and one,
but say the word "stop" and I'm still as a stone,
'cause the brakes, my friend, are yours alone.

[Shout chorus – up a step]
I'm small, but I'm something,
built right from the ground,
I sign every message
that I'm passing around,
keep my center low and my promises true —
that's the little machine, and it's rolling to you.

[Tag – button]
Next stop... the printer.
(spoken) Ready when you are.
```
