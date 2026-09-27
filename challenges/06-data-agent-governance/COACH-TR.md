# Challenge 06 — Coach rehberi: Fabric Data Agent yönetişimi

> [İlk kurulum](../../docs/tr/ilk-kurulum.md) ·
> [Coach el kitabı](../../docs/tr/coach-el-kitabi.md) · [Özgün görev](challenge.md)
> Ürün kaynakları 24 Eylül 2026 tarihinde kontrol edilmiştir; tenant/bölge koşullarını yeniden okuyun.

## 1. Öğretim hedefi ve 60 saniyelik anlatım

“GitHub Copilot bizim kod yazma yardımcımızdır. Fabric Data Agent ise onaylı
veriye doğal dille soru sormamızı sağlar. MCP, asistanın araçlara ulaşma yoludur;
bu üçü aynı ürün değildir. Agent talimatı güvenlik duvarı değildir:
veri erişimi kimlik, kaynak izinleri ve uygulanmış politikalarla sınırlandırılır.
Biz hem agent'ın hangi kaynaklara bağlanacağını hem cevabının doğruluğunu test ederiz.”

**Süre:** 15 dk kavram/izin, 30 dk sözleşme, 40 dk geliştirme/test, 20 dk demo.
Tam otomatik agent uygulayıcısı ve Purview sinyalleri için ek geliştirme zamanı gerekir.
Başlangıç kapsamı: **bir agent, bir sentetik kaynak, üç soru, iki test kullanıcısı**.

## 2. Repo gerçeği: bu bir geliştirme challenge'ıdır

| Hazır | Hazır olmayan |
|---|---|
| Workspace şeması, kurallar ve oluşturma döngüsü | Agent şeması, kaynak allow-list doğrulaması |
| Workspace açıklaması/varlığı drift'i | Agent tanımı, instructions SHA ve source drift'i |
| `validate.yml` ve `provision.yml` iskeleti | Agent oluşturma, publish, paylaşım ve RAI lint adımları |

`schemas/agent.schema.json`, `agents/`, `scripts/lint_agent_instructions.py`,
`scripts/provision_agents.py`, `rules/agent/banned_phrases.yaml`:
**oluşturulacak — bu repoda hazır değil**.
Challenge 02 item sözleşmesi ve 03/04 kontrolleri de tamamlanmış kabul edilmez.
Mevcut `provision.py` herhangi bir Data Agent oluşturmaz.
PR kuralı tek başına portalda agent oluşturmayı tenant genelinde engellemez.

## 3. Güncel ürün/izin önkontrolü

1. Challenge 00–04'ün gereken parçalarını tamamlayın.
   Gold model kullanılacaksa Challenge 05'in veri doğruluğu kanıtını alın.
2. Güncel Learn, Fabric Data Agent'ı **genel kullanıma açık** olarak tanımlar.
   Bütün Purview entegrasyonlarını veya bağlı özellikleri GA saymayın; preview alanları vardır.
3. **Ücretli F2+** veya Fabric etkin **P1+** kapasite önkoşulunu kontrol edin.
   Sadece trial/PPU bulunmasını yeterli kabul etmeyin.
4. Data Agent tenant ayarları, gerekli cross-geo işleme/depolama izinleri
   ve kurumun veri yerleşimi onayı eğitimden önce değerlendirilmelidir.
5. Agent ve kaynak kapasitelerinin bölgeleri uyumlu olmalı.
   Farklı bölgede kaynak sorgulama sınırlamasını canlı planınızda kontrol edin.
6. Yazarın agent/item oluşturma izni ile tüketicinin agent'ı ve kaynağı okuma
   izinleri ayrıdır. Paylaşım otomatik olarak kaynak erişimi vermez.
7. Güncel dokümana göre semantic model üzerinden agent sorgusunda **Read**
   yeterlidir; bu kullanım için Build varsaymayın. Model yazarlığı farklı izin ister.
8. Kullanıcı ve service principal akışlarını karıştırmayın.
   Yayınlanmış agent'ı SPN ile sorgulama **preview**'dır; yönetim endpoint'i değildir.
   Bu akışta managed identity ve KQL kaynağı için SPN desteği şu anda yoktur.
   Token audience'ını endpoint belgesinden alın; Core Fabric token'ını her yere taşımayın.
   Create, definition, publish, sharing ve query işlemlerini ayrı destek matrisiyle değerlendirin.
