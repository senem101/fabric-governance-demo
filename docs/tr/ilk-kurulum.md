# İlk kurulum: GitHub, VS Code ve Copilot'u sıfırdan kullanma

[Rehber dizini](README.md) | [Coach el kitabı](coach-el-kitabi.md)

Bu rehber **Windows + PowerShell + VS Code** içindir. İlk yerel prova için
Fabric yöneticisi olmanız gerekmez. Canlı bağlantı ve otomasyon kimliği daha
sonra [Challenge 00](../../challenges/00-setup/COACH-TR.md) içinde hazırlanır.

## 1. Önce altı kavram

| Kavram | Ne demek? |
|---|---|
| Git | Dosya değişikliklerinin geçmişini bilgisayarınızda tutan araç |
| GitHub | Git deposunun çevrimiçi tutulduğu, ekipçe incelendiği hizmet |
| Repository / repo | Dosyalar ve değişiklik geçmişinden oluşan proje |
| Clone | GitHub'daki depoyu bilgisayarınıza indirme; yerel Git geçmişi de gelir |
| Fork | GitHub üzerinde kaynak depodan kendi hesabınıza/kurumunuza kopya açma |
| VS Code | Bu dosyaları açacağınız editör; kendi başına Fabric değildir |

**GitHub Copilot** editörde açıklama ve kod önerisi veren yardımcıdır.
**GitHub Actions** GitHub'da komutları çalıştıran otomasyondur. İkisi aynı
şey değildir. **MCP**, Copilot'un harici araçları çağırmasını sağlar.

## 2. Hesapları ve görünürlüğü hazırlayın

1. Kurumun izin verdiği GitHub hesabıyla giriş yapın; gerekiyorsa
   organizasyon davetini ve SSO oturumunu tamamlayın.
2. Copilot erişiminizin bu hesapta tanımlı olduğunu kontrol edin.
   GitHub hesabınız olması sınırsız Copilot kullanımı sağladığı anlamına gelmez.
3. Fabric için Microsoft iş/okul hesabınızı hazırlayın. Bu, GitHub hesabınızdan
   ayrı bir oturumdur.
4. Coach ile müşteri verilerinin nerede tutulacağını belirleyin.
   **Public bir reponun fork'u da public olur; gizli müşteri deposu sanmayın.**
5. Sadece yapay verili kişisel öğrenme için public fork kullanılabilir.
   Müşteri çalışması için kurum yöneticisinin hazırladığı private/internal
   kopyayı kullanın. Onaylı repo yoksa yerel incelemeyle sınırlı kalın.

Public kaynak adresi:
<https://github.com/microsoft/frontier-fabric-governance-rvas>.

## 3. Bilgisayarınıza gereken araçlar

