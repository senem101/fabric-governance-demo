# Challenge 05 — Coach rehberi: Bronze, Silver ve Gold

> **Önce:** [İlk kurulum](../../docs/tr/ilk-kurulum.md) ve
> [coach el kitabı](../../docs/tr/coach-el-kitabi.md).
> [Özgün görev](challenge.md) hedef tasarımı anlatır; aşağıdaki ayrımlar mevcut kodu açıklar.
> Ürün kaynakları 24 Eylül 2026 tarihinde kontrol edilmiştir.

## 1. Derste ne öğreteceksiniz?

**60 saniyelik anlatım:** “Bronze gelen veriyi olduğu gibi saklar.
Silver tekrarları ve biçim sorunlarını düzeltir. Gold iş sorusunu cevaplayan
özetleri sunar. Bir lakehouse oluşturmak veriyi dönüştürmez.
Manifest istediğimiz yapının tarifi, notebook dönüşümün kodu, test ise doğruluğun
kanıtıdır. GitHub incelemeyi; Actions onaylı uygulamayı yönetir.”

**Süre:** 15 dk kavram, 25 dk modelleme, 45–60 dk geliştirme, 20 dk test/demo.
Sıfırdan item altyapısı gerekiyorsa ek yarım gün ayırın; 90 dakikada tam otomasyon vaat etmeyin.
Çiftlerde biri veri mühendisi, diğeri politika inceleyicisi olsun.

## 2. Hazır olan ile geliştirilecek olan

| Depoda bugün | Bu challenge'da yapılacak |
|---|---|
| `schemas/workspace.schema.json` ve workspace validator | Medallion şeması ve katmanlar arası kurallar |
| Workspace açıklaması/kapasitesi ve eksik rol ekleme | Lakehouse, notebook ve semantic model oluşturma |
| Workspace adı/varlığı/açıklaması için drift | Item, veri kaynağı, etiket ve endorsement karşılaştırması |
| Dört workflow: validate, provision, drift, pages | Medallion doğrulama, uygulama ve bağımlılık sırası |

`schemas/medallion.schema.json`, `scripts/validate_medallion.py`,
`scripts/capture_medallion_output.py`, `.github/workflows/medallion.yml`:
**oluşturulacak — bu repoda hazır değil**.
Challenge 02'deki item şeması/uygulayıcısı da tamamlanmadıysa hazır sayılmaz.
`provision.py --items ...` mevcut betiğin desteklediği bir arayüz değildir.
Özgün metindeki `copilot skill run ...` satırını doğrulanmış CLI komutu diye çalıştırmayın.
Skill, asistanın kullandığı rehberdir; deterministik CI betiğinin yerine geçmez.

## 3. Önkoşullar ve izin kartı

1. Challenge 00–01 tamamlanmalı; Challenge 02'nin item sözleşmesi geliştirilmiş olmalı.
2. Etiket/endorsement için 03, grup sahipliği için 04 tasarımını kullanın.
3. Workspace oluşturma/kapasite atama kimliği ile notebook çalıştırma kimliğini ayırın.
   Her item ve işlem için service principal desteğini ayrıca doğrulayın.
4. Fabric destekli eğitim kapasitesi, uygun bölge ve çalışma alanı erişimi gerekir.
   F4+ özgün labın planlama önerisidir; evrensel minimum veya performans garantisi değildir.
5. Power BI model/rapor yazarı ve tüketicisi lisanslarını kapasite SKU'suyla birlikte kontrol edin.
6. Certification, tenant tarafından etkinleştirilmiş olmalı ve yetkili reviewer bulunmalı.
   Workspace Admin olmak tek başına sertifikalandırma yetkisi vermez.
7. Kurulu katalogda `e2e-medallion-architecture` varsa taslak hazırlamada kullanın.
   Alt skill adlarını katalogdan okuyun; eski `*-authoring-cli` adlarını varsaymayın.

**Başlama kapısı:** veri sentetik, bütçe sahibi belli, canlı ortam hedefleri onaylı.
Etiketleme yetkisi yoksa bunu “bekleyen kontrol” yazın; onayı atlayıp başarılı demeyin.