9. Purview DSPM/DLP için ayrı yönetici, lisans ve desteklenen workload gerekir.
   Erişilemeyen risk sinyalini “risk yok” diye yorumlamayın.
10. Güncel doküman İngilizce dışı dilleri desteklenen kapsamda saymıyor.
    Dersi Türkçe anlatın; agent instructions ve değerlendirme sorularını İngilizce hazırlayın.

## 4. Coach hazırlığı

1. VS Code'da aşağıdaki incelemeyi repo kökünden çalıştırın:

   ```powershell
   Get-Content .\schemas\workspace.schema.json
   Test-Path .\schemas\agent.schema.json
   Test-Path .\scripts\lint_agent_instructions.py
   ```

   **Beklenen:** taban checkout'ta son iki sonuç `False`.
2. Ayrı eğitim branch'i açın; Copilot'a sadece taslak yazma sınırı verin.
3. Model olarak `sm_gold_revenue`, workspace olarak
   `pt-nlyt-sales-gld-prd-lab01` kullanabilirsiniz; bu örnek adı onaylı lab hedefiyle eşleyin.
   Özgün `prd-fin-gold` adı mevcut workspace şemasına uymaz.
4. Yetkili kullanıcı A ve kaynak erişimi olmayan kullanıcı B hazırlayın.
   B'nin kaynak workspace'inde Admin/Member/Contributor gibi dolaylı erişimi bulunmasın.
5. Kaynaktaki sentetik toplamı bağımsız hesaplayın: BOOK=150, PEN=200, toplam=350 EUR.
   Agent cevabı bu beklenen değere karşı sınanacak; kendi cevabı kendi kanıtı olamaz.

## 5. Öğrenci: yeni sözleşmeyi tasarlayın

1. Yeni `schemas/agent.schema.json` ve `agents/revenue-qa.yaml` hazırlayın.
   Bunlar **yeni agent şemasının alanlarıdır**, workspace manifestine kopyalanmaz:

   ```yaml
   name: agent-finance-revenue-qa
   workspace: pt-nlyt-sales-gld-prd-lab01
   clearance: Confidential
   dataSources:
     - kind: SemanticModel
       workspace: pt-nlyt-sales-gld-prd-lab01
       name: sm_gold_revenue
   instructionsFile: agents/instructions/revenue-qa.md
   exampleQuestions:
     - "What is the total revenue in EUR?"
     - "What is revenue by product?"
     - "Can you provide employee salaries?"
   ```

   **Beklenen:** tam şema ayrıca owners, description ve gereken referansları tanımlar.
   Bu kısa parça tam hazır provisioning manifesti değildir.
2. Kaynak allow-list'ini Challenge 02'nin item manifestleriyle eşleştirin.
   İsim çakışmalarında workspace+type+name ve çözümlenmiş item ID birlikte kullanılmalı.
3. `clearance` için kurumun açık etiket sıralamasını yazın.
   Bu alan yerel politika niyetidir; Entra clearance yetkisi veya otomatik DLP değildir.
4. `instructionsFile` yolunun repo içindeki izinli dizinde olduğunu doğrulayın.
   Dosya yoksa, repo dışına çıkıyorsa veya gerçek sır içeriyorsa engelleyin.
5. Talimatlarda kapsam, veri tanımı, reddetme, belirsizlik ve kaynak belirtme bölümleri olsun.
   Örneğin: “Use only the approved revenue source. Do not infer missing data.
   For requests about salaries, explain that this source is out of scope.”
6. 200–2000 kelime kuralını ve zorunlu başlıkları linter'da uygulayın.
   Kelime sayımı politikasını test edin; üç cümlelik örnek yukarıdaki kurala tek başına uymaz.
7. Yasak ifade kontrolünü review'a yardımcı olarak tasarlayın.
   Regex geçmesi prompt injection direnci veya güvenlik sertifikası değildir.
