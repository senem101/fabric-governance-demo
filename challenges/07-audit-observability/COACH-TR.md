# Challenge 07 — Coach rehberi: Audit ve gözlemlenebilirlik

> [İlk kurulum](../../docs/tr/ilk-kurulum.md) ·
> [Coach el kitabı](../../docs/tr/coach-el-kitabi.md) · [Özgün görev](challenge.md)
> Ürün kaynakları 24 Eylül 2026 tarihinde kontrol edilmiştir.

## 1. Hedef, süre ve 60 saniyelik açıklama

“PR bir değişiklik isteğidir; workflow bir yürütmedir; audit olayları ne olduğunu
kaydeder. Eventstream olayları taşır, Eventhouse/KQL saklar ve sorgular,
Power BI görünür kılar, Activator koşul oluşunca haber verir.
Yeşil workflow bütün yönetişim kontrollerinin geçtiği anlamına gelmez.
Her metriğin kaynağı, zaman damgası ve eksik veri davranışı açık olmalıdır.”

**Süre:** 20 dk olay modeli, 40 dk offline dönüşüm/test, 45–60 dk canlı demo,
20 dk negatif test/kapanış. Güvenli webhook alıcısı, audit exporter ve raporun
sıfırdan geliştirilmesi ayrıca yarım–bir gün sürebilir.
İlk derste tek tablo/tek metrik; beş rapor sayfası ileri kapsam olsun.

## 2. Hazır durum ve yapılacaklar

| Hazır | Geliştirilecek |
|---|---|
| GitHub validate/provision/drift workflow iskeletleri | Olayları toplayan bağlantı ve normalizasyon |
| Workspace manifesti, mevcut Markdown raporları | Eventhouse, Eventstream, KQL tablo/mapping tanımları |
| Workspace adı/açıklaması drift'i | Envanter/erişim snapshot'ları ve metrik hesapları |
| Hiçbir audit dashboard/alert uygulaması yok | Power BI raporu, Activator kuralı ve bildirim |

`scripts/export_activity.py`, `scripts/normalize_audit.py`,
`.github/workflows/audit-export.yml`, `audit/` ve audit item tanımları:
**oluşturulacak — bu repoda hazır değil**.
GitHub webhook'unu Eventstream'e doğrudan HTTP URL olarak bağlamak hazır çözüm değildir.
Custom endpoint belgesi Event Hubs/AMQP/Kafka protokollerini anlatır;
GitHub webhook imzasını doğrulayan HTTP alıcısı ve protokol köprüsü ayrıca gerekir.
“Purview Audit → Activity Explorer → Eventstream” hazır konektör zincirini doğrulamadan vaat etmeyin.

## 3. Önkoşullar, izinler ve veri sınırı

1. Challenge 00–01; item otomasyonu için Challenge 02.
2. Onaylı eğitim workspace'i ve Fabric kapasitesi gerekir.
   F4+ lab planlama önerisidir; her ekip için zorunlu minimum değildir.
3. Eventstream düzenleme için Contributor veya üstü; Entra ile custom endpoint
   bağlantısı için güncel dokümandaki ilave Member/kimlik koşullarını kontrol edin.
4. Eventhouse/KQL query, ingestion ve yönetim izinleri aynı değildir.
   Öğrencinin query erişimi olması tablo oluşturma yetkisi olduğu anlamına gelmez.
5. Power BI yazarlık/paylaşım lisansını ve kapasite koşullarını doğrulayın.
   Sadece rapora bakacak katılımcıyla raporu yayımlayacak kişinin ihtiyaçları ayrıdır.
6. Activator için Fabric kapasitesi, desteklenen kaynak ve bildirim alıcısı gerekir.
   İlk bildirim yalnız coach'un test adresine; müşteri dağıtım listesine değil.
7. Activity Events için kullanıcı Fabric admin olmalı veya izin verilmiş SPN kullanılmalı.
   SPN read-only admin API tenant ayarı ve endpoint'e özel kısıtlar ayrıca gerekir.
8. Activity endpoint'i **Power BI REST** ailesindedir; Fabric Core endpoint'i değildir.
   Token audience'ını doğru seçin; `_fabric.py` yardımcısını körlemesine yeniden kullanmayın.
9. Gerçek audit olaylarında UPN, IP, nesne adları olabilir.
   İzinli alanları seçin, takma kimlik kullanın, ham payload'ı public repo veya Copilot'a vermeyin.
