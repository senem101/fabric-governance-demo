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
| `LIVE_CHECKS` | İlk provada `false` |
| `DRY_RUN` | İlk provada **`true`**; canlıya bilinçli geçişte `false` |

Eski rehberlerdeki `DEFAULT_OWNER_UPN` mevcut workflow/script tarafından
kullanılmıyor. Bu değişkeni koyarak örnek owner'ın değişmesini beklemeyin.

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
Bu nedenle ilk eğitimde `LIVE_CHECKS=false` tutun; müşteri kopyasındaki
`validate` workflow'unda Azure login adımını kaldırın ve `id-token: write`
iznini kaldırın. PR canlı kontrolü gerekiyorsa ayrı, okuma amaçlı kimlik,
ayrı değişkenler ve güvenilir PR politikası mühendislik ekibince hazırlanmalı.
Hazır tek-SPN tasarımını production güvenlik modeli diye sunmayın.

## 9. Runner: komutları hangi bilgisayar çalıştıracak?

Üç hazır workflow **`runs-on: [self-hosted, fabric-gov]`** kullanır; Python
kurulumu Linux biçimindedir. Yeni fork'ta böyle bir runner yoksa job bekler.

**Başlangıç için**, kurum politikasının izin verdiği GitHub-hosted Linux runner:

1. Kendi müşteri kopyanızda bir hazırlık branch'i açın.
2. `.github\workflows\validate.yml`, `provision.yml`, `drift.yml` dosyalarının
   her birinde `runs-on: [self-hosted, fabric-gov]` satırını
   `runs-on: ubuntu-latest` yapın. Diğer action sürümlerini değiştirmeyin.
3. Her dosyada **Setup Python venv** adımından önce kurumun onayladığı
   `actions/setup-python` sürümünü ekleyip Python `3.12` seçin; action'ı
   repo politikasına göre gözden geçirilmiş tam commit SHA'sına sabitleyin.
   Aşağıdaki örnek, rehber hazırlanırken `v6` için doğrulanan SHA'yı kullanır;
   müşterinizin izinli action listesine uygunluğunu ayrıca kontrol edin.
4. `validate` komutundan `--changed-only` seçeneğini kaldırıp
   `python scripts/validate.py` kullanın. Böylece policy/schema değişince
   bütün mevcut manifestler tekrar sınanır.
5. `provision` içine, kaynak yazma adımından önce aynı tam doğrulama komutunu
   ekleyin. Mevcut provisioner kendi başına schema/policy kontrolü yapmaz.
6. İlk PR kontrolünü Azure kimliği olmadan çalıştırmak için 8. adımdaki
   validate login/OIDC düzenlemesini uygulayın.
7. Hazırlık PR'ını repo yöneticisine inceletip birleştirin.
   `DRY_RUN=true` ve environment gate önceden hazır olmalı.

`steps:` altında diğer `- name:` satırlarıyla aynı hizaya eklenecek Python adımı:

```yaml
      - name: Set up Python
        uses: actions/setup-python@ece7cb06caefa5fff74198d8649806c4678c61a1
        with:
          python-version: '3.12'
```

`provision.yml` içinde **Provision workspaces** adımının hemen önüne eklenecek kontrol:

```yaml
      - name: Validate all workspace manifests
        env:
          LIVE_CHECKS: 'false'
        run: python scripts/validate.py
```

İkinci örnek dosya/policy kontrolüdür, canlı grup yetki testi değildir.
Bu bloklar tam workflow dosyası değildir; mevcut `on`, `permissions`,
checkout, Azure login ve environment bölümlerinin yerine yapıştırmayın.

Bunlar **müşteri kopyasında yapılacak hazırlık değişiklikleridir**; bu Türkçe
rehberin eklenmesi orijinal workflow'ları değiştirmez.
Hosted runner dakikaları/billing ve ağ erişimi kurum tarafından onaylanmalıdır.

Kurum self-hosted istiyorsa yönetici **Settings > Actions > Runners > New
self-hosted runner** yolundan **ayrı Linux** makine kaydeder; `fabric-gov`
etiketi, Python 3.12+, venv/pip, Git ve Azure CLI hazır olmalıdır.
Katılımcının günlük iş bilgisayarını veya ortak production sunucusunu runner
yapmayın. Güvenilmeyen public fork PR'larını self-hosted runner'da çalıştırmayın.

## 10. Review ve branch koruması

1. `.github\CODEOWNERS` içindeki `@your-org/...` yer tutucularını gerçek,
   repo'da write yetkisi olan kullanıcı/takımla değiştirin.
2. Eski `/workspaces/prd-*.yaml` üretim deseni güncel altı parçalı adları
   yakalamaz. Gerçek ihtiyaca göre örneğin `/workspaces/*-prd-*.yaml`
   desenini ve sorumlusunu gözden geçirin.
3. GitHub **Settings > Rules > Rulesets** veya **Branches > Branch protection**
   üzerinden `main` için PR, en az bir review ve CODEOWNERS onayı isteyin.
4. `validate` ilk kez çalıştıktan sonra görünen gerçek check adını required
   check olarak seçin. Sadece doküman PR'larında path filtresi yüzünden
   çalışmayabileceğini repo yöneticisiyle çözün.
5. Force push ve silmeyi engelleyin; yetkili reviewer'ın PR merge edebildiğini
   doğrulayın. “Sadece Actions push etsin” diye insan onaylı merge'i yanlışlıkla
   kullanılamaz hale getirmeyin.
6. **Actions** sekmesinde gerekiyorsa workflow'ları etkinleştirin.
   `drift` zamanlamasını gerçek kimlik/izin hazır olmadan açmayın.
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
| Kendi repo'nuzda manifest PR'ı | Validate raporu ve doğru reviewer |
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
| Azure login hata verdi ama validate yeşil | Mevcut workflow'da login `continue-on-error`; canlı kimlik doğrulanmış sayılmaz |
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
