# Challenge 08 — Coach rehberi: Dev → Stg → Prd terfisi

> [İlk kurulum](../../docs/tr/ilk-kurulum.md) ·
> [Coach el kitabı](../../docs/tr/coach-el-kitabi.md) · [Özgün görev](challenge.md)
> Kaynak kontrolü: 24 Eylül 2026. Desteklenen item/kimlik listeleri değişebilir.

## 1. 60 saniyelik açıklama ve eğitim planı

“Git, hangi sürümü istediğimizi saklar. GitHub Actions doğrulama ve onaylı işleri
çalıştırır. Fabric Git integration, desteklenen item tanımlarını bir workspace ile
Git arasında eşitler. Fabric deployment pipeline ise item'ları ortamlar arasında
terfi ettirir. Bunlar dört farklı görevdir. Merge yapınca Fabric kendiliğinden
eşitlenmez; deploy yapınca kaynak veri ve bütün izinler taşınmış olmaz.”

**Süre:** 15 dk kavram, 25 dk sözleşme, 45–60 dk kod/test, 25 dk onaylı demo.
Eksik item/Git altyapısı veya rollback uygulaması için ek yarım gün planlayın.
İlk demo tek desteklenen Notebook veya Lakehouse ile dev→stg olsun.
Prd ve geri alma ancak ilk akışın kanıtından sonra eklenir.

## 2. Bugün hangi otomasyon var?

| Depoda mevcut | Bu challenge'da geliştirilecek |
|---|---|
| Workspace provisioning ve `production` environment kullanan workflow | Fabric deployment pipeline oluşturma/bağlama |
| Workspace validator ve kısıtlı drift | Pipeline şeması, item seçimi ve terfi doğrulaması |
| `validate`, `provision`, `drift`, `pages` | `promote.yml`, `promote.py`, rollback sürüm kaydı |

`schemas/pipeline.schema.json`, `pipelines/`, `.github/workflows/promote.yml`,
`scripts/promote.py`: **oluşturulacak — bu repoda hazır değil**.
Etiket eklemek mevcut repoda promotion başlatmaz.
`production` adının YAML'da yazması, reviewer koruması gerçekten yapılandırılmış demek değildir.
Mevcut provisioner item tanımı, label, endorsement veya izin kaldırma işlemi yapmaz.

## 3. İzin, kapasite ve sürüm önkontrolü

1. Challenge 00–02'nin gereken uygulamaları çalışmalı; 03/04 prod kontrolleri tamamlanmalı.
2. Üç ayrı eğitim workspace'i ve onaylı kapasite/region planı hazırlayın.
   Örnekler: `pt-nlyt-sales-gld-dev-lab01`, `pt-nlyt-sales-gld-stg-lab01`,
   `pt-nlyt-sales-gld-prd-lab01`. Özgün `dev-fin-gold` şemaya uymaz.
3. Fabric subscription/uygun workspace kapasitesi ve Power BI item'ları varsa
   yazarlık/tüketim lisansları kontrol edilmeli; PPU'yu bütün Fabric workload'larına genellemeyin.
4. Pipeline yönetimi için pipeline Admin; workspace bağlama için workspace Admin gerekir.
   Deploy API çağrısında pipeline Admin ve kaynak/hedefte en az Contributor aranır.
5. Kullanıcı akışının delegated scope'u `Pipeline.Deploy`'dur.
   Bunu SPN'ye “aynı delegated scope'u ver” şeklinde çevirmeyin.
6. Deploy Stage Content SPN/managed identity desteği, işlemdeki **bütün item'ların**
   ilgili kimliği desteklemesine bağlıdır. Tenant ayarını ve her item'ı ayrı doğrulayın.
7. Notebook, Lakehouse, Data Agent gibi item'lar güncel destek listesinde bulunur.
   Listedeki bazı Power BI/diğer item'lar ve yeni pipeline UI preview durumundadır.
   “Fabric item ise deploy olur” varsayımını bırakın.
8. Semantic model kullanıyorsanız Enhanced Metadata koşulunu kontrol edin.
   Eski metadata modellerinin pipeline desteği 12 Şubat 2026 itibarıyla kaldırılmıştır.
