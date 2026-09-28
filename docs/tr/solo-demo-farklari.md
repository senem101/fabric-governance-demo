# Solo demo ile orijinal tasarım arasındaki farklar

**Karar ve durum tarihi:** 28 Eylül 2026.
**Karşılaştırma temeli:** Orijinal `913bbf7` sürümündeki Challenge 00,
kimlik dokümanı ve üç GitHub Actions workflow'u.

Bu belge, tek kişiyle yapılan eğitim demosunda hangi kontrollerin korunduğunu,
hangilerinin bilinçli olarak değiştirildiğini ve hangi adımların henüz
tamamlanmadığını açıklar. **Bir kararın alınmış olması, ayarın GitHub'da
uygulandığı veya gerçek çalıştırmayla doğrulandığı anlamına gelmez.**

## 1. Solo demoda push ve GitHub Actions kullanılabilir mi?

**Evet.** Solo demo, push veya GitHub Actions kullanımını yasaklamaz.
Dosyaları çalışma branch'ine göndermek, onları `main`e almak ve
workflow'ları etkinleştirmek ayrı adımlardır.

Bu demonun gönderim hedefi yalnız kişisel `senem101/fabric-governance-demo`
reposudur. Microsoft kaynak reposuna push, PR veya ayar değişikliği yapılmaz.
Yerel `origin` adresi kaynak repoyu gösterdiği için gönderimde kişisel fork'un
adresi açıkça seçilir.

Seçilen hedef akış:

1. Değişikliği bir çalışma branch'inde hazırlayıp commit ve push yap.
2. Kendi fork'undaki `main` dalına PR aç.
3. GitHub Actions'ın `validate` kontrolünü çalıştırmasını bekle.
4. Gerekli kontroller geçince kendi PR'ını `main`e birleştir.
5. `production` environment'ını kullanan provision işi için ayrıca onay ver.
6. `DRY_RUN=true` ise yalnız yapılacak işlemleri gör; gerçek kaynak değişikliği
   için ayrıca canlıya geçiş hazırlığını tamamla.

**Push ile merge farklıdır:** Çalışma branch'ine kod göndermek serbesttir.
Uygulanan `main` koruması ise değişikliklerin kontrolsüz doğrudan push yerine
PR ve otomatik kontrolden geçmesini ister.

**PR onayı ile merge de farklıdır:** Kendi PR'ına bağımsız bir reviewer gibi
`Approve` veremezsin. Ancak başka kişinin onayını zorunlu tutmayan solo
kurulumda, gerekli otomatik kontroller geçince kendi PR'ını merge edebilirsin.

## 2. Orijinal kurallar ve seçilen solo uyarlaması

