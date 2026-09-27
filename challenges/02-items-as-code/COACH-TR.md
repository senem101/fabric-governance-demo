# Challenge 02 — Fabric öğelerini kodla yönetme: coach rehberi

[Türkçe başlangıç](../../docs/tr/README.md) · [İlk kurulum](../../docs/tr/ilk-kurulum.md) · [Coach el kitabı](../../docs/tr/coach-el-kitabi.md) · [Asıl challenge](challenge.md)

**Kime yönelik?** Kendi müşterisine eğitim veren coach ve GitHub'ı ilk kez kullanan katılımcılar.
**Tahmini süre:** 20 dakika açıklama + 35 dakika çevrimdışı demo + 50–80 dakika geliştirme atölyesi + 15 dakika değerlendirme.
İlk kez item otomasyonu geliştiren bir ekip için tamamlanması ek çalışma gerektirir; bu bir hazır dağıtım tarifi değildir.

## 1. Müşteriye 60 saniyede anlatın

> “Workspace bir proje odasıdır. Lakehouse verinin tutulduğu alan, notebook
> veriyi işleyen talimat defteri, warehouse ise SQL ile sorgulanan veri deposudur.
> Odayı onaylamak yeterli değildir; içine konulan araçların da amacı ve sahibi belli olmalı.
> İstediğimiz düzeni YAML adlı okunabilir bir dosyada tarif edeceğiz.
> GitHub bu dosyanın geçmişini tutar; pull request, değişikliği başkasına inceletme isteğidir.
> Copilot taslak hazırlamaya yardım eder, müşteri adına onay vermez.
> Bugün repoda çalışan workspace kontrolünü kullanacağız; item otomasyonunu ise ayrı bir geliştirme olarak tasarlayacağız.”

**Başarı mesajı:** “Dosya hazır”, “kontrol geçti” ve “Fabric'te oluştu” üç farklı kanıttır.

## 2. Bugün ne var, ne geliştirilecek?

| Konu | Bugün repoda | Bu challenge'da geliştirilecek |
|---|---|---|
| Şema | Yalnız `schemas/workspace.schema.json` | `schemas/item.schema.json` — **OLUŞTURULACAK** |
| Kontrol | `validate.py` workspace şemasını, `rules_engine.py` workspace kurallarını kullanır | Item dosyaları, tür bazlı ad ve bağımlılık denetimi |
| Uygulama | `provision.py` workspace/açıklama/kapasite ve eksik rol ekleme işlemleri | `scripts/provision_items.py` — **OLUŞTURULACAK** |
| Örnek item | Bu challenge altında hazır starter item dosyası yok | `starter/items/<workspace>/` örnekleri — **OLUŞTURULACAK** |
| CI | `validate`, `provision`, `drift`, `pages` workflow dosyaları | `.github/workflows/items.yml` — **OLUŞTURULACAK** |
| Drift | Görülebilen workspace adları ve açıklama | Item tanımı, bağlar, etiket ve izin karşılaştırması |

`rules/policy.yaml` içine `items:` yazmak tek başına yeni kural çalıştırmaz.
Mevcut provisioner item, domain, sensitivity label, tag veya “managed-by” işareti uygulamaz.
Asıl challenge'daki rol/tag uygulama maddeleri hedef tasarımdır; bütün item türlerine uyan tek bir API varmış gibi anlatmayın.

## 3. Dersten önce coach kontrol listesi

- [ ] Challenge 00–01'in temel kavramları ve [ilk kurulum](../../docs/tr/ilk-kurulum.md) tamamlandı.
- [ ] Müşteriye ayrılmış eğitim fork'u açık; üretim reposuna veya upstream `main` dalına yazılmıyor.
- [ ] VS Code klasörü, Git hesabı, Python sanal ortamı ve Copilot erişimi çalışıyor.
- [ ] Copilot kullanımında müşteri verisi/kimlik bilgisi paylaşımı için kurum politikası biliniyor.
- [ ] Yerel bölüm için Fabric hesabı, Azure aboneliği veya admin yetkisi gerekmediği açıklanıyor.
- [ ] Canlı gözlem isteniyorsa müşteri yöneticisi sandbox workspace ve izinli öğeleri önceden onayladı.
- [ ] Canlı item oluşturma için desteklenen Fabric kapasitesi, açık tenant özelliği ve en az Contributor yetkisi doğrulandı.
- [ ] Service principal kullanılacaksa ilgili item türü/API kimlik desteği ve tenant ayarları ayrıca doğrulandı.
- [ ] Power BI Pro/PPU'nun tek başına Lakehouse/Warehouse için Fabric kapasitesi yerine geçmediği biliniyor.
- [ ] Müşteri veri sahibi, workspace yöneticisi ve kapasite maliyet sahibi isimleri belli.

