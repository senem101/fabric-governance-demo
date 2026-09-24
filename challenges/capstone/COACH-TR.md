# Capstone — Coach rehberi: Uçtan uca kanıtlanabilir teslim

> [İlk kurulum](../../docs/tr/ilk-kurulum.md) ·
> [Coach el kitabı](../../docs/tr/coach-el-kitabi.md) · [Özgün görev](challenge.md)
> Ürün kaynakları 24 Eylül 2026 tarihinde kontrol edilmiştir.
> Bu çalışma, müşteri prod'una hazır bir platform sertifikasyonu değildir.

## 1. 60 saniyelik açılış

“Bugün tek tek özellik değil, bir iş senaryosu teslim ediyoruz:
sentetik satış verisi onaylı bir workspace'e gelir, kaliteli hale getirilir,
izinli kişilerce sorgulanır, değişiklikler izlenir ve onayla terfi eder.
Her iddianın bir kanıtı olacak. Dosya yazmak, workflow çalıştırmak ve canlı
kaynağı doğrulamak farklı aşamalardır. Yapmadığımız kontrolü başarılı göstermeyeceğiz.”

**Örnek iş sorusu:** “BOOK ve PEN ürünlerinin toplam geliri nedir?”
Sentetik ham veri Challenge 05'teki 4 satırdır: Silver=3 satır, Gold=350 EUR.
Agent aynı sonucu söylemeli; dashboard da bu teslimin olaylarını göstermelidir.

## 2. Coach'un repo gerçeği açıklaması

Bu checkout, bütün challenge'ların tamamlanmış çözümü değildir.
Mevcut çekirdek: `schemas/workspace.schema.json`, `scripts/validate.py`,
`scripts/rules_engine.py`, `scripts/provision.py`, `scripts/drift.py`, `_fabric.py`;
workflow'lar `validate`, `provision`, `drift`, `pages`.

Item/access/domain/medallion/agent/audit/promotion sözleşmeleri ve uygulayıcılarının
önemli kısmı challenge'larda **geliştirilecek hedef** olarak tarif edilir.
Özgün örnek isimler güncel workspace şemasına uymayabilir.
Örneğin `dev-fin-revenue` yerine `pt-nlyt-sales-gld-dev-lab01` kullanın;
workspace'in ayrı `country`, `area`, `subject`, `dataProductType`, `environment`,
`suffix` alanları isimle eşleşmelidir.

Mevcut provisioner açıklama/kapasite ve eksik rol eklemeyi kapsar.
Domain, label, tag ve `managed-by` marker uygulaması; rol kaldırma, süre bitimi
ve silme hazır değildir. Bazı kapasite/rol hataları sadece warning üretir.
Mevcut drift ad/varlık/açıklama kıyaslar; label, erişim, agent veya item drift'i değildir.
Görülebilen workspace listesi de tüm tenant envanteriyle aynı olmayabilir.

## 3. Kapsamı dersten önce seçin

| Mod | Süre / bağımlılık | Dürüst teslim adı |
|---|---|---|
| Offline mini | 2–3 saat; yerel kurulum ve fixture'lar | Sözleşme/test prototipi, canlı kanıt yok |
| Canlı mini | 3–4 saat; 00/01 önceden doğrulanmış, seçilen uzantılar hazır | Seçilen alanlarda çalışan lab |
| Tam kapsam | Ön çalışmalar sonrası 1–2 günlük entegrasyon; sıfırdan ek geliştirme gerekir | 00–08 için ayrı kanıtlı uçtan uca lab |

Özgün görev herhangi **5 artifact** ile güçlü bir katılımı mümkün kılar.
Bu, 00–08'in tamamlandığı veya bütün prod kontrollerinin uygulandığı anlamına gelmez.
Mini kapsamda örneğin workspace, tek item, sahiplik politikası, negatif validator testi
ve drift kanıtı seçin; agent/audit/promotion'u “kapsam dışı” bırakabilirsiniz.
Tam kapsamda aşağıdaki dokuz satırın hiçbiri yalnız tasarım kanıtıyla kapatılamaz.