## 4. Coach hazırlığı: 15 dakikalık kontrol

1. VS Code'da repo kökünü açın; terminalin repo kökünde olduğuna bakın.
2. Explorer'da `schemas`, `scripts`, `workspaces` ve `.github/workflows` dizinlerini gösterin.
3. Aşağıdaki salt yerel incelemeyi PowerShell'de yapın:

   ```powershell
   Get-Content .\schemas\workspace.schema.json
   Get-Content .\workspaces\pt-nlyt-sample-ndf-dev-hello1.yaml
   Test-Path .\scripts\validate_medallion.py
   ```

   **Beklenen:** taban checkout'ta son sonuç `False`; bu bir kurulum hatası değil, geliştirme görevidir.
4. Workspace adlarını güncel şemadan üretin; `dev-fin-bronze` geçerli değildir.
   Örnekler: `pt-nlyt-sales-brz-dev-lab01`, `pt-nlyt-sales-slv-dev-lab01`,
   `pt-nlyt-sales-gld-prd-lab01`. İsimdeki tüm parçalar manifest alanlarıyla eşleşmelidir.
5. `domain`, `capacity`, `costCenter` değerlerini gerçek onaylı policy'den seçin.
   Repo örneğindeki GUID'ler canlı ortam kimliği değildir.
6. Eğitim için önceden onaylanmış üç workspace varsa yalnız listeleyin.
   Yoksa ilk oturumu yerel tasarım/test olarak planlayın.

## 5. Sentetik veri ve açık doğruluk beklentisi

Katılımcıdan aşağıdaki küçük veriyi kendi test fixture'ına aktarmasını isteyin.
Gerçek müşteri/çalışan kimliği veya bağlantı sırrı kullanmayın.

| transaction_id | product | amount | currency |
|---|---|---:|---|
| T001 | BOOK | 100 | EUR |
| T001 | BOOK | 100 | EUR |
| T002 | PEN | 200 | EUR |
| T003 | BOOK | 50 | EUR |

Bronze **4 ham kayıt** tutar. Silver aynı `transaction_id` tekrarını kaldırır:
**3 kayıt**. Gold toplamı **350 EUR**, BOOK **150**, PEN **200** olmalıdır.
İkinci çalıştırmada kayıt sayısı artmamalı; idempotency testini bununla yapın.
Para birimi dönüşümü bu küçük kapsamda yoktur; farklı currency gelirse karantinaya ayırın.

## 6. Öğrenci uygulaması: önce taslak, sonra test

1. VS Code Source Control ile ayrı bir çalışma dalı açın.
   **Beklenen:** `main` değişmez; değişiklikler yalnız kendi branch'inizdedir.
2. **Yeni sözleşme** olarak `schemas/medallion.schema.json` tasarlayın.
   `tiers`, `endorsement`, `sourceSystem` workspace şemasına eklenmeyecek.
3. `medallion/finance-revenue.yaml` taslağını oluşturun.
   Aşağıdaki parça **yeni medallion şemasına ait taslak örnektir**, mevcut validator girdisi değildir:

   ```yaml
   name: finance-revenue
   sourceSystem:
     kind: SyntheticFixture
   tiers:
     bronze:
       workspace: pt-nlyt-sales-brz-dev-lab01
       lakehouse: lh_bronze_revenue
     silver:
       workspace: pt-nlyt-sales-slv-dev-lab01
       lakehouse: lh_silver_revenue
     gold:
       workspace: pt-nlyt-sales-gld-prd-lab01
       lakehouse: lh_gold_revenue
       semanticModel: sm_gold_revenue
       sensitivityLabel: Confidential
       endorsement: Certified
   ```

4. Referans verilen her workspace için mevcut şemaya uygun tam manifest hazırlayın.
   `environment: prd` ve en az iki Group owner gibi kuralları doğrulayın.
   Prd koşulunu `^prd-` ile değil manifestin `environment` alanıyla kontrol edin.
5. Medallion validator'ını geliştirin: katmanlar, referanslar, policy sıralaması,
   zorunlu Gold etiketi ve certification niyeti ayrı hata mesajları üretmeli.
   Etiket sırasını alfabetik kıyaslamayın; açık izinli sıralama kullanın.
