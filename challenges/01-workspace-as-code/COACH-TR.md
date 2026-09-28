# Challenge 01 - Coach rehberi: workspace'i dosyadan yönetme

[Tüm rehberler](../../docs/tr/README.md) |
[Önceki: 00](../00-setup/COACH-TR.md) |
[Orijinal challenge](challenge.md) |
[Sonraki: 02](../02-items-as-code/COACH-TR.md)

**Amaç:** İstek dosyası, kural kontrolü, PR onayı, Actions ve gerçek Fabric
workspace'i arasındaki ilişkiyi öğretmek.
**Tahmini süre:** 90-120 dk; 00 önceden tamamlanmış olmalı.

## 1. Bir dakikalık anlatım

> “Portalda doğrudan bir oda açmak yerine önce bir talep formu hazırlıyoruz.
> Formda odanın adı, kapasitesi ve kimlerin girebileceği yazıyor. Otomasyon
> formun kurallara uyup uymadığını kontrol ediyor. Bir ekip arkadaşı onaylıyor.
> Sonra otomasyon formdaki isteği Fabric'e uyguluyor. Sonuç yalnız yeşil bir
> ışık değil; gerçek workspace ve doğru yetkilerle kanıtlanmalı.”

## 2. Bu challenge'da hazır olanlar ve sınırlar

| Hazır | Hazır değil / sınır |
|---|---|
| Workspace JSON schema ve policy doğrulama; bütün manifestler için yazma öncesi kontrol | Kontroller ve API erişimi, tenant genelinde isim yokluğu kanıtı değildir |
| Workspace açma; açıklama, `managed-by` işareti ve kapasiteyi güncelleme; sonucu geri okuma | Domain/label/tag uygulama ve otomatik rollback |
| Eksik owner rolünü ekleme | Fazla rolü kaldırma, mevcut rolü dönüştürme, expiry |
| Görünür workspace adları/açıklamalarını karşılaştırma | Tüm tenant, roller, kapasite ve hassasiyet drift'i |
| Drift raporu ve workflow ile issue açma | Otomatik düzeltme veya issue kapatma |

Orijinal challenge'daki `dev-plt-...` örneklerini güncel manifest olarak
kullanmayın. Aşağıdaki altı parçalı yapı mevcut şemaya uygundur.

## 3. Hazırlık

1. [00 rehberini](../00-setup/COACH-TR.md) bitirin. İlk provada
   `LIVE_CHECKS=false`, GitHub `DRY_RUN=true` olsun.
2. Repo kökünü VS Code'da açın. Aktif branch'inizi ve `origin` adresini
   [ilk kurulumdaki](../../docs/tr/ilk-kurulum.md) şekilde kontrol edin.
3. Canlı demo için gerçek kapasite ID'sinin **policy içinde** güncellendiğini
   ve en az iki owner kimliğinin hazır olduğunu doğrulayın. Dev örneğimiz
   bir Group Admin ve bir User Member kullanır; iki Group şartı `prd` içindir.
4. Provisioner tüm `workspaces\*.yaml` dosyalarını işler. Depodaki
   `tr-nlyt-sample-ndf-dev-hello1.yaml` örneğini de gerçek değerlere uyarlayın
   veya müşteri lab'ı hazırlık PR'ında kaldırın. Sahte owner'larla bırakmayın.
5. Var olan müşteri workspace'iyle aynı adı seçmeyin. Kod, aynı ad birden çok
   görünür kaynakta varsa veya mevcut kaynak bu repo'nun `managed-by` işaretini
   taşımıyorsa durur; otomatik sahiplenme yapmaz. İşaret yetkilendirme sınırı
   değildir; gerçek erişim kontrolü Fabric RBAC ve GitHub onaylarıdır.

## 4. Dosyaları önce birlikte okuyun

VS Code Explorer'da sırayla açın:

| Dosya | Katılımcıya gösterilecek |
|---|---|
| `schemas\workspace.schema.json` | Zorunlu alanlar ve izinli biçimler |
| `rules\policy.yaml` | Kapasite, domain, cost center listeleri |
| `scripts\rules_engine.py` | Kuralların gerçekten uygulandığı yer |
| `.github\workflows\validate.yml` | PR gelince yapılan kontrol |
| `.github\workflows\provision.yml` | Merge sonrası onaylı uygulama |