Read-only bir soru için bütün tenant'a Admin vermeyin.
`getDefinition` işlemi veri değiştirmez fakat API item üzerinde okuma **ve yazma** izni isteyebilir.
İzin yoksa onu genişletmek yerine metadata ile yetinin ve “tanım doğrulanamadı” yazın.
Skill ve MCP araç adlarını kurulu katalogdan kontrol edin; asıl challenge'daki eski kurulum/skill adlarını ezbere çalıştırmayın.

## 4. Ekran başında adım adım başlangıç

1. **GitHub → eğitim fork'u → Code** ekranında adresin müşterinin eğitim kopyasına ait olduğunu gösterin.
   “GitHub ortak dosya dolabı; bilgisayarımızdaki klasör bunun çalışma kopyasıdır” deyin.
2. **VS Code → File → Open Folder** ile bu kopyanın kökünü açın. Explorer'da `schemas`, `scripts`, `workspaces` görünmeli.
3. Sol alt dal adına tıklayın → **Create new branch** → `egitim/items-lab01`.
   Dalın amacı ana sürümü bozmadan taslak hazırlamaktır; mevcut başka değişiklikleri taşımayın.
4. **Ctrl+P** ile `schemas/workspace.schema.json`, ardından `scripts/validate.py` dosyalarını açın.
   `additionalProperties: false` satırını gösterin: workspace dosyasına rastgele item alanı eklenemez.
5. **Terminal → New Terminal → PowerShell** açın. Aşağıdaki komutlar yalnız yerel envanter ve kontrol içindir:

   ```powershell
   Get-Location
   git status --short
   Test-Path .\schemas\item.schema.json
   Test-Path .\scripts\validate_items.py
   Test-Path .\scripts\provision_items.py
   $env:LIVE_CHECKS = 'false'
   .\.venv\Scripts\python.exe .\scripts\validate.py .\workspaces\pt-nlyt-sample-ndf-dev-hello1.yaml
   $LASTEXITCODE
   ```

6. Mevcut sürümde üç `Test-Path` sonucu `False`; örnek workspace kontrolü `PASS` ve çıkış kodu `0` olmalı.
   `validation-report.md` yerelde üretilir; bu bir dağıtım kaydı değildir. Sanal ortam yoksa ortak kuruluma dönün.
7. Örnekteki kapasite/grup kimliklerinin sahte olduğunu gösterin. `LIVE_CHECKS=false` gerçek grubun varlığını kanıtlamaz.
   Bu bölümde `provision.py` çalıştırmayın; varsayılanı gerçek değişikliğe izin verir.

## 5. Güvenli sentetik demo: önce tasarım

1. Tahtaya hedef adı yazın: `pt-nlyt-sales-ndf-dev-lab01`.
   Altı parça `pt`, `nlyt`, `sales`, `ndf`, `dev`, `lab01`; `environment` alanı da `dev` olmalıdır.
2. Workspace örneğinin **ayrı bir yerel taslağında** `name`, `subject`, `suffix` alanlarını değiştirin.
   Diğer zorunlu alanları silmeyin: özellikle `country`, `area`, `dataProductType`, `domain`, `subDomain`.
   Taslağı canlıya hazır `workspaces/` girdisi saymayın; sahte kimliklerle merge/deploy yapılmaz.
