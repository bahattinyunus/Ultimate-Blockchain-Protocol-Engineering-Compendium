# 🛡️ Ultimate Smart Contract Audit Checklist (120+ Checkpoints)

Bu kontrol listesi, kurumsal seviyede güvenlik denetçileri (auditors) ve protokol mimarları için hazırlanmış kapsamlı bir denetim rehberidir.

---

## 1. Erişim Kontrolü ve Yetkilendirme (Access Control & Authorization)
- [ ] Kritik fonksiyonlarda `onlyOwner`, `onlyRole` veya multisig kontrolleri eksiksiz mi?
- [ ] `tx.origin` yerine mutlaka `msg.sender` kullanılmış mı?
- [ ] Rol iptali (revocation) ve yönetici transferi iki adımlı mı (`transferOwnership` + `acceptOwnership`)?
- [ ] Varsayılan fonksiyon görünürlükleri (`external`, `public`, `internal`, `private`) doğru atanmış mı?
- [ ] Constructor veya `initialize` fonksiyonlarında yetkilendirme açığı var mı?
- [ ] Upgradeable sözleşmelerin implementation kontratında `_disableInitializers()` çağrılmış mı?
- [ ] Kendi kendine çağrılabilen (`address(this).call`) fonksiyonlarda yetki sızıntısı var mı?

---

## 2. Reentrancy & Durum Geçişleri (State Transitions)
- [ ] Tüm durum güncellemeleri Checks-Effects-Interactions (CEI) desenine uyuyor mu?
- [ ] Dış çağrılardan (`call`, `transfer`, `safeTransferFrom`) önce storage güncelleniyor mu?
- [ ] Read-only reentrancy riski olan `view` fonksiyonlarında (özellikle fiyat oraceları) kontrol var mı?
- [ ] Transient Storage veya SSTORE tabanlı `nonReentrant` kilitleri doğru sırada mı?
- [ ] Cross-function reentrancy (aynı state'i paylaşan iki farklı fonksiyona giriş) test edildi mi?
- [ ] Cross-contract reentrancy ihtimalleri değerlendirildi mi?

---

## 3. Matematik, Hesaplama ve Hassasiyet (Precision & Math)
- [ ] Bölme işleminden önce çarpma yapılıyor mu (ör. `(a * b) / c`)?
- [ ] Hassasiyet kaybı (precision loss) var mı (küçük tamsayı bölünmeleri)?
- [ ] Yuvarlama yönü her zaman protokolün lehine, kullanıcının aleyhine mi (rounding in favor of protocol)?
- [ ] `unchecked` blokları yalnızca taşma (overflow) ihtimalinin kesinlikle imkansız olduğu yerlerde mi kullanılmış?
- [ ] Katı eşitlik kontrolü (`==`) yerine toleranslı veya eşitsizlik (`>=`, `<=`) kontrolleri tercih edilmiş mi?
- [ ] Faiz, ücret ve pay (share) hesaplamalarında 1e18 / 1e27 (WAD/RAY) çarpanları tutarlı mı?

---

## 4. Oracelar ve Fiyat Beslemeleri (Oracles & Price Feeds)
- [ ] Spot DEX havuz rezervleri (`getReserves`) doğrudan fiyat kaynağı olarak kullanılmaktan kaçınılmış mı?
- [ ] Chainlink fiyat beslemesinde `updatedAt`, `answeredInRound` ve staleness (zaman aşımı) kontrolleri var mı?
- [ ] Chainlink `minAnswer` / `maxAnswer` devre kesici (circuit breaker) sınırları kontrol ediliyor mu (LUNA çöküşü senaryosu)?
- [ ] L2 ağlarında (Arbitrum, Optimism) Chainlink Sequencer Uptime Feed kontrolü yapılıyor mu?
- [ ] TWAP (Time-Weighted Average Price) kullanılıyorsa pencere süresi en az 30 dakika mı?
- [ ] Oracle çökmesi veya manipülasyonu durumunda fallback oracle mekanizması var mı?

---

## 5. Token Entegrasyonları (ERC20, ERC721, ERC4626)
- [ ] Standart dışı ERC20'ler (USDT'nin dönüş değeri döndürmemesi) için `SafeERC20` (`safeTransfer`, `safeApprove`) kullanılmış mı?
- [ ] Fee-on-transfer (transferde vergi kesen) tokenlar hesaba katılmış mı (bakiye transfer öncesi ve sonrası ölçülüyor mu)?
- [ ] Rebasing tokenlar (stETH, AMPL) ile bakiye senkronizasyonu sağlanıyor mu?
- [ ] ERC777 / ERC1155 alıcı kancaları (`tokensReceived`, `onERC1155Received`) ile gelen reentrancy vektörleri engellendi mi?
- [ ] ERC-4626 kasalarında ilk yatıran saldırısı (inflation/donation attack) için sanal pay veya dead share var mı?
- [ ] `approve(0)` yapmadan tekrar `approve(amount)` çağrılmasına izin vermeyen tokenlar destekleniyor mu?