8. Örnek soruları fixture beklenen sonuçlarıyla eşleştirin.
   Semantic model kaynaklarında soru–query örnek çiftleri ekleme desteğini varsaymayın;
   `exampleQuestions` burada yerel değerlendirme listesidir.

## 6. Öğrenci: uygulayıcı ve GitHub entegrasyonu

1. Yeni agent validator, linter ve test komutlarının sözleşmesini belirleyin.
   Yerel testler bağlantısız çalışmalı; canlı kontroller ayrı ve açıkça istenmiş olmalı.
2. `scripts/provision_agents.py` **oluşturulacak — bu repoda hazır değil**.
   Önce plan/diff üretin; uygulama için workspace/item ID çözümleme,
   tanım güncelleme, publish ve sharing adımlarını gerçek API belgelerine bağlayın.
3. API'deki tür adını ve definition biçimini güncel dokümandan doğrulayın.
   Portal adı “Data Agent” diye bütün generic MCP araçlarının `DataAgent` türünü
   desteklediğini varsaymayın. Aracın mevcut şemasını okuyun.
4. En az yetkiyle idempotent uygulama ve desteklenmeyen auth için kapalı hata tasarlayın.
   Kaynak izinlerini otomatik genişletmek bir “düzeltme” adımı olmasın.
5. Bu kopyadaki `validate.yml` tüm PR'larda çalışır; `agents/**`, `items/**`,
   `tests/**` değişikliklerinin de gerekli kontrolleri çağırdığını doğrulayın.
6. Workflow'a agent validator ve instruction linter adımlarını gerçekten ekleyin.
   Mevcut `validate.py` agent dosyalarını doğrulamaz.
   Item, policy veya instructions değişince bağımlı agent'ları yeniden doğrulayın.
7. Uygulama için yeni `.github/workflows/agents.yml` seçerseniz güvenilir `main`
   push filtreleri: `agents/**`, `items/**`, `workspaces/**`, `schemas/**`,
   `rules/**`, `scripts/**` ve kendi workflow yolu. Bu workflow bugün yoktur.
8. Üretim job'ına OIDC, doğrulanmış `production` reviewers/branch kuralları,
   concurrency ve başarısız publish'in raporlanmasını ekleyin.
   PR etiketini doğrudan ayrıcalıklı uygulama izni saymayın.
9. Drift'e agent source set ve normalize edilmiş instruction hash karşılaştırması ekleyin.
   `drift.py` bugün bunları kontrol etmez; erişilemeyen tanımı eşit kabul etmeyin.
10. Bu kopyadaki mevcut workflow'ların GitHub-hosted Linux (`ubuntu-latest`) ve Python 3.12 seçimini yeni işlerde de değerlendirin.
    GitHub'da dosyanın bulunması Fabric'e Git sync veya agent publish yapılmış demek değildir.

## 7. Canlı demo: uygulama hazırsa

1. Onaylı plan ve PR incelemesinden sonra yalnız lab agent'ını uygulayın.
   **Beklenen:** workspace/item ID, kullanılan commit ve publish sonucu.
2. Kaynak seçimini açın; sadece beklenen model veya tablo seti görünmeli.
   Lakehouse dosyaları doğrudan kaynak değildir; veri seçili tablolarda sunulmalıdır.
3. A kullanıcısıyla yeni konuşmada “What is the total revenue in EUR?” sorun.
   **Beklenen:** 350 EUR ve doğru kaynak/kapsam; tolerans ve cevap formatını kaydedin.
4. “What is revenue by product?” sorusuyla BOOK=150, PEN=200 kontrolünü yapın.
5. “Can you provide employee salaries?” sorusuyla kapsam dışı davranışı gösterin.
   Reddetme metni tek başına erişim izolasyonu kanıtı değildir.
6. B kullanıcısıyla aynı gelir sorusunu sorun.
   **Beklenen:** yetkisiz veri dönmemesi; gerekirse agent paylaşımı ile kaynak iznini ayırarak test edin.
7. Ayrı lab kopyasında instruction değişikliği yapın; geliştirilen drift kontrolünün
   bunu bulduğunu kanıtlayın. Müşteri prod'unda bozma testi yapmayın.

## 8. Güvenli istemler

**Copilot — dosya yazımı:**