3. VS Code Explorer'da `challenges/02-items-as-code/starter/items/pt-nlyt-sales-ndf-dev-lab01/` klasörünü oluşturun.
   Bu yol **OLUŞTURULACAK alıştırma çıktısıdır**, mevcut otomasyon tarafından taranmaz.
4. İçinde `lh_bronze_raw.yaml` adlı yeni dosya açıp aşağıdaki **önerilen sözleşmeyi** kaydedin.
   Bu, Fabric REST gövdesi veya mevcut workspace şemasına uygun dosya değildir.

   ```yaml
   workspace: pt-nlyt-sales-ndf-dev-lab01
   kind: Lakehouse
   name: lh_bronze_raw
   description: "Yalnizca uydurma satis olaylariyla yapilan egitim icin ham veriyi tutan lakehouse."
   sensitivityLabel: General
   owners:
     - principalType: Group
       identifier: "44444444-4444-4444-4444-444444444444"
   tags:
     purpose: synthetic-training
   Lakehouse:
     schemaEnabled: true
     shortcuts: []
   ```

5. Sahte GUID'yi gerçek gruba çözmeye çalışmayın. Dış veri bağlantısı veya shortcut açmayın.
6. Yeni iki taslak tasarlayın: `nb_silver_clean` notebook ve `wh_marts_sales` warehouse.
   Notebook için dil ve bağlı lakehouse; warehouse için desteklenen collation kararı yazın.
   Her dosyada ≥60 karakter anlamlı açıklama ve sahip grup bulunmasını hedefleyin.
7. Sentetik giriş olarak yalnız `(event_id, timestamp, amount)` satırlarını kullanın:
   `(1, 2026-01-01T10:00:00Z, 10)`, aynı satır tekrar, `(2, 2026-01-01T10:01:00Z, 20)`.
   Beklenen tekilleştirme sonucu **3 giriş → 2 olay → toplam 30**.
8. Şimdilik bu sonucu kağıtta veya yerel hesapla gösterin. Notebook çalıştırmak/Spark oturumu başlatmak bu demoya dahil değildir.
   Lakehouse'a veri yazıldığını veya warehouse tablolarının oluştuğunu iddia etmeyin.

## 6. Copilot ile güvenli geliştirme alıştırması

**VS Code → Copilot Chat** açın. Dosyaları bağlam olarak seçin; aşağıdaki isteği gönderin:

```text
Yalnız yerel taslak üret. scripts/validate.py, scripts/rules_engine.py ve workspace
şemasını incele. Challenge 02 için OLUSTURULACAK item şemasını, item validatorünü
ve sentetik testleri öner. Önce plan ve dosya farkını göster; incelemem olmadan
değişiklikleri uygulama. Terminal, MCP mutasyonu, oturum açma, dağıtım, notebook
çalıştırma, commit/push/PR merge yapma. Müşteri tenant'ına bağlanma.
pt-nlyt-sales-ndf-dev-lab01 adını kullan. Tür bazlı ad, mevcut workspace referansı,
>=60 karakter açıklama, Group sahip, bağımlılık ve sahte secret negatif testi ekle.
API tanımlarını resmi belgelerle doğrula; desteklenmeyen özelliği uydurma.
Yeni şema/scriptten varmış gibi söz etme; test sonucu çalıştırılmadıysa belirt.
```

Coach incelemesinde şu sırayı izleyin:

1. `schemas/item.schema.json` **OLUŞTURULACAK:** türler arası alan karışmasını engelleyen şema ve yerel testler.
2. `scripts/validate_items.py` **OLUŞTURULACAK:** dosya tarama, parent workspace referansı, notebook içeriği ve policy kontrolleri.
   Mevcut `validate.py`'a item dosyası vermek item kontrolü değildir; workspace şemasına takılır.
3. Secret testi için yalnız `DEMO_NOT_A_SECRET` gibi açıkça sahte değer kullanın.
   Regex kontrolünün gerçek secret taraması ve güvenlik incelemesinin yerini tutmadığını söyleyin.
4. `scripts/provision_items.py` **OLUŞTURULACAK:** önce hiçbir API çağrısı yapmayan plan çıktısı; sonra mock API testleri.
   Aynı `(workspaceId, tür, ad)` için tekrar çalıştırma kopya item oluşturmamalı.