**Coach sorusu:** “YAML'e yeni bir özellik eklersek otomasyon bunu kendiliğinden
uygular mı?” Beklenen yanıt: Hayır; şema, doğrulayıcı, uygulayıcı ve gerekirse
workflow birlikte desteklemelidir.

## 5. İlk manifesti oluşturun

1. Kendi branch'inizde `workspaces` klasörüne sağ tıklayın, **New File** seçin.
2. Dosya adı: `tr-nlyt-sales-ndf-dev-lab01.yaml`.
3. Aşağıdaki **yerel prova örneğini** yapıştırın; `Ctrl+S` ile kaydedin.
   İki örnek GUID canlıya gitmeden gerçek grup Object ID'leriyle değiştirilmeli.

```yaml
name: tr-nlyt-sales-ndf-dev-lab01
country: tr
area: nlyt
subject: sales
dataProductType: ndf
environment: dev
suffix: lab01
domain: dom-ops-dat
subDomain: sdm-nlyt-sales
description: "Training workspace for sales analytics using synthetic data only."
capacity: senem2fabric
region: westeurope
sensitivityLabel: General
costCenter: CC-1001
owners:
  - principalType: Group
    identifier: "11111111-1111-1111-1111-111111111111"
    role: Admin
    groupName: grp_fabric_dev_nlyt_admin
  - principalType: Group
    identifier: "22222222-2222-2222-2222-222222222222"
    role: Member
    groupName: grp_fabric_dev_nlyt_member
tags:
  purpose: coach-training
```

| Alan | Açıklama |
|---|---|
| `tr` | Türkiye ülke kodu; bu demo için policy'deki onaylı ülkelere eklendi |
| `nlyt`, `sales` | Sorumlu alan ve veri konusu |
| `ndf` | Henüz Bronze/Silver/Gold ayrımı olmayan veri ürünü |
| `dev` | Geliştirme ortamı |
| `lab01` | Takımınıza özel kısa ayırt edici ek |
| `capacity` | Policy anahtarı; görünen kapasite adı veya GUID yerine mantıksal ad |
| `owners` | En az iki kayıt, en az bir Group, en az bir Admin |

`name` parçaları ile ayrı alanlar aynı olmalı. Örneğin suffix değişince hem
`name` son parçasını hem `suffix` değerini değiştirin; dosya adını da tutarlı
tutun. `description` en az 30 karakter olmalı.
`groupName` grubu oluşturmaz veya yeniden adlandırmaz; rol hedefi `identifier`dır.
`tags` ve `sensitivityLabel` bu kodla Fabric'e uygulanmaz.

## 6. Doğrulayın ve kasıtlı hata gösterin

Repo kökündeki PowerShell:

```powershell
$env:PYTHONUTF8 = "1"
$env:LIVE_CHECKS = "false"
.\.venv\Scripts\python.exe .\scripts\validate.py .\workspaces\tr-nlyt-sales-ndf-dev-lab01.yaml
$LASTEXITCODE
```

**Beklenen:** `Overall: PASS`, exit code `0`, `validation-report.md`.
Bu dosya her çalıştırmada yenilenir; önceki raporun yerine yeni sonuç gelir.

1. Manifestte `costCenter: CC-1001` değerini `costCenter: CC-1234` yapıp kaydedin.
2. Aynı komutu yeniden çalıştırın.
3. **Beklenen:** `cost-center-allow-list`, `FAIL`, exit code `1`.
   `CC-1234` biçimsel olarak doğru ama policy'de onaylı değil.
4. Değeri tekrar `CC-1001` yapın; PASS sonucunu gösterin.
5. Zaman varsa `suffix` alanını değiştirip `name`i aynı bırakın.
   `name-segments-match-fields` hatası görülmeli; sonra düzeltin.
6. PR öncesi **bütün** manifestleri kontrol edin:

```powershell
.\.venv\Scripts\python.exe .\scripts\validate.py
```