| Konu | Orijinal tasarım / başlangıç uygulaması | Solo demo kararı | Sonuç |
|---|---|---|---|
| Repo sahipliği | Challenge 00, GitHub organization yetkilerini varsayar | Kişisel, public fork kullanılır | Organization'a özgü ayarlar birebir uygulanamaz; yalnız paylaşılabilir demo içeriği tutulur |
| Görev ayrılığı | Katılımcı, reviewer/CODEOWNER ve environment approver rolleri tanımlıdır | Kod hazırlama, merge ve dağıtım onayı aynı kişidedir | Bağımsız ikinci kişi kontrolü yoktur |
| PR zorunluluğu | `main` değişiklikleri PR üzerinden gelir | Korunur | Solo demo, PR'ı atlamak demek değildir |
| PR review | En az bir yetkili kişinin onayı istenir | GitHub'da zorunlu onay sayısı `0` olarak ayarlandı | Kişi kendi PR'ını başka reviewer beklemeden merge edebilir |
| CODEOWNERS | Gerçek dosya sorumluları tanımlanır ve onların onayı zorunludur | Yerel dosyada repo sahibi yazıldı; GitHub'da zorunlu CODEOWNERS onayı kapalı | Dosya sahipliği kaydı korunur, bağımsız onay kapısı oluşmaz |
| `validate` kontrolü | Merge öncesi zorunludur | Korunur | Başka kişinin onayı olmaması, otomatik kontrolü kaldırmaz |
| `main`i güncelleyen aktör | Challenge metni “yalnız GitHub Actions push etsin” der | Kontroller geçince repo sahibi PR'ı merge eder | Actions-only güncelleme şartı uygulanmaz |
| Yönetici için branch kuralları | Branch korumasının kapsamı yapılandırılmalıdır | Kurallar repo yöneticisine de uygulanır | Admin olmak normal PR/check yolunu atlama gerekçesi değildir; repo sahibinin ayarları değiştirebilmesi ayrı bir yetkidir |
| Force push ve branch silme | Korunan branch için varsayılan olarak engellenir | GitHub'da `main` için kapatıldı | Çalışma branch'ine normal push ile karıştırılmamalıdır |
| Production onayı | En az bir environment reviewer istenir | Tek reviewer repo sahibidir; kendi başlattığı dağıtımı onaylayabilir | Manuel duraklama vardır; iki kişiyle görev ayrılığı yoktur |
| Runner | Başlangıçtaki üç YAML dosyası `[self-hosted, fabric-gov]` bekler | GitHub-hosted `ubuntu-latest` ve açıkça Python `3.12` seçilir | Kişisel bilgisayara runner kurulmaz; komutları geçici Linux makine çalıştırır |
| Genel tenant kapsamı | API kullanımı ve workspace oluşturma demo grubuyla sınırlandırılır | Önceden `Entire organization` olan iki Core SPN ayarı ve `Create workspaces` korunur | Diğer kullanıcı ve otomasyonları etkilememek için mevcut kapsam daraltılmaz; tenant yalnız demo grubuna izole edilmiş sayılmaz |
| PR kontrolünün kapsamı | Path filtreleriyle tetiklenir; yalnız değişen workspace manifestlerini denetler | Yerel workflow tüm PR'larda bütün workspace manifestlerini denetleyecek şekilde hazırlandı | Doküman PR'ları zorunlu check beklerken takılmaz; policy/schema değişikliği tüm workspace'ler için değerlendirilir |
| OIDC giriş hatası | `validate` içindeki login hatasıyla devam edilebilir | Yerel workflow'da login hatası işi başarısız yapar | Başarısız kimlik doğrulama başarılı zorunlu kontrol gibi sunulmaz |
| Drift başlangıcı | İş zamanlanmış veya manuel tetiklendiğinde doğrudan çalışabilir | `DRIFT_ENABLED` yalnız `true` olduğunda job çalışır; başlangıç değeri `false` | Rapor kapsamı gözden geçirilmeden otomatik tenant taraması ve public issue oluşturulması önlenir |
| Canlı grup sorgusu hataları | Her HTTP hatası “grup yok” sayılır; bazı istisnalar uyarıyla atlanır | HTTP 404 ile diğer hatalar ayrılır; sorgu tamamlanamazsa doğrulama bloklanır, başarıda HTTP 200 kanıtı yazılır | Erişim hatası veya atlanan kontrol başarılı canlı doğrulama gibi sunulmaz |

**Production onayı hakkında nüans:** Orijinal Challenge 00 en az bir reviewer
ister; reviewer'ın mutlaka PR yazarından farklı olacağını açıkça şart koşmaz.
Solo tercih, bu rolün aynı kişide olduğunu açık hale getirir.

**Runner hakkında nüans:** Orijinal kimlik dokümanı hosted ve self-hosted
runner'ı destekler. Buradaki fark kimlik mimarisinde değil, başlangıçtaki
workflow dosyalarının çalıştırma ortamındadır.

**“Yalnız Actions push etsin” hakkında nüans:** Klasik branch protection
ekranındaki aktör bazlı push kısıtlaması organization repolarında sunulur.
Başlangıçtaki üç workflow ayrıca bir PR merge otomasyonu içermez. `validate`
sonucunun kaynağını GitHub Actions olarak seçmek, `main`e yalnız Actions'ın
push edebilmesiyle aynı kontrol değildir.

## 3. Değişmeyen kimlik tasarımı

Orijinal **tek-SPN ve üç OIDC bağlantılı model** seçilmiştir.
Kimliksiz PR ve yalnız environment onayından sonra canlı erişim önerisi
bu demo için seçilmemiştir.

| İş | Kullanılan OIDC bağlamı | `production` onayını bekler mi? |
|---|---|---|
| PR doğrulaması | `pull_request` | Hayır |
| `main` üzerinden drift | `ref:refs/heads/main` | Hayır |
| Provision | `environment:production` | Evet |

Üç bağlam aynı SPN'ye bağlanır. Fabric Administrator ve seçilen kapasitedeki
Capacity Admin yetkileri kaldırılmaz. Güvenlik grubu ve admin API tenant
ayarları da kullanılmaya devam eder.