6. Notebook taslaklarında ham veri koruma, deterministik dedup ve Gold toplama yapın.
   “Notebook oluşturuldu” ile “notebook başarıyla çalıştı” sonuçlarını ayırın.
7. Yerel testlerde 4 → 3 → 350 beklentisini, ikinci çalıştırmayı ve hatalı currency'yi sınayın.
   **Beklenen:** başarılı/başarısız test sayısı ve dosya adı görülebilir.
8. Item uygulayıcısını önce işlem planı üretecek biçimde geliştirin.
   Kimlikler, sıralama, hata ve yeniden deneme davranışı taslakta açık olsun.
   Ayrı workspace'ler arası veri erişimi/bağlantıları ayrıca onaylayın.
9. Skill çıktısını insan incelemesinden sonra sürümlenen dosyalara dönüştürün.
   Çıktı klasörü, manifest biçimi ve artifact hash'i için açık bir sözleşme yazın.
10. PR açın; reviewer örnek veri sonucunu ve politika testlerini kontrol etsin.
    Uygulama kodu yoksa “tasarım PR'ı” olarak etiketleyin; merge canlı kaynak üretmez.

## 7. GitHub/Actions entegrasyonu: mutlaka eklenecek

- Bu kopyadaki `validate.yml` path filtresi olmadan tüm PR'larda çalışır;
  `medallion/**`, `items/**`, `notebooks/**`, `tests/**` değişiklikleri de tetikler.
- Tetiklenmek yeterli değildir: yeni validator/test adımlarını çağırın.
  Mevcut `validate.py` yalnız workspace manifestlerini doğrular.
- Policy/şema/notebook değiştiğinde bütün bağımlı medallion dosyalarını yeniden doğrulayın.
  “No workspace manifests changed” medallion doğrulama kanıtı değildir.
- Yeni `.github/workflows/medallion.yml` için korumalı `main` push veya manuel dispatch seçin.
  Push filtreleri: `medallion/**`, `items/**`, `notebooks/**`, `workspaces/**`,
  `schemas/**`, `rules/**`, `scripts/**` ve workflow'un kendi yolu.
- Workspace provisioning ve item bootstrap için tek uygulama sahibi belirleyin;
  iki workflow'un aynı anda aynı nesneyi oluşturmasını engelleyin.
- Üretim job'ı `production` environment, gerçekten yapılandırılmış reviewer,
  OIDC, kısıtlı branch ve güvenilir runner gerektirir. PR kodunu ayrıcalıklı runner'da çalıştırmayın.
- Bu kopyadaki mevcut workflow'lar GitHub-hosted `ubuntu-latest` ve Python 3.12 kullanır; adımlar Linux shell varsayar.
  Windows terminal komutlarını workflow'a olduğu gibi taşımayın.
- GitHub merge, Fabric Git eşitlemesi değildir. Git kullanılıyorsa desteklenen item
  tanımları için ayrı bağlantı ve “Update from Git”/onaylı sync adımı gerekir.

## 8. Canlı demo: yalnız altyapı tamamlandıysa

1. Onaylı eğitim hedefinde uygulama planını açın; prd adlı eğitim workspace'inin
   gerçek müşteri prod'u olmadığını teyit edin.
2. Environment onayından sonra workspace → lakehouse → notebook → model sırasını izleyin.
   **Beklenen:** her işlem için nesne kimliği ve ayrı başarı/hata kaydı.
3. Sentetik veriyi yükleyin; Bronze, Silver, Gold kontrollerini ayrı ayrı çalıştırın.
4. Gold için label ve endorsement durumunu item üzerinden okuyun.
   API/kimlik desteği doğrulanmadıysa yetkili reviewer'ın belgeli işlemini ayrı kanıtlayın.
   Bu elle yapılan adımı “PR ile tamamen otomatik” diye sunmayın.
5. Tekrar uygulayın: ek workspace/item oluşmamalı, toplam **350 EUR** kalmalı.
6. Mevcut workspace drift raporunu gösterin, ardından item kontrollerini gösterin.
   Workspace drift=0, label/endorsement/notebook drift=0 anlamına gelmez.

