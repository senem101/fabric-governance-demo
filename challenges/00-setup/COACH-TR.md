# Challenge 00 - Coach rehberi: ortam, kimlik ve araçlar

[Tüm rehberler](../../docs/tr/README.md) |
[İlk kurulum](../../docs/tr/ilk-kurulum.md) |
[Orijinal challenge](challenge.md) |
[Sonraki: 01](../01-workspace-as-code/COACH-TR.md)

**Amaç:** Katılımcının bilgisayarı, GitHub reposu ve Fabric test ortamı
birbirine doğru kimliklerle bağlanabilsin.
**Tahmini süre:** Araçlar için 60-90 dk; yöneticiyle kimlik/Actions hazırlığı
için 90-150 dk. Kurumsal izin bekleme süresi dahil değildir.

## 1. Müşteriye bir dakikada anlatım

> “İki farklı çalışanımız var. Siz VS Code'da kendi hesabınızla keşif
> yapacaksınız. GitHub otomasyonu ise ona özel bir uygulama hesabıyla
> çalışacak. Bu ayrım sayesinde bir işlemi kimin yaptığını görebileceğiz.
> Önce yalnız okuma ve dosya kontrolü yapacağız; oluşturma işlemini onaylı
> test ortamına geçince açacağız.”

## 2. Kim neyi hazırlayacak?

| Sorumlu | İş |
|---|---|
| Katılımcı | Git, VS Code, Python, Copilot ve kendi hesabı |
| GitHub repo yöneticisi | Müşteri reposu, runner, değişkenler, reviewer ve branch koruması |
| Entra yöneticisi / yetkili uygulama sahibi | App registration, service principal, güvenlik grubu, OIDC |
| Fabric yöneticisi | Tenant ayarları ve test alanı politikası |
| Kapasite yöneticisi | Aktif test kapasitesi ve gereken kapasite yetkisi |
| Coach | Hazırlığı kontrol etme, yerel prova, kimlik farkını açıklama |

Coach'a otomatik olarak tenant yöneticiliği verilmez. Önce müşterinin mevcut
test kapasitesini kullanmayı değerlendirin. Yeni kapasite oluşturmak maliyet
doğurur; bu rehber kapasite satın almaz veya deploy etmez.

## 3. Başlamadan önce hazır/dur listesi

- [ ] [İlk kurulum](../../docs/tr/ilk-kurulum.md) tamamlandı; yerel validator PASS.
- [ ] Müşteriye ait onaylı repo var; public fork'ta müşteri verisi tutulmayacak.
- [ ] Tenant, kapasite bölgesi ve bütçe sahibi belli.
- [ ] İki farklı onaylı Entra güvenlik grubunun Object ID'si alınabiliyor.
- [ ] En az bir ekip arkadaşı GitHub PR review yapabiliyor.
- [ ] Gerekli environment onayı kullanılan GitHub planında destekleniyor.
- [ ] Canlı kaynaklar sadece ayrılmış eğitim ortamında olacak.

Onay/kimlik hazır değilse 4-5. adımlardaki tasarımı anlatın, yerel çalışmaya
devam edin; yetki artırarak veya onayları atlayarak ilerlemeyin.

## 4. Kimlik bilgilerini karıştırmadan kaydedin

Değerleri müşterinin erişim kontrollü not alanında tutun. GUID'ler parola
değildir, ancak müşteri ortam envanteridir; public eğitim dosyalarına taşımayın.

| Değer | Nerede bulunur? | Nerede kullanılır? |
|---|---|---|
| Tenant ID | Entra admin center > Overview | GitHub `AZURE_TENANT_ID` |
| Application (client) ID | App registrations > uygulama > Overview | GitHub `AZURE_CLIENT_ID` |
| Service principal Object ID | Enterprise applications > aynı uygulama > Overview | Grup üyeliği ve Fabric yetkileri |
| App registration Object ID | App registrations ekranı | SPN Object ID ile aynı değildir; rol hedefi diye kullanmayın |
| Grup Object ID'leri | Entra > Groups > grup > Overview | `owners[].identifier` |
| Fabric Capacity ID | Fabric kapasite yönetimi / yetkili capacity listeleme sonucu | Policy içindeki `capacityId` |
| GitHub owner/repo | Tarayıcıdaki repo adresi | OIDC güven eşleşmesi |

