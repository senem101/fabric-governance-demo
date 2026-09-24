# Challenge 04 — Erişim ve rol yaşam döngüsü: coach rehberi

[Türkçe başlangıç](../../docs/tr/README.md) · [İlk kurulum](../../docs/tr/ilk-kurulum.md) · [Coach el kitabı](../../docs/tr/coach-el-kitabi.md) · [Asıl challenge](challenge.md)

**Amaç:** Müşteriye “kim, neden, ne kadar süreyle erişiyor ve bunu kim geri alacak?” sorularını öğretebilmek.
**Tahmini süre:** 20 dakika kavramlar + 30 dakika mevcut kontroller + 45–60 dakika erişim modeli/mock test + 20 dakika değerlendirme.
Tam otomatik erişim sonlandırma bu repoda hazır değildir; bu rehber yetki verme/geri alma işlemi yaptırmaz.

## 1. Müşteriye 60 saniyede anlatın

> “Bir ofisin kapı kartını verirken görevi ve bitiş tarihini bilmek isteriz.
> Fabric'te rol, kişinin çalışma alanında yapabileceklerini belirler.
> İsimleri tek tek eklemek yerine kurumun yönettiği gruplara görev vermek daha sürdürülebilirdir.
> Geçici erişimi bir dosyada gerekçesi ve süresiyle kaydedeceğiz.
> GitHub'daki pull request bu talebin inceleme kuyruğu; VS Code talep formunu düzenlediğimiz araçtır.
> Copilot taslak üretir; müşteri adına erişim kararı vermez.
> Bitiş tarihini yazmak kapı kartını kapatmaz: bunun için çalışan ve doğrulanmış bir iptal mekanizması gerekir.”

**Dört rol:** Admin yönetir; Member geniş işbirliği yetkileri taşır; Contributor içerik geliştirir; Viewer desteklenen içeriği okur.
Bunlar basitleştirilmiş açıklamalardır; item, SQL, OneLake ve grup üyeliklerinden gelen ek izinler ayrıca değerlendirilir.

## 2. Mevcut kodun gerçek sınırı

| Özellik | Bugün |
|---|---|
| Workspace sahipleri | `owners`: en az iki kayıt, en az bir Group, en az bir Admin |
| Üretim ek kontrolü | `environment: prd` için en az iki Group ve Confidential/Highly Confidential |
| User Admin yasağı | **Yok**; iki Group koşulu sağlanırsa User Admin ayrıca bulunabilir |
| Süre/gerekçe | Workspace `owners` şeması `expiresOn`, `createdOn`, `justification` kabul etmez |
| Provisioner | Eksik `(principal ID, role)` çiftlerini eklemeyi dener |
| Rol değiştirme/kaldırma | **Yok**; aynı kişiye başka rol eklemeyi denemek doğru bir update değildir |
| Erişim drift'i | **Yok**; mevcut drift ad/açıklama farkıyla sınırlı |
| Review/JIT | `access-review.yml`, `access-jit.yml`, access şeması ve okuyucu **OLUŞTURULACAK** |

“İki owner” ile “iki Admin” aynı değildir.
`allowRemovals: true` bugün hiçbir şey etkinleştirmez; workspace manifestine eklenirse şema reddeder.
Asıl challenge'ın otomatik review/remediation PR çıktıları hedeflerdir, bugün çalışan özellikler değildir.

## 3. Dersten önce: görev ve izin kontrolü

- [ ] [İlk kurulum](../../docs/tr/ilk-kurulum.md), eğitim fork'u, VS Code, Git, Python ve Copilot hazır.
- [ ] Coach ile müşteri güvenlik sorumlusu “yalnız sentetik kullanıcılar/kimlikler” sınırını onayladı.
- [ ] Yerel alıştırma için bulut lisansı/tenant yönetici rolü gerekmediği açıklandı.
- [ ] Canlı gözlem yalnız müşteri admin onaylı sandbox'ta ve doğru hesapla yapılacak.
- [ ] Workspace rol listesini REST ile okumak için Member veya daha yüksek rol gerektiği biliniyor.
- [ ] Rol ekleme API'sinde Member yalnız Member veya daha düşük rol ekleyebilir; Admin ataması ayrı yetki gerektirir.
- [ ] Rol silme için workspace Admin gerekir; API son Admin'in silinmesini engeller, fakat buna tek güvence olarak dayanılmaz.
- [ ] Graph ile kullanıcı/grup çözümü gerekiyorsa yalnız seçilen okuma endpoint'ine uygun izin ve admin consent değerlendirildi.
- [ ] Graph MCP zorunlu değil; kurulu katalog/kurum politikası doğrulanmadan bağlantı veya tenant genel izni eklenmiyor.
- [ ] Canlı içerik kullanılacaksa uygun Fabric kapasitesi/lisans var; rol ataması lisans yerine geçmez.
- [ ] İki bağımsız yönetici erişim yolu ve müşterinin acil durum prosedürü belli; son erişim yolu lab'da kaldırılmayacak.

