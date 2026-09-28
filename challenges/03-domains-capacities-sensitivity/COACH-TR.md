# Challenge 03 — Domain, kapasite ve etiket: coach rehberi

[Türkçe başlangıç](../../docs/tr/README.md) · [İlk kurulum](../../docs/tr/ilk-kurulum.md) · [Coach el kitabı](../../docs/tr/coach-el-kitabi.md) · [Asıl challenge](challenge.md)

**Amaç:** Müşterinin “verinin iş sahibi kim, hangi kaynakta çalışıyor, hangi hassasiyette?” sorularını ayrı ayrı yanıtlaması.
**Tahmini süre:** 20 dakika kavramlar + 35 dakika yerel test + 30 dakika portal gözlemi/tasarımlar + 25 dakika PR değerlendirmesi.
Domain ve etiket entegrasyonunu gerçekten geliştirmek ek mühendislik çalışmasıdır.

## 1. Müşteriye 60 saniyede anlatın

> “Bir binada departman tabelası, elektrik sayacı ve dosyanın gizlilik işareti aynı şey değildir.
> Fabric'te domain, veriyi iş alanına göre düzenler; kapasite, işi çalıştıran ortak kaynak havuzudur.
> Sensitivity label, içeriğin hassasiyetini sınıflandırır ve desteklenen politikalara bağlanabilir.
> Bu kararları dosyada yazıp GitHub'da inceleyeceğiz.
> VS Code dosyayı düzenlediğimiz yer; Copilot öneri üreten yardımcıdır.
> Dosyadaki istek ile platformda gerçekten uygulanmış durumun aynı olduğunu ayrıca ölçmek zorundayız.”

**Önemli düzeltme:** Domain ataması tek başına veri erişimi veya öğe görünürlüğü vermez; workspace/item izinleri ayrıdır.
Bir etiket adı da tek başına her dışa aktarımı engellediği anlamına gelmez; gerçek politika, öğe türü ve aktarım yolu önemlidir.

## 2. Bugünkü kod ile hedefi ayırın

| Konu | Bugün çalışan kapsam | Henüz olmayan |
|---|---|---|
| Domain | Zorunlu `domain`, onaylı liste ve ad kalıbı | Domain oluşturma/atama, domain ID çözümü |
| Subdomain | Zorunlu `subDomain` ve `sdm-...` kalıbı | Gerçek parent/child ilişkisi ve atama kontrolü |
| Kapasite | Policy allow-list, ortam ve bölge kontrolü; provisioner kapasite atamayı dener | `capacities/*.yaml` loader, kapasite kaynağı oluşturma/ölçekleme |
| Etiket | Policy'de isim kontrolü; `prd` için daha yüksek sınıflandırma | Fabric öğelerinde etiket uygulama/okuma entegrasyonu |
| Drift | Görülebilen workspace adları ve açıklama | Kapasite/domain/etiket farkı |
| Şema | Yalnız workspace şeması | Domain ve kapasite şemaları |

`domains/`, `capacities/`, ilgili şemalar ve uygulama adımları **OLUŞTURULACAK alıştırma çıktılarıdır**.
Mevcut provisioner açıklamaya managed-by işareti ekler ve kapasite sonucunu
geri okur; `tags` uygulamaz. Yeşil job tüm metadata'nın eşleştiğini kanıtlamaz.
`drift.yml` yalnız mevcut rapor için `drift, governance` etiketleriyle issue açar; `drift/configuration` ve otomatik kapanış yoktur.

## 3. Kurulum, roller ve lisanslar