İlk hata demosunu yerelde yapın; bozuk dosyayı `main`e taşımayın.
Canlı grup kontrolü için Graph erişimi ayrıca gerekir. İlk lab'da GUID kullanmak
UPN çözümlemesi ihtiyacını azaltır; grupların gerçekten var olduğunu yönetici
doğrular. `LIVE_CHECKS=false` iken bu doğrulanmış sayılmaz.

## 7. Copilot'u yardımcı olarak kullanın

Schema, policy ve kendi manifestinizi Chat'e ekleyin:

```text
Bu workspace isteğini mevcut schema ve policy ile karşılaştır.
Varsaydığın alan ekleme. Hataları kural adıyla ve sade Türkçeyle açıkla.
Önce yalnız öneri ver; hiçbir terminal veya Fabric aracı çalıştırma.
```

Katılımcıdan önerinin doğruluğunu dosyada göstermesini isteyin. Onaylanan
düzenlemeyi uygularsa tekrar validator çalıştırmalı; Copilot'un “uygun”
demesi teknik kontrolün yerine geçmez.

## 8. GitHub PR ve Actions demosu

1. [İlk kurulumdaki PR adımlarıyla](../../docs/tr/ilk-kurulum.md) yalnız
   manifestinizi stage/commit edin, branch'i kendi repo'nuza push edin.
2. PR'da **base repository** müşteri reposu, **base branch** `main` olmalı.
3. **Checks > validate** açın. Raporun gerçekten sizin dosyanızı kontrol
   ettiğini gösterin; “No workspace manifests changed” kabul kanıtı değildir.
4. Sticky comment yoksa job logunu açın; başarısız yorum gönderimi ile
   başarısız doğrulamayı ayrı değerlendirin.
5. Ekip arkadaşı diff'i okur ve review verir. PR onayından sonra merge edin.
6. **Actions > provision > ilgili run** ekranını açın.
   **Review deployments** görünmesi `production` gate'inin devrede olduğunu gösterir.
7. Yetkili reviewer onaylar. İlk çalışmada `DRY_RUN=true` ile plan görünmeli.
   Bu aşamada Fabric'te workspace oluşmasını beklemeyin.

### Canlıya geçiş - sadece onaylı eğitim ortamında

1. Bütün manifestler, kapasite ve grup ID'leri gerçek; tam validation PASS;
   branch/environment korumaları hazır olmalı.
   Eski `production` onayı bekleyen çalıştırmaları inceleyin; yeni canlı
   ayarla yanlış sürümü çalıştırmamak için yetkili kişi eski run'ı iptal etmelidir.
2. Müşteri yöneticisi GitHub variable `DRY_RUN` değerini `false` yapar.
   Bu, provisioner'ı gerçek yazma moduna geçirir.
3. **Actions > provision > Run workflow**, branch **main** seçilir.
4. Environment onayı yine alınır; loglarda oluşturma/güncelleme ve rol
   ekleme sonucunu inceleyin.
5. Kapasite atamasında HTTP 202 yalnız kabul anlamına gelir. Script,
   `GET /workspaces/{id}` yanıtında hedef `capacityId` ve
   `capacityAssignmentProgress=Completed` birlikte görülene kadar en fazla
   300 saniye bekler. `Failed`, bilinmeyen durum ve zaman aşımı hata üretir.
6. İstenen roller en fazla 60 saniye tekrar okunarak doğrulanır; açıklama ve
   workspace adı da kontrol edilir. Kapasite/rol hatası veya çözülemeyen User
   UPN artık atlanmaz, job başarısız olur. Önceki başarılı API yazmaları otomatik
   geri alınmaz; logdaki workspace ID'sini inceleyip sebebi düzeltin.