Entra uygulamasının client/application ID'si ile service principal object ID'sini karıştırmayın.
Object ID parola değildir, fakat kullanıcı/rol dökümü kurumsal bilgi içerir; herkese açık PR'a taşımayın.
Grup sahipliği ve üyelik yönetimi Fabric rol dosyasından ayrı bir müşteriye ait süreçtir.

## 4. Adım adım mevcut davranışı görün

1. **GitHub → eğitim fork'u** adresini gösterin. “Bu derste kimseye gerçek erişim vermiyoruz” sınırını söyleyin.
2. **VS Code → File → Open Folder** ile kopyayı açın; sol alt dal adından `egitim/access-lab01` dalını oluşturun.
3. **Ctrl+P → `schemas/workspace.schema.json`** açın; `owners` alanındaki kabul edilen anahtarları okuyun.
4. **Ctrl+P → `scripts/provision.py`** açın; `existing_keys` ve `add_role_assignment` satırlarını gösterin.
   UPN çözümlenemezse atlanabildiğini, rol ekleme hatasının warning olabildiğini açıklayın.
   Dolayısıyla “workflow yeşil” erişim listesinin tam uygulandığı anlamına gelmez.
5. **Terminal → New Terminal → PowerShell** ile mevcut olmayan parçaları kontrol edin:

   ```powershell
   Get-Location
   git status --short
   Test-Path .\schemas\access.schema.json
   Test-Path .\.github\workflows\access-review.yml
   Test-Path .\.github\workflows\access-jit.yml
   $env:LIVE_CHECKS = 'false'
   .\.venv\Scripts\python.exe .\scripts\validate.py .\workspaces\pt-nlyt-sample-ndf-dev-hello1.yaml
   $LASTEXITCODE
   ```

6. Beklenen: üç `False`, workspace için `PASS` ve çıkış kodu `0`.
   Örnek iki owner içerir ama yalnız biri Admin'dir; doğrulamanın iki Admin zorlamadığını birlikte gözlemleyin.
   Kimlikler eğitim yer tutucularıdır; yerel `validation-report.md` gerçek Entra varlığını doğrulamaz.

## 5. Güvenli negatif test: mevcut boşluğu ispatlayın

Bu PowerShell bloğu mevcut motoru bellekte çalıştırır; dosyaları veya tenant'ı değiştirmez.
Yerel sanal ortam yoksa ortak kuruluma dönün; `provision.py` veya erişim değiştiren MCP aracı çalıştırmayın.

```powershell
$env:LIVE_CHECKS = 'false'
@'
import copy
import sys
from pathlib import Path
sys.path.insert(0, str(Path("scripts").resolve()))
from rules_engine import load_yaml, validate_manifest
base = load_yaml(Path("workspaces") / "pt-nlyt-sample-ndf-dev-hello1.yaml")
base.update(name="pt-nlyt-sales-ndf-dev-lab01", subject="sales", suffix="lab01")
result = validate_manifest(base)
print("iki-owner-tek-admin", result.passed)
assert result.passed
expiry = copy.deepcopy(base)
expiry["owners"][1]["expiresOn"] = "2030-01-02T09:00:00Z"
result = validate_manifest(expiry)
print("owners-icinde-expiry", [f.rule_id for f in result.blocking])
assert any(f.rule_id == "schema" for f in result.blocking)
prod = copy.deepcopy(base)
prod.update(name="pt-nlyt-sales-ndf-prd-lab01", environment="prd", sensitivityLabel="Confidential")
prod["owners"] = [
    {"principalType": "Group", "identifier": "44444444-4444-4444-4444-444444444444", "role": "Admin"},
    {"principalType": "Group", "identifier": "55555555-5555-5555-5555-555555555555", "role": "Member"},
    {"principalType": "User", "identifier": "66666666-6666-6666-6666-666666666666", "role": "Admin"},
]
result = validate_manifest(prod)
print("prd-user-admin-mevcut-kural-boslugu", result.passed)
assert result.passed
'@ | .\.venv\Scripts\python.exe -
```