Her ekip başlangıçta **planlanan**, **geliştirilen**, **test edilen**, **canlı doğrulanan**,
**offline**, **engelli** durumlarını ayrı işaretlesin.
Tam canlı akış mümkün değilse ders boşa gitmez; doğru sınırlama da öğrenme çıktısıdır.

## 4. Öğretim sırası ve kolaylaştırıcı düzeni

1. **00 — Kurulum:** kimlikleri, repo izinlerini, MCP ve skill kataloğunu tanıtın.
   Başarı: yerel kontrol ve onaylı salt-okuma bağlantısı; yoksa offline kararı.
2. **01 — Workspace:** schema→policy→PR→approval→provision→readback döngüsünü gösterin.
   Başarı: bir olumlu, bir engellenen örnek; canlı modda gerçek kaynak kimliği.
3. **02 — Items:** çalışma alanından item tanımına geçişi anlatın.
   Başarı: hazırlanmış item uygulayıcısı veya açık geliştirme listesi.
4. **03 ve 04 — Sınırlar:** domain/kapasite/label ile grup erişimi farklı kavramlardır.
   Başarı: desteklenen API/kimlik matrisi ve onaylı izin testi.
5. **05 — Veri:** Bronze/Silver/Gold dönüşümünde sentetik 4→3→350 sonucunu gösterin.
6. **06 — Agent:** kaynak allow-list, instructions lint ve yetkisiz kullanıcı testini bağlayın.
7. **07 — Audit:** sadece oluşturmayı değil, korelasyonlu kanıtı ve eksik veri durumunu gösterin.
8. **08 — Promotion:** onaylı sürümün farklı ortama gitmesini ve tanım rollback'ini gösterin.
9. **Capstone:** sınıfı ekip demolarına bölün; her ekip iş sonucunu ve kalan riski anlatsın.

Üç rol önerisi: uygulayıcı, reviewer, kanıt sorumlusu.
Bir kişi aynı prod değişikliğinin hem yazarı hem tek onaylayıcısı olmasın.
Coach kritik geçişlerde durur: canlı ilk yazma, erişim değişikliği, certification,
bildirim açma, prd terfisi ve cleanup.

## 5. Önkoşul ve izin kapısı

- Ortak kurulumdaki güvenli fork, VS Code, GitHub Copilot, Python, branch/PR adımları tamam.
- Fabric eğitim kapasitesi, bölge, bütçe sahibi ve ders bitiş zamanı belirli.
- Workspace/item/Power BI yetkileri işlem bazında doğrulanmış; tüm öğrencilere admin verilmemiş.
- F4+ bazı lablar için öneridir; Data Agent için ücretli F2+/Fabric etkin P1+ koşulu ayrı.
- Data Agent İngilizce soru/talimat, bölge ve cross-geo koşulları değerlendirilmiş.
  SPN ile agent sorgulaması preview; KQL kaynağı ve managed identity sınırlamaları bilinmiş.
- Certification yetkili reviewer'ı, Purview lisans/ayar sahibi ve audit okuma kimliği mevcut
  veya bu kısımlar açıkça kapsam dışı.
- GitHub environment reviewers gerçekten yapılandırılmış; YAML'daki isim yeterli değil.
- Güvenilir runner çevrimiçi: mevcut workflow adımları Linux self-hosted
  `[self-hosted, fabric-gov]` bekler. Canonical repoda canlı çalışma varsaymayın.
- Müşteri verisi, gerçek erişim token'ı, sertifika veya bağlantı sırrı repo/Copilot girdisi değil.

## 6. Öğrenci adımları: birleşik teslimi hazırlayın

1. Repo kökünü VS Code'da açın; branch ve değişiklik durumunu kontrol edin.

   ```powershell
   git status --short
   Get-ChildItem .\schemas
   Get-ChildItem .\.github\workflows
   ```

   **Beklenen:** taban checkout'ta yalnız workspace şeması ve dört workflow.
   Önceki challenge uzantıları eklenmişse hangilerinin test edildiğini kaydedin.
2. Bir sayfalık teslim kapsamı yazın: iş sorusu, veri, kaynaklar, izin sınırı ve bitiş ölçütleri.
   Bu eğitim notu kanıt planıdır; mevcut workspace manifestine yeni alan eklemeyin.