Canlı çalıştırmada `GITHUB_REPOSITORY` ve tam `GITHUB_SHA` zorunludur; Actions
bunları otomatik sağlar. Açıklamanın sonuna `managed-by:gh:<repo>@<sha>`
eklenir; açıklama ve işaret toplamı Fabric'in 4000 karakter sınırını aşamaz.
Yerel dry-run'da bu iki değer yoksa işaret önizlemesinin eksik olduğu açıkça
yazılır. Provision workflow'u `LIVE_CHECKS` ayarını da kullanır; `true` ise
yazma öncesi Entra grup kontrolü yeniden yapılır. Provision run'ları aynı
concurrency grubunda seri çalışır; bu, bağımsız portal değişikliklerini kilitlemez.

Provisioner için “idempotent” ifadesini **aynı adla yeniden çalıştırınca
ikinci workspace açmama** kapsamında anlatın; rol kaldırma/değiştirme gibi
tam durum eşitlemesi desteklenmez.

## 9. Sonucu bağımsız kontrol edin

Fabric portalında workspace'i açın. Workspace ayarları ve erişim ekranından
ad, açıklama, kapasite ve hedef grupların rollerini karşılaştırın.
Kullanıcınızın workspace'i görebilmesi için uygun grup üyeliği gerekebilir.

Core MCP ile salt okunur istem:

```text
Yalnız tr-nlyt-sales-ndf-dev-lab01 adlı eğitim workspace'ini oku.
Adını, ID'sini, açıklamasını, kapasitesini ve mevcut rol atamalarını göster.
Bu isim birden çok kaynağa karşılık gelirse dur.
Kaynak veya rol oluşturma, değiştirme ya da silme.
```

**Beklenen:** API/portal değerleri manifestin provisioner tarafından desteklenen
alanlarıyla uyumlu. Otomasyonu oluşturan SPN gibi ek roller bulunabilir;
mevcut kod bunları temizlemez.

Workspace açıklamasının sonunda `managed-by:gh:<repo>@<dağıtım-commit-SHA>`
işaretini arayın. `tags.managedBy` ayrı manifest metadata'sıdır ve Fabric tag
olarak uygulanmaz. Marker'ın varlığı tek başına bütün ayarların doğru olduğunu
kanıtlamaz; kapasite ve roller ayrıca doğrulanır.

## 10. Drift demosu: açıklamayı değiştirin

1. `DRIFT_ENABLED=false` iken job çalışmaz. Raporun public kapsamı ayrıca
   incelenip onaylanmadan bu ayarı açmayın. Onaylı kapsam hazırsa
   **Actions > drift > Run workflow > main** ile başlangıç taraması alın.
   SPN başka workspace'ler de görüyorsa raporda “unmanaged” çıkabilir.
   Bunları demo adına silmeyin; taramanın kapsam sınırını anlatın.
2. Müşteri onayıyla yalnız eğitim workspace'inin açıklama gövdesini portalda
   geçici bir metne değiştirin; sondaki `managed-by` satırı ve önündeki boş satır
   kalsın. İşaret silinirse güvenli provisioner otomatik sahiplenmeyi reddeder.
   Erişim rolü kaldırmayın: mevcut drift kodu bunu yakalamaz.
3. `drift` workflow'unu tekrar çalıştırın.
4. **Beklenen:** Hedef workspace `description mismatch` kapsamında görünür;
   script exit code `2` üretebilir, workflow `drift, governance` issue'su açar.
   Workflow exit code'u yakaladığından job'ın yeşil olması drift yok demek değildir.
5. İstenen durum manifestteki açıklamaysa onaylı provision workflow'unu
   tekrar çalıştırın. Yeni açıklama isteniyorsa manifest değişikliğini PR ile alın.
6. Drift'i tekrar çalıştırın; hedef kaynak farkının gittiğini gösterin.
   Başka unmanaged kaynak varsa genel rapor temiz olmayabilir.
7. Issue'yu kanıtı ekleyerek **elle** kapatın. Otomatik kapandığını söylemeyin.

Drift teknik hatayla da sıfır olmayan kod döndürebilir; her açılan issue'yu
“kanıtlanmış yapılandırma farkı” saymadan önce log ve raporu okuyun.
Karşılaştırma detay API'sinden okunan açıklamayı kullanır. Aynı repo'nun geçerli
işaretindeki commit'in daha eski olması tek başına drift değildir; açıklama
değişikliği, eksik/bozuk işaret veya başka repo işareti drift sayılır.
Yerel drift çağrısında da `GITHUB_REPOSITORY` doğru repo'yu belirtmelidir.