5. Gerçek API eşlemesinde `kind/name` ile `type/displayName` ayrımını yapın.
   `creationPayload` ve `definition` birlikte gönderilmez; notebook tanımı türün belgelerine göre hazırlanır.
   Generic Create Item açıklaması en fazla 256 karakterdir; taslakta ≥60 kuralıyla birlikte bu üst sınırı da kontrol edin.
6. `202 Accepted`, işlemin tamamlandığı anlamına gelmez: operasyon durumunu izleme, timeout ve `Retry-After` ele alınmalı.
   Lakehouse → notebook bağımlılığı çözülmeden notebook oluşturma denenmemeli.
7. Item izinleri, tag ve sensitivity kalıtımı için tür/API destek matrisi hazırlayın.
   Workspace `sensitivityLabel` alanından otomatik platform kalıtımı varmış gibi davranmayın.

## 7. PR ve workflow entegrasyonunun dürüst sınırı

1. **Source Control → değişen dosya** ile farkı gösterin; katılımcı neyin değiştiğini kendi sözleriyle anlatmalı.
2. Yalnız onaylı eğitim kopyasında dosyaları seçerek stage/commit yapın, dalı yayınlayın.
   **GitHub → Pull requests → New pull request** ekranında base repo'nun eğitim fork'u olduğunu doğrulayın.
3. PR açıklamasına “yerel doğrulama”, “mock test”, “canlı doğrulama yapılmadı” bölümlerini ekleyin.
   PR açmak ve birleştirmek farklıdır; müşteri reviewer'ı incelemeden merge etmeyin.
4. Bu kopyadaki `validate.yml` tüm PR'larda çalışır, ancak mevcut script yalnız workspace manifestlerini doğrular.
   Workflow'un item değişikliğinde tetiklenmesi tek başına item kontrolü sağlamaz.
5. Yeni `items.yml` **OLUŞTURULACAK**; gerçek veri yolu, şema, validator, policy ve test değişikliklerini kapsamalı.
   Starter dosyaları root `items/` dizinine taşınacaksa bu sözleşmeyi ve referans çözümünü açıkça belirleyin.
6. `provision.yml`'de item yolu ve item uygulama adımı yok; bunlar **OLUŞTURULACAK**.
   Canlı merge'den önce required checks, deployment environment onayı ve doğru hedef workspace zorunlu olmalı.
7. Bu kopyadaki mevcut workflow'lar GitHub-hosted `ubuntu-latest`, Python 3.12 ve Linux `.venv/bin` kullanır; canonical Actions hazır servis değildir.
   Runner/izolasyon için [ilk kurulumu](../../docs/tr/ilk-kurulum.md) izleyin; Windows terminal komutunu workflow'a aynen taşımayın.

## 8. Canlı ortam varsa: yalnız onaylı, salt okunur doğrulama

1. Müşteri admin onayıyla **Fabric → Workspaces → onaylı sandbox → öğe listesi** açın.
   Ekrandaki workspace adı/kimliği ile PR hedefini karşılaştırın; **New item** veya **Run** seçmeyin.
2. Item oluşumu ancak geliştirme, test ve PR üzerinden onaylı uygulama tamamlandıysa beklenir.
   Yoksa “mevcut değil” gözlemi doğrudur; boşluğu portalda elle doldurmayın.
3. İzinli MCP sunucusunda araç listesini kontrol edip şu doğrulama isteğini kullanın:

   ```text
   Yalnız pt-nlyt-sales-ndf-dev-lab01 adlı, müşteri tarafından onaylı sandbox'ı oku.
   Önce workspace kimliğini ve kullandığın hesabın kapsamını bildir. Sadece öğeleri
   listele ve destekleniyorsa lh_bronze_raw, nb_silver_clean, wh_marts_sales
   metadata/tanımlarını oku. getDefinition semantik olarak okuma olsa da POST ve
   yazma izni gerektirebilir; yetki yoksa dur, etiketi kaldırma/izni genişletme.
   Hiçbir item oluşturma/güncelleme/silme, notebook çalıştırma veya veri yükleme.
   Manifest ile farkları, çağrı zamanını ve doğrulanamayan alanları açıkça göster.
   ```