3. Yeni branch'te workspace manifestlerini güncel şemadan üretin.
   Kapasite/domain/costCenter allow-list ve gerçek Group object ID'lerini doğrulayın.
   Sentetik GUID'lerle canlı apply yapmayın.
4. Tam medallion+promotion için kaynak yerleşimini açık planlayın:
   Bronze-dev, Silver-dev, Gold-dev/stg/prd ve ayrı audit workspace'i kullanılabilir.
   Sadece üç workspace ile üç veri katmanı ve üç ortamın hepsini temsil ettiğinizi iddia etmeyin.
5. Aşağıdaki artifact sözleşmelerinden sadece seçilen kapsamdakileri geliştirin.
   Yeni şemaların validator'larını, uygulayıcılarını ve mock testlerini dosyalarla birlikte teslim edin.
6. Yerel olumlu/olumsuz testleri çalıştırın; failures önce düzeltilsin.
   `validate.py` yalnız workspace içindir; diğer dosyalarda yeşil sonuç beklemeyin.
7. PR açın; mümkünse küçük bağımlı PR'lar kullanın:
   sözleşme/test → workspace/item → veri/agent → audit/promotion.
   “Tek PR” şartı için okunamayacak büyüklükte değişiklik üretmeyin.
8. Reviewer test sonuçlarını, path filtrelerini, erişim ve kaynak silme risklerini incelesin.
9. Canlı modda merge edilmiş SHA'dan, gerçek environment onayıyla planı uygulayın.
   Warning'leri tek tek değerlendirin; yeşil job bütün ayarları doğrulamaz.
10. Bağımsız salt-okuma ile hedef metadata ve sentetik veri sonucunu toplayın.
    Kaynak ID, commit SHA, workflow run ve gözlem zamanı aynı teslimle eşleşsin.
11. Salt lab kopyasında bir negatif test ve bir geri dönüş senaryosu gösterin.
    Restore/silme için açık onay olmadan müşteri kaynağını değiştirmeyin.
12. Kanıt matrisini kapatın; desteklenmeyen/erişilemeyen alanlar “engelli” kalsın.

## 7. Geliştirilecek artifact ve entegrasyon listesi

| Alan | Ek dosya/sözleşme örneği |
|---|---|
| 02 | `schemas/item.schema.json`, `items/<workspace>/...` |
| 03 | Domain/capacity sözleşmeleri ve etiket/endorsement uygulama adımları |
| 04 | `schemas/access.schema.json`, `access/...`, süre sonu/revoke uygulayıcısı |
| 05 | `schemas/medallion.schema.json`, `medallion/finance-revenue.yaml`, notebook'lar |
| 06 | `schemas/agent.schema.json`, `agents/...`, instructions linter |
| 07 | `audit/...`, exporter/normalizer, Eventhouse/rapor/alert tanımları |
| 08 | `schemas/pipeline.schema.json`, `pipelines/...`, `scripts/promote.py` |

Tablodaki uzantılar **oluşturulacak — bu repoda hazır değil**;
önceki ekip geliştirmişse kendi test/commit kanıtıyla “hazır” olarak yeniden sınıflandırın.
Manifest klasörü ile Fabric Git'in yerel item definition formatı aynı şey değildir.

**Workflow kontrol listesi:**

1. `validate.yml` PR filtreleri seçilen `items/**`, `domains/**`, `capacities/**`,
   `access/**`, `medallion/**`, `notebooks/**`, `agents/**`, `audit/**`,
   `pipelines/**`, `tests/**` ve ilgili yeni workflow yollarını kapsasın.
2. Her yeni aile için gerçek validator/test adımı eklensin; path filtresi tek başına yetmez.
   Mevcut `--changed-only` yalnız workspace'leri tarar.
3. Schema/policy değişiminde bütün bağımlı manifestler doğrulansın.
   “Dosya değişmedi” nedeniyle etkilenmiş aileyi atlamayın.
4. Main push tabanlı yeni uygulama workflow'ları aynı ilgili dizinler, `workspaces/**`,
   `schemas/**`, `rules/**`, `scripts/**` ve kendi workflow yolunu kapsasın.