10. Tenant genel ayarlarını eğitim uğruna herkese açmayın; adminle dar kapsamı belirleyin.

## 4. Coach hazırlığı: küçük ve ölçülebilir örnek

1. Eğitim workspace adını `pt-nlyt-sales-ndf-dev-aud01` olarak örnekleyin.
   Özgün `dev-plt-gov-audit` mevcut isim şemasına uymaz.
   Cost bilgisi için mevcut `costCenter` alanını kullanın; tag uygulanmış varsaymayın.
2. Repo kökünde hazır/eksik durumunu gösterin:

   ```powershell
   Get-Content .\.github\workflows\drift.yml
   Test-Path .\scripts\export_activity.py
   Test-Path .\.github\workflows\audit-export.yml
   ```

   **Beklenen:** taban checkout'ta son iki sonuç `False`.
3. Gerçek kaynak açmadan aşağıdaki sentetik olay setini öğrenciye verin.
   Tarihler UTC; aynı PR ile aynı head SHA ilişkisini açıkça işaretleyin.

| event_id | event_type | occurred_at | pr_id | run_id | result |
|---|---|---|---:|---:|---|
| e01 | pr_opened | 2026-09-24T09:00:00Z | 101 | — | — |
| e02 | pr_merged | 2026-09-24T09:10:00Z | 101 | — | — |
| e03 | provision_completed | 2026-09-24T09:12:00Z | 101 | 501 | success |
| e03 | provision_completed | 2026-09-24T09:12:00Z | 101 | 501 | success |
| e04 | provision_completed | 2026-09-24T09:15:00Z | 102 | 502 | failure |

**Beklenen:** 5 teslimat, 4 benzersiz olay, 1 başarılı ve 1 başarısız provision.
PR101 için açılış→başarılı provision **12 dakika**.
PR102 açılış olayı olmadığından süre metriğine dahil edilmez; “0 dakika” yazılmaz.
`received_at` sonradan alıcıda ölçülür; olay zamanı ile alım zamanı aynı alan değildir.

## 5. Öğrenci: olay sözleşmesini ve offline testleri geliştirin

1. `audit/` altında **yeni** olay sözleşmesi tasarlayın; workspace şemasını değiştirmeyin.
   `event_id`, `event_type`, `occurred_at`, `received_at`, `repo`, `head_sha`,
   `pr_id`, `run_id`, `workspace_id`, `synthetic` alanlarının tiplerini belirleyin.
2. Eksik alan/bozuk timestamp için karantina davranışı; duplicate için idempotency anahtarı yazın.
   Repo+run_id+attempt gibi anahtarların yeniden çalıştırmaları ayırt etmesini sağlayın.
3. PR opened/closed/merged ve workflow completed payload'larını ayrı normalize edin.
   Closed her zaman merged değildir; status=completed her zaman success değildir.
4. Activity Events dönüşümünde olay ID'sini ve UTC zamanını koruyun.
   Bilinmeyen event türünü sessizce atmak yerine sayın ve raporlayın.
5. Sentetik fixture'ları test edin: 5→4 dedup, 12 dk süre, 1/1 outcome.
   İkinci ingestion sonunda mantıksal metrikler değişmemeli.
6. KQL tabloları/mapping/retention dosyalarını taslak olarak sürümleyin.
   Özgün görev 90 gün ister; labda veri minimizasyonuna uygun kısa retention seçin
   ve bu kapsam farkını kaydedin. Saklama süresi kurum onayına tabidir.

## 6. Öğrenci: canlı bağlantıyı ayrı bir iş olarak kurun

1. En küçük güvenli başlangıç: onaylı, temizlenmiş dosyadan toplu ingestion.
   Bu aşama webhook veya canlı audit entegrasyonu değildir.
2. Gerçek webhook için HTTPS alıcısı geliştirin:
   GitHub imzasını doğrula → event/repo allow-list → tekrar teslimat kontrolü →
   alan maskeleme → queue/yeniden deneme → Eventstream destekli protokole gönderim.
   Sırları repo dosyasına veya endpoint query string'ine yazmayın.
3. Eventstream'de Custom endpoint source ve Eventhouse destination tanımlayın;
   tablo mapping'ini seçin, test verisini önizleyin, onayla yayımlayın.
   **Beklenen:** bağlantı durumu ve alınan olay sayısı görünür.