4. `getDefinition` sensitivity label içermez; etiket için ayrı desteklenen metadata kaynağı gerekir.
   Tanımdaki base64 parçalarını karşılaştırırken değişken sistem alanlarını ayırın; gerçek secret/çıktıyı PR'a taşımayın.

## 9. Kabul ve negatif test kartı

| Deneme | Gözlenebilir sonuç |
|---|---|
| Bugün: örnek workspace kontrolü | `PASS`; item oluşturulmuş olduğu sonucu çıkarılmaz |
| Geliştirilecek: üç geçerli item | Üç dosya raporda görünür; sessizce atlanmaz |
| Eksik/kısa açıklama, yanlış tür adı | İlgili dosya/rule ile blok ve sıfırdan farklı çıkış kodu |
| Var olmayan parent/bağlı lakehouse | Blok; keyfi workspace yaratma yok |
| Sahte hard-coded secret | Notebook testi blok; gerçek kimlik bilgisi kullanılmaz |
| İkinci uygulama/mock `202`/`429` | Tekilleştirilmiş plan; tamamlanmayı bekleme; sınırlı yeniden deneme |
| Canlı başarı, yalnız uygulama geliştirildikten sonra | PR SHA + workflow kaydı + üç item kimliği + okunmuş tanım karşılaştırması |

**Sık hata:** `No workspace manifests changed` item'in geçtiği anlamına gelmez.
**403:** tenant, hedef workspace rolü ve item API kimlik desteğini kontrol edin; otomatik Admin vermeyin.
**Tanım okunamıyor:** desteklenmeyen tür/korunan etiket olabilir; etiketi kaldırmayın, metadata kanıtı ile sınırı yazın.
**Yeşil workflow ama öğe yok:** mevcut script item uygulamaz; ayrıca warning'leri inceleyin, doğru tenant/kimliği doğrulayın.
**Kapasite kapalı:** yöneticinin planını kontrol edin; sırf demo için kapasite açmayın/büyütmeyin.

## 10. Kapanış, yedek demo ve kaynaklar

- **Soru:** “YAML kaydedersem lakehouse oluşur mu?” **Yanıt:** Hayır; uygulanmış ve onaylanmış bir entegrasyon gerekir.
- **Soru:** “Copilot'un kodu neden inceleniyor?” **Yanıt:** API biçimini veya eksik script'i uydurabilir; test kanıtı şarttır.
- **Soru:** “İkinci çalıştırma neden önemli?” **Yanıt:** Tekrarlanan dağıtımın kopya nesne üretmediğini gösterir.
- **Demo yoksa:** yerel şema kontrolü, sentetik üç satır ve elle hazırlanmış “BEKLENEN/MOCK” item listesiyle ilerleyin.
  Bu çıktı **gerçek dağıtım kanıtı değildir**; canlı kabul maddelerini “yapılmadı” bırakın.
- **Maliyet/temizlik:** bu ders için otomatik Spark/SQL çalıştırma, kapasite satın alma veya yeniden boyutlandırma yok.
  Onaylı canlı çalışmada bitiş saati/sahip belirleyin; yalnız eğitim kaynaklarını yönetici kontrolünde temizleyin.
  YAML silmek Fabric item silmez; paylaşılan kapasiteyi durdurmayın. Sentetik dosyaları ve yerel raporu seçerek kaldırın.

Kaynaklar (24 Eylül 2026'da kontrol edildi):
[Create Item](https://learn.microsoft.com/en-us/rest/api/fabric/core/items/create-item) ·
[Get Item Definition](https://learn.microsoft.com/en-us/rest/api/fabric/core/items/get-item-definition) ·
[Fabric lisansları](https://learn.microsoft.com/en-us/fabric/enterprise/licenses) ·
[Workspace rolleri](https://learn.microsoft.com/en-us/fabric/fundamentals/roles-workspaces) ·
[VS Code kaynak kontrolü](https://code.visualstudio.com/docs/sourcecontrol/overview).