**OIDC bağlamı yetkiyi salt okumaya düşürmez.** Mevcut scriptin yalnız kontrol
yapması, giriş yaptığı yönetici kimliğinin yazma yetkisini ortadan kaldırmaz.
PR ve main işleri bu kimliği production onayından bağımsız kullanabilir.
GitHub-hosted runner seçmek de SPN yetkilerini azaltmaz. Yeni
`DRIFT_ENABLED` koşulu yalnız drift job'ının başlamasını kontrol eder;
OIDC güven bağlantısını veya SPN'nin mevcut yetkilerini daraltmaz.

Gerçek deponun OIDC subject'i owner/repo kimlik numaralarını içeren immutable
biçimdedir. Orijinal dokümandaki eski subject örneklerinin buna uyarlanması
ayrı bir güvenlik mimarisi seçimi değil, token ile tam eşleşme gereğidir.
Bu belgede gerçek tenant, uygulama, grup veya kapasite GUID'leri yayımlanmaz.

## 4. Geçici hazırlık ayarları kalıcı solo kuralı değildir

| Konu | Şimdiki durum | Nasıl yorumlanmalı? |
|---|---|---|
| `DRY_RUN=true` | Açık | Provision scriptinin gerçek değişiklik yapmasını önleyen başlangıç ayarıdır; bütün Azure/Fabric işlemlerini engelleyen bir yetki sınırı değildir |
| `LIVE_CHECKS=true` | Kişisel repo variable'ı açıldı | Gerçek demo grubu bu çalışma branch'inde hazır; SPN ile başarılı Graph sorgusu yeni PR'da ayrıca doğrulanacak |
| `DRIFT_ENABLED=false` | Başlangıçta kapalı | Koşulu içeren GitHub workflow'unda zamanlanmış ve manuel drift job'ı atlanır; `true` ancak izinler ve yayımlanacak rapor kapsamı onaylandıktan sonra seçilir |
| Gerçek manifest sahipleri ve policy kapasitesi | Grup owner hazır; kullanıcı owner ve kapasite örnek değer | Demo grubunun Object ID'sinin public manifestte tutulması açıkça onaylandı; diğer örnek değerler düzeltilmeden gerçek provisioning yapılmamalıdır |
| `DEFAULT_OWNER_UPN` | Kişisel repoya eklendi; API ile dolu bir değer bulunduğu doğrulandı | Orijinal listede vardır, mevcut scriptler kullanmaz; sırf eklemek sahip ataması sağlamaz |
| `validate` tetikleme kapsamı | İlk PR ile kişisel main'e alındı; tüm PR'ları kapsıyor | Her yeni PR güncel commit için yeniden değerlendirilir |
| Tam workspace doğrulaması | Yerel workflow `python scripts/validate.py` kullanıyor | Scriptteki `--changed-only` seçeneği kaldırılmadı; yalnız bu CI işinde artık kullanılmıyor |
| Azure login hata davranışı | `continue-on-error` kaldırıldı; ilk PR'da gerçek OIDC girişi başarılı | Yeni canlı grup kontrolünün Graph erişimi ayrıca kanıtlanmalıdır |

Bu satırlar, “solo demoda canlı doğrulama yapılmaz” veya “Actions
çalıştırılamaz” şeklinde yorumlanmamalıdır.

**Drift kontrolünün sınırı:** Job atlandığında Azure login, tarama ve issue
oluşturma adımları çalışmaz; GitHub yine de atlanmış bir çalışma kaydı
gösterebilir. Koşulu içermeyen eski bir workflow sürümü veya doğrudan
çalıştırılan `scripts/drift.py` bu değişkeni kontrol etmez. Değişkeni eklemek
tek başına yeterli değildir; koşulun bulunduğu workflow sürümü kullanılmalıdır.
Mevcut drift scripti hâlâ çağıranın görebildiği workspace listesini karşılaştırır;
demo kaynaklarına özgü bir kapsam filtresi henüz eklenmemiştir.

## 5. Uygulama durumu: ne yapıldı, ne bekliyor?

Bu bölüm yukarıdaki tarih için bir durum kaydıdır; canlı bir takip ekranı
değildir. Sonraki değişikliklerde gerçek GitHub ve tenant ayarları yeniden
kontrol edilmelidir.