9. GitHub planınızın repo görünürlüğünde environment reviewers ve branch korumasını
   desteklediğini doğrulayın. Görünmeyen güvenlik özelliğini kurulmuş saymayın.

## 4. Coach hazırlığı

1. Explorer'da workflow'ları gösterin; terminalde:

   ```powershell
   Get-Content .\.github\workflows\provision.yml
   Test-Path .\scripts\promote.py
   Test-Path .\schemas\pipeline.schema.json
   ```

   **Beklenen:** taban checkout'ta son iki sonuç `False`.
2. Güvenli eğitim hedeflerini ve source/target kimliklerini listeleme sonucundan alın.
   GUID tahmin etmeyin; aynı adlı birden fazla nesne varsa seçim belirsizliğini giderin.
3. Bir Notebook tanımına sentetik `release-v1`, sonra `release-v2` notu ekleyeceğiniz
   senaryoyu hazırlayın. Müşteri verisi veya bağlantı sırrı kullanmayın.
4. Önceki başarılı tanım paketinin saklanacağı repo/artifact alanını ve saklama süresini belirleyin.
   Pipeline operasyon geçmişi, kendiliğinden indirilebilir rollback snapshot deposu değildir.

## 5. Öğrenci: yeni pipeline sözleşmesi

1. `schemas/pipeline.schema.json` **yeni şema** olarak tasarlansın.
   Aşağıdaki yapı mevcut workspace şemasına eklenmez:

   ```yaml
   name: revenue-lab
   stages:
     - name: dev
       workspace: pt-nlyt-sales-gld-dev-lab01
     - name: stg
       workspace: pt-nlyt-sales-gld-stg-lab01
     - name: prd
       workspace: pt-nlyt-sales-gld-prd-lab01
   promotionRules:
     - from: stg
       to: prd
       label: promote/prd
       environment: production
   itemsToPromote:
     - kind: Notebook
       namePattern: "^nb_revenue_.*$"
   ```

   Bu kısa taslağı description, dev→stg kuralı, reviewer politikası ve testlerle tamamlayın.
2. Stages listesini referans workspace manifestleriyle eşleştirin.
   Pipeline 2–10 stage desteklese de bu lab politikası dev→stg→prd sırası ister.
3. `namePattern` için **regex** veya glob kararını açık verin.
   Burada regex kullanılır; özgün `lh_gold_*` glob görünümü regex'te aynı anlama gelmez.
   `^lh_gold_.*$` gibi sabitlenmiş regex ve örnek eşleşme testleri yazın.
4. PR etiketini talep niyeti olarak saklayın, yetkilendirme olarak kullanmayın.
   Reviewer listesi manifestte yazılı diye GitHub onay kontrolü otomatik oluşmaz.
5. Commit SHA, kaynak item ID'leri, tanım hash'leri, hedef stage ve plan zamanı içeren
   release kaydı tasarlayın. Tanım hash'inde ortam bağlarının nasıl normalize edildiğini belirtin.
6. Kaynak workspace sürümünü commit'e bağlayan kontrolü ekleyin.
   PR doğru olsa bile source workspace'e başka değişiklik geldiyse promotion durmalıdır.

## 6. Öğrenci: önce plan, sonra uygulayıcı

1. `scripts/promote.py` için listeleme/plan modu tasarlayın; uygulama açık seçim olsun.
   Kaynak item setini izinli type+regex ile kesiştirin; boş sonucu sessiz başarı saymayın.
2. Pipeline/stage/workspace ID'lerini gerçek listeleme çağrılarından çözün.
   Mevcut pipeline'ı silip yeniden yaratmayı idempotency sanmayın.
3. Bağımlılıkları ve item pairing'i inceleyin.
   Sadece aynı isimde olmak paired olmak değildir; eşleşmemiş item kopyalanıp çoğalabilir.
4. Desteklenmeyen item'ları açık raporlayın; kısmi deploy'u tam başarı saymayın.
   Tek deploy isteği en fazla 300 item içerir; küçük labda bir item yeterlidir.
5. API 202 döndürürse `Location`, `x-ms-operation-id` ve `Retry-After` bilgisini saklayın.
   Operasyonu terminal sonuca kadar, süre sınırı ve backoff ile izleyin.
   202 “kabul edildi” demektir, “deployment başarılı” değildir.