---

## 6. Yükseltilebilirlik ve Proxy Mimarisi (Upgradability & Proxies)
- [ ] Storage layout çakışması (collision) var mı? Yeni değişkenler yalnızca en sona mı ekleniyor?
- [ ] Base kontratlarda `__gap` (storage gap array) bırakılmış mı?
- [ ] Constructor içinde immutable değişken atanması proxy'de veri kaybına yol açıyor mu?
- [ ] `delegatecall` yapılan adreste `selfdestruct` opkodu bulunmadığı kesin mi?
- [ ] UUPS implementasyonunda `_authorizeUpgrade` fonksiyonu korumalı mı?
- [ ] Diamond Storage kullanılıyorsa benzersiz keccak-256 slotları doğru tanımlanmış mı?

---

## 7. DoS (Hizmet Engelleme) & Gaz Limitleri
- [ ] Dinamik boyutlu diziler üzerinde dönen sınırsız (unbounded) döngüler var mı?
- [ ] Kullanıcı fon dağıtımlarında Push yerine Pull modeli (kullanıcının kendi çekmesi) uygulanmış mı?
- [ ] Harici bir çağrının `revert` etmesi tüm sistem akışını kilitliyor mu?
- [ ] Blok gaz limitini (30M gas) aşabilecek karmaşıklıkta işlemler var mı?

---

## 8. Kriptografi ve İmzalar
- [ ] `ecrecover` çağrısında `address(0)` (sıfır adres) doğrulaması yapılıyor mu?
- [ ] İmza dövülebilirliği (signature malleability - $s > n/2$) koruması var mı?
- [ ] EIP-712 tipik yapısal hash ve domain separator (`chainId`, kontrat adresi) kullanılıyor mu?
- [ ] Tek kullanımlık nonce takibi yapılarak imza tekrarı (signature replay) engellenmiş mi?
- [ ] Deadline / geçerlilik süresi kontrol ediliyor mu?

---

## 9. MEV, Mempool ve Önüne Geçme (Front-Running)
- [ ] Kritik DEX takaslarında `minAmountOut` (slippage toleransı) parametresi zorunlu tutuluyor mu?
- [ ] Tasfiyeler (liquidations) veya arbitrajlar sandwich saldırısına açık mı?
- [ ] Commit-reveal şeması veya özel RPC desteği düşünülmüş mü?
- [ ] EIP-2612 `permit` çağrılarının mempool'da önden koşturulup geçersiz kılınması (revert) senaryosu ele alınmış mı?

---

## 10. Yönetişim & Acil Durum Protokolü
- [ ] Kritik parametre değişikliklerinde Timelock (zaman kilidi) gecikmesi var mı (en az 24-48 saat)?
- [ ] Acil durum duraklatma (`pause`/`unpause`) mekanizması ve devreden çıkarma yetkileri açıkça tanımlı mı?
- [ ] Flash loan ile oy gücü manipülasyonunu engellemek için anlık snapshot (geçmiş blok ağırlığı) kullanılıyor mu?