- [ ] [İlk kurulum](../../docs/tr/ilk-kurulum.md), ayrı müşteri eğitim fork'u, VS Code ve Python ortamı hazır.
- [ ] Yerel testte müşteri tenant'ına giriş yok; `LIVE_CHECKS=false`.
- [ ] Canlı gözlem için müşteri admin onayı, doğru tenant ve yalnız sandbox kapsamı kayıtlı.
- [ ] Workspace yöneticisi ve kapasite sahibi aynı kişi varsayılmıyor.
- [ ] Kapasite atama için workspace Admin ve kapasitede gerekli contributor/admin izni doğrulanıyor.
- [ ] Domain portal ataması için Fabric/domain admin veya yetkilendirilmiş domain contributor + workspace Admin modeli seçiliyor.
- [ ] Asıl challenge'ın kullandığı **Assign Domain Workspaces By Ids admin API** için Fabric Administrator gereksinimi ayrıca değerlendiriliyor.
- [ ] Etiketler Purview yöneticisi tarafından tanımlanmış/yayınlanmış; uygun Information Protection lisansı var.
- [ ] Power BI öğesine etiket uygulayan kullanıcı için ek Pro/PPU gereksinimi kontrol ediliyor.
- [ ] Service principal'ın “Fabric Admin olması her API'yi çalıştırır” varsayımı yapılmıyor; kimlik desteği endpoint bazında doğrulanıyor.
- [ ] Maliyet sahibi kapasiteyi ve bölgeyi onayladı; otomatik trial/satın alma/ölçekleme yapılmıyor.

Etiket admin API belgeleri kullanıcı/delegated kullanıcı hakları ve label policy kapsamını şart koşar.
Bir SPN'yi gruba ekleyerek gözetimsiz etiketlemenin çözüldüğünü söylemeyin.
Copilot, Graph veya MCP bağlantısı eksikse yetki istemek yerine çevrimdışı rota ile devam edin.

## 4. İlk ekranlar: kavramı dosyada gösterin

1. **VS Code → File → Open Folder** ile eğitim kopyasını açın; sol alt dal adından `egitim/metadata-lab01` dalını oluşturun.
   Ana sürüme yazmadığınızı gösterin; GitHub ve Fabric hesaplarının farklı yetkiler taşıdığını açıklayın.
2. **Ctrl+P → `workspaces/tr-nlyt-sample-ndf-dev-hello1.yaml`** dosyasını açın.
   `domain`, `subDomain`, `capacity`, `region`, `sensitivityLabel` ve `costCenter` satırlarını birlikte okuyun.
3. **Ctrl+P → `rules/policy.yaml`** açın. `dom-ops-dat`, `senem2fabric`, `CC-1001` girdilerini bulun.
   Bu kişisel kopyada `senem2fabric` kaydı gerçek F64 kapasitesine bağlanmıştır.
4. **Ctrl+P → `schemas/workspace.schema.json`** açın. Desteklenen ortamlar `poc/dev/sit/uat/stg/prd`; `sbx` yoktur.
   Alan adı tam olarak `subDomain` olmalı. Yeni bir `domainId` alanı eklemek mevcut şemada reddedilir.
5. **Terminal → New Terminal → PowerShell** açıp aşağıdakini çalıştırın:

   ```powershell
   Get-Location
   git status --short
   Test-Path .\schemas\domain.schema.json
   Test-Path .\schemas\capacity.schema.json
   $env:LIVE_CHECKS = 'false'
   .\.venv\Scripts\python.exe .\scripts\validate.py .\workspaces\tr-nlyt-sample-ndf-dev-hello1.yaml
   $LASTEXITCODE
   ```

6. Beklenen: şemalar için `False`, workspace için `PASS`, çıkış kodu `0`.
   Sahte kapasite kimliğiyle bile yerel kontrol geçer; bu aşama **bölge/ortam sözleşmesini** kontrol eder, kaynak varlığını değil.
   `validation-report.md` oluşur; müşteri verisi taşımadan yerel kanıt olarak inceleyin.

## 5. Sentetik, buluta dokunmayan uygulamalı test

Bu kod mevcut örneği belleğe alır; dosya/policy/tenant değiştirmez.
Hedef ad `tr-nlyt-sales-ndf-dev-lab01`, domain `dom-ops-dat`, bölge `westeurope` olacaktır.
Sanal ortam yoksa [ilk kuruluma](../../docs/tr/ilk-kurulum.md) dönün; bu bölümde `provision.py` çalıştırmayın.

