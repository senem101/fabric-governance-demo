# Coach el kitabı: müşteriye nasıl anlatırım?

[Rehber dizini](README.md) | [İlk kurulum](ilk-kurulum.md)

## 1. Sizin rolünüz

Amaç bütün komutları ezberlemek değil; müşterinin **neden bir kontrol
uyguladığını, kontrolün nerede çalıştığını ve çalıştığını nasıl kanıtlayacağını**
öğrenmesini sağlamaktır. Coach yön gösterir; tenant yöneticisinin veya
müşterinin güvenlik onayının yerini almaz.

Müşteriye açılışta şöyle anlatabilirsiniz:

> “Fabric'te herkes farklı şekilde workspace açarsa kimin neye eriştiğini ve
> hangi standardın uygulandığını takip etmek zorlaşır. Bu çalışmada isteği bir
> dosyaya yazacağız. GitHub kuralları kontrol edecek, bir kişi onaylayacak ve
> otomasyon uygulayacak. Copilot dosyayı hazırlamamıza yardımcı olacak; karar
> ve onay yine bizde olacak.”

**Verilecek söz:** İncelenebilir ve tekrarlanabilir bir yönetişim yaklaşımı.
**Verilmeyecek söz:** Bu repoyu indirince bütün tenant'ın otomatik ve eksiksiz
yönetileceği veya mevzuata uyumluluğun garanti edildiği.

## 2. Repo analizi: hazır olan ile hedeflenen

Bu tablo başlangıç sürümü `913bbf7` için kaynak koduna dayanır. Repo değişirse
müşteri demosundan önce yeniden kontrol edin.

| Konu | Gerçek uygulama | Sunumda kullanacağınız ifade |
|---|---|---|
| Workspace kuralları | `workspace.schema.json`, `policy.yaml`, `rules_engine.py` var | “Bu kontrolleri burada çalıştırabiliyoruz.” |
| Workspace açma | `provision.py` workspace, açıklama, kapasite ve eksik rol ekleme yapar | “Temel oluşturma akışı hazır; gerçek izinlerle prova gerektiriyor.” |
| Diğer alanlar | Domain, subdomain, label ve tags manifestte var; provisioner bunları uygulamaz | “İstek kontrolü var; canlı uygulama eklenecek.” |
| Rol yaşam döngüsü | Mevcut rolü değiştirme/kaldırma, süre sonu ve erişim review yok | “Erişim ekleme ile yaşam döngüsü farklı kapsamlar.” |
| Production erişim kuralı | İki Group ve uygun label istenir; ek bir User Admin kaydı ayrıca yasaklanmaz | “Grup sayısı kontrolü, kişisel admin erişimini engelleyen kontrol değildir.” |
| Drift | Kimliğin görebildiği workspace adları ve açıklamaları karşılaştırılır | “Şimdilik görünür workspace'lerde sınırlı tutarlılık kontrolü.” |
| Tenant kapsamı | `_fabric.py` normal `/workspaces` API'sini kullanır | “Bu sonuç bütün tenant'ın envanteri değildir.” |
| Yönetim işareti | `managed-by:gh:...` işareti otomatik yazılmaz veya taranmaz | “Orijinal challenge'daki bu hedef henüz uygulanmamış.” |
| Workspace silme | Manifest silinince canlı workspace silinmez | “Dosyayı silmek veri temizliği değildir.” |
| Drift issue | Workflow `drift, governance` etiketleriyle issue açabilir; otomatik kapatma yok | “Düzeltmeden sonra sonucu kontrol edip issue'yu biz kapatacağız.” |
| Hata davranışı | Bazı kapasite/rol hataları yalnız uyarı; UPN çözülemezse atlanabilir | “Yeşil job tek başına başarılı dağıtım kanıtı değil.” |
| Canlı grup kontrolü | `LIVE_CHECKS=true` Graph kontrolünü açar; başarısız sorgular bloklanır, her bulunan grup için HTTP 200 kanıt satırı yazılır | “Offline PASS veya yalnız Azure login yeterli değildir; `owner-groups-exist` sonucunu da göster.” |
| Kotalar | Policy'de kota değerleri var; mevcut kural motoru bunları uygulamaz | “Tanımlı kota, çalışan kota kontrolü demek değil.” |
| CI kapsamı | Bu kopyada `validate` tüm PR'larda bütün workspace manifestlerini doğrular | “Policy/schema değişikliği de tüm workspace'lere uygulanır; yeni kaynak ailelerinin validator'ları hâlâ eklenmelidir.” |
| Yeni kaynak türleri | 02-08'in birçok schema, script ve workflow'u mevcut değil | “Bunlar geliştirme atölyesi görevleri.” |
| İsim örnekleri | Kod altı parçalı ad ister; eski `dev-plt-...` örnekleri uyumsuz | “Şemanın istediği güncel adı kullanıyoruz.” |
| CODEOWNERS | Yerel dosyada repo sahibi ve `*-prd-*.yaml` deseni var; solo kurulumda owner onayı zorunlu değil | “Dosya sahipliği ile bağımsız onay farklıdır; ekipli kurulum için ikinci reviewer gerekir.” |
| Runner | Bu kopyada üç yönetişim workflow'u GitHub-hosted `ubuntu-latest` ve Python 3.12 kullanır | “Runner komutları çalıştıran geçici makinedir; Fabric kapasitesi değildir. GitHub'a gönderme ve etkinleştirme ayrı adımlardır.” |
| Onay sınırı | Aynı SPN PR ve provision'da kullanılabilir; OIDC subject izni daraltmaz | “Production için okuma/yazma kimliklerini ve güven sınırını ayırmalıyız.” |