6. Timeout'ta ikinci deploy'u hemen başlatmayın; mevcut operasyonun durumunu okuyun.
   Aynı pipeline'da eşzamanlı terfiyi job concurrency ile engelleyin.
7. Hedef item tanımlarını ve bağlantılarını tekrar okuyun.
   Veri taşınmış varsaymayın; gerekli seed/load/refresh ayrı onaylı aşamadır.
8. Labels, certification, erişim izinleri ve ortam bağlantılarını ayrıca kontrol edin.
   Pipeline tanım kopyalama işlemini tüm güvenlik ayarlarını eşitleyen araç diye anlatmayın.
9. Deployment/parameter rules gerekiyorsa desteklenen UI adımlarını belgeleyin.
   Oluşturma API'si mevcutmuş gibi uydurmayın; portal istisnasını otomasyon kapsamından ayırın.

## 7. GitHub workflow bağlantısı: etiket tek başına yeterli değil

- `validate.yml` PR path filtrelerine `pipelines/**`, `items/**`, `tests/**`,
  `.github/workflows/promote.yml` ekleyin.
  Mevcut `schemas/**`, `rules/**`, `scripts/**` filtreleri korunur.
- Yeni pipeline validator ve test adımlarını ayrıca ekleyin;
  `validate.py --changed-only` yalnız workspace manifestlerini seçer.
- Güvenli ilk sürüm: `promote.yml` içinde korumalı main'den `workflow_dispatch`;
  input olarak onaylı pipeline, stage ve merge edilmiş release SHA seçilsin.
  Dispatch'in path filtresi yoktur; input allow-list ve SHA kontrolü gerekir.
- Etiket akışı gerekiyorsa ayrı, **yetkisiz** PR `labeled` job'ı sadece talebi kaydetsin.
  Sonradan etiket eklemeyi yakalamak için bunu dosya-diff filtresine bağımlı kılmayın.
  Talep onaylandıktan sonra korumalı workflow güvenilir main kodunu çalıştırsın.
- Prd işi ayrı job ve `environment: production` kullansın;
  OIDC subject, required reviewers, branch kuralları ve gerekli status check'leri doğrulansın.
- PR head'ini checkout edip etiket üzerinden bulut kimliği vermeyin.
  `pull_request_target` ile PR kodu çalıştıran kestirme kullanmayın.
- Push tabanlı bir release workflow seçilirse filtreler `pipelines/**`, `items/**`,
  `workspaces/**`, `schemas/**`, `rules/**`, `scripts/**` ve kendi workflow yolu olsun.
- Kaynak workspace sync/uygulama, test ve promotion arasında bağımlılık kurun.
  GitHub merge ile Fabric “Update from Git” veya API sync ayrı işlemlerdir.
- Mevcut `[self-hosted, fabric-gov]` runner Linux shell varsayar.
  Ortak kurulumdaki güvenli fork/runner adımlarını tamamlamadan canlı job açmayın.

## 8. Canlı demo ve geri alma

1. Yalnız onaylı labda v1 tanımını dev'e uygulayıp bağımsız okuma ile doğrulayın.
2. Planı review edin; dev→stg deploy'un LRO sonunu ve hedef v1'i gösterin.
3. Stg smoke testi geçince prd talebi açın.
   **Beklenen:** environment onayından önce hedefte değişiklik yoktur.
4. Coach reviewer onayından sonra deploy sonucu ve hedef ID/sürüm eşleşmesini gösterin.
5. v2 tanımını aynı zincirle geçirin; rollback için önceki v1 artifact'ını seçin.
6. Geri alma, v1 tanımını kaynak aşamaya kontrollü geri yükleyip yeniden doğrulama ve
   **ileri yönde yeniden deploy** planıdır. Eski operasyon ID'si “snapshot restore” komutu değildir.
7. Hedef veri için ayrı restore/geri dönüş planı gerekir.
   Tanım rollback'i işlenmiş veriyi, izinleri veya harici sistemi otomatik geri almaz.
8. Hedefte kaldırılmış kaynak item'ların kendiliğinden silineceğini varsaymayın.
   Silme için ayrı etki analizi ve onay gerekir.