1. Aşağıdaki PowerShell bloğunu tek parça kopyalayın:

   ```powershell
   $env:LIVE_CHECKS = 'false'
   @'
   import copy
   import sys
   from pathlib import Path
   sys.path.insert(0, str(Path("scripts").resolve()))
   from rules_engine import load_yaml, load_policy, validate_manifest
   base = load_yaml(Path("workspaces") / "tr-nlyt-sample-ndf-dev-hello1.yaml")
   base.update(name="tr-nlyt-sales-ndf-dev-lab01", subject="sales", suffix="lab01")
   policy = load_policy()
   cases = [("dogru", copy.deepcopy(base), copy.deepcopy(policy), None)]
   for title, key, value, rule in [
       ("yanlis-bolge", "region", "northeurope", "region-matches-capacity"),
       ("onaysiz-domain", "domain", "dom-ops-lab", "domain-allow-list"),
       ("etiket-yok", "sensitivityLabel", None, "sensitivity-required"),
       ("desteksiz-alan", "domainId", "DEMO", "schema"),
   ]:
       item = copy.deepcopy(base)
       if value is None:
           item.pop(key, None)
       else:
           item[key] = value
       cases.append((title, item, copy.deepcopy(policy), rule))
   prod = copy.deepcopy(base)
   prod.update(name="tr-nlyt-sales-ndf-prd-lab01", environment="prd", sensitivityLabel="Confidential")
   prod["owners"][1] = {"principalType": "Group", "identifier": "55555555-5555-5555-5555-555555555555", "role": "Member"}
   restricted = copy.deepcopy(policy)
   restricted["approvedCapacities"][base["capacity"]]["allowedEnvironments"] = ["dev"]
   cases.append(("prd-dev-kapasitesi", prod, restricted, "capacity-allowed-for-env"))
   for title, item, rules, expected in cases:
       result = validate_manifest(item, policy=rules)
       blocks = [f.rule_id for f in result.blocking]
       print(title, "PASS" if result.passed else "BLOCK", blocks)
       assert result.passed if expected is None else expected in blocks
   '@ | .\.venv\Scripts\python.exe -
   ```

2. Beklenen: `dogru PASS`; diğer beş satır ilgili kural adıyla `BLOCK`.
   Son kapasite testi yalnız bellekte `allowedEnvironments=["dev"]` yapar.
   Repodaki mevcut F2 örneği `prd` dahil tüm tanımlı ortamlara izin verir; aksini öğretmeyin.
3. Katılımcıdan yanlış bölgeyi düzeltince hangi kuralın kaybolacağını açıklamasını isteyin.
   Bu testleri ileride CI'a taşımak ayrı iştir; burada workflow/tenant değişmedi.

## 6. Geliştirme sırası: hangi dosya ne işe yarayacak?

1. `schemas/domain.schema.json` ve `domains/dom-ops-dat.yaml` **OLUŞTURULACAK**:
   iş adı, açıklama, onaylı gerçek domain ID eşlemesi ve parent/subdomain ilişkisi tasarlayın.
   `domain` zorunluyken “boş bırak, hiçbir şey yapma” davranışını mevcut şemaya mal etmeyin.
2. `schemas/capacity.schema.json` ve `capacities/contoso-f2-northeurope.yaml` **OLUŞTURULACAK**:
   logicalName, capacityId, region, sku, allowedEnvironments alanlarını tanımlayın.
   Bu dosya **mevcut kapasitenin envanteridir**; Azure kapasitesi satın alan bir dağıtım şablonu değildir.
3. Loader/kural değişiklikleri **OLUŞTURULACAK**: bugün tek kaynak `rules/policy.yaml`'dır.
   Yeni dosyayı ekleyip eski allow-list'i silmek çalışan kontrolü bozar; geçişi aynı PR'da test edin.
4. Domain uygulaması **OLUŞTURULACAK**: isim → doğrulanmış domain ID; yalnız tek onaylı sandbox kimliği.
   Kapasiteye veya admin'e göre toplu atamayı eğitimde kullanmayın; çok sayıda workspace etkilenebilir.
5. Etiket modeli **OLUŞTURULACAK**: workspace dosyasındaki `sensitivityLabel` şu an mantıksal yönetişim niyetidir.
   Gerçek etiket hedefi desteklenen Fabric **öğesidir**; her item için uygulanabilir yöntem/kimlik/kanıt seçin.
6. Asıl challenge'daki `admin/workspaces/{id}/sensitivityLabel` çağrısını çalışan API diye kopyalamayın.
   Resmi `setLabels` API öğe kimlikleriyle çalışır; genel Fabric destek sayfası ile hedef türün güncel REST sözleşmesini birlikte kontrol edin.
   Domain varsayılan etiketi de koşullara bağlıdır, workspace'e tek bir label yazmakla eşdeğer değildir.