Beklenen: `True`, `['schema']`, `True`.
Son `True` bir öneri değildir: **production User Admin yasağı henüz uygulanmadı** demektir.
Katılımcıdan “neden tarihi mevcut owners'a eklemek yeterli değil?” sorusunu kendi sözleriyle yanıtlamasını isteyin.

## 6. Erişim dosyasını tasarlayın — henüz çalışan entegrasyon değil

1. VS Code Explorer'da `access/` klasörünü ve `pt-nlyt-sales-ndf-dev-lab01.yaml` dosyasını oluşturun.
   Bu yol **OLUŞTURULACAK alıştırma çıktısıdır**; bugünkü script'ler bu dizini okumaz.
2. Aşağıdaki önerilen sözleşmeyi yazın. Bütün ID'ler sahtedir; hiçbirini canlı istekte kullanmayın.
   Tarihler sabit saatli test içindir; canlı erişim talebi veya bugün geçerli süre anlamına gelmez.

   ```yaml
   workspace: pt-nlyt-sales-ndf-dev-lab01
   allowRemovals: false
   bindings:
     - principalType: Group
       identifier: "44444444-4444-4444-4444-444444444444"
       role: Admin
       expiresOn: null
     - principalType: Group
       identifier: "55555555-5555-5555-5555-555555555555"
       role: Admin
       expiresOn: null
     - principalType: User
       identifier: "66666666-6666-6666-6666-666666666666"
       role: Contributor
       createdOn: "2030-01-01T09:00:00Z"
       expiresOn: "2030-01-02T09:00:00Z"
       justification: "Yalnizca sentetik veriyle bir gunluk egitim gorevi icin gecici erisim."
   ```

3. `schemas/access.schema.json` **OLUŞTURULACAK**; `expiresOn` için UTC tarih-saat biçimi seçin.
   Sadece gün içeren tarih, 24 saatlik JIT süresini kesin ifade edemez.
   `createdOn`, kontrol anı ve saat dilimini tanımlayın; “en fazla 90 gün” hangi başlangıca göre ölçülüyor açık olsun.
4. İki **farklı** Admin kimliği kontrolü tasarlayın; aynı grubu iki kez yazmak sayıyı artırmamalı.
   Group için `null` kurumsal onayla mümkün olabilir; User için süre ve ≥30 karakter gerekçe zorunlu olsun.
5. `prd` kararını workspace manifestinin `environment` alanından okuyun.
   Ad `pt-nlyt-sales-ndf-prd-lab01` biçimindedir; adı `prd-` ile başlayan dosya aramak bu modeli kaçırır.
6. `owners` ve `access/bindings` için tek kaynak kararı verin: bootstrap yöneticileri hangisinde, sürekli roller hangisinde?
   İki farklı uygulayıcı birbirinin kaldırdığını tekrar eklememeli; geçiş/backward compatibility testi gerekir.

## 7. Copilot ile test ve reconciliation planı

**Copilot Chat** içinde şu isteği kullanın; çıktıyı uygulamadan önce müşteri reviewer'ıyla okuyun:

```text
Sadece yerel tasarım/diff üret. Mevcut workspace owners şeması ve provision.py
ile yeni access modeli arasındaki boşlukları açıkla. access şeması, saf validator,
mock reconciliation ve sabit UTC saatli testleri öner. Önce planı göster;
incelemem olmadan dosya değişikliği, terminal çalıştırma, commit/push/merge yapma.
Tenant'a bağlanma, kullanıcı/grup ekleme, rol atama/kaldırma, PIM aktivasyonu
veya Graph mutasyonu yapma. OLMAYAN script/workflow'ları OLUSTURULACAK diye işaretle.
Son iki güvenli Admin yolunu ve otomasyon kimliğini koru; eksik canlı envanterde
removal planlama. İzin iptalini yalnız PR açılmış olmasına dayanarak başarılı sayma.
```

1. Validator **OLUŞTURULACAK**: referans workspace, unique binding, iki Admin, User gerekçe/süre ve production yasağı.
   Mantığı paylaşılan `rules_engine.py` kullanımıyla tutarlı tasarlayın; yalnız policy'ye rule adı eklemek çalıştırmaz.
2. Reconciler **OLUŞTURULACAK**: önce `add/update/remove/no-op` planı üretir; mock API dışında işlem yapmaz.
   Güncelleme/silmede API'nin role assignment ID'si ile principal ID'sini birbirinin yerine kullanmayın.