5. Dispatch/schedule için path filtresi güvenlik mekanizması değildir.
   Dispatch input allow-list, schedule checkpoint ve güvenilir main kodu gerekir.
6. PR label işini taleple sınırlayın; ayrıcalıklı promote job'ı korumalı kod+SHA+onay kullansın.
7. Workspace, item, data load, agent publish ve promotion sırası tanımlı olsun.
   Aynı kaynağı iki workflow eşzamanlı yönetmesin.
8. GitHub merge → Fabric Git sync → Fabric deploy ayrımını her demo geçişinde söyleyin.
   Otomatik sync veya hazır pipeline entegrasyonu bu repoda varsayılmaz.

## 8. Kanıt matrisi: 00–08'in tamamı

Her satıra durum, kanıt bağlantısı/dosya, commit, gözlem zamanı ve doğrulayan kişi ekleyin.
Offline fixture, ekran provası ve canlı servis sonucu ayrı sütunlarda tutulmalıdır.

| Challenge | Olumlu kanıt | Negatif/limit kanıtı |
|---|---|---|
| [00](../00-setup/COACH-TR.md) | Araç sürümleri; onaylı kimlikle salt-okuma smoke testi; kullanılan skill kataloğu | Yetkisiz erişim reddi; token/sır yok; eksik kapasite açık |
| [01](../01-workspace-as-code/COACH-TR.md) | Manifest PASS, PR/run/onay, workspace ID+açıklama+kapasite+roller readback | Yanlış ad/owner engeli; description drift yakalanır |
| [02](../02-items-as-code/COACH-TR.md) | Item schema/test, uygulama kaydı, canlı item ID ve tanımı | Yanlış referans/tür engeli; item yoksa açık hata |
| [03](../03-domains-capacities-sensitivity/COACH-TR.md) | Gerçek domain/kapasite ve item label/endorsement gözlemi | İzinli olmayan kapasite engeli; certifier yoksa bekleyen kontrol |
| [04](../04-access-rbac-lifecycle/COACH-TR.md) | Grup temelli erişim ve test kullanıcı sonucu | Süresi dolmuş erişim gerçekten kaldırılır; taslak `expiresOn` yeterli değil |
| [05](../05-medallion-bootstrap/COACH-TR.md) | Bronze=4, Silver=3, Gold=350; üç katman ID; model/etiket sonucu | Tekrar çalıştırmada artış yok; Gold certification eksikliği engellenir |
| [06](../06-data-agent-governance/COACH-TR.md) | Allow-list kaynakları, linter, 350 EUR cevabı ve kaynak doğrulaması | B kullanıcısına veri yok; unmanaged source/refusal eksikliği engeli |
| [07](../07-audit-observability/COACH-TR.md) | PR/run/SHA korelasyonu, Eventhouse olayı, rapor metriği, test bildirimi | Duplicate çift sayılmaz; eksik feed “0” değil “unknown” |
| [08](../08-deployment-pipelines/COACH-TR.md) | Release SHA, gate, LRO success, hedef item/readback ve tanım rollback'i | Onaysız/eskimiş source deploy engeli; 202 tek başına başarı değil |

`managed-by` marker özgün rubric'te geçer ama mevcut provisioner bunu yazmaz.
Geliştirilmediyse “yok” yazın; isterseniz ayrı uzantı ve testle ekleyin.
Benzer şekilde “drift=0” cümlesinin yanına **hangi alanlar ve hangi görünür kaynaklar**
kontrol edildiğini mutlaka yazın; genel uyumluluk sertifikası gibi sunmayın.

## 9. Güvenli Copilot/MCP istemleri ve 10 dakikalık demo

**Copilot — yerel hazırlık:**

> Seçili challenge kapsamımızı repo koduyla karşılaştır. Yalnız dosya taslakları,
> eksik validator/test önerileri ve kanıt matrisi hazırla. Yeni alanları mevcut
> workspace şemasına ekleme. Eksik script/komutları var sayma.
> Tenant işlemi, deploy, share, ingestion, Git push/merge veya bildirim yapma.
> Sentetik veriyi kullan; canlı/fixture kanıtlarını ayrı göster.