7. Drift genişletmesi **OLUŞTURULACAK**: domain/capacity ID ve item label ID bazında desired/actual karşılaştırması.
   Okuma yetkisi yoksa “uyumlu” değil “doğrulanamadı” raporlayın; otomatik düzeltme eklemeyin.

**Copilot Chat'e verilecek güvenli istek:**

```text
Yalnız yerel tasarım ve diff öner. Mevcut workspace şeması, rules_engine.py,
provision.py ve drift.py üzerinden domain/kapasite/item etiketi boşluklarını listele.
Önce mevcut davranışı koruyan şema/loader/mock test planını göster; incelememden
önce dosya değişikliği, commit/push veya workflow çalıştırma yapma. Tenant'a
bağlanma; API mutasyonu, satın alma, rol/etiket değişikliği yapma.
tr-nlyt-sales-ndf-dev-lab01 kullan. OLMAYAN dosyaları OLUSTURULACAK diye işaretle.
Workspace sensitivityLabel alanını gerçek item etiketiyle karıştırma.
Endpoint/kimlik desteğini resmi belgeye bağla; destek kanıtı yoksa canlı adımı durdur.
```

## 7. Portal ve MCP: yalnız gözlem

1. Admin onaylı hesapla **Fabric → Workspaces → sandbox → Workspace settings** açın.
   Domain ve capacity/license bilgisini okuyun; ekran adları dile/sürüme göre değişebilir. **Apply/Save** seçmeyin.
2. Yalnız yetkili coach, **Settings → Admin portal → Domains** üzerinden mevcut domain'i görüntüler.
   “Create”, “Assign”, “Default domain” değişikliği yapmayın; default atama başka çalışma alanlarını etkileyebilir.
3. Sandbox öğe listesinde **Sensitivity** sütununa veya öğenin ayrıntılarına bakın; etiket kaldırarak test yapmayın.
   Purview yayın kapsamını müşteri yöneticisi doğrulasın; genel katılımcılara yönetici yetkisi vermeyin.
4. Kurulu MCP araçlarını kontrol edip salt okunur isteği gönderin:

   ```text
   Yalnız müşteri onaylı tr-nlyt-sales-ndf-dev-lab01 sandbox'ını oku.
   Workspace kimliği, kapasite kimliği/bölgesi, domain ataması ve desteklenen
   öğelerin sensitivity label metadata'sını mevcut okuma araçlarıyla doğrula.
   Veri içeriği çekme. Domain/workspace/item oluşturma, atama, label değiştirme,
   rol değişikliği veya kapasite başlatma/ölçekleme yapma.
   Policy'deki mantıksal adları gerçek kaynak kimliklerinden ayır. Çağrı zamanı,
   sorgu kapsamı ve okuyamadığın alanları bildir; boş cevabı uyum sayma.
   ```

## 8. PR, onay ve workflow kapıları

1. **VS Code → Source Control → dosya farkı**: sahte kimlikler, yanlış tenant veya kapsam genişlemesini birlikte inceleyin.
2. Eğitim fork'una dal yayınlayın → **GitHub → Pull requests → New pull request**.
   Taslak PR'da çalıştırılan yerel testleri ve henüz uygulanmamış entegrasyonu açıkça yazın.
3. Bu kopyadaki `validate.yml` tüm PR'larda bütün workspace manifestlerini kontrol eder.
   `domains/**`/`capacities/**` değişikliğinin workflow'u tetiklemesi bu yeni manifestlerin doğrulandığı anlamına gelmez.
   Domain/kapasite validatorleri ve bunların bağımlılık kontrolleri ayrıca geliştirilmelidir.
4. `provision.yml` bu yeni yolları/uygulamaları içermez; mevcut kapasite ataması hata verirse warning ile devam edebilir.
   Sahte `capacityId` policy'de dururken yalnız `FABRIC_CAPACITY_ID` değişkenini doldurmak çözmez: policy'deki ID önce gelir.
5. `CODEOWNERS` YAML içeriğine göre etiket değişimini anlayamaz; dosya yoluna göre çalışır.
   Gerekirse `/workspaces/*-prd-*.yaml` gibi gerçek altı parçalı adı yakalayan kapsam kullanın.
   Eski `prd-*` başlangıç kalıbı bu repodaki workspace adlarını yakalamaz.