3. Mock actual listesine manifestte olmayan tek sahte Viewer ekleyin.
   `allowRemovals=false` iken beklenen: “drift bildir, kaldırma”.
4. `allowRemovals=true` dahi tek başına izin değildir: exact removal listesi, ayrı onay, yönetilen kapsam ve Admin koruması gerekir.
   Eksik sayfalama, `403`, yanlış tenant veya bilinmeyen kimlik durumunda yıkıcı planı durdurun.
5. Test saatini `2030-01-01T09:00:00Z` olarak sabitleyin; 23:59 saat sonra geçerli, tam 24 saat sonra süresi dolmuş sayılmasını tasarlayın.
   Bilgisayar/tenant saatini değiştirmeyin. Bu saate bağlı test altyapısı **OLUŞTURULACAK**, mevcut script seçeneği değildir.
6. Bir doğrudan rolün kaldırılması bütün erişimin bittiği anlamına gelmez.
   Kullanıcı başka bir grup, item paylaşımı veya SQL izniyle erişebilir; etkili erişim ayrı kanıt ister.

## 8. Quarterly review, JIT ve GitHub kapıları

1. **Source Control → dosya farkı** ekranında müşteriyle dosyaları inceleyin; yalnız lab değişikliklerini stage/commit edin.
   Eğitim dalını yayınlayın → **GitHub → Pull requests → New pull request**; base repo eğitim fork'u olmalı.
2. Mevcut `validate.yml` `access/**` yolunu izlemez; `--changed-only` access dosyasını bulmaz.
   Access manifesti/şeması/validator/policy testlerini kapsayan path filtreleri ve gerçek validation adımı **OLUŞTURULACAK**.
3. Mevcut `provision.yml` access klasörünü veya expiry işlemini kullanmaz.
   Uygulama, environment onayı ve ayrı live verification eklenmeden merge “rol güncellendi” sayılmaz.
4. `.github/workflows/access-review.yml` **OLUŞTURULACAK**:
   asıl challenge'daki `0 9 1 */3 *`, Ocak/Nisan/Temmuz/Ekim'in ilk günü 09:00 UTC'dir.
   Yaklaşan 30 gündeki sona ermeleri inceleme önerisine dönüştürür; kendiliğinden süre uzatmaz.
5. Reviewer ve GitHub `contents/pull-requests` izinleri, Actions'ın PR açma ayarı ve tekrarlı PR önleme kontrolü tasarlanmalı.
   CODEOWNERS request'i gerçek branch protection/required review olmadan zorunlu onay değildir.
6. `.github/PULL_REQUEST_TEMPLATE/jit-break-glass.md` ve `.github/workflows/access-jit.yml` **OLUŞTURULACAK**.
   `workflow_dispatch` gelecekte kendiliğinden çalışacak zamanlayıcı değildir; expiry taraması/scheduler ve retry tasarımı gerekir.
7. **Follow-up PR açmak erişimi geri almaz.** PR onay/merge/apply bekliyorsa yetki devam eder.
   Kesin 24 saat sınırı isteniyorsa müşterinin önceden onayladığı zaman sınırlı erişim sistemi gerekir; lab otomasyonu bunu garanti etmez.
8. Acil durum sürecini normal PR kuyruğuna bağımlı hale getirmeyin; kurumsal break-glass/PIM politikası ve lisansı ayrıca değerlendirilir.
9. Workflow'lar bugün `[self-hosted, fabric-gov]` ile Linux `.venv/bin` bekler; canonical Actions hazır çalışan servis değildir.
   Runner, OIDC ve güvenli enable adımları [ortak kurulumdadır](../../docs/tr/ilk-kurulum.md); dersi kurtarmak için tenant admin izni vermeyin.

## 9. Canlı ortam mevcutsa: yalnız rol listesini okuyun

1. Müşteri admin onayıyla **Fabric → Workspaces → sandbox → Manage access** açın.
   Rol listesini okuyun; **Add**, rol seçicisi veya **Remove** işlemi yapmayın.
2. Gerekirse yetkili müşteri yöneticisi **Entra → Groups → ilgili grubun Overview** ekranında Object ID'yi doğrulasın.
   Grup üyelerini değiştirmeyin; gerçek kişi listesini eğitim kaydına veya açık PR'a eklemeyin.