4. Eventhouse `eh_gov_audit`, KQL database `gov_audit` ve tabloları yetkili planla oluşturun.
   `pr_events`, `workflow_runs`, `fabric_activity` başlangıç tablolarıdır.
5. Activity exporter'ı saatlik planlamadan önce bir UTC günüyle sınayın.
   API penceresi **aynı UTC gününde**, **son 28 gün** içinde olmalı.
   `continuationToken` bitene kadar sayfalayın; 200 istek/saat sınırına ve 429'a uyun.
6. Checkpoint'i ancak kalıcı ingestion onayından sonra ilerletin.
   Geç gelen olaylar için örtüşen pencere+dedup uygulayın.
   Saatlik çekim, olayın saat içinde mutlaka hazır olacağı SLA'sı değildir.
7. Envanter ve RBAC snapshot kaynaklarını ayrıca geliştirin.
   PR/audit olaylarından tek başına güncel domain/label coverage ve User Admin sayısı çıkarılamaz.
8. Drift raporunu yapılandırılmış olaylara dönüştürün; açık issue yaşları için
   GitHub issue durumunu okuyun. Mevcut drift workflow'u otomatik issue kapatma sağlamaz.
9. Power BI'da önce provision başarı/başarısızlık sayfasını bağlayın.
   Sonra workspace envanteri, PR süreleri, drift ve erişim sayfalarını ekleyin.
   Veri kaynağı kurulmamış sayfaya 0 yerine “veri yok” yazın.
10. Activator'da tek test koşulu kullanın: lab başarısız provision sayısı eşiği aşarsa bildir.
    Nesne anahtarı, pencere, yeniden bildirim/cooldown ve alıcıyı açıkça belirleyin.
    Kuralı başlatın, sentetik koşulu tetikleyin, bildirim kanıtını alın, kuralı durdurun.

## 7. Workflow ve araç entegrasyonu

- `validate.yml` PR path filtrelerine `audit/**`, `items/**`, `tests/**`,
  `.github/workflows/audit-export.yml` ekleyin; yeni normalizasyon/test adımlarını çağırın.
- Mevcut workspace validator audit dosyalarını doğrulamaz.
  Şema/mapping değişince tüm audit fixture testlerini çalıştırın.
- Yeni `audit-export.yml`: başlangıçta yalnız `workflow_dispatch`, doğrulamadan sonra
  gerekirse saatlik `schedule`. Schedule path filtresiyle kısıtlanmaz.
- Exporter güvenilir varsayılan branch'ten çalışmalı; checkpoint deposu, en az yetkili
  kimlik, `concurrency`, timeout ve retry limitleri tanımlanmalı.
- Audit item uygulaması ayrı workflow olacaksa main push filtreleri `audit/**`,
  `items/**`, `schemas/**`, `rules/**`, `scripts/**` ve kendi workflow yolu olsun.
- OIDC her serviste aynı token/izin demek değildir; Power BI admin, Fabric item ve
  Eventstream ingestion kimliklerini endpoint başına eşleyin.
- Mevcut `[self-hosted, fabric-gov]` Linux runner'ı ve korumalı environment kurulumunu
  ortak rehberden tamamlayın. Güvenilmeyen PR koduna audit kimliği vermeyin.
- Kurulu skill kataloğundaki Eventhouse/Eventstream/Activator becerileri taslak üretmeye
  yardımcı olabilir; eski skill komut adlarını çalışır CI arayüzü kabul etmeyin.
- GitHub manifestleri ile Fabric Git tanımlarını ayırın; item sync için ayrı adım gerekir.

## 8. Güvenli istemler ve demo akışı

**Copilot — yalnız yerel taslak:**

> audit fixture normalizer, mapping taslağı ve offline testlerini hazırla.
> HMAC doğrulama, dedup, UTC gün sınırı ve eksik veri davranışını tasarımda belirt.
> Gerçek token/payload isteme. Tenant, webhook, Eventhouse veya alert oluşturma;
> herhangi bir bağlantı, ingestion, e-posta, push/merge ya da workflow çalıştırma.
> Eksik altyapıyı hazır gibi gösterme; dosya diff'ini ve test beklentisini sun.

**MCP — sadece query/metadata:**