| Araç | Kurulum | Neden? |
|---|---|---|
| Git | [Git for Windows](https://git-scm.com/downloads/win); kurulumda PATH seçeneğini koruyun | Clone, commit ve push |
| VS Code | [Resmi indirme](https://code.visualstudio.com/download) | Dosya ve terminal |
| Python 3.12 veya üzeri | [Python Windows](https://www.python.org/downloads/windows/); PATH/launcher seçeneğini etkinleştirin | Manifest doğrulama |
| Azure CLI | [Windows kurulumu](https://learn.microsoft.com/cli/azure/install-azure-cli-windows) | Canlı yerel API işlemlerinde Microsoft oturumu |
| Node.js LTS | [Node.js](https://nodejs.org/en/download); yalnız seçilen araç gerektirirse | Site build, npm tabanlı araçlar; temel validator için şart değil |

Araçları yükledikten sonra VS Code'u kapatıp açın. **Terminal > New Terminal**
seçin; açılan pencerenin türünün PowerShell olduğunu kontrol edin.

```powershell
git --version
python --version
az version
```

Her komut bir sürüm göstermeli. Python komutu Microsoft Store açıyorsa
Python kurulumunu/PATH'i düzeltin veya `py -3.12 --version` ile launcher'ı
kontrol edin. Hata varken sonraki adıma geçmeyin.

## 4. Repo'yu bilgisayara indirin

**Bu çalışma zaten yerel bir repo klasöründeyse tekrar clone yapmayın.**
VS Code'da **File > Open Folder** ile mevcut klasörü açın.
Worktree, aynı Git deposuna bağlı ayrı bir çalışma klasörüdür; bu da yerel
kopyadır. Yeni bilgisayarda aşağıdaki yolu kullanın:

1. GitHub'da kurumunuzun kopyasını açın. **Code > Local > HTTPS** adresini
   kopyalayın. Müşteri lab'ında kaynak `microsoft/...` yerine kendi kurumunuzun
   adresini seçin.
2. VS Code'da `Ctrl+Shift+P` basın; **Git: Clone** yazıp seçin.
3. Adresi yapıştırın. Yerel hedef olarak örneğin `C:\Labs` seçin.
4. **Open** ile yeni klasörü açın. Workspace Trust sorusunda önce kaynak
   dosyaları ve `.vscode` ayarlarını inceleyin; kuruma ait güvenilir kopyayı
   bilinçli olarak güvenilir ilan edin.
5. Soldaki **Explorer** dosya listesinden `README.md` açın.
   `Ctrl+Shift+V` Markdown önizlemesini açar.

Yalnız public kaynağı incelemek için terminal alternatifi:

```powershell
New-Item -ItemType Directory -Path C:\Labs -Force
Set-Location C:\Labs
git clone https://github.com/microsoft/frontier-fabric-governance-rvas.git
Set-Location .\frontier-fabric-governance-rvas
code .
```

Bu komutlar aynı isimde mevcut klasör varsa tekrar çalıştırılmamalı.
ZIP indirmek Git geçmişi/remote bağlantısı kurmaz; PR eğitimi için clone tercih edin.

Terminalin repo kökünde olduğunu doğrulayın:

```powershell
Get-Location
git remote -v
git status
```

`origin` uzak deponun takma adıdır. `push` adresi hâlâ `microsoft/...` ise
kendi müşteri reponuza bağlı değilsiniz; değişiklikleri oraya göndermeye
çalışmayın. Coach'un verdiği müşteri kopyasını açın.

## 5. VS Code ekranını tanıyın

| Bölüm | Kullanım |
|---|---|
| Explorer | Dosya açma, yeni dosya ekleme |
| Source Control (`Ctrl+Shift+G`) | Değişiklikleri karşılaştırma, stage ve commit |
| Extensions (`Ctrl+Shift+X`) | Eklenti yükleme; yayıncıyı kontrol edin |
| Terminal | Komut çalıştırma; satırı yazıp Enter'a basın |
| Command Palette (`Ctrl+Shift+P`) | Adını bildiğiniz editör komutunu bulma |
| Chat | Copilot'a soru veya görev verme |

Dosyayı değiştirdikten sonra `Ctrl+S` ile kaydedin. Kaydedilmemiş içerik
terminaldeki validator'a gitmez. YAML dosyalarında girinti önemlidir:
**Tab yerine boşluk** kullanın; örnek dosyanın hizasını koruyun.

Repo'nun mevcut **F5 / Run and Debug** ayarı Azure Functions eklentisine
yöneliktir. Challenge çalıştırmak için F5'e basmanız gerekmez.

## 6. Python ortamı ve ilk güvenli çalışma

Repo kökündeki PowerShell terminalinde:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r .\scripts\requirements.txt
$env:PYTHONUTF8 = "1"
$env:LIVE_CHECKS = "false"
.\.venv\Scripts\python.exe .\scripts\validate.py
```

`.venv` bu proje için ayrı Python ortamıdır; başka projelerin paketlerini
değiştirmez. Aktivasyon gerekmez; komutlar Python'un tam yolunu kullanır.
Bu nedenle `Activate.ps1` için execution policy gevşetmeniz gerekmez.

**Beklenen:** İlk örnek manifest için `Overall: PASS` ve repo kökünde
`validation-report.md`. Örnekte gerçek olmayan ID'ler vardır; canlı kontrol
kapalı olduğundan PASS, kaynakların varlığı veya erişim yetkisi kanıtı değildir.

Hiç dosya değiştirmeden planı görmek için:

```powershell
$env:DRY_RUN = "true"
.\.venv\Scripts\python.exe .\scripts\provision.py
Remove-Item Env:\DRY_RUN
```

**Beklenen:** `[dry-run] would ...` satırları. Fabric kaynağı oluşturulmaz.
Bu seçenek bir API/izin testi de yapmaz. **Dry-run olmadan provisioner'ı
yerelde çalıştırmayın**; oturum açmış kişisel kimliğinizle yazabilir.

`DRY_RUN` yalnız provisioner tarafından kullanılır. `LIVE_CHECKS` ise
validator'ın grup varlığı kontrolünü etkiler. İkisi birbirinin yerine geçmez.

## 7. GitHub Copilot kurulumu

1. VS Code'da Copilot simgesinden **Use AI Features / Sign in** seçin.
   Alternatif: komut paletinde **GitHub Copilot: Sign in**.
2. Tarayıcıda kurumsal Copilot erişimi olan GitHub hesabınızı seçin.
   Yanlış hesapta lisans varsa kurum yöneticisiyle düzeltin.
3. Extensions ekranında GitHub'ın yayınladığı Copilot/Chat bileşenlerinin
   etkin olduğunu kontrol edin. Kullanıcı arayüzü sürüme göre değişebilir.
4. `Ctrl+Alt+I` ile Chat açın. İlk denemede açıklama modunu kullanın;
   dosya değiştirmek/araç çağırmak için **Agent** seçildiğinde izinleri inceleyin.
5. `schemas\workspace.schema.json` ve `rules\policy.yaml` dosyalarını Chat'e
   **Add Context / dosya ekleme** ile ekleyin.

İlk istem:

```text
Bu iki dosyayı hiç GitHub veya Fabric bilmeyen birine Türkçe açıkla.
Şema ile policy arasındaki farkı ve geçerli workspace adının yapısını göster.
Dosya değiştirme, terminal çalıştırma, bulut kaynağına bağlanma.
```

**Beklenen:** Dosyalardaki altı parçalı isim yapısına dayanan açıklama.
Copilot'un ürettiği örneği yine şemayla karşılaştırın.
Özel müşteri verisi, token, parola veya gizli dosyayı Chat'e eklemeyin.
Kuruluşunuzun Copilot veri kullanım politikası esas alınır.

## 8. MCP: Copilot'u Fabric'e bağlayın

MCP sunucusu kurmak ona bütün izinleri vermek değildir. Chat'teki araç
çağrılarını inceleyin; **bütün araçlara otomatik izin vermeyin**.

### 8.1 Uzak Fabric Core MCP - gerçek ortamı okuma

1. Fabric'te eğitim workspace'ine erişiminiz olduğunu portalda kontrol edin.
2. VS Code komut paleti > **MCP: Add Server > HTTP**.
3. Adres: `https://api.fabric.microsoft.com/v1/mcp/core`.
4. Ad: `fabric`. Kendi profiliniz için **User/Global** kapsamını seçebilirsiniz.
   Workspace kapsamı seçerseniz `.vscode\mcp.json` oluşur; değişikliği inceleyin.
5. Tarayıcıda **müşterinin doğru Entra tenant'ındaki** hesabınızla oturum açın.
6. **MCP: List Servers** ile sunucunun çalıştığını kontrol edin.
7. Chat'te **Configure Tools** üzerinden yalnız gerekli okuma araçlarını seçin.

```text
Fabric Core MCP üzerinden yalnız erişebildiğim workspace'leri listele.
Hiçbir kaynak veya yetki oluşturma, değiştirme ya da silme.
Sonucun hangi bağlı kullanıcı kapsamını temsil ettiğini belirt.
```

Araç çağrısı ve gerçek sonuç görünmeli; yalnız modelin tahmini liste yeterli
değildir. Boş liste yanlış tenant veya eksik erişim olabilir. Core MCP,
bu rehber hazırlanırken **preview** durumundadır; kurumsal kullanıma uygunluğu
yöneticiyle kontrol edin.

### 8.2 Yerel Fabric MCP - API belgeleri ve geliştirme yardımı

1. Extensions ekranından resmi belgede bağlantısı verilen **Fabric MCP Server**
   eklentisini açın: `fabric.vscode-fabric-mcp-server`.
2. Yayıncıyı/kurum onayını kontrol edip kurun. Sadece genel Microsoft Fabric
   eklentisinin bulunmasını MCP kurulmuş saymayın.
3. **MCP: List Servers** içinden sunucuyu başlatın.
4. Chat'teki araç listesinden dokümantasyon araçlarını etkinleştirin.
5. “Fabric Lakehouse için API işlemlerini belgelerden göster; canlı işlem yapma”
   isteğini verin.

Dokümantasyon araçları Fabric oturumu olmadan kullanılabilir. **Yerel**
sunucunun OneLake ve diğer canlı araçları ise veriye bağlanabilir; “yerel”
kelimesi bütün işlemler çevrimdışı demek değildir.

Yerel canlı okuma gerekiyorsa ayrı PowerShell terminalinde şu şablonu,
tenant ID'sini değiştirdikten sonra kullanın:

```powershell
az login --tenant "<TENANT-ID>" --allow-no-subscriptions
az account show --query "{tenant:tenantId,user:user.name}" --output table
```

Çıktıyı müşterinin önünde paylaşmadan önce kişisel bilgileri gizleyin.
Token üretip Chat'e veya bir dosyaya yapıştırmayın. Yerel Azure CLI oturumu,
Core MCP tarayıcı oturumu ve Actions SPN oturumu birbirinden ayrıdır.

## 9. Skills: Copilot'a uzman talimatı ekleyin

Skill, genellikle bir `SKILL.md` ve yardımcı dosyalardan oluşur. MCP **araç**,
skill ise o işi yapma **talimatıdır**. Skill yüklemek Fabric'te kaynak açmaz.

Başlangıç için güncel [Skills for Fabric kataloğunda](https://github.com/microsoft/skills-for-fabric)
`spark-cli` veya `e2e-medallion-architecture` gibi ihtiyacınız olan skill'i
kontrol edin. Eski belgelerdeki `spark-authoring-cli` gibi adların halen
mevcut olduğunu varsaymayın.

**VS Code için tek skill kurma yolu (kurum onayıyla):**

1. Kataloğun README ve skill talimatlarını okuyun; çalıştıracağı komutları inceleyin.
2. Repo kökündeki terminalde mevcut `.venv` içine APM aracını kurun:

```powershell
.\.venv\Scripts\python.exe -m pip install apm-cli
.\.venv\Scripts\apm.exe install microsoft/skills-for-fabric --skill spark-cli --target copilot --only apm
```

3. `--only apm` skill içeriğini kurar; tüm MCP sunucularını kendiliğinden
   ekletmez. Az önce kurduğunuz MCP bağlantıları ayrı kalır.
4. Source Control'da yeni dosyaları inceleyin. `.agents\skills\`, APM manifest/
   lock dosyaları ve bağımlılıklar oluşabilir; anlamadan hepsini commit etmeyin.
   Katalogdaki sürümü/commit'i workshop boyunca sabit tutun.
5. Chat'e `/skills` yazın veya **Chat: Open Customizations > Skills** bölümünü
   açın. Kurulu skill'in görüldüğünü kontrol edin; gerekirse pencereyi yeniden yükleyin.
6. Skill'i seçip “Yalnızca örnek notebook taslağı öner, çalıştırma ve dağıtma”
   isteğiyle deneyin. Çıktıyı okumadan çalıştırmayın.

**İsteğe bağlı CLI:** GitHub Copilot CLI, VS Code'dan ayrı bir uygulamadır;
bu eğitimi tamamlamak için şart değildir. Kuruluysa Copilot'un etkileşimli
ekranında, PowerShell'e değil, şu komutlar girilir:

```text
/plugin marketplace add microsoft/skills-for-fabric
/plugin install fabric-skills@fabric-collection
```

Bunlar tek skill yerine paket yükler. CLI eklenti/MCP ayarlarının VS Code'a
otomatik taşındığını varsaymayın. Eski `gh copilot mcp add` veya
`copilot skill install` örnekleri yerine kullandığınız istemcinin güncel
belgesini izleyin.

## 10. Bir değişikliği GitHub'da incelemeye açma

Bu adımları **müşterinin kendi reposunda** uygulayın; ilk yerel okuma sırasında
push veya PR açmanız gerekmez.

| İşlem | Anlamı |
|---|---|
| Branch | `main`i değiştirmeden çalıştığınız ayrı dal |
| Stage | Bir sonraki kayıt için dosya seçme |
| Commit | Seçili değişiklikleri açıklamasıyla yerel geçmişe kaydetme |
| Push | Yerel commit'i GitHub'a gönderme |
| Pull request (PR) | “Bu değişikliği ana dala alalım mı?” inceleme isteği |
| Merge | Onaylı PR'ı ana dala birleştirme |

1. Temiz bir kopyada VS Code sol alttaki branch adına tıklayıp
   **Create new branch** seçin; örneğin `lab/workspace-istegi`.
   Hazır bir workshop branch'indeyseniz coach'un yönlendirmesini izleyin.
2. Challenge'ın belirttiği dosyayı düzenleyin; kaydedin ve doğrulayın.
3. Source Control'da dosyaya tıklayın: solda eski, sağda yeni içerik görünür.
   Yalnız beklediğiniz değişiklikleri dosyanın yanındaki **+** ile stage edin.
4. Açıklayıcı mesaj yazın ve **Commit** seçin.
   Git kimlik istiyorsa, yalnız bu repoda `git config user.name "Ad Soyad"`
   ve kurumunuzun onayladığı e-posta ile `git config user.email "..."` kullanın.
5. **Publish Branch / Push** seçin. Bu işlem `main`e merge etmez.
6. GitHub'da **Compare & pull request** açın.
   **Base repository** kendi kurumunuzun reposu; **base branch** `main`;
   **compare** sizin branch'iniz olmalı. Fork'larda yanlışlıkla Microsoft
   kaynak reposuna PR açılmadığını özellikle kontrol edin.
7. Açıklamaya neden, kapsam, test sonucu ve geri dönüş yaklaşımını yazın.
8. **Checks** otomasyon sonuçlarını, **Files changed** değişikliği gösterir.
   **Reviewers** alanından gerçek bir ekip arkadaşını seçin.
9. Reviewer **Review changes > Approve** seçer. Yazar kendi PR'ının gerekli
   onayını veremez. Kontroller tamamlanınca yetkili kişi merge eder.
10. Sonrasında **Actions** sekmesinden workflow run'ını açın; job ve step
    satırları yürütülen komutları gösterir. `production` onayı PR onayından
    ayrı, ikinci bir kapıdır.

Gerekli status check görünmüyorsa workflow'un dosya yolu filtresine bakın.
Sadece Markdown değiştiren PR'da `validate` hiç tetiklenmeyebilir; required
check bekliyorsa korumayı rastgele kaldırmak yerine repo yöneticisiyle
workflow/ruleset kapsamını uyumlu hale getirin.

## 11. İlk gün sorun giderme

| Belirti | Kontrol / çözüm |
|---|---|
| `git/python/az is not recognized` | Aracı yükleyin; PATH ve yeni terminal oturumunu kontrol edin |
| `No module named yaml` | Pip ve çalıştırma için aynı `.venv\Scripts\python.exe` yolunu kullanın |
| YAML parse error | Girinti, iki nokta ve tırnakları örnekle karşılaştırın |
| Copilot açılmıyor | Doğru GitHub hesabı, plan/kota ve kurum politikasını kontrol edin |
| MCP aracı görünmüyor | Sunucu durumu, Agent modu, Configure Tools ve kurum MCP izni |
| `401` | Oturum/token sorunu; doğru hesapla yeniden kimlik doğrulayın |
| `403` | Oturum var ama izin yok; tenant ayarı ve hedef kaynak rolünü yöneticiyle kontrol edin |
| `Repository not found` | URL, GitHub hesabı, davet ve SSO yetkisini kontrol edin |
| Push reddedildi | `main` yerine kendi branch'inizi gönderin; korumayı kaldırmayın |
| Commit'te bilinmeyen çok dosya | Stage işlemini durdurun; `.venv`, token ve müşteri verisini göndermeyin |

Hazır olma ölçütü: Dosyayı bulabiliyor, açıklayabiliyor, yerel doğrulamayı
çalıştırabiliyor ve GitHub ile Fabric oturumlarının farkını anlatabiliyorsunuz.

## Kaynaklar

- [GitHub Hello World: branch, commit ve PR](https://docs.github.com/en/get-started/using-github/hello-world)
- [VS Code Copilot kurulumu](https://code.visualstudio.com/docs/setup/copilot)
- [VS Code MCP yönetimi](https://code.visualstudio.com/docs/agent-customization/mcp-servers)
- [VS Code Agent Skills](https://code.visualstudio.com/docs/agent-customization/agent-skills)
- [Fabric Core MCP kurulumu](https://learn.microsoft.com/rest/api/fabric/articles/mcp-servers/core-remote/get-started-core)
- [Fabric local MCP kurulumu](https://learn.microsoft.com/rest/api/fabric/articles/mcp-servers/pro-dev-local/get-started-local)
- [Skills for Fabric güncel kurulum](https://github.com/microsoft/skills-for-fabric)