3. MCP katalog/bağlantısı varsa şu salt okunur doğrulama isteğini verin:

   ```text
   Sadece müşteri onaylı pt-nlyt-sales-ndf-dev-lab01 sandbox'ının rol atamalarını oku.
   Önce workspace kimliğini ve sorgu hesabını doğrula. Bütün sayfaları okuyup
   Group/User/ServicePrincipal ve role göre sayıları göster; kişisel isimleri maskele.
   Erişim ekleme/değiştirme/silme, grup üyeliği düzenleme veya yetki yükseltme yapma.
   access dosyası henüz taslaksa bunu belirt. Workspace rol listesini tüm tenant
   veya etkili erişim envanteri diye sunma. Okuma hatasında dur; boş listeyi uyum
   sayma. Zaman damgası, kapsam ve doğrulanamayan alanları bildir.
   ```

## 10. Kabul, hatalar, yedek demo ve temizlik

| Test | Beklenen sonuç |
|---|---|
| Bugünkü üç bellek testi | PASS, schema BLOCK, production User Admin boşluğu için PASS |
| Yeni User binding: süre/gerekçe yok | Geliştirilecek validator bloklar; bugün bu kural varmış gibi raporlanmaz |
| İki aynı Admin kimliği veya tek Admin | Yeni validator unique Admin kontrolünde bloklar |
| Production User Admin, >90 gün, geçmiş süre | Sabit saatli yeni testlerde blok |
| `allowRemovals=false` + ekstra actual rol | Yalnız drift/plan; API DELETE çağrısı yok |
| Eksik sayfa/403/son güvenli Admin | Kaldırma durur; API hatası başarıya çevrilmez |
| JIT review testi | Bir tekrarsız öneri PR'ı; uygulanmadıysa erişim hâlâ açık olarak raporlanır |
| Gelecekte canlı iptal | Onay + apply kaydı + rol listesi farkı; etkili erişim ayrıca test edilir |

- **403 ile liste okunamıyor:** Viewer/Contributor rolü liste API'si için yetersiz olabilir; otomatik yükseltmeyin, coach mock'a dönsün.
- **UPN çözümlenemiyor:** doğru tenant, object ID ve Graph okuma kapsamını admin kontrol etsin; provisioner atlamasını log'da arayın.
- **Dosyada rol sildim, portalda duruyor:** mevcut provisioner rol kaldırmaz; bu beklenen davranıştır.
- **Tarih geçti, erişim duruyor:** tarih Fabric rolüne yerleşik bir sayaç eklemez; çalışan revocation mekanizması yoktur.
- **Review job kuyruğa takıldı:** runner/enable/izinleri ortak kurulumla kontrol edin; boş job'u başarı saymayın.
- **Coach sorusu:** “User yerine Group neden?” **Yanıt:** Kimlik yaşam döngüsünü merkezi yönetmek için; grup üyelerinin incelemesi yine gerekir.
- **Coach sorusu:** “PR'ı geri almak rolü geri alır mı?” **Yanıt:** Hayır; mevcut add-only kod eksik kullanıcıyı silmez.
- **Yedek demo:** iki Admin grubu + bir geçici User + bir fazla Viewer içeren elle hazırlanmış mock liste kullanın.
  Kartı **SİMÜLASYON — GERÇEK YETKİ İPTALİ/DAĞITIM KANITI DEĞİL** diye işaretleyin.
- **Maliyet/temizlik:** bu ders kapasite/Spark başlatmaz; GitHub runner ve Copilot kullanım maliyeti olabilir.
  Lab'da gerçek erişim açılmışsa müşteri yöneticisi ayrı onaylı süreçle kapatıp doğrulasın; bu repo otomatik cleanup sağlamaz.
  Gerçek acil durum hesaplarına/gruplarına dokunmayın; sentetik dosya ve yerel raporları seçerek temizleyin.

Kaynaklar (24 Eylül 2026):
[Workspace rolleri ve grup etkisi](https://learn.microsoft.com/en-us/fabric/fundamentals/roles-workspaces) ·
[Rol listesini okuma](https://learn.microsoft.com/en-us/rest/api/fabric/core/workspaces/list-workspace-role-assignments) ·
[Rol ekleme](https://learn.microsoft.com/en-us/rest/api/fabric/core/workspaces/add-workspace-role-assignment) ·
[Rol silme ve son Admin koruması](https://learn.microsoft.com/en-us/rest/api/fabric/core/workspaces/delete-workspace-role-assignment) ·
[GitHub CODEOWNERS](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-code-owners).
