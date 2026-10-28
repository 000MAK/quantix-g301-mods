# G301: yedek → bootloader kilidi → Android 14/15 GSI → Magisk root

Telefon bilgisi (ADB'den okundu, 28.10.2026): MT6762/MT6765 (`k62v1_64_bsp`), Android 11, VNDK 30, Treble var,
dinamik bölümler (`super`), tek slot (A-only), sistem kökü (system-as-root) → **GSI türü: `arm64 ab`**. vbmeta: kilitli.

> ⚠️ Kilit açılınca telefon silinir. Root ve GSI sonrası banka uygulamaları, e-Devlet ve Google Wallet büyük ihtimalle çalışmaz.
> **1. adımdaki yedeği almadan devam etme:** MediaTek'te `nvram`/`nvdata`/`proinfo` kaybolursa IMEI ve şebeke gider.

Komutlar bu klasörde çalışır: `F:\Quantix_Master_Vault\08_GM20_Quantix_Edition\tools`.
`adb` ve `fastboot` Google'ın resmi aracı: `..\..\07_Note20Ultra_Clone\tools\platform-tools\`.

## 0. Telefonda
Ayarlar → Sistem → Geliştirici seçenekleri → **OEM kilit açma: AÇIK**.

## 1. Tam yedek (mtkclient, github.com/bkerler/mtkclient; zaten `tools\mtkclient` içine indirildi)
1. Sürücü: github.com/daynix/UsbDk/releases → `UsbDk_*_x64.msi` kur (yönetici).
2. Kurulum:
   ```
   py -3.12 -m venv .venv-mtk
   .venv-mtk\Scripts\pip install -r mtkclient\requirements.txt
   ```
3. Telefonu kapat. **Ses+ ve Ses− tuşlarına birlikte basılı tutarak** USB kablosunu tak (BROM modu).
4. ```
   .venv-mtk\Scripts\python mtkclient\mtk.py rl ..\backup --skip userdata
   ```
   Sonuç: `..\backup\` içinde `boot.bin`, `vbmeta.bin`, `super.bin`, `nvram.bin`, `nvdata.bin`, `proinfo.bin`, `seccfg.bin` vb.
   Bu klasörü ayrıca başka bir diske/Drive'a da kopyala.

## 2. Bootloader kilidini aç (resmi yol)
```
adb reboot bootloader
fastboot flashing unlock        (telefonda Ses+ ile onayla → telefon silinir)
```
Olmazsa: `.venv-mtk\Scripts\python mtkclient\mtk.py da seccfg unlock`

## 3. GSI (Android 14/15, arm64 ab)
Kaynaklar (GitHub): **ponces/treble_aosp** (Android 15/16, GApps'li sürüm var) veya **TrebleDroid/treble_experimentations** (Android 14).
İndir: `*arm64-ab*gapps*.img.xz` → aç → `gsi.img`.
```
fastboot --disable-verity --disable-verification flash vbmeta ..\backup\vbmeta.bin
fastboot reboot fastboot                         (fastbootd: dinamik bölümler için şart)
fastboot erase system
fastboot delete-logical-partition product         (yer yetmezse)
fastboot flash system gsi.img
fastboot -w
fastboot reboot
```

## 4. Magisk root
1. github.com/topjohnwu/Magisk/releases → `Magisk-v*.apk` kur.
2. `..\backup\boot.bin` dosyasını telefona kopyala, Magisk → Yükle → "Bir dosya seç ve yamala".
3. ```
   adb pull /sdcard/Download/magisk_patched-*.img magisk_patched.img
   adb reboot bootloader
   fastboot flash boot magisk_patched.img
   fastboot reboot
   ```

## 5. Sonra
Claude'a "telefon hazır" de: uygulamalar, Simba sesleri, sticker'lar, klavye, debloat ve ayarlar yeniden kurulur.

## Geri dönüş (her şeyi fabrika haline döndürmek)
BROM modunda: `.venv-mtk\Scripts\python mtkclient\mtk.py wl ..\backup` (userdata hariç tüm bölümleri geri yazar),
sonra `fastboot flashing lock`.

## 6. Açılış ekranı (General Mobile yazısı yerine Quantix)
Tasarım: `bootlogo\` (`make_boot.py`, önizleme `preview.png`).
- **Animasyon** (Android açılırken): root'tan sonra Magisk → Modüller → "Depodan yükle" → `bootlogo\Quantix_Bootanimation_Magisk.zip` → yeniden başlat.
  (GSI kendi animasyonunu getirirse modül onun üstüne yazar.)
- **İlk logo** (telefon açılırken yanan ilk görüntü, `logo` bölümü): 1. adımdaki yedekten `logo.bin` gelince Claude
  `quantix_logo.png`'yi bu cihazın logo.bin biçimine çevirir; `fastboot flash logo quantix_logo.bin` (kilit açıkken).
  Orijinali yedekte kalır: `fastboot flash logo ..\backup\logo.bin` ile geri dönülür.