**Kaynakları açıp gösterin:**

Tek kişiyle yapılan eğitim için [solo demo ile orijinal tasarım farklarını](solo-demo-farklari.md)
ayrıca okuyun. Bu belge onaylanan istisnaları, push/Actions kullanımını ve
henüz uygulanmamış kararları birbirinden ayırır.

[şema](../../schemas/workspace.schema.json),
[policy](../../rules/policy.yaml),
[validator](../../scripts/validate.py),
[kural motoru](../../scripts/rules_engine.py),
[provisioner](../../scripts/provision.py),
[drift](../../scripts/drift.py),
[API istemcisi](../../scripts/_fabric.py),
[workflow'lar](../../.github/workflows/).

### Diğer klasörler ne işe yarar?

| Yol | Eğitim açısından anlamı |
|---|---|
| `challenges/` | 00-08 ve Capstone görevleri; buradan ilerleyin |
| `workspaces/` | İstenen workspace durumunu anlatan YAML dosyaları |
| `schemas/`, `rules/`, `scripts/` | Dosyanın yapısı, kurum kuralları ve uygulayıcı kod |
| `.github/` | Otomasyonlar, reviewer tanımları ve PR formu |
| `.vscode/` | Editör ayarları; mevcut F5 görevleri ayrı Azure Functions uygulamasına ait |
| `api/`, `agent/`, `infra/`, `azure.yaml` | Ek M365 agent/API ve Azure dağıtım yolu; temel workshop için kurulmaz |
| `site/`, `package.json` | Dokümanların web yayını; Fabric kurulumu değildir |
| `dist/` | Dağıtım çıktıları; challenge çözümü veya canlı kurulum kanıtı değildir |

Ek M365/Copilot Studio agent yolu ile **Fabric Data Agent (Challenge 06)**
aynı uygulama değildir. Müşteri bu ek yolu istemiyorsa `azd up`, F5 veya API
dağıtımıyla eğitimin kapsamını büyütmeyin.

## 3. İlk müşteri görüşmesinde sorulacaklar

Bu soruları workshop'tan en az bir hafta önce müşteri sorumlusuyla yanıtlayın.

| Soru | Neden gerekli? |
|---|---|
| Hangi sorun öncelikli: erişim, maliyet, standart, veri akışı, denetim? | Challenge seçimini belirler |
| Ayrı test tenant/workspace ve yapay veri kullanabilir miyiz? | Üretim verisini ve hizmeti riske atmamak için |
| Fabric, Entra, GitHub ve Purview yöneticileri kimler? | Coach bütün yönetici rollerine sahip değildir |
| Hangi kapasite/SKU, bölge ve lisanslar mevcut? | Özellik ve eşzamanlı çalışma sınırlarını görmek için |
| GitHub planı gerekli branch/environment onaylarını destekliyor mu? | Ekranda görünmeyen özelliği demo günü aramamak için |
| Copilot ve MCP kullanımı kurum tarafından onaylı mı? | Kod/veri paylaşımı ve araç çalıştırma kuralları için |
| Public fork uygun mu; müşteri için private repo mu gerekli? | Kamuya açık fork müşteri sırlarını taşıyamaz |
| Ağ, proxy, MFA ve cihaz kuralları nedir? | Kurulum ve oturum açma engellerini önceden görmek için |
| Demo sonunda kimin hangi çıktıyı devralması bekleniyor? | Teknik başarıyı iş hedefiyle eşleştirmek için |
| Bütçe, kaynak kapatma zamanı ve sorumlusu kim? | Eğitim sonrası maliyetlerin devam etmesini önlemek için |

Canlı ortama izin yoksa oturumu **yerel kural demosu ve tasarım atölyesi**
olarak planlayın. Canlı kurulum yapmış gibi bir değerlendirme hazırlamayın.

## 4. Kendinizi hazırlama planı

Süreler tahmindir; yetki onayları ve eksik otomasyon geliştirmesi dahil değildir.

| Oturum | Sizin yapacağınız prova | Hazır olduğunuzu gösteren kanıt |
|---|---|---|
| 1 - 60-90 dk | İlk kurulum; dosya, terminal, commit ve PR kavramları | Bir dosya değişikliğinin diff'ini açıklayabiliyorsunuz |
| 2 - 90-150 dk | 00; yöneticiyle kimlik, runner ve onay kapıları | Hangi adımın hangi kimlikle çalıştığını anlatabiliyorsunuz |
| 3 - 90-120 dk | 01; bozuk manifest, düzeltme, dry-run, izin varsa canlı demo | FAIL/PASS, PR ve gerçek workspace kontrolü birbirinden ayrılıyor |
| 4 - Seçilen kapsam | 02-08'den müşteri ihtiyacına uygun tek modül | Eksik dosyaları ve tamamlanma koşullarını biliyorsunuz |
| 5 - 45-60 dk | Demo akışını baştan sona sesli anlatın | Canlı bağlantı olmadan da aynı iş değerini açıklayabiliyorsunuz |

Yeni başlayan biri için bütün challenge'ları tek günde “kurup bitirme” sözü
vermeyin. Coach önce 00/01'i rahat anlatmalı, sonra bir uzmanlık modülüne geçmeli.

## 5. Müşteriye göre eğitim kapsamı

| Müşteri ihtiyacı | Önce | Sonra |
|---|---|---|
| Standart workspace açma | 00 + 01 | 03 |
| Kim hangi veriye erişiyor? | 00 + 01 + 04 | 03 + 06 |
| Tekrarlanabilir veri ürünü | 00 + 01 + 02 | 05 + 08 |
| Denetim ve izleme | 00 + 01 + 02 | 07 |
| Governed Data Agent | 00 + 01 + 02 + 03 + 04 | 06; isteğe bağlı 07 |

README'deki genel “02-08 paralel” önerisini mutlak bağımsızlık gibi
anlatmayın. Özellikle 05 ve 06, item ve erişim çalışmalarına dayanır.
Takımlar paralel çalışabilir, ancak ortak şema/kimlik sözleşmeleri gerekir.

### 90 dakikalık tanıtım

| Dakika | Akış |
|---|---|
| 0-10 | İş sorunu, temel terimler ve mevcut uygulamanın sınırları |
| 10-25 | Manifest, policy ve GitHub PR ekranını gösterme |
| 25-40 | Hatalı isteği reddetme ve düzeltme |
| 40-60 | Önceden hazırlanmış test ortamında onay/dağıtım; yoksa açıkça dry-run |
| 60-75 | Copilot ile dosya açıklaması ve salt okunur MCP doğrulaması |
| 75-90 | Müşteri ihtiyacına uygun sonraki modül ve sorumlular |

### Bir günlük başlangıç workshop'u

00'ı önceden bitirin. Sabah GitHub/Copilot temelleri + 01; öğleden sonra
**tek** seçmeli challenge'ın tasarım ve küçük uygulaması; son saat kanıtlar
ve devir. Geliştirilmemiş 02-08 çözümlerini birkaç tıklamalık hazır lab gibi
zamanlamayın. Bütün kapsam için çok oturumlu çalışma planlayın.

## 6. Her challenge için öğretme ritmi

1. **Sorunu sorun:** “Bu kontrol olmazsa ne yanlış gidebilir?”
2. **İş değerini anlatın:** Bir dakikalık açıklamayı challenge rehberinden okuyun.
3. **Küçük demo yapın:** Tek bir dosya ve tek bir sonuçla başlayın.
4. **Kontrollü hata gösterin:** Örneğin onaysız cost center değerini kullanın.
5. **Katılımcıya verin:** Benzer ama farklı bir isteği kendisi hazırlasın.
6. **Kanıt isteyin:** Copilot cevabı değil, rapor/PR/API veya portal çıktısı.
7. **Sınırı sorun:** “Bu kontrolün yakalamadığı bir şey söyleyin.”

Kod bilmeyen grupta ikili çalışın: bir kişi dosyayı değiştirir, diğeri nedenini
açıklar. Sonra rolleri değiştirin. Git hatalarını katılımcının önünde aceleyle
destructive komutlarla düzeltmeyin.

## 7. Müşteriye kullanabileceğiniz benzetmeler

| Kavram | Sade anlatım | Benzetmenin sınırı |
|---|---|---|
| Manifest | “Talep formu” | Dosya kendi başına kaynak oluşturmaz |
| Schema | “Formda hangi kutular var?” | İş kuralını tek başına kapsamaz |
| Policy | “Form hangi kurallara uymalı?” | Kural kod tarafından uygulanmalı |
| PR | “Talebi inceleme ve onay masası” | Merge sonrası canlı sonuç ayrıca kontrol edilir |
| Actions | “Onaylı işi yapan otomasyon” | Yanlış yetki/kodla yanlış işlem de yapabilir |
| OIDC | “Kısa süreli giriş kartı” | Kısa süre, az yetki demek değildir |
| MCP | “Copilot'un sisteme bağlandığı araç kapısı” | Bağlanmak sınırsız yetki sağlamaz |
| Skill | “Uzman çalışma talimatı” | Kalite veya güvenlik sertifikası değildir |
| Drift | “Talep formu ile gerçek durum arasındaki fark” | Bu repoda bütün alanlar taranmaz |

## 8. Demo günü öncesi devam/durma kararı

- [ ] Repo, tenant, kapasite ve oturum açan hesaplar doğru müşteriye ait.
- [ ] Sadece onaylı test kaynakları ve yapay veriler kullanılacak.
- [ ] `LIVE_CHECKS=false` ile yerel doğrulama gösterilebiliyor.
- [ ] Gerçek kapasite ve grup ID'leri şablon değerlerinin yerine yazılmış.
- [ ] Runner çalışıyor; required reviewer gerçekten onay verebiliyor.
- [ ] `production` environment yalnız onaylı branch'ten dağıtım kabul ediyor.
- [ ] Yeni repo için OIDC `sub` biçimi doğrulanmış; eski örnek körlemesine kopyalanmamış.
- [ ] Seçilen challenge'ın hazır olmayan kısmı müşteriye önceden bildirilmiş.
- [ ] Repo ve Pages yayınının görünürlüğü kontrol edilmiş.
- [ ] Kanıtlar izinli yerde, kişisel veri ve token içermeden saklanacak.
- [ ] Temizlik ve maliyet takibinden sorumlu kişi belli.

Kimlik/izin veya onay kapısı hazır değilse **canlı yazma demosunu durdurun**.
Sorunu “çözmek” için herkese admin vermeyin veya onay kuralını kaldırmayın.

## 9. Canlı demo bozulursa

| Durum | Yapılacak | Açıklama |
|---|---|---|
| Fabric/MCP bağlantısı yok | Yerel validator ve mevcut API belgelerini gösterin | “Şu an bağlantıyı değil, kural mantığını gösteriyorum.” |
| Runner bekliyor | Actions job'unda runner etiketini inceleyin; yerel dry-run'a geçin | “Talep alınmış ama çalıştıracak makine yok.” |
| Yetki reddedildi | Doğru tenant/kimliği kontrol edin; yöneticiyi dahil edin | “Yetki sınırı çalışıyor; rastgele yetki genişletmeyeceğiz.” |
| Copilot uygun çıktı üretmedi | Hazırladığınız küçük örneği açın, hatayı beraber okuyun | “AI çıktısı öneridir; doğrulama bu yüzden var.” |
| İleri challenge yetişmedi | Mevcut çıktıyı, eksikleri ve takip işini ayrı kaydedin | “Tasarım tamamlandı; canlı otomasyon tamamlanmadı.” |

Önceki başarılı demo kanıtını gösterebilirsiniz; tarihini ve hangi ortamdan
geldiğini söyleyin. Başka müşterinin verisini veya ekranını kullanmayın.

## 10. Değerlendirme ve devir

Her takım şu beş soruyu cevaplamalı:

1. İsteği hangi dosyaya yazdınız?
2. Hangi kural yanlış bir isteği engelledi?
3. Kim onayladı; otomasyon hangi kimlikle çalıştı?
4. Gerçek sonucu nereden kontrol ettiniz?
5. Hangi kontrol henüz uygulanmıyor?

Devir paketinde müşteri reposunun bağlantısı, PR/run numaraları, doğrulanmış
test kaynakları, eksiklerin sahibi, işletim sorumlusu ve temizlik zamanı
bulunsun. Tüm modüller yapıldıysa
[Capstone değerlendirmesini](../../challenges/capstone/COACH-TR.md) kullanın.

## 11. Sık gelen müşteri sorularına kısa yanıtlar

**“Copilot bizim yerimize onay verebilir mi?”** Dosya veya review önerisi
hazırlayabilir. Kurumsal onay sorumluluğunu ona devretmiyoruz.

**“Bunu doğrudan production'a kurabilir miyiz?”** Bu bir başlangıç blueprint'i.
Yetki ayrımı, hata yönetimi, bütün kaynakların drift kapsamı, testler ve geri
dönüş süreçleri müşteri için tamamlanıp değerlendirilmeden bunu önermiyoruz.

**“GitHub'daki dosya değişince Fabric otomatik güncellenir mi?”** Yalnız ilgili
workflow tetiklenir, onaylanır ve o kaynağı destekleyen kod başarıyla çalışırsa.
Bu repo ayrıca otomatik Fabric Git integration kurmaz.

**“F2 her challenge için yeterli mi?”** Depo başlangıç için F2, bazı yoğun
egzersizler için F4+ önerir. Bu bir performans veya özellik garantisi değildir.
Gerçek workload, bölge, tenant ayarları ve lisans önkoşulları ayrıca kontrol edilir.

## Resmi ve repo içi başvuru

- [İngilizce delivery guide](../delivery-guide.md) - orijinal hedef/ajanda
- [GitHub environment korumaları ve plan sınırları](https://docs.github.com/en/actions/reference/workflows-and-actions/deployments-and-environments)
- [GitHub OIDC; yeni repo subject biçimi](https://docs.github.com/en/actions/reference/security/oidc)
- [VS Code Copilot kurulumu ve veri kullanımı](https://code.visualstudio.com/docs/setup/copilot)
- [Fabric tenant geliştirici ayarları](https://learn.microsoft.com/fabric/admin/service-admin-portal-developer)

Ürün belgeleri ve ekran adları değişebilir. Müşteri oturumundan önce kaynakları
yeniden açın; kendi test ortamınızda görmediğiniz sonucu doğrulanmış diye sunmayın.
