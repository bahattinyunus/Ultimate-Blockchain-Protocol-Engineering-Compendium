# 🚀 Mainnet Readiness & Production Deployment Checklist (12 Aşamalı Kılavuz)

Bir akıllı sözleşme veya Web3 protokolü mainnet ortamına (ana ağ) dağıtılmadan önce bu 12 aşamalı kurumsal güvenlik kontrolünden geçmelidir.

---

## 📋 Aşama 1: Mimari & Tehdit Modellemesi (Architecture & Threat Modeling)
- [ ] Protokolün durum makineleri (state machines), veri akışları ve aktörleri tam olarak belgelendi mi?
- [ ] Tüm güven varsayımları (trust assumptions) ve harici bağımlılıklar (DEX'ler, köprüler, oracelar) listelendi mi?
- [ ] Ekonomik teşvik modelleri (incentive compatibility) ve oyun teorisi saldırıları modellendi mi?

---

## 📋 Aşama 2: Test Kapsamı & Fuzzing (Test Coverage & Fuzzing)
- [ ] Satır kapsamı (line coverage) $> 95\%$, dal kapsamı (branch coverage) $> 90\%$ mı?
- [ ] Foundry ile en az 100,000 iterasyonluk State & Invariant Fuzzing çalıştırıldı mı?
- [ ] Olumsuz durum testleri (`test_RevertWhen_*`) tüm olası başarısız senaryoları kapsıyor mu?
- [ ] Farklılaşma testleri (Differential testing) alternatif implementasyonlarla karşılaştırıldı mı?

---

## 📋 Aşama 3: Bağımsız Güvenlik Denetimleri (Audits & Bug Bounties)
- [ ] En az iki saygın bağımsız denetim firmasından (Trail of Bits, OpenZeppelin, Spearbit vb.) tam denetim raporu alındı mı?
- [ ] Topluluk odaklı rekabetçi denetim yarışması (Code4rena / Sherlock) düzenlendi mi?
- [ ] Rapordaki tüm Critical, High ve Medium bulgular çözüldü veya hafifletildi mi?

---

## 📋 Aşama 4: Formal Doğrulama (Formal Verification)
- [ ] Protokolün temel matematiksel kuralları (Solvency, Share Ratio, Conservation of Value) Certora veya Halmos ile teorem olarak ispatlandı mı?
- [ ] SMTChecker modelleme hataları vermeden sıfır uyarı ile derleniyor mu?

---

## 📋 Aşama 5: Dağıtım Scriptleri & Deterministik Adresler
- [ ] Dağıtım scriptleri (Foundry Script / Hardhat) yerel Fork (`anvil --fork-url`) üzerinde hatasız çalıştırıldı mı?
- [ ] Tüm zincirlerde aynı sözleşme adresini elde etmek için `CREATE2` fabrikası kullanıldı mı?
- [ ] Bayt kodu Etherscan / Blockscout üzerinde tam olarak doğrulandı (verified) mı?

---

## 📋 Aşama 6: Multisig & Yönetişim Mimarisi (Safe & Timelock)
- [ ] Tüm yönetici (admin) anahtarları Safe (Gnosis Safe) çoklu imzalı (multisig) cüzdana devredildi mi (min. 3/5 veya 4/7 eşiği)?
- [ ] Tüm kritik yönetimsel fonksiyonlar en az 48 saatlik bir `TimelockController` arkasına bağlandı mı?
- [ ] Tekil geliştirici özel anahtarlarında (EOA) hiçbir yönetici yetkisi bırakılmadı mı?

---

## 📋 Aşama 7: Acil Durum & Devre Kesiciler (Emergency & Circuit Breakers)
- [ ] Acil durumlarda para yatırma veya borçlanmayı durduran `Pausable` mekanizması var mı?
- [ ] Anormal fiyat veya hacim hareketlerinde otomatik duraklatma yapan zincir içi devre kesici (circuit breaker) entegre edildi mi?
- [ ] Yetkili güvenlik komitesi (Security Council) acil duraklatma yetkisine sahip mi?

---

## 📋 Aşama 8: Oracle Sağlamlığı & L2 Sequencer Kontrolü
- [ ] Fiyat beslemelerinde Chainlink staleness, round completeness ve min/max sınır kontrolleri aktif mi?
- [ ] Arbitrum / Optimism / Base üzerinde `Chainlink SequencerUptimeFeed` devrede mi (sequencer çöktüğünde tasfiyeler donduruluyor mu)?
- [ ] Oracle arızası durumunda devralacak ikincil bir yedek oracle (fallback) var mı?

---

## 📋 Aşama 9: Canlı İzleme & Tehdit Tespiti (Real-Time Monitoring)
- [ ] Tenderly Alerts, Forta Network botları veya OpenZeppelin Defender ile şüpheli işlemler için 7/24 uyarı sistemleri kuruldu mu?
- [ ] Büyük çekimler, aşırı borçlanmalar ve flashloan çağrıları anlık Telegram/Slack kanallarına düşüyor mu?

---

## 📋 Aşama 10: Bug Bounty Programı & Sorumlu İfşa
- [ ] Immunefi veya benzeri bir platformda en az $500,000 - $1,000,000 ödül havuzlu bug bounty programı başlatıldı mı?
- [ ] `security.txt` veya depoda sorumlu ifşa (responsible disclosure) iletişim adresi tanımlandı mı?

---

## 📋 Aşama 11: Likidite Başlatma & MEV Koruması
- [ ] İlk likidite ekleme işlemleri genel mempool yerine özel RPC (Flashbots Builder) üzerinden yapıldı mı?
- [ ] DEX takaslarında sandwich saldırılarına karşı varsayılan $\%0.5$ slippage sınırı zorunlu tutuluyor mu?

---

## 📋 Aşama 12: Dağıtım Sonrası Doğrulama & Şeffaflık
- [ ] Dağıtılan sözleşmelerin durum parametreleri (parametreler, faiz oranları, teminat eşikleri) ana ağda manuel kontrol edildi mi?
- [ ] Topluluk ve kullanıcılar için şeffaf dağıtım duyurusu ve sözleşme adresleri paylaşıldı mı?