Fabric Capacity ID bir GUID'dir; Azure'un `/subscriptions/.../providers/...`
ile başlayan ARM resource ID'si değildir.

## 5. Entra uygulaması ve güvenlik grubu

Bu adımları müşteri yöneticisiyle yapın; önceden hazırlanmışsa yeniden oluşturmayın.

1. Entra admin center > **Applications > App registrations > New registration**.
2. Örnek ad: `gh-fabric-workspace-provisioner`. Kurumun tenant kapsamına uygun
   hesap türünü seçin; yalnız bu müşteri için genellikle single tenant kullanılır.
3. Uygulamayı kaydedin; Tenant ID ve Application (client) ID'yi alın.
   GitHub OIDC için client secret üretmeniz gerekmez.
4. **Enterprise applications** altında aynı client ID'li uygulamayı bulun;
   buradaki **Object ID**, service principal'ın kimliğidir.
5. **Groups > New group > Security** ile örneğin
   `sg-fabric-workspace-provisioner` grubu oluşturun.
6. Grubun **Members > Add members** bölümünden uygulamanın service principal'ını
   ekleyin. Yalnız bir insan kullanıcıyı eklemek otomasyona izin vermez.
7. Workspace sahipliği için müşteri yöneticisinin belirlediği iki güvenlik
   grubunu hazırlayın; örneğin admin grubu ve üye grubu. Gruba uygun insan
   katılımcıları da ekleyin. Kendinizi erişimsiz bırakmayın.

**Beklenen:** SPN doğru grubun üyesi; client ID ile SPN Object ID arasındaki
fark açıklanabiliyor. Bunların hiçbiri tek başına Fabric erişimi sağlamaz.

## 6. Fabric tenant ve kapasite izinleri

1. Fabric portalında yönetici **Settings > Admin portal > Tenant settings**
   ekranını açar.
2. Güncel **Developer settings** altında şu ayarları bulun:
   **Service principals can create workspaces, connections, and deployment pipelines**
   ve **Service principals can call Fabric public APIs**.
3. Gereken ayarları **Specific security groups** ile yalnız onaylı provisioning
   grubuna açın. Eski dokümandaki “Service principals can use Fabric APIs”
   adı farklı görünebilir; güncel açıklamayı kontrol edin.
4. Workspace oluşturma politikasını ve insan kullanıcıların yaratma kapsamını
   yöneticiyle değerlendirin. Başka ekipleri etkileyen tenant geneli ayarı
   workshop sırasında onaysız daraltmayın.
5. Hedef kapasitede SPN'ye gerekli yetkiyi kapasite yöneticisi verir.
   Create Workspace API için kapasitede **Contributor veya Admin** gerekir.
   Azure subscription rolü ile Fabric kapasite rolünü aynı şey sanmayın.
6. Önceden var olan workspace üzerinde çalışılacaksa API'nin gerektirdiği
   workspace rolünü ayrıca tanımlayın.
7. Ayar yayılımı için süre tanıyın; orijinal rehber 15 dakikaya kadar beklemeyi
   önerir. Sonucu gerçek API çağrısıyla doğrulayın.

**En az yetki notu:** Sadece 00/01 için SPN'ye otomatik olarak tenant geneli
Fabric Administrator vermeyin. Core workspace API'leri ile admin API'lerinin
izin modelleri farklıdır. Admin ayarını değiştiren insanın Fabric yöneticisi
olması, her otomasyon kimliğinin aynı role sahip olması gerektiği anlamına gelmez.

03/07 gibi admin API kullanan modüllerde read-only/update admin tenant ayarlarını
ayrı değerlendirin. Her endpoint'in desteklediği kimliği kontrol edin. Power BI
read-only admin API'leri için uygulamaya rastgele geniş Power BI application
permissions eklemek doğru çözüm değildir.

## 7. GitHub repo'yu önce güvenli deneme moduna alın

Repo yöneticisi, Actions'ı etkinleştirmeden önce şu hazırlıkları yapar:

1. **Settings > Actions > General** içinde kurumun izinli action politikasını
   kontrol edin. Mevcut action'ların çalışmasına izin olup olmadığını görün.
2. **Settings > Secrets and variables > Actions > Variables** sekmesinden
   aşağıdaki repository variables değerlerini ekleyin.
3. **Settings > Environments > New environment** ile adı tam olarak
   `production` olan ortamı oluşturun. İsim mevcut workflow'da böyledir;
   bu lab'da hedeflediğiniz Fabric workspace yine `dev` olabilir.
