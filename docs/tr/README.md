# Türkçe coach rehberleri

Bu rehber seti, **Agentic Governance Blueprint for Fabric** içeriğini kendi
müşterilerine anlatacak coach'lar içindir. GitHub, GitHub Copilot ve VS Code'u
ilk kez kullanan katılımcılar da düşünülerek hazırlanmıştır.

**Başlangıç noktası:** Önce [Coach el kitabını](coach-el-kitabi.md), sonra
[ilk kurulum rehberini](ilk-kurulum.md) okuyun. Müşteri ortamına geçmeden önce
Challenge 00 ve 01'i yalnızca eğitim ortamında kendiniz prova edin.

## Hangi belgeyi ne zaman kullanmalıyım?

| Belge | Kullanım |
|---|---|
| [Coach el kitabı](coach-el-kitabi.md) | Müşteri görüşmesi, kapsam seçimi, anlatım, ajanda, prova ve teslim |
| [İlk kurulum](ilk-kurulum.md) | GitHub/Git, VS Code, Copilot, Python, MCP ve Skills'i sıfırdan öğrenme |
| [Solo demo ile orijinal tasarım farkları](solo-demo-farklari.md) | Tek kişilik demoda korunan kontroller, onay istisnaları, push/Actions akışı ve henüz tamamlanmayan işler |
| [00 - Ortam, kimlik ve araçlar](../../challenges/00-setup/COACH-TR.md) | Yöneticiyle birlikte GitHub Actions ve Fabric bağlantısını hazırlama |
| [01 - Workspace as code](../../challenges/01-workspace-as-code/COACH-TR.md) | Mevcut kodla doğrulama, PR, onay, oluşturma ve drift demosu |
| [02 - Items as code](../../challenges/02-items-as-code/COACH-TR.md) | Lakehouse, notebook ve warehouse için otomasyon geliştirme |
| [03 - Domain, kapasite ve hassasiyet](../../challenges/03-domains-capacities-sensitivity/COACH-TR.md) | Organizasyon, maliyet sınırları ve veri sınıflandırması |
| [04 - Erişim ve RBAC yaşam döngüsü](../../challenges/04-access-rbac-lifecycle/COACH-TR.md) | Grup tabanlı erişim, süre sonu ve erişim değerlendirmesi |
| [05 - Medallion başlangıcı](../../challenges/05-medallion-bootstrap/COACH-TR.md) | Bronze, Silver, Gold veri katmanları |
| [06 - Fabric Data Agent yönetişimi](../../challenges/06-data-agent-governance/COACH-TR.md) | İzinli kaynaklar, erişim sınırları ve agent değerlendirmesi |
| [07 - Denetim ve gözlemlenebilirlik](../../challenges/07-audit-observability/COACH-TR.md) | Olay toplama, görünürlük ve uyarılar |
| [08 - Deployment pipelines](../../challenges/08-deployment-pipelines/COACH-TR.md) | Geliştirme, test ve üretim arasında kontrollü geçiş |
| [Capstone - Bütünleşik uygulama](../../challenges/capstone/COACH-TR.md) | Seçilen challenge'ların kanıtlarıyla müşteri demosu ve değerlendirme |

Her challenge rehberinde hazırlık, sade anlatım, adım adım uygulama,
Copilot/MCP kullanımı, başarı kanıtı, sorun giderme ve coach notları bulunur.
Orijinal İngilizce `challenge.md` dosyaları hedefleri korur; Türkçe rehberler
bu hedefleri mevcut uygulama durumuyla birlikte açıklar.

## Önce bilin: Bu repo bir ürün kurulum paketi değil

**İncelenen başlangıç sürümü:** `913bbf7` (10 Eylül 2026).
**Rehber hazırlık tarihi:** 24 Eylül 2026.

| Durum | Bu repoda karşılığı |
|---|---|
| Hazır uygulama kodu | Workspace şeması, kurallar, doğrulayıcı, temel provisioner ve sınırlı drift taraması |
| Müşteriye göre kurulacak | Entra kimliği, kapasite, gerçek kimlik numaraları, runner, GitHub onayları ve MCP bağlantıları |
| Geliştirilecek alıştırmalar | 02-08 için item, erişim, medallion, data agent, audit ve promotion otomasyonlarının önemli bölümü |
| Bu dokümantasyonun yapmadığı | Tenant kurulumu, canlı kaynak oluşturma, lisans satın alma, production dağıtımı |

**“Dokümanda anlatılmış” ile “kodda uygulanmış” aynı şey değildir.** Örneğin
mevcut provisioner domain veya sensitivity label uygulamaz; drift taraması
rol değişikliklerini kontrol etmez. Ayrıntılı farklar
[coach el kitabındaki analizde](coach-el-kitabi.md) açıklanır.

## Eğitim için üç uygulama seviyesi

| Seviye | Ne yaparsınız? | Ne iddia edemezsiniz? |
|---|---|---|
| Yerel prova | Dosyaları okuyun, manifest doğrulayın, dry-run çıktısını inceleyin | Fabric'e dağıtım yapıldığını |
| Kontrollü canlı demo | Müşteri yöneticisinin onayladığı test ortamında PR ve Actions çalıştırın | Production'a hazır, eksiksiz yönetişim kurulduğunu |
| Geliştirme atölyesi | Eksik otomasyonları yazın, test edin, onaylatın | Sadece şema veya Copilot taslağıyla challenge'ın tamamlandığını |

Canlı bağlantı yoksa yerel prova da değerli bir eğitimdir. Bunu açıkça
**“canlı dağıtım yapılmadı”** diye etiketleyin.

## Okuma ve paylaşma

VS Code'da bu dosyayı açıp `Ctrl+Shift+V` ile okunabilir önizlemeye geçin.
GitHub'da aynı dosya bağlantılarıyla okunabilir. Reponun mevcut Pages iş akışı
`docs/` ve `challenges/` altındaki Markdown dosyalarını siteye dönüştürür;
ayrı bir web uygulaması kurmanız gerekmez.

Müşteriye özel notları, gerçek kullanıcı bilgilerini, ekran görüntülerini veya
kimlik bilgilerini bu kamuya açık eğitim deposuna koymayın. Her müşteri için
kurumun onayladığı ayrı bir çalışma alanı ve kanıt paylaşım yeri kullanın.

İngilizce kaynaklar: [Ana README](../../README.md),
[delivery guide](../delivery-guide.md), [terimler](../glossary.md).