| Alan | Kanıt / durum |
|---|---|
| SPN, güvenlik grubu ve Fabric yönetici hazırlığı | Kullanıcı tarafından kurulduğu bildirildi; doğru kapasitenin yönetici listesinde SPN'nin bulunduğu kullanıcı tarafında CLI ile kontrol edildi |
| Üç federated credential | Kullanıcı tarafından oluşturuldu; kaydedilmiş issuer, audience ve subject değerleri CLI çıktısında karşılaştırıldı |
| Production environment | Reviewer, kendi dağıtımını onaylayabilme, main branch sınırı ve admin bypass kapalı ayarları daha önce GitHub API ile kontrol edildi |
| Hosted runner uyarlaması | İlk kişisel PR main'e merge edildi; PR doğrulaması GitHub-hosted runner'da başarılı çalıştı |
| Solo branch protection | GitHub'da uygulandı: PR zorunlu, onay sayısı 0, CODEOWNERS onayı kapalı, `validate` kaynağı GitHub Actions, branch güncel olmalı, kurallar admin'e de uygulanır, force push/silme kapalı |
| Solo CODEOWNERS | İlk kişisel PR ile main'e alındı; sahip repo kullanıcısı, üretim dosya deseni düzeltildi |
| GitHub Actions / OIDC çalıştırması | İlk kişisel PR çalışmasında `Azure login (OIDC)` ve `Validate` başarılı oldu. Yeni commit'ler için güncel kontrol sonucu ayrıca beklenir |
| Drift başlangıç kontrolü | İlk kişisel PR ile main'e alındı; `DRIFT_ENABLED=false` |
| Microsoft Graph grup izni | `Group.ReadBasic.All` Application için yönetici onayı verildi; gerçek SPN app-role ataması salt okunur CLI sorgusuyla doğrulandı |
| Canlı grup girdisi | Gerçek demo grup ID'si bu çalışma branch'inde hazır. Yeni PR'da SPN ile HTTP 200 sonucu henüz bekleniyor; insan hesabının grup sorgusu bu kanıtın yerine geçmez |
| MCP smoke kontrolleri | Kullanıcı dört gerçek araç çağrısını doğruladı: workspace ve kapasite listeleri, en az 6 iş yükü türü ve Lakehouse OpenAPI içeriği |
| Tam Challenge 00 kabulü | Canlı grup doğrulaması ve 60 saniyelik kimlik akışı özeti bekliyor. Bağlı setup rehberindeki gerçek workspace oluşturma provası ayrıca tamamlanmalı; dry-run bunu kanıtlamaz |
| GitHub Pages | Pages kurulmadığı için ayrı yayın işi hata verdi; kullanıcı bu hatayı olduğu gibi bırakmayı seçti. Challenge 00'ın şartı değildir |

**Yerel dosya değişikliği GitHub ayarı değildir.** GitHub branch koruması,
CODEOWNERS dosyasının doğru branch'e ulaşması ve Actions'ın gerçek
çalışması ayrı ayrı tamamlanmalıdır. Bu belgeyi yazmak bunları kendiliğinden
uygulamaz.

**Şu an beklenebilecek durum:** `main` koruması aktiftir. Her yeni push
sonrasında güncel commit için `validate` sonucu beklenebilir; önceki commit'in
başarılı sonucu yeni değişikliklerin doğrulandığı anlamına gelmez.
Bu bekleme, çalışma branch'ine push yapılmasını engellemez.

## 6. Müşteriye nasıl anlatılmalı?

> Bu, tek kişiyle yapılan bir eğitim demosudur. PR, otomatik doğrulama ve
> manuel dağıtım onayı akışını göstereceğiz. Bağımsız ikinci kişi onayı ve
> yalnız otomasyonun main'i güncellemesi şartlarını uygulamıyoruz. Orijinal
> tek-SPN/OIDC modeli korunuyor; bu nedenle demo, eksiksiz görev ayrılığına
> sahip bir production yönetişim kurulumu olarak sunulmamalıdır.

**Solo demo kabulü ile orijinal bütün şartların karşılanması aynı değildir.**
Onaylanan istisnalar ve henüz yapılmamış işler açıkça belirtilmelidir.

Ekipli kurulumda ikinci reviewer'ın write erişimi ve gerçek CODEOWNERS
eşleşmeleri hazırlanmalı; PR ve CODEOWNERS onayı zorunlu hale getirilmelidir.
Actions-only güncelleme isteniyorsa uygun repo/uygulama yetkileri ve gerçek
merge otomasyonu ayrıca tasarlanmalıdır. Tenant kapsamları da diğer
kullanıcıları etkilemeyecek, yönetici onaylı bir planla ele alınmalıdır.

## Kaynaklar

- [Orijinal Challenge 00](../../challenges/00-setup/challenge.md)
- [Orijinal kimlik modeli](../identity-model.md)
- [Orijinal kurulum runbook'u](../setup.md)
- [Türkçe Challenge 00 rehberi](../../challenges/00-setup/COACH-TR.md)
- [GitHub: branch protection](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches)
- [GitHub: CODEOWNERS](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-code-owners)