4. **Required reviewers** ekleyin; mümkünse kendi çalışmasını onaylamayı ve
   yönetici bypass'ını engelleyin. **Deployment branches and tags** için yalnız
   `main`e izin verin.
5. Bu onay özellikleri repo görünürlüğü/GitHub planı nedeniyle yoksa canlı
   yazma workflow'unu açmayın. Planı veya onaylı kontrol tasarımını yöneticiyle
   çözün; yalnız `production` isminin varlığı onay kapısı sağlamaz.

| Variable | Başlangıç değeri / anlamı |
|---|---|
| `AZURE_TENANT_ID` | Kendi tenant GUID'niz |
| `AZURE_CLIENT_ID` | Kendi uygulamanızın client GUID'si |
| `FABRIC_CAPACITY_ID` | Gerçek Fabric kapasite GUID'si; aşağıdaki öncelik notuna bakın |
| `DEFAULT_OWNER_UPN` | Orijinal kurulum listesi için demo sahibinin Entra kullanıcı oturum açma adı; mevcut kod kullanmaz |
| `LIVE_CHECKS` | İlk provada `false` |
| `DRY_RUN` | İlk provada **`true`**; canlıya bilinçli geçişte `false` |
| `DRIFT_ENABLED` | Bu demo için eklenen başlangıç kontrolü: **`false`**; drift rapor kapsamı onaylanmadan açmayın |

Orijinal Challenge 00'daki `DEFAULT_OWNER_UPN` değişkenini de ekleyin.
Değerini **Entra ID > Users > ilgili kullanıcı > User principal name**
alanından alın; GitHub kullanıcı adı veya SPN Object ID'si değildir.
Mevcut workflow/script bu değişkeni kullanmaz; sahip atamaları manifestteki
`owners` listesinden gelir. Değişkeni eklemek örnek owner'ı değiştirmez.
UPN değerini public dosyalara veya loglara yazdırmayın.

`DRIFT_ENABLED`, orijinal değişken listesine eklenen bir demo kontrolüdür.
`drift.yml` job'ı yalnız değer `true` olduğunda çalışır; değişken eksik,
boş veya `false` ise hem zamanlanmış hem manuel tetiklemede job atlanır.
Bu durumda runner adımları, Azure login, tarama ve issue oluşturma çalışmaz.
GitHub'da bir workflow kaydı veya `skipped` sonucu görünmesi drift taraması
yapıldığı anlamına gelmez.

Bu koruma, koşulu içeren workflow sürümünde geçerlidir; yalnız değişken
eklemek eski `main`deki koşulsuz workflow'u değiştirmez. `DRY_RUN` drift'i
durdurmaz. `DRIFT_ENABLED` de doğrudan çalıştırılan `scripts/drift.py`
komutunu engellemez; kontrol GitHub job'ındadır. Demo dışı workspace
isimlerinin public rapora çıkmayacağı doğrulanmadan değeri `true` yapmayın.

`rules\policy.yaml` içindeki `capacityId` şu an örnek `3333...` değeridir.
**Gerçek GUID ile değiştirin.** Kod policy'deki dolu ID'yi variable'dan önce
kullanır; yalnız `FABRIC_CAPACITY_ID` eklemek örnek değeri ezmez.
Manifestteki mantıksal kapasite adı ile policy anahtarı birebir eşleşmelidir.

## 8. OIDC: GitHub'ın kısa süreli kimliğine güven tanımlayın

OIDC, parola saklamadan GitHub job'ının Entra'dan kısa süreli kimlik almasıdır.
App registration > **Certificates & secrets > Federated credentials >
Add credential** yolunu Entra yöneticisi açar.

**Issuer:** `https://token.actions.githubusercontent.com`
**Audience:** `api://AzureADTokenExchange`

Önce repo'nuzun OIDC `sub` formatını GitHub'ın OIDC ayarları/resmi belgesi
üzerinden doğrulayın. **15 Temmuz 2026 sonrası oluşturulan veya yeniden
adlandırılan/taşınan GitHub.com repoları**, owner/repo ID içeren immutable
format kullanabilir; eski repo örneklerini kopyalamayın. GHES ve kurumsal
custom subject politikaları ayrıca değerlendirilir.