## 11. Başarı kanıtı ve öğrenci uygulaması

| Katılımcının yapacağı | İstenecek kanıt |
|---|---|
| Kendine özel suffix ile ikinci bir istek | Şemaya uyan YAML |
| Onaysız cost center denemesi | FAIL ve ilgili kural; ardından PASS |
| Ekip içi PR review | Kendi repo'sunda PR ve reviewer |
| Dry-run | `[dry-run]` logu; “kaynak oluşturulmadı” açıklaması |
| İzin varsa canlı uygulama | Run ve workspace ID, kapasite/rol karşılaştırması |
| İzin varsa açıklama drift'i | Önce/sonra raporu ve elle kapatılan issue |

Canlı izin yoksa ilk dört maddeyi tamamlayın; sonuç kaydına **“yerel/CI
doğrulama tamam; canlı provision ve drift denenmedi”** yazın.

## 12. Sık hatalar ve coach cevapları

| Belirti | Çözüm |
|---|---|
| Schema isim hatası | Altı parçayı ve `name`/alan eşleşmesini kontrol edin |
| Capacity not approved | Mantıksal adı policy anahtarıyla eşleştirin |
| Yanlış bölge | Manifest `region` ve policy kapasite bölgesini eşleştirin |
| Owner rolü oluşmadı | Job hata verir; Object ID ve SPN workspace yetkisini kontrol edin, kısmi yazmaları inceleyin |
| UPN çözülemedi | Yazma öncesi işlem durur; doğrulanmış Entra Object ID kullanın veya gerekli Graph erişimini onaylatın |
| Management marker yok | Mevcut kaynağı otomatik sahiplenmeyin; ID ve kaynağın gerçek sahibini doğrulayın. Drift demosunda marker'ı koruyun |
| PR kontrolü hiç çalışmadı | `.yaml` dosyasının `workspaces` altında olduğunu ve path filtresini kontrol edin |
| Policy değişti ama dosyalar sınanmadı | Çalışan workflow sürümünü kontrol edin; bu kopyanın CI işi tüm workspace manifestlerini doğrular, eski `--changed-only` çağrısı aynı kapsamı sağlamaz |
| Workspace var ama ben göremiyorum | Kendi Entra hesabınız/tenant'ınız ve grup üyeliğiniz |

**“Label alanı var; hassasiyet etiketi uygulandı mı?”** Hayır. Bu aşamada
istenen label'ın kurala uygunluğu kontrol edildi. Canlı etiket uygulama 03'ün
geliştirme kapsamıdır.

**“Manifesti silersem workspace silinir mi?”** Hayır. Repo artık onu talep
etmez; canlı veri ve maliyet kalabilir, drift unmanaged gösterebilir.

**“Rolü dosyadan çıkarınca erişim kalkar mı?”** Hayır. Mevcut kod yalnız ekler;
erişimi kaldırma 04'te ayrıca tasarlanır.

## 13. Güvenli temizlik

Demo bitince GitHub `DRY_RUN=true` değerini geri koyun veya canlı workflow'u
yetkili yöneticiyle durdurun. Eğitim workspace'ini silmek gerekiyorsa veri
sahibinden ayrıca onay alın, tam ID'yi kontrol edin ve yalnız o kaynağı
yetkili yöneticiyle kaldırın. Manifesti de ayrı PR ile güncelleyin.
Kapasiteyi silmek/paylaşılan kaynağı durdurmak bu işlemin parçası değildir.

## Kaynaklar

- [Workspace schema](../../schemas/workspace.schema.json)
- [Policy](../../rules/policy.yaml)
- [Provisioner](../../scripts/provision.py)
- [Drift kodu](../../scripts/drift.py)
- [Create Workspace API](https://learn.microsoft.com/rest/api/fabric/core/workspaces/create-workspace)
- [Core MCP kurulumu ve okuma örnekleri](https://learn.microsoft.com/rest/api/fabric/articles/mcp-servers/core-remote/get-started-core)