9. Pairing düzeltmek için workspace unassign/reassign işlemini otomatik uygulamayın;
   deployment history/rules kaybı gibi etkileri önceden inceleyin.

## 9. Güvenli istemler

**Copilot — sadece taslak:**

> Yeni pipeline schema, offline validator/test ve promote.py plan arayüzünü taslakla.
> Regex/glob farkını, immutable release SHA kontrolünü ve 202 polling'i test et.
> Gerçek tenant çağrısı, deploy, pipeline create/delete, stage bind, sync, rollback,
> workflow dispatch veya push/merge yapma. Production approval zorunlu kalsın.
> İşlem/item kimlik desteğini resmi belgede doğrulanacak madde olarak göster.

**MCP — yalnız okuma:**

> Erişebildiğim revenue-lab pipeline'ının stages ve paired item metadata'sını oku.
> Kaynak/hedef kimliklerini, son operasyonun durumunu ve gözlem zamanını özetle.
> Deploy, create, assign/unassign, Git sync veya rule değişikliği yapma.
> Son deploy zamanı son edit zamanı değildir; değiştiğine dair kanıt yoksa bunu belirt.

## 10. Negatif testler ve sorun giderme

| Test / belirti | Beklenen veya müdahale |
|---|---|
| Prd kuralından environment kaldırılır | Yeni validator bloklar |
| `promote/prd` yetkisiz kişi tarafından eklenir | Canlı deploy yok; review talebi dışında işlem yok |
| Source hash onaydan sonra değişir | Eski plan reddedilir |
| Item seçimi boş/unsupported | Açık hata veya kapsamlı partial rapor; tam başarı değil |
| Deploy 202 sonra Failed | Job başarısız, hedef tekrar incelenir |
| Pipeline listeleniyor, deploy 403 | Pipeline rolü + iki workspace rolü + kimlik/item desteği ayrı kontrol |
| Hedefte iki aynı isimli item | Pairing'i incele; rastgele kopyayı silme |
| Workflow başlamıyor | Dispatch seçimi, label job'ı, runner ve workflow etkinliği |

Kanıt: plan ve release SHA, review/onay zamanı, LRO kimliği/sonucu,
kaynak-hedef item eşleşmesi, smoke test ve rollback sonrası bağımsız sürüm okuması.

## 11. Offline seçenek, sorular ve kapanış

Canlı kapasite/izin yoksa v1/v2 tanım fixture'ları ve mock LRO durumlarıyla test edin.
“OFFLINE — gerçek deploy, environment gate, auth, pairing ve rollback doğrulanmadı” yazın.
Ekran görüntüsündeki demo gate'i gerçek GitHub approval kanıtı gibi sunmayın.

- **GitHub Actions ile Fabric pipeline aynı mı?** Hayır; biri iş çalıştırır, diğeri item terfi ettirir.
- **Rollback tek tık geçmişe dönüş mü?** Hayır; sürümlenmiş tanım ve ayrı veri geri dönüş planı gerekir.
- **Prod etiketi onay mı?** Hayır; gerçek yetkilendirme ve korumalı environment kontrolü gerekir.

Üç stage için kapasite/refresh maliyetini önceden planlayın; test verisini küçük tutun.
Gereksiz yeniden deploy ve refresh döngülerini durdurun.
Ders sonunda sadece kayıtlı lab pipeline/item/workspace'lerini sahip onayıyla temizleyin;
manifesti veya pipeline'ı silmenin bütün workspace/veriyi temizlediğini varsaymayın.

## Kaynaklar

- [Deployment pipelines ve güncel item desteği](https://learn.microsoft.com/fabric/cicd/deployment-pipelines/intro-to-deployment-pipelines)
- [İlk pipeline ve aşama bağlama](https://learn.microsoft.com/fabric/cicd/deployment-pipelines/get-started-with-deployment-pipelines)
- [Deploy Stage Content: izin, kimlik, LRO](https://learn.microsoft.com/rest/api/fabric/core/deployment-pipelines/deploy-stage-content)
- [Kopyalanan ve kopyalanmayan özellikler](https://learn.microsoft.com/fabric/cicd/deployment-pipelines/understand-the-deployment-process)
- [Fabric Git integration](https://learn.microsoft.com/fabric/cicd/git-integration/intro-to-git-integration)