| Amaç | Eski varsayılan biçimde subject örneği |
|---|---|
| Provision - environment onayı sonrası | `repo:ORG/REPO:environment:production` |
| Drift - main | `repo:ORG/REPO:ref:refs/heads/main` |
| PR canlı kontrolü - yalnız onaylı tasarımda | `repo:ORG/REPO:pull_request` |

Yeni immutable biçim için aynı bağlamlar, örneğin:

```text
repo:ORG@OWNER-ID/REPO@REPO-ID:environment:production
repo:ORG@OWNER-ID/REPO@REPO-ID:ref:refs/heads/main
repo:ORG@OWNER-ID/REPO@REPO-ID:pull_request
```

Buradaki büyük harfli alanlar yer tutucudur. Gerçek repo'nun subject'ini,
büyük/küçük harf dahil tam eşleştirin. Entra'daki GitHub sihirbazı eski format
üretirse **Other issuer** / desteklenen düzenleme yoluyla doğru subject'i
girmeniz gerekebilir. Token'ın kendisini ekrana veya Chat'e yazdırmayın.

**Güvenlik sınırı:** `pull_request` subject'i SPN'yi read-only yapmaz.
Aynı SPN'ye yazma yetkisi verdiyseniz o kimliği kullanan PR kodu da yazabilir.
Bu çalışma kopyasında eğitim için **orijinal tek-SPN ve üç OIDC bağlantılı
tasarım** korunur: PR Azure login adımı ve `id-token: write` izni kaldırılmaz.
`production` onayı yalnız o environment'ı kullanan provision işini korur;
PR ve main bağlantıları aynı yönetici kimliğine bu onayı beklemeden giriş
sağlayabilir. `LIVE_CHECKS=false` yalnız canlı grup kontrolünü kapatır,
OIDC girişini veya SPN'nin yetkilerini kaldırmaz.

Kimliksiz PR doğrulaması ve yalnız onaylı canlı işler ayrı bir güvenlik
alternatifidir; bu kopyada uygulanmamıştır. Hazır tek-SPN tasarımını
production güvenlik modeli diye sunmayın.

## 9. Runner: komutları hangi bilgisayar çalıştıracak?

**Runner**, workflow dosyasındaki komutları çalıştıran bilgisayardır.
GitHub-hosted runner, GitHub'ın iş için sağladığı geçici sanal makinedir;
katılımcının bilgisayarına Linux veya runner kurması gerekmez. Bu makine
Python scriptlerini çalıştırır; Fabric kapasitesinin yerine geçmez.

Orijinal kaynak workflow'ları **`runs-on: [self-hosted, fabric-gov]`**
bekler. Bu çalışma kopyasındaki `.github\workflows\validate.yml`,
`provision.yml` ve `drift.yml` ise **`runs-on: ubuntu-latest`** kullanır.
Üçüne de Linux sanal ortamı oluşturulmadan önce Python `3.12` hazırlığı
eklenmiştir. Mevcut action sürümleri, OIDC izinleri ve `production`
environment onayı korunur. Zorunlu PR kontrolü için `validate` kapsamı
ve hata davranışı ayrıca uyarlanmıştır; ayrıntı 10. bölümdedir.

Üç dosyada da bulunan Python hazırlığı, doğrulanan `actions/setup-python`
`v6` commit'ine sabitlenmiştir:

```yaml
      - name: Set up Python
        uses: actions/setup-python@ece7cb06caefa5fff74198d8649806c4678c61a1
        with:
          python-version: '3.12'
```

**Etkinleştirmeden önce:**

1. Kurumun GitHub-hosted runner ve kullanılan action'lara izin verdiğini doğrulayın.
2. Repo değişkenlerini, üç OIDC bağlantısını ve seçilen ekip/solo onay modelini hazırlayın.
3. `DRY_RUN=true` ile `production` environment onay/branch kurallarını kontrol edin.
4. Yerel dosya değişikliği GitHub'daki workflow'u güncellemez. Hazırlık branch'ini
   doğru fork'a gönderme, inceleme ve birleştirme adımlarını ayrıca tamamlayın.
5. Actions'ı bu hazırlıklardan sonra etkinleştirin. Merge öncesinde
   `DRIFT_ENABLED=false` değerini ve PR'daki job koşulunu kontrol edin;
   drift raporunun public repo'da hangi bilgileri yayımlayacağını ayrıca değerlendirin.