## 9. Güvenli Copilot ve MCP istemleri

**Copilot — sadece dosya taslağı:**

> Önce workspace.schema.json, rules_engine.py ve challenge'ı oku.
> Yeni medallion şeması, sentetik fixture, validator ve negatif testleri yalnız dosya
> taslağı olarak hazırla. Mevcut workspace şemasına alan ekleme.
> 4 ham satırdan 3 benzersiz satır ve 350 EUR üreten dönüşümü tasarla.
> Tenant, CLI, REST, notebook çalıştırma, Git push/merge veya deploy yapma.
> Eksik item uygulayıcısını varmış gibi çağırma. Diff ve varsayımları göster.

**MCP — sadece okuma:**

> Yalnız erişebildiğim pt-nlyt-sales-brz-dev-lab01, pt-nlyt-sales-slv-dev-lab01 ve
> pt-nlyt-sales-gld-prd-lab01 workspace'lerini ve item metadata'sını listele.
> Desteklenen read araçlarıyla etiket/endorsement bilgisini göster.
> Araç bu alanı sunmuyorsa “doğrulanamadı” de; hiçbir kaynak oluşturma/değiştirme.
> Sonuçlara workspace/item kimliğini ve gözlem zamanını ekle.

## 10. Negatif test, kanıt ve sorun giderme

| Deneme / belirti | Beklenen / coach müdahalesi |
|---|---|
| Gold `Certified` kaldırılır | Yeni validator engeller; bugün mevcut validator bunu yapmaz |
| Referans workspace yok | Uygulamadan önce referans hatası |
| Aynı veri ikinci kez çalışır | Silver=3, Gold=350; artıyorsa yükleme idempotent değil |
| Notebook erişim hatası | Kaynak/hedef item izni ve farklı workspace bağlantısını inceleyin |
| Sertifika seçeneği pasif | Yetkili certifier ve tenant ayarını kontrol edin |
| Workflow hiç başlamadı | Yeni dizin path filtresi, workflow etkinliği ve runner kontrolü |
| Yeşil provision ama rol yok | Logdaki warning'i inceleyin; mevcut betikte bazı hatalar uyarıdır |

Kanıt paketi: PR/diff, doğrulama raporu, test sonuçları, onay zamanı,
item kimlikleri, veri sayımları ve kontrol edilmeyen alanların listesi.
**Canlı yoksa:** fixture ve mock API cevaplarıyla sözleşmeyi sınayın.
Ekrana “OFFLINE — canlı tenant, izin, certification ve performans doğrulanmadı” yazın.

## 11. Coach soruları, maliyet ve kapanış

- **Gold mutlaka prod mu?** Medallion veri kalitesidir, dev/stg/prd yaşam döngüsüdür.
  Özgün görevin Gold→prd şartı yerel politikadır; evrensel Fabric kuralı değildir.
- **Skill her şeyi otomatik kurar mı?** Hayır; ürettiği dosyalar sözleşme ve review ister.
- **Label yazmak erişimi kapatır mı?** Tek başına değil; item desteği, izinler ve politikalar ayrıca doğrulanır.

Küçük veri, tek seferlik çalıştırma ve ders süresi sınırı kullanın; schedules açmayın.
Spark oturumlarını bitirin; paylaşılan kapasiteyi diğer ekipler kullanırken durdurmayın.
Silmeden önce demo artifact/kanıtlarını saklayın ve kaynak listesini sahiplerine onaylatın.
Manifest silmek bu repoda kaynak silmez; cleanup ayrı, kontrollü işlemdir.

## Kaynaklar

- [Fabric medallion tasarımı](https://learn.microsoft.com/fabric/onelake/onelake-medallion-lakehouse-architecture)
- [Endorsement ve yetkili certification](https://learn.microsoft.com/fabric/fundamentals/endorsement-promote-certify)
- [Fabric Git desteği](https://learn.microsoft.com/fabric/cicd/git-integration/intro-to-git-integration)
- [Mevcut workspace uygulayıcısı](../../scripts/provision.py) ve [drift kapsamı](../../scripts/drift.py)