> Yalnız onaylı lab gov_audit kaynağında son bir saatin sentetik olay sayısını
> ve success/failure toplamını oku. En fazla 10 özet satır döndür.
> Ham payload, UPN/IP veya bağlantı sırrı getirme.
> Create/ingest/alter, alert etkinleştirme ve bildirim gönderme yapma.
> Kaynağa erişilemiyorsa bunun yerine sayı uydurma.

**5 dakikalık canlı demo:** PR101 → run501 → head SHA → Eventhouse satırı →
Power BI metriği → tek Activator bildirimi zincirini aynı korelasyonla gösterin.
Alım gecikmesini `received_at - occurred_at` olarak ölçün.
Özgün 60 saniye kriteri ölçülecek lab hedefidir, ürün garantisi değildir.
Fixture kullanıldıysa “sentetik canlı ingestion”; gerçek audit export'u yoksa “audit doğrulanmadı” deyin.

## 9. Negatif testler, sorun giderme ve kanıt

| Deneme / belirti | Beklenen veya teşhis |
|---|---|
| Aynı delivery tekrar gönderilir | Metrik çift sayılmaz |
| Geçersiz webhook imzası | Alıcı reddeder; ingestion yapılmaz |
| UTC gece yarısını geçen pencere | İkiye bölünür; olay atlanmaz |
| İkinci sayfa erişim hatası | Checkpoint ilerlemez; retry sınırlıdır |
| Audit 403 | Admin API tenant ayarı/kimliği; SPN için Power BI admin-consent kısıtını kontrol et |
| Tablo boş | Alıcı → protokol → publish → destination → mapping sırasıyla incele |
| Rapor hep 0 | Kaynak boş mu, filtre mi yanlış, snapshot hiç yok mu ayır |
| Bildirim yok/çok fazla | Kural durumu, zaman penceresi, nesne anahtarı ve cooldown |

Kanıt: fixture/test raporu, ingestion zamanı, dedup sonucu, korelasyon kimlikleri,
metrik tanımı, gerçek bildirim zamanı ve veri kapsamı.
Dashboard ekranı tek başına olayın gerçekten GitHub/Fabric'ten geldiğini ispatlamaz.

## 10. Offline seçenek, sorular ve maliyet

Canlı kapasite/admin yoksa fixture üzerinde normalizasyon ve beklenen metrikleri gösterin.
“OFFLINE — webhook, tenant audit, canlı dashboard ve bildirim doğrulanmadı” notu zorunludur.
Sahte run URL'si veya gerçekmiş gibi uydurma audit satırı kullanmayın.

- **Audit bütün kontrol durumunu verir mi?** Hayır; güncel envanter ve erişim snapshot'ları ayrıca gerekir.
- **Saatlik exporter gerçek zamanlı mı?** Hayır; toplama periyodu ve kaynak gecikmesi vardır.
- **Eventstream URL'sini GitHub'a yazsak yetmez mi?** Protokol, auth ve imza kontrolü için köprü gerekir.

Eventstream/Activator'ı ders dışında çalışır bırakmayın; minimum kapasite/always-on
ayarlarını maliyet sahibinin onayı olmadan açmayın.
Cleanup'ta önce webhook ve schedule'ı kapatın, sonra alert ve stream'i durdurun.
Kanıtları izinli yerde saklayıp retention politikasına göre veriyi temizleyin.
Paylaşılan workspace/kapasiteyi silmeyin; sadece kaydı tutulan lab kaynaklarını onayla kaldırın.

## Kaynaklar

- [Eventhouse](https://learn.microsoft.com/fabric/real-time-intelligence/eventhouse)
- [Eventstream custom endpoint protokolleri/izinleri](https://learn.microsoft.com/fabric/real-time-intelligence/event-streams/add-source-custom-app)
- [Activity Events: UTC, sayfalama ve kimlik koşulları](https://learn.microsoft.com/rest/api/power-bi/admin/get-activity-events)
- [Read-only admin API için SPN ayarı](https://learn.microsoft.com/fabric/admin/enable-service-principal-admin-apis)
- [Activator davranışı ve kaynakları](https://learn.microsoft.com/fabric/real-time-intelligence/data-activator/activator-introduction)
- [GitHub webhook imza doğrulama](https://docs.github.com/en/webhooks/using-webhooks/validating-webhook-deliveries)