**Henüz uygulanmayan ek iyileştirme:** Provision'dan hemen önce schema/policy
doğrulaması eklemek. PR workflow'u artık bütün workspace manifestlerini
kontrol eder; ancak provisioner bu kontrolü kendi başına yapmaz.
**Provision workspaces** öncesi için önerilen örnek:

```yaml
      - name: Validate all workspace manifests
        env:
          LIVE_CHECKS: 'false'
        run: python scripts/validate.py
```

İkinci örnek dosya/policy kontrolüdür, canlı grup yetki testi değildir.
Bu bloklar tam workflow dosyası değildir; mevcut `on`, `permissions`,
checkout, Azure login ve environment bölümlerinin yerine yapıştırmayın.

Hosted runner dakikaları/billing ve ağ erişimi kurum tarafından onaylanmalıdır.

Kurum self-hosted istiyorsa yönetici **Settings > Actions > Runners > New
self-hosted runner** yolundan **ayrı Linux** makine kaydeder ve ilgili
workflow'larda `runs-on: [self-hosted, fabric-gov]` seçer. `fabric-gov`
etiketi, venv/pip, Git ve Azure CLI hazır olmalı; makine Python hazırlığı için
kullanılan action'ın güncel runner gereksinimlerini de karşılamalıdır.
Katılımcının günlük iş bilgisayarını veya ortak production sunucusunu runner
yapmayın. Güvenilmeyen public fork PR'larını self-hosted runner'da çalıştırmayın.

## 10. Review ve branch koruması

**Bu demo için solo uyarlaması:** PR ve `validate` zorunludur; bağımsız
PR/CODEOWNERS onayı aranmaz. Orijinalden farklar ve yerel/remote uygulama
durumu [solo demo karşılaştırmasında](../../docs/tr/solo-demo-farklari.md)
ayrı tutulur. Solo demo, push veya GitHub Actions kullanımını yasaklamaz.

1. Yerel `.github\CODEOWNERS` repo sahibini gösterir; üretim deseni
   `/workspaces/*-prd-*.yaml` olarak düzeltilmiştir. Bu dosya tek başına
   zorunlu onay oluşturmaz ve GitHub'a gönderilmeden remote main'i değiştirmez.
2. GitHub'da `main` için PR zorunlu, gereken onay sayısı `0`, CODEOWNERS
   ve son push için başka kişi onayı kapalıdır. Bu bağımsız inceleme değildir.
3. Gerekli check `validate`, beklenen kaynak GitHub Actions'tır.
   Branch'in main ile güncel olması gerekir. Check henüz çalışmadıysa
   merge bekler; çalışma branch'ine push engellenmez.
4. Kurallar repo yöneticisine de uygulanır. `main` için force push ve silme
   kapalıdır; “yalnız Actions merge etsin” kısıtı yoktur.
5. Yerel `validate.yml` artık path filtresi olmadan tüm PR'larda bütün
   workspace manifestlerini doğrular. Azure login hatası işi başarısız yapar.
   Rapor üretilemediyse sticky comment adımı çalışmaz; asıl hata gizlenmez.
6. Orijinal ekip kurulumuna geçerken ikinci reviewer'a write erişimi verin,
   gerçek CODEOWNERS eşleşmelerini hazırlayın ve en az bir PR/CODEOWNERS
   onayını zorunlu hale getirin.
7. **Actions** sekmesinde gerekiyorsa workflow'ları etkinleştirin.
   `DRIFT_ENABLED=false` tutun; gerçek kimlik/izin ve rapor kapsamı
   onaylanmadan drift'i açmayın. Bu opt-in koşulu SPN/OIDC modelini değiştirmez.
   Issues özelliği ve `drift`, `governance` etiketleri de hazır olmalı.

## 11. MCP/Skills ve kabul demosu

[İlk kurulumdaki](../../docs/tr/ilk-kurulum.md) Core MCP, local MCP ve skill
adımlarını uygulayın. Müşteriye üç ayrı oturumu gösterin:
GitHub hesabı, Entra kullanıcısı, Actions service principal'ı.