> Sadece agent schema, instructions, offline validator/linter ve test taslaklarını yaz.
> Workspace şemasını değiştirme. Kaynak izinleriyle clearance niyetini ayır.
> Yalnız sentetik BOOK=150, PEN=200 fixture'ını kullan.
> Tenant'a bağlanma; kaynak yaratma, publish, share, izin genişletme, push/merge yapma.
> Eksik API desteğini TODO olarak ve resmi kaynak bağlantısıyla göster.

**MCP — salt okuma:**

> Yalnız onaylı lab workspace'inin agent metadata'sını ve araç destekliyorsa
> kaynak referanslarını/instruction hash'ini oku. Ham hassas talimatları çıktı olarak verme.
> Mevcut araç tanımı desteklemiyorsa dur ve “doğrulanamadı” yaz.
> Create, update, publish, share, permission değişikliği veya veri dışa aktarma yapma.

## 9. Hata testleri ve kanıt

| Test | Beklenen |
|---|---|
| Unmanaged item kaynak olarak eklenir | Yeni validator bloklar |
| Refusal bölümü silinir | Yeni linter bloklar; satır/dosya gösterir |
| Veri etiketi clearance üstündedir | Yerel policy ihlali; otomatik erişim verilmez |
| Instruction dosyası bulunamaz | CI başarısız; boş metinle publish yapılmaz |
| B kullanıcısı soru sorar | Yasak veri yok; kimlik/izin testi kayıtlı |
| Model yok veya kapasite farklı bölgede | Açık hata; uydurma cevap kabul edilmez |
| Kaynak karşılaştırması okunamıyor | “Unknown”, asla “no drift” değil |

403 için tenant ayarı, agent izni ve veri kaynağı iznini ayrı kontrol edin.
Yanlış toplamda model ölçüsü, filtre, bölge ve yeni sohbet bağlamını inceleyin.
Workflow çalışmıyorsa path filtreleri ve runner'a; linter çalışmıyorsa yeni job adımına bakın.

## 10. Offline seçenek, coach Q&A ve kapanış

**Canlı ortam yoksa:** metadata/permission fixture'ları ve sabit beklenen cevaplarla
validator/linter testlerini gösterin. “OFFLINE — gerçek agent cevabı, RLS/DLP,
SPN ve publish doğrulanmadı” ibaresini kanıt matrisine ekleyin.
Mock'un B'yi reddetmesi gerçek kaynak güvenliğini ispatlamaz.

- **Agent'ı paylaşmak bütün veriyi paylaşmak mı?** Hayır; kullanıcı kaynak izinleri ayrıca uygulanır.
- **RAI lint güvenliği garanti eder mi?** Hayır; içerik kontrolüdür, kimlik testi ve review gerekir.
- **DSPM yoksa ders biter mi?** Hayır; opsiyonel entegrasyon “uygulanmadı” kalır, risksiz ilan edilmez.

Ücretli kapasite/AI tüketimi için soru sayısını ve oturum süresini sınırlayın.
Konuşmalara gerçek kişisel veri koymayın; audit erişimini de kısıtlayın.
Ders sonunda paylaşım izinlerini, test kullanıcılarını ve oluşturulan agent'ı sahip onayıyla temizleyin.
Manifest silmenin agent'ı silmediğini; mevcut workspace drift'in bu agent'ı görmediğini hatırlatın.

## Kaynaklar

- [Data Agent: kapasite, kaynak, dil ve güvenlik sınırları](https://learn.microsoft.com/fabric/data-science/concept-data-agent)
- [Data Agent oluşturma](https://learn.microsoft.com/fabric/data-science/how-to-create-data-agent)
- [Data Agent tenant ayarları](https://learn.microsoft.com/fabric/data-science/data-agent-tenant-settings)
- [Data Agent SPN sorgulaması: preview ve sınırlamalar](https://learn.microsoft.com/fabric/data-science/data-agent-service-principal)
- [Fabric ve Purview](https://learn.microsoft.com/fabric/governance/microsoft-purview-fabric)
- [Fabric kimlik desteğini işlem bazında doğrulama](https://learn.microsoft.com/rest/api/fabric/articles/identity-support)
