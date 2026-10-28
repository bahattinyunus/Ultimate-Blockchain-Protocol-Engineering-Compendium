# Contributing to Ultimate Blockchain & Protocol Engineering Compendium

Protokol mühendisliği, dağıtık sistemler, kriptografi ve akıllı sözleşme güvenliği alanında açık kaynaklı bir başvuru kaynağı inşa ediyoruz. Katkılarınız bu ekosistemin büyümesi ve doğruluğu için çok değerlidir.

## 🤝 Katkı Türleri

1. **Yeni PoC ve Exploit Vektörleri:**
   - DeFi protokollerinde veya sanal makinelerde (EVM, SVM vb.) gerçekleşmiş gerçek saldırıların simülasyonları.
   - Her PoC için hem zafiyetli sözleşme (vulnerable), hem saldırgan sözleşmesi (attacker), hem de düzeltilmiş versiyon (mitigated) bulunmalıdır.
2. **Kriptografi ve Protokol Simülatörleri:**
   - Sıfır bağımlılıklı (zero-dependency) veya minimal kütüphaneli Python/Rust/TypeScript simülasyonları (KZG, Merkle Trees, Consensus, P2P).
3. **Formal Doğrulama ve Audit Kontrolleri:**
   - Certora (CVL), Halmos veya SMTChecker kuralları ve test spesifikasyonları.
4. **Düzeltmeler ve Dokümantasyon Geliştirmeleri:**
   - Matematiksel formüllerdeki imla/kavram hataları, güncel EIP referansları ve EVM opkod maliyet güncellemeleri.

## 📐 Standartlar & Kurallar

- **Solidity Versiyonu:** Minimum `^0.8.24` (Cancun uyumlu - Transient Storage `tstore`/`tload` destekli).
- **Yul & Assembly:** Her assembly bloğu anlaşılır İngilizce/Türkçe açıklamalar içermelidir (stack state, memory offsets).
- **Format:** Markdown dokümanlarında LaTeX matematik formülleri standart `$ ... $` veya `$$ ... $$` formatında yazılmalıdır.
- **Foundry Standartları:** Test dosyaları `*.t.sol` formatında ve `test_RevertWhen_*`, `testFuzz_*` standardında adlandırılmalıdır.

## 🚀 Katkı Süreci (PR Akışı)

1. Depoyu forklayın (`fork`).
2. Yeni bir dal açın (`git checkout -b feat/yeni-modul-veya-poc`).
3. Değişikliklerinizi yapın ve test edin.
4. Anlaşılır bir commit mesajı yazın:
   - `feat(crypto): add KZG multiproof verification script`
   - `fix(evm): correct gas schedule for MLOAD/MSTORE quadratic formula`
   - `poc(defi): add read-only reentrancy attack scenario`
5. Ana depoya Pull Request (PR) açın.