| Deneme | Beklenen kanıt |
|---|---|
| Yerel `validate.py`, `LIVE_CHECKS=false` | PASS raporu; canlı yetki iddiası yok |
| Core MCP: “Yalnız erişebildiğim workspace'leri listele” | Gerçek okuma aracı ve sonuç |
| Core MCP: “Yalnız görebildiğim kapasiteleri listele” | Eğitim kapasitesinin doğru kimlikle görüldüğü sonuç; boşsa yetki/tenant kontrolü |
| Local MCP: “API belgesi bulunan Fabric iş yüklerini listele” | Sunucunun mevcut dokümantasyon kataloğu; sabit araç sayısı beklemeyin |
| Local MCP: “Lakehouse API belgelerini göster” | Dokümantasyon aracı; kaynak yazımı yok |
| Kurulu skill ile çalıştırılmayan taslak | Skill'in yüklendiği ve taslağın gözden geçirildiği görülebilir |
| Kendi repo'nuzda manifest PR'ı | Validate raporu ve seçilen ekip/solo onay modeline uygun merge kontrolü |
| Onaylı `production` job'ı, `DRY_RUN=true` | Azure login başarılı, dry-run logları; bu henüz Fabric API yazma testi değil |

Canlı workspace oluşturma ve SPN'nin Fabric yetkisini doğrulama 01'de yapılır.
Core MCP'de sizin liste görebilmeniz SPN'nin de görebildiğini kanıtlamaz.

**Copilot'a güvenli kontrol istemi:**

```text
Workflow dosyalarını ve workspace şemasını oku.
Runner, environment, variables ve path filtrelerini tabloyla açıkla.
Henüz uygulanmayan kontrolleri işaretle. Dosya değiştirme ve canlı araç çağırma.
```

## 12. Sorun giderme ve coach soruları

| Sorun | İlk kontrol |
|---|---|
| Job `Queued / Waiting for runner` | Runner etiketi ve çevrimiçi durumu |
| Job `Waiting for approval` | Environment reviewer; bu normal bir bekleme olabilir |
| `AADSTS70021` / federated credential eşleşmiyor | Issuer, audience, gerçek `sub`, immutable ID'ler, environment harfleri |
| Azure login hata verdi ama validate yeşil | Eski workflow sürümünü çalıştırıp çalıştırmadığınızı kontrol edin; bu kopyada login hatası işi durdurur |
| Fabric `403` | SPN grup üyeliği, tenant ayarı, kapasite ve workspace rolü |
| Gerçek capacity variable'ı var ama yanlış ID kullanılıyor | Policy'deki örnek `capacityId` daha öncelikli |
| Review istenmiyor | CODEOWNERS base branch'te mi, gerçek takımın write yetkisi var mı, PR draft mı? |
| `LIVE_CHECKS` group failed | Graph izni ve doğru grup Object ID; kayıt bulunamadı ile erişim reddini ayırın |

**“Parolayı GitHub'a nereye yazıyoruz?”** Bu OIDC yolunda client secret
yazmıyoruz. Tenant/client ID değişkendir; giriş kartı çalışma anında alınır.

**“production adlı gate neden dev workspace açıyor?”** GitHub environment
iş akışının onay sınırıdır. Fabric ortamını manifestin `environment` alanı
ve kapasitesi belirler; isimler kendiliğinden eşleşmez.

**“Admin ayarlarını göremiyorum.”** Beklenen durum olabilir; bu iş yöneticiye
aittir. Katılımcı rolünü yükseltmek yerine yöneticiden hazırlık isteyin.

## 13. Temizlik ve kaynaklar

Workshop bitince yöneticinin onayıyla kullanılmayan federated credential,
runner ve geçici grup üyeliklerini kaldırın; ortak kimlik/kapasiteyi silmeyin.
Schedule'ları durdurmak kapasite faturalamasını kendiliğinden durdurmaz.

- [GitHub OIDC: Azure](https://docs.github.com/en/actions/how-tos/secure-your-work/security-harden-deployments/oidc-in-azure)
- [OIDC subject biçimleri](https://docs.github.com/en/actions/reference/security/oidc)
- [GitHub environment korumaları](https://docs.github.com/en/actions/reference/workflows-and-actions/deployments-and-environments)
- [CODEOWNERS](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-code-owners)
- [Python setup action](https://github.com/actions/setup-python)
- [Fabric geliştirici ayarları](https://learn.microsoft.com/fabric/admin/service-admin-portal-developer)
- [Create Workspace izinleri](https://learn.microsoft.com/rest/api/fabric/core/workspaces/create-workspace)
- [Admin API service principal modeli](https://learn.microsoft.com/fabric/admin/enable-service-principal-admin-apis)