6. CODEOWNERS kaydı tek başına merge'i engellemez; required review/branch protection ve test gerekir.
   Birden çok owner yazmak her ekibin ayrı onayını garanti etmez; platform **ve** güvenlik onayı için ek süreç/check tasarlayın.
7. Etiketi düşürme veri açığa çıkma riski, yükseltme erişim/iş akışı etkisi yaratabilir; ikisini de inceleyin.
   Mevcut kodda etiket değişimi için özel karşılaştırma/onay kapısı yoktur.
8. Bu kopyada GitHub-hosted `ubuntu-latest`, Python 3.12 ve Linux sanal ortamı kullanılır; canonical Actions çalışır demo değildir.
   Runner seçimi, environment onayı ve güvenli etkinleştirme için [Challenge 00 kurulumunu](../00-setup/COACH-TR.md) kullanın.

## 9. Kabul, hata ayıklama ve kapanış

| Kontrol | Beklenen kanıt |
|---|---|
| Bugünkü sentetik testler | 1 PASS + 5 doğru kuraldan BLOCK; tenant'a çağrı yok |
| Yeni domain/kapasite manifesti | Yeni şema ve referans testi çalışır; dosya sessizce atlanmaz |
| Bölge/ortam uyumsuzluğu | PR merge'inden önce blok; kapasite değiştirme denenmez |
| Etiket tasarımı | Workspace niyeti ile item gerçek durumu ayrı; API tür/kimlik desteği kayıtlı |
| Gelecekte canlı uygulama | PR SHA + onay + uygulama kaydı + domain/capacity/item label ID okuması |
| Mock drift/okuma hatası | İlgili alan farkı veya “doğrulanamadı”; bugünkü drift'e olmayan kapsam atfedilmez |

- **Etiket menüsü boş:** yayın kapsamı, lisans, tenant ayarı ve kullanım hakkını admin kontrol etsin; sahte etiket oluşturmayın.
- **Domain 403:** portal rolü ile seçilen admin API rolünü ayırın; toplu yönetici atamasıyla çözmeye çalışmayın.
- **Kapasite yanlış/işlem bekliyor:** gerçek policy ID, bölge ve kapasite iznini kontrol edin; `202`/yeşil job son durumu kanıtlamaz.
- **“Etiketi değiştirdim, drift neden bulmadı?”** Bugünkü drift yalnız ad/açıklama okur; bu beklenen sınırdır.
- **Coach sorusu:** “Domain'e geçince veri herkesçe görünür mü?” **Yanıt:** Hayır; erişim domain üyeliğiyle verilmez.
- **Coach sorusu:** “F2 üretime uygun mu?” **Yanıt:** Buradaki allow-list bir iş kararı örneğidir; performans/bütçe ölçümü değildir.
- **Yedek demo:** bölüm 5, mock desired/actual tablo ve anonim ekran görüntüsü kullanın.
  Üzerine **SİMÜLASYON — GERÇEK DAĞITIM KANITI DEĞİL** yazın; canlı kabul maddelerini açık bırakın.
- **Maliyet/temizlik:** bölge taşıma, kapasite büyütme, etiket düşürme veya ortak domain silme yapmayın.
  Onaylı sonraki lab kaynaklarını yönetici ayrı planla temizlesin; manifest silmek canlı kaynağı silmez.
  Eğitim dalı/raporunu seçerek temizleyin; paylaşılan kapasiteyi kapatmayın.

Resmi kaynaklar (24 Eylül 2026):
[Domains ve erişim sınırı](https://learn.microsoft.com/en-us/fabric/governance/domains) ·
[Domain admin API yetkisi](https://learn.microsoft.com/en-us/rest/api/fabric/admin/domains/assign-domain-workspaces-by-ids) ·
[Kapasite atama](https://learn.microsoft.com/en-us/rest/api/fabric/core/workspaces/assign-to-capacity) ·
[Information protection](https://learn.microsoft.com/en-us/fabric/governance/information-protection) ·
[Etiket admin API kullanımı](https://learn.microsoft.com/en-us/fabric/governance/service-security-sensitivity-label-inheritance-set-remove-api) ·
[SetLabelsAsAdmin](https://learn.microsoft.com/en-us/rest/api/power-bi/admin/information-protection-set-labels-as-admin) ·
[GitHub CODEOWNERS](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-code-owners).