**MCP — salt-okuma kanıtı:**

> Yalnız onaylı lab workspace/item kimlikleri için mevcut read araçlarıyla
> metadata'yı ve izin verilen toplu test sonuçlarını oku.
> Ham kişisel veri, token veya bağlantı sırrı döndürme. Create/update/delete,
> notebook run, agent publish, Git sync ve deploy yapma.
> Eksik yetki/araç varsa “doğrulanamadı”; liste boşsa “her şey uyumlu” deme.

**Demo sırası:** 1 dk iş sorusu/kapsam → 2 dk PR ve negatif test →
2 dk run/onay/readback → 2 dk veri ve agent → 2 dk audit/promotion → 1 dk kalan risk/cleanup.
Mini ekip, kapsam dışı bölümlerin yerine yaptığı kontrolün sınırını anlatır.
Canlı yoksa ekranda “OFFLINE — tenant, auth, gate ve servis sonucu doğrulanmadı” dursun.

## 10. Değerlendirme, sorun giderme ve kapanış

| Alan | Puan | Coach ölçütü |
|---|---:|---|
| Doğruluk | 25 | Test ve iddia eşleşmesi; canlı iddiası için bağımsız readback |
| Kapsam | 20 | Tamamlanan matris satırları; kapsam dışı alanlar açık |
| Yönetişim disiplini | 20 | Review/onay, en az yetki, negatif test, bilinen eksikler |
| MCP + Skills | 15 | Gerçekte mevcut araçların güvenli kullanımı ve kayıtlı çıktı |
| Gözlemlenebilirlik | 10 | Korelasyon, gecikme/eksik veri davranışı, kaynak kanıtı |
| Anlatım | 10 | İş değeri, sınırlama ve sorumlu kapanış |

Offline ve canlı teslimleri ayrı kategoride değerlendirin; mock başarıdan canlı başarı puanı üretmeyin.
Workflow kuyruğunda kalırsa runner/etiket; başlamazsa workflow etkinliği/path filtreleri;
PASS ama kaynak yoksa kapsam/DRY_RUN/warning; 403'te işlem bazlı kimlik/izin incelenir.
Etiket/agent/audit kanıtı bulunmuyorsa “başarısız sistem” demeden önce uzantı gerçekten yazılmış mı bakın.

- **Tek PR her şeyi kurmalı mı?** Hedef olabilir; güvenli küçük PR zinciri aynı öğretim amacını karşılar.
- **Beş artifact tam kapsam mı?** Hayır; mini teslimdir, dokuz challenge satırı ayrıca değerlendirilir.
- **Hiç drift yoksa hazır mıyız?** Yalnız ölçülen alanlar için; ölçülmeyen kontrol hakkında sonuç çıkarılamaz.

Son 10 dakikayı maliyet ve cleanup'a ayırın: schedules/webhooks → alerts/streams →
Spark/refresh oturumları → onaylı lab nesneleri.
Kanıtı saklamadan silmeyin; paylaşılan kapasiteyi durdurmayın.
Manifest silme bu repoda decommission değildir; silinecek kaynak ID'lerini sahiplerine onaylatın.
Takip işlerini sahibi ve kanıtlanacak kriteriyle devredin; otomatik issue kapanışı varsaymayın.

## Kaynaklar

- [Fabric medallion yaklaşımı](https://learn.microsoft.com/fabric/onelake/onelake-medallion-lakehouse-architecture)
- [Data Agent güncel önkoşul/sınırlamaları](https://learn.microsoft.com/fabric/data-science/concept-data-agent)
- [Data Agent SPN preview](https://learn.microsoft.com/fabric/data-science/data-agent-service-principal)
- [Activity Events izin ve tarih sınırları](https://learn.microsoft.com/rest/api/power-bi/admin/get-activity-events)
- [Deployment pipeline item desteği](https://learn.microsoft.com/fabric/cicd/deployment-pipelines/intro-to-deployment-pipelines)
- [Fabric Git entegrasyonu](https://learn.microsoft.com/fabric/cicd/git-integration/intro-to-git-integration)
