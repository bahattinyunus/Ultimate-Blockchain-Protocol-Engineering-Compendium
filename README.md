# ⚡ Ultimate Blockchain & Protocol Engineering Compendium

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Foundry](https://img.shields.io/badge/Built%20With-Foundry-red.svg)](https://getfoundry.sh/)
[![Rust](https://img.shields.io/badge/Engineered%20With-Rust-orange.svg)](https://www.rust-lang.org/)
[![Solidity](https://img.shields.io/badge/Solidity-0.8.26-363636.svg)](https://soliditylang.org/)
[![Cancun Ready](https://img.shields.io/badge/EVM-Cancun%20EIP--1153%20%7C%20EIP--4844-green.svg)](https://eips.ethereum.org/)
[![Restaking](https://img.shields.io/badge/Restaking-EigenLayer%20%7C%20Symbiotic-blueviolet.svg)](modules/13-restaking-shared-security/)
[![Intents](https://img.shields.io/badge/Intents-ERC--7683%20%7C%20Solvers-ff69b4.svg)](modules/14-intents-solvers-erc7683/)
[![Post-Quantum](https://img.shields.io/badge/Post--Quantum-Lattice%20ML--DSA-blue.svg)](modules/15-post-quantum-cryptography/)
[![CI Status](https://img.shields.io/badge/CI-Automated%20Verification-brightgreen.svg)](.github/workflows/ci.yml)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)

Bu depo; Web3 alanına adım atan bir bilgisayar bilimcisini **protokol mühendisliği**, **kriptografik altyapılar**, **akıllı sözleşme mimarileri**, **dağıtık konsensüs mekanizmaları**, **sıfır bilgi ispatları (ZKP)**, **paylaşımlı güvenlik (restaking)**, **niyet odaklı çözücüler (intents)**, **kuantum sonrası kriptografi** ve **saldırı/savunma teknikleri** konusunda en üst düzeye ulaştırmak; alandaki kıdemli mühendislere ve araştırmacılara ise doğrudan üretim seviyesinde mimari, denetim (audit) ve PoC referansı sunmak için tasarlanmış uçtan uca teknik bir rehberdir.

---

## 🏛️ Kapsamlı Protokol Mimarisi

```mermaid
flowchart TB
    subgraph L1_Consensus [Katman 1: Konsensüs & Kriptografik Güvenlik]
        direction TB
        P2P[P2P Ağ: libp2p / DiscV5 / Gossipsub] --> Gasper[Konsensüs: LMD-GHOST + Casper FFG]
        Gasper --> EngineAPI[Engine API: Forkchoice & Execution]
        EngineAPI --> StateStorage[Durum Deposu: MDBX / RocksDB]
        StateStorage --> PostQuantum[Kuantum Sonrası Güvenlik: ML-DSA / Dilithium & Hibrit İmzalar]
    end

    subgraph Restaking_Layer [Paylaşımlı Güvenlik & AVS Katmanı]
        direction TB
        StateStorage --> Restaking[EigenLayer & Symbiotic: Operator Delegasyonu]
        Restaking --> AVS[AVS Kuorum Konsensüsü & Kaskat Slashing Koordinatörü]
    end

    subgraph EVM_Execution [Yürütme Ortamı & Sanal Makineler]
        direction TB
        Restaking --> EVM[Cancun EVM: TSTORE/TLOAD, MSTORE, SLOAD]
        EVM --> VM_Compare[SVM Parallel Sealevel & Move VM]
    end

    subgraph L2_Modular [Katman 2, Modüler Rolluplar & ZK]
        direction TB
        EVM --> RollupArch[Execution / Settlement / Consensus / DA]
        RollupArch --> FraudProof[Optimistic: İnteraktif Bisection Fraud Proof]
        RollupArch --> ZKProof[ZK Rollup: Type 1-4 zkEVM & STARK/SNARK]
        RollupArch --> EIP4844[Veri Erişilebilirliği: EIP-4844 Blobs, DAS & KZG]
        ZKProof --> ZKCircuits[ZK Devreleri: R1CS, Plonkish, Poseidon Circom]
    end

    subgraph CrossChain_Intents [Birlikte Çalışabilirlik & Niyetler]
        direction TB
        RollupArch --> IBC[Cosmos IBC: Işık İstemciler & Paket Taahhütleri]
        IBC --> Bridges[Köprüler: Güvenli Röle vs Nomad 0x00 Açığı]
        Bridges --> ERC7683[ERC-7683 Niyet Standartları: Dutch Decay & Çözücü / Solver Pazarı]
    end

    subgraph App_Security [Uygulama Katmanı, MEV & Güvenlik]
        direction TB
        ERC7683 --> SmartContracts[UUPS Proxy, ERC-4337 Account Abstraction, Permit2, Diamond]
        SmartContracts --> MEV[MEV: PBS, Arbitraj, Sandwich & JIT Liquidity]
        MEV --> Audit[Denetim: 120+ Kontrol Listesi & Formal Doğrulama]
        Audit --> PoCLab[DeFi Hack PoC Laboratuvarı: Flashloan, Reentrancy & Governance Hijack]
    end
```

---

## 📌 İçindekiler
1. [Öğrenim & Çalışma Rotaları (Learning Tracks)](#-öğrenim--çalışma-rotaları-learning-tracks)
2. [Modül 1: Kriptografik Temeller & Matematik](#-modül-1-kriptografik-temeller--matematik)
3. [Modül 2: Dağıtık Sistemler, Ağ Katmanı & Konsensüs](#-modül-2-dağıtık-sistemler-ağ-katmanı--konsensüs)
4. [Modül 3: Sanal Makineler (EVM, SVM, Move VM)](#-modül-3-sanal-makineler-evm-svm-move-vm)
5. [Modül 4: Akıllı Sözleşme Geliştirme & Gas Optimizasyonu](#-modül-4-akıllı-sözleşme-geliştirme--gas-optimizasyonu)
6. [Modül 5: L2, Rollup Mimarileri & Modüler Blockchain](#-modül-5-l2-rollup-mimarileri--modüler-blockchain)
7. [Modül 6: Güvenlik, Denetim (Audit) & Formal Doğrulama](#-modül-6-güvenlik-denetim-audit--formal-doğrulama)
8. [Modül 7: MEV, Mempool Mühendisliği & Node Operasyonu](#-modül-7-mev-mempool-mühendisliği--node-operasyonu)
9. [Modül 8: DeFi Hack PoC Laboratuvarı](#-modül-8-defi-hack-poc-laboratuvarı)
10. [Modül 9: Üretim Ortamı Kontrol Listesi (Mainnet Readiness Checklist)](#-modül-9-üretim-ortamı-kontrol-listesi-mainnet-readiness-checklist)
11. [Modül 10: İstemci Mühendisliği, Depolama Motorları & Node Operasyonu](#-modül-10-istemci-mühendisliği-depolama-motorları--node-operasyonu)
12. [Modül 11: Çapraz Zincir Mimarileri, Köprüler & Birlikte Çalışabilirlik](#-modül-11-çapraz-zincir-mimarileri-köprüler--birlikte-çalışabilirlik)
13. [Modül 12: Sıfır Bilgi İspatları & ZK Devre Mühendisliği](#-modül-12-sıfır-bilgi-ispatları--zk-devre-mühendisliği)
14. [Modül 13: Yeniden Stake Etme, Paylaşımlı Güvenlik & AVS](#-modül-13-yeniden-stake-etme-paylaşımlı-güvenlik--avs)
15. [Modül 14: Niyet Odaklı Mimariler, Çözücüler & ERC-7683](#-modül-14-niyet-odaklı-mimariler-çözücüler--erc-7683)
16. [Modül 15: Kuantum Sonrası Kriptografi & Hibrit Durum Makineleri](#-modül-15-kuantum-sonrası-kriptografi--hibrit-durum-makineleri)

---

## 🧭 Öğrenim & Çalışma Rotaları (Learning Tracks)

*   **Rota A: Akıllı Sözleşme & Protokol Geliştiricisi (Smart Contract Track)**
    *   *Sıra:* [Modül 1](./modules/01-cryptography/) (Hash & İmzalar) $\rightarrow$ [Modül 3](./modules/03-virtual-machines/) (EVM/SVM) $\rightarrow$ [Modül 4](./modules/04-smart-contract-patterns/) (Foundry/ERC-4337/Yul) $\rightarrow$ [Modül 6](./modules/06-security-audit-formal-verification/) (Audit & Fuzzing).
    *   *Hedef:* Yüksek güvenlikli, optimize edilmiş DeFi ve altyapı sözleşmeleri yazmak.
*   **Rota B: Çekirdek Protokol & L2 Mühendisi (Core Protocol Track)**
    *   *Sıra:* [Modül 1](./modules/01-cryptography/) (Tamamı) $\rightarrow$ [Modül 2](./modules/02-distributed-systems-consensus/) (P2P & Konsensüs) $\rightarrow$ [Modül 5](./modules/05-layer2-modular-rollups/) (Rolluplar & ZK) $\rightarrow$ [Modül 10](./modules/10-client-engineering-node-ops/) (Client/Node geliştirme).
    *   *Hedef:* Reth/Geth gibi istemciler geliştirmek, sequencer/prover yazmak, L2 zincirleri kurmak.
*   **Rota C: Güvenlik Araştırmacısı (Security & Auditor Track)**
    *   *Sıra:* [Modül 3](./modules/03-virtual-machines/) (EVM/Yul) $\rightarrow$ [Modül 4](./modules/04-smart-contract-patterns/) (Assembly & Storage) $\rightarrow$ [Modül 6](./modules/06-security-audit-formal-verification/) (Vulnerability Vectors & Formal Verification) $\rightarrow$ [Modül 8](./modules/08-defi-hack-pocs/) (DeFi PoC Laboratuvarı).
    *   *Hedef:* Protokol seviyesinde denetim (audit) yapmak, beyaz şapkalı güvenlik ödülleri (bug bounty) kovalamak.
*   **Rota D: ZK & Kriptografi Mühendisi (ZKP & Cryptography Track)**
    *   *Sıra:* [Modül 1](./modules/01-cryptography/) (Alan Teorisi, BLS & KZG) $\rightarrow$ [Modül 5](./modules/05-layer2-modular-rollups/) (zkEVM Mimarileri) $\rightarrow$ [Modül 12](./modules/12-zero-knowledge-circuits/) (R1CS, Plonkish & Circom Devreleri) $\rightarrow$ [Modül 15](./modules/15-post-quantum-cryptography/) (Kafes Tabanlı ML-DSA).
    *   *Hedef:* ZK devreleri yazmak, rollup proverları geliştirmek, kuantum dirençli protokoller tasarlamak.
*   **Rota E: Paylaşımlı Güvenlik & AVS Mimarı (Restaking & Shared Security Track)**
    *   *Sıra:* [Modül 2](./modules/02-distributed-systems-consensus/) (Konsensüs) $\rightarrow$ [Modül 10](./modules/10-client-engineering-node-ops/) (Node Ops) $\rightarrow$ [Modül 13](./modules/13-restaking-shared-security/) (EigenLayer/Symbiotic AVS & Slashing).
    *   *Hedef:* Merkeziyetsiz AVS ağları kurmak, operatör koordinatörü yazmak ve slashing risk modelleri geliştirmek.
*   **Rota F: Niyetler & Çözücü Mühendisi (Intents & Solvers Track)**
    *   *Sıra:* [Modül 4](./modules/04-smart-contract-patterns/) (Permit2 & ERC-4337) $\rightarrow$ [Modül 7](./modules/07-mev-mempool-engineering/) (MEV & Arbitraj) $\rightarrow$ [Modül 14](./modules/14-intents-solvers-erc7683/) (ERC-7683 Çapraz Zincir Çözücüler).
    *   *Hedef:* CoW batch açık artırmaları çalıştırmak, gazsız kullanıcı deneyimi ve çapraz zincir likidite çözücüleri yazmak.

---

## 🔐 Modül 1: Kriptografik Temeller & Matematik
📁 **Detaylı Rehber ve Kodlar:** [`modules/01-cryptography/`](./modules/01-cryptography/)

*   **Eliptik Eğri Kriptografisi (ECC):**
    *   Sonlu alanlar (Finite Fields) ve grup teorisi temelleri.
    *   `secp256k1` (Bitcoin, Ethereum), `Ed25519` (Solana) matematiği.
    *   BLS12-381 pairing-friendly eğrileri ve eşleşme tabanlı kriptografi.
*   **İmza Şemaları:**
    *   ECDSA, EdDSA, Schnorr İmzaları (Taproot mekanizması).
    *   BLS İmzaları ve imza birleştirme (Signature Aggregation).
*   **Doğrulama & Veri Ağaçları:**
    *   Merkle Trees ve Merkle Proof üretimi.
    *   Verkle Trees: 256-ary vektör taahhütleri ve $O(1)$ boyutlu stateless ispatlar.
    *   Kate-Zaverucha-Goldberg (KZG) Polinom Taahhütleri.
*   **Sıfır Bilgi İspatları (Zero-Knowledge Proofs - ZKP):**
    *   Etkileşimli ve Etkileşimsiz Argümanlar (SNARK vs STARK).
    *   Aritmetizasyon: R1CS, Plonkish Arithmetization, AIR.
*   💻 **Çalıştırılabilir Kodlar:**
    *   [`secp256k1_ecdsa_demo.py`](./modules/01-cryptography/secp256k1_ecdsa_demo.py): Sıfırdan sonlu alan ve ECDSA motoru.
    *   [`bls_signature_aggregation.py`](./modules/01-cryptography/bls_signature_aggregation.py): Ethereum Beacon Chain BLS imza birleştirme motoru.
    *   [`verkle_tree_simulator.py`](./modules/01-cryptography/verkle_tree_simulator.py): 256-ary Verkle tree ve stateless tanık (witness) sıkıştırma simülatörü.
    *   [`merkle_tree.py`](./modules/01-cryptography/merkle_tree.py): OpenZeppelin uyumlu Merkle tree ve audit proof motoru.
    *   [`kzg_polynomial_commitment.py`](./modules/01-cryptography/kzg_polynomial_commitment.py): KZG taahhüt ve açılış ispatı simülatörü.

---

## 🌐 Modül 2: Dağıtık Sistemler, Ağ Katmanı & Konsensüs
📁 **Detaylı Rehber ve Kodlar:** [`modules/02-distributed-systems-consensus/`](./modules/02-distributed-systems-consensus/)

*   **Ağ Katmanı & P2P İletişim:**
    *   Kademlia Dağıtık Hash Tabloları (DHT) ve XOR metriği.
    *   `libp2p` protokol ailesi, DiscV5 (Node Discovery Protocol).
    *   Gossipsub v1.1 mekaniği, peer scoring ve mesaj yayılım gecikmeleri.
*   **Konsensüs Mekanizmaları:**
    *   Nakamoto Consensus (Proof of Work, Fork-choice kuralları, Longest-chain rule).
    *   Klasik Bizans Hata Toleransı (PBFT, Tendermint / CometBFT).
    *   Modern Hibrit Konsensüs: Ethereum PoS (LMD-GHOST + Casper FFG - Gasper mimarisi).
*   💻 **Çalıştırılabilir Kodlar:**
    *   [`gossipsub_network_sim.py`](./modules/02-distributed-systems-consensus/gossipsub_network_sim.py): 100 düğümlü Gossipsub mesh simülasyonu.
    *   [`casper_ffg_lmd_ghost_sim.py`](./modules/02-distributed-systems-consensus/casper_ffg_lmd_ghost_sim.py): Gasper konsensüs, LMD-GHOST head ve FFG kesinleşme motoru.

---

## ⚙️ Modül 3: Sanal Makineler (EVM, SVM, Move VM)
📁 **Detaylı Rehber ve Kodlar:** [`modules/03-virtual-machines/`](./modules/03-virtual-machines/)

*   **Ethereum Virtual Machine (EVM) Derinlemesine:**
    *   256-bit yığın tabanlı (stack-based) mimari sınırları.
    *   Stack, Memory, Storage, Calldata ve Transient Storage (`TSTORE`/`TLOAD` - EIP-1153 Cancun).
    *   Memory quadratic expansion formülü: $\text{Cost}(a) = 3a + \lfloor a^2 / 512 \rfloor$.
    *   Storage Layout: Packed slots, bitmap dizilimleri, mapping/array çakışma riskleri.
*   **Solana Sealevel (SVM):**
    *   Account-based veri modeli (State ve kodun ayrılması).
    *   Önceden bildirilen okuma/yazma kilitleri ile donanım düzeyinde paralel yürütme.
*   **Move Sanal Makinesi (Move VM):**
    *   Doğrusal Mantık (Linear Logic) ve Kaynak Odaklı Programlama.
*   💻 **Referans Sözleşmeler & Kodlar:**
    *   [`svm_parallel_runtime_sim.py`](./modules/03-virtual-machines/svm_parallel_runtime_sim.py): Solana Sealevel paralel işlem çatışma tespiti ve çok çekirdekli yürütme simülatörü.
    *   [`TransientStorageReentrancyGuard.sol`](./modules/03-virtual-machines/contracts/TransientStorageReentrancyGuard.sol): 100 gas maliyetli EIP-1153 reentrancy kilidi.
    *   [`YulMinimalERC20.sol`](./modules/03-virtual-machines/contracts/YulMinimalERC20.sol): Saf Yul Assembly ile yazılmış ultra-optimize ERC-20.
    *   [`StoragePackingDemo.sol`](./modules/03-virtual-machines/contracts/StoragePackingDemo.sol): Storage packing ve bitmap bitwise operasyonları.

---

## 🛠️ Modül 4: Akıllı Sözleşme Geliştirme & Gas Optimizasyonu
📁 **Detaylı Rehber ve Kodlar:** [`modules/04-smart-contract-patterns/`](./modules/04-smart-contract-patterns/)

*   **Geliştirme Araç Seti & Standartlar:**
    *   **Foundry:** `forge` (hızlı test/derleme), `cast` (RPC etkileşimi), `anvil` (yerel node).
    *   **ERC-4337 Account Abstraction:** Akıllı cüzdanlar, `validateUserOp`, paymaster gas sponsorluğu ve 2D nonceler.
    *   **Uniswap Permit2:** İmza tabanlı izinler, süreli yetkilendirmeler ve front-running koruması.
*   **Sözleşme Yükseltilebilirlik Kalıpları (Upgradability):**
    *   Transparent Upgradeable Proxy vs Universal Upgradeable Proxy Standard (UUPS - ERC-1822).
    *   Minimal Proxy Standardı (EIP-1167) 45-baytlık klon mimarisi.
    *   ERC-2535 Diamond Standard ve Diamond Storage deseni.
*   💻 **Referans Sözleşmeler:**
    *   [`ERC4337AccountAbstraction.sol`](./modules/04-smart-contract-patterns/contracts/ERC4337AccountAbstraction.sol): Üretim seviyesi ERC-4337 akıllı hesap sözleşmesi.
    *   [`Permit2Integration.sol`](./modules/04-smart-contract-patterns/contracts/Permit2Integration.sol): Uniswap Permit2 entegrasyonu ve sıfır-onaylı fon yatırma.
    *   [`UUPSUpgradeableVault.sol`](./modules/04-smart-contract-patterns/contracts/UUPSUpgradeableVault.sol): Üretim seviyesi UUPS kasası ve storage gap rezervi.
    *   [`MinimalProxyFactory.sol`](./modules/04-smart-contract-patterns/contracts/MinimalProxyFactory.sol): EIP-1167 CREATE/CREATE2 minimal klon fabrikası.
    *   [`DiamondStoragePattern.sol`](./modules/04-smart-contract-patterns/contracts/DiamondStoragePattern.sol): Çakışmasız modüler diamond storage yapısı.

---

## 🏗️ Modül 5: L2, Rollup Mimarileri & Modüler Blockchain
📁 **Detaylı Rehber ve Kodlar:** [`modules/05-layer2-modular-rollups/`](./modules/05-layer2-modular-rollups/)

*   **Rollup Temelleri & Görev Ayrımı:**
    *   Execution, Settlement, Consensus ve Data Availability ayrımı.
*   **Optimistic Rollups:**
    *   Fraud Proof (Sahtekarlık İspatı) sistemleri.
    *   Tek turlu vs Çok turlu interaktif iki taraflı bölme (Interactive Bisection).
    *   OP Stack mimarisi (`op-node`, `op-geth`, Cannon VM) ve Arbitrum Nitro.
*   **Zero-Knowledge (ZK) Rollups:**
    *   Validity Proof üretimi ve on-chain doğrulama maliyetleri.
    *   Vitalik Buterin'in 4 seviyeli zkEVM taksonomisi (Type 1'den Type 4'e).
*   **Veri Erişilebilirliği (Data Availability - DA):**
    *   Proto-Danksharding (EIP-4844) Blob Space ve KZG point evaluation precompile `0x0a`.
    *   Data Availability Sampling (DAS) ve 2D Reed-Solomon silinti kodlaması (Erasure Coding).
*   💻 **Çalıştırılabilir Kodlar:**
    *   [`interactive_fraud_proof_bisection.py`](./modules/05-layer2-modular-rollups/interactive_fraud_proof_bisection.py): $O(\log N)$ adımlı interaktif sahtekarlık ispatı simülatörü.
    *   [`das_erasure_coding_sim.py`](./modules/05-layer2-modular-rollups/das_erasure_coding_sim.py): 2D Reed-Solomon Data Availability Sampling (DAS) hafif düğüm simülatörü.
    *   [`blob_gas_calculator.py`](./modules/05-layer2-modular-rollups/blob_gas_calculator.py): EIP-4844 blob gas fiyatı ve calldata karşılaştırma motoru.

---

## 🛡️ Modül 6: Güvenlik, Denetim (Audit) & Formal Doğrulama
📁 **Detaylı Rehber ve Kodlar:** [`modules/06-security-audit-formal-verification/`](./modules/06-security-audit-formal-verification/)

*   **En Kritik Açık Vektörleri:**
    *   Reentrancy: Single-function, Cross-function ve Cross-contract Read-only Reentrancy.
    *   DeFi Matematik Hataları: Precision loss, rounding direction hataları, strict equality (`==`) riskleri.
    *   Fiyat Manipülasyonları: Spot DEX havuzlarından fiyat çekme, AMM TWAP süresi manipülasyonları.
    *   Erişim Kontrolü (Access Control): Missing modifier, uninitialized logic contracts.
*   **Statik & Dinamik Güvenlik Araçları:**
    *   Statik Analiz: Slither, Aderyn (Rust tabanlı AST analizcisi).
    *   Fuzzing: Echidna, Medusa, Foundry invariant testing.
    *   Formal Doğrulama (Formal Verification): Certora Prover (CVL), Halmos ve SMTChecker.
*   💻 **Referans Dosyalar:**
    *   [`AUDIT_CHECKLIST.md`](./modules/06-security-audit-formal-verification/AUDIT_CHECKLIST.md): 120+ maddelik kapsamlı akıllı sözleşme denetim kontrol listesi.
    *   [`Certora_Spec_Example.cvl`](./modules/06-security-audit-formal-verification/Certora_Spec_Example.cvl): Solvency kuralları formal spesifikasyon dosyası.
    *   [`Halmos_Formal_Verification_Test.sol`](./modules/06-security-audit-formal-verification/Halmos_Formal_Verification_Test.sol): Halmos sembolik test şablonu.

---

## ⚡ Modül 7: MEV, Mempool Mühendisliği & Node Operasyonu
📁 **Detaylı Rehber ve Kodlar:** [`modules/07-mev-mempool-engineering/`](./modules/07-mev-mempool-engineering/)

*   **Maximal Extractable Value (MEV):**
    *   Searcher, Builder, Relay ve Proposer (Validator) ekosistemi.
    *   PBS (Proposer-Builder Separation) mimarisi ve MEV-Boost protokolü.
    *   Arbitraj, Sandwich Attacks, Tasfiye ve JIT likidite stratejileri.
*   **Mempool Dinamikleri:**
    *   P2P Transaction propagation, txpool yönetimi ve Priority Gas Auctions (PGA).
    *   Özel RPC sistemleri: Flashbots Protect, MEV-Share, SUAVE.
*   💻 **Çalıştırılabilir Kodlar:**
    *   [`bellman_ford_arbitrage.py`](./modules/07-mev-mempool-engineering/bellman_ford_arbitrage.py): Havuzlar arası negatif döngü arayan Bellman-Ford çapraz-DEX arbitraj motoru.
    *   [`sandwich_attack_sim.py`](./modules/07-mev-mempool-engineering/sandwich_attack_sim.py): Optimal front-run/back-run boyutu hesaplayan ve kâr realize eden sandwich simülatörü.
    *   [`jit_liquidity_simulator.py`](./modules/07-mev-mempool-engineering/jit_liquidity_simulator.py): Uniswap v3 Just-In-Time (JIT) likidite MEV saldırısı simülatörü.

---

## 💥 Modül 8: DeFi Hack PoC Laboratuvarı
📁 **Detaylı Rehber ve Kodlar:** [`modules/08-defi-hack-pocs/`](./modules/08-defi-hack-pocs/)

*   **Gerçek Dünyadan İstismar Simülasyonları:**
    *   **Euler Finance Tarzı Read-Only Reentrancy:** AMM havuzunun ara durumundaki sanal fiyat bozulmasıyla kredi protokolünü boşaltma.
    *   **Flash Loan Spot Fiyat Manipülasyonu:** Anlık rezervleri bozan saldırganın teminatsız kredi çekerek hazineyi soyması.
    *   **ERC-4626 İlk Yatıran Enflasyon Saldırısı:** 1 wei yatırıp büyük bağış yaparak sonraki kullanıcıların paylarını sıfıra yuvarlama ve paralarını çalma.
    *   **Beanstalk Tarzı Flash Loan Yönetişim Darbesi (Governance Hijack):** Anlık oylarla hazineyi boşaltma ve ERC20Votes kontrol noktası savunması.
    *   **EIP-2612 İmza Tekrarı (Signature Replay):** Statik domain separator ve zincir çatallanmalarında imza istismarı.
*   💻 **Referans Sözleşmeler:**
    *   [`ReadOnlyReentrancyPoC.sol`](./modules/08-defi-hack-pocs/contracts/ReadOnlyReentrancyPoC.sol): Savunmasız havuz, istismar senaryosu ve Cancun transient lock ile düzeltilmiş havuz.
    *   [`FlashLoanPriceManipulationPoC.sol`](./modules/08-defi-hack-pocs/contracts/FlashLoanPriceManipulationPoC.sol): Spot fiyat açığı ve TWAP oracle savunması.
    *   [`ERC4626InflationAttackPoC.sol`](./modules/08-defi-hack-pocs/contracts/ERC4626InflationAttackPoC.sol): Enflasyon saldırısı ve sanal pay (virtual shares) savunması.
    *   [`GovernanceFlashLoanHijackPoC.sol`](./modules/08-defi-hack-pocs/contracts/GovernanceFlashLoanHijackPoC.sol): Flash loan yönetişim saldırısı ve `getPastVotes` geçmiş blok kontrol noktası savunması.
    *   [`SignatureReplayPermitPoC.sol`](./modules/08-defi-hack-pocs/contracts/SignatureReplayPermitPoC.sol): Dinamik EIP-712 domain separator ve imza tekrarı koruması.

---

## 🚀 Modül 9: Üretim Ortamı Kontrol Listesi (Mainnet Readiness Checklist)
📁 **Detaylı Rehber:** [`modules/09-production-checklist/MAINNET_READINESS_CHECKLIST.md`](./modules/09-production-checklist/MAINNET_READINESS_CHECKLIST.md)

12 aşamalı ana ağa çıkış kontrol listesi:
1. Mimari & Tehdit Modellemesi Onayı
2. Test Kapsamı ($> 95\%$) & Invariant Fuzzing
3. Bağımsız Güvenlik Denetimleri & Rekabetçi Audit Yarışmaları
4. Formal Doğrulama (Certora / Halmos)
5. Dağıtım Scriptleri & CREATE2 Deterministik Adresleme
6. Safe Multisig & TimelockController Entegrasyonu
7. Acil Durum Duraklatma (Pausable) & Devre Kesiciler
8. Oracle Güvenliği, Yedekleme & L2 Sequencer Kontrolleri
9. Canlı İzleme & Tehdit Tespiti (Forta / Tenderly)
10. Bug Bounty Programı (Immunefi)
11. Likidite Başlatma & MEV/Slippage Korumaları
12. Dağıtım Sonrası Doğrulama ve Şeffaflık

---

## 🖥️ Modül 10: İstemci Mühendisliği, Depolama Motorları & Node Operasyonu
📁 **Detaylı Rehber ve Kodlar:** [`modules/10-client-engineering-node-ops/`](./modules/10-client-engineering-node-ops/)

*   **Execution Layer (EL) vs Consensus Layer (CL):**
    *   İstemci mimarileri: Reth (Rust), Geth (Go), Nethermind (C#), Lighthouse, Prysm.
    *   Durum Depolama Motorları: MDBX (B+ Tree, zero-copy `mmap`) vs RocksDB (LSM-Tree).
*   **Engine API Protokolü:**
    *   `8551` portu üzerinden HMAC-SHA256 JWT yetkilendirmesi.
    *   `engine_forkchoiceUpdatedV3`, `engine_newPayloadV3`, `engine_getPayloadV3` yürütme döngüsü.
*   **Düğüm Senkronizasyonu:**
    *   Snap Sync, Full Archive Node, Stateless Node modelleri.
*   💻 **Çalıştırılabilir Kodlar:**
    *   [`engine_api_rpc_mock.py`](./modules/10-client-engineering-node-ops/engine_api_rpc_mock.py): JWT HS256 kimlik doğrulamalı ve forkchoice yürütmeli Engine API mock sunucusu.

---

## 🌉 Modül 11: Çapraz Zincir Mimarileri, Köprüler & Birlikte Çalışabilirlik
📁 **Detaylı Rehber ve Kodlar:** [`modules/11-cross-chain-bridges/`](./modules/11-cross-chain-bridges/)

*   **Birlikte Çalışabilirlik Trilemması:** Trustless, Generalizable ve Extensible mimari sınırları.
*   **Köprü Güvenlik Modelleri:**
    *   Multisig / MPC Köprüleri (Ronin, Wormhole).
    *   Optimistic Köprüler ve Nomad $190M sıfır kök (0x00) açığı analizi.
    *   Cosmos IBC (Inter-Blockchain Communication): TCP/IP for blockchains.
    *   LayerZero v2 DVN'leri ve Chainlink CCIP Risk Management Network.
*   💻 **Referans Sözleşmeler & Kodlar:**
    *   [`CrossChainBridgeVulnerableAndSecure.sol`](./modules/11-cross-chain-bridges/contracts/CrossChainBridgeVulnerableAndSecure.sol): Nomad 0x00 kök açığı simülasyonu ve EIP-712 imzalı güvenli köprü sözleşmesi.
    *   [`ibc_light_client_sim.py`](./modules/11-cross-chain-bridges/ibc_light_client_sim.py): Cosmos IBC 4 aşamalı bağlantı el sıkışması ve ışık istemci paket doğrulama simülatörü.

---

## ⚡ Modül 12: Sıfır Bilgi İspatları & ZK Devre Mühendisliği
📁 **Detaylı Rehber ve Kodlar:** [`modules/12-zero-knowledge-circuits/`](./modules/12-zero-knowledge-circuits/)

*   **Hesaplamadan SNARK'a Aritmetizasyon Boru Hattı:**
    *   Program Düzleştirme (Flattening) ve R1CS (Rank-1 Constraint Systems).
    *   Plonkish Aritmetizasyon ve Lookup Tabloları (Plookup, LogUp) ile Keccak/SHA-256 hızlandırma.
    *   Özyinelemeli İspatlar (Recursive SNARKs) ve Nova Katlama Şemaları (Folding Schemes).
    *   Modern Devre Çerçeveleri: Circom, Halo2 (Rust), Noir (Aztec).
*   💻 **Referans Devreler & Kodlar:**
    *   [`r1cs_arithmetization_engine.py`](./modules/12-zero-knowledge-circuits/r1cs_arithmetization_engine.py): Polinom düzleştirme, $A, B, C$ matris inşası ve tanık doğrulama motoru.
    *   [`hasher_preimage.circom`](./modules/12-zero-knowledge-circuits/circuits/hasher_preimage.circom): Gizli girdi (preimage) bilgisini kanıtlayan üretim standardı Circom devresi.

---

## 💎 Modül 13: Yeniden Stake Etme, Paylaşımlı Güvenlik & AVS
📁 **Detaylı Rehber ve Kodlar:** [`modules/13-restaking-shared-security/`](./modules/13-restaking-shared-security/)

*   **Paylaşımlı Güvenlik & Restaking Paradigması:**
    *   EigenLayer & Symbiotic mimari ve çekirdek farkları.
    *   AVS (Actively Validated Services) görev orkestrasyonu ve $\%67$ kuorum konsensüsü.
    *   Objektif vs Subjektif Slashing ve kaskat sermaye bulaşma riskleri (Cascading Contagion).
*   💻 **Referans Sözleşmeler & Kodlar:**
    *   [`AVSSlashingCoordinator.sol`](./modules/13-restaking-shared-security/contracts/AVSSlashingCoordinator.sol): AVS operatör delegasyonu, görev doğrulama ve zincir üstü slashing koordinatörü.
    *   [`eigenlayer_restaking_sim.py`](./modules/13-restaking-shared-security/eigenlayer_restaking_sim.py): Çoklu AVS paylaşımı, ağırlıklı kuorum konsensüsü ve kaskat slashing riski simülatörü.

---

## 🎯 Modül 14: Niyet Odaklı Mimariler, Çözücüler & ERC-7683
📁 **Detaylı Rehber ve Kodlar:** [`modules/14-intents-solvers-erc7683/`](./modules/14-intents-solvers-erc7683/)

*   **İşlem (Imperative) vs Niyet (Declarative Intent):**
    *   UniswapX ve Across tarafından geliştirilen ERC-7683 Çapraz Zincir Niyet Standardı.
    *   Hollanda Açık Artırması (Dutch Auction) fiyat azalımı ve kullanıcı kâr fazlalığı (Surplus).
    *   Çözücü (Solver) ekonomisi, CEX arbitrajı ve CoW (Coincidence of Wants) eşleşmesi.
*   💻 **Referans Sözleşmeler & Kodlar:**
    *   [`ERC7683CrossChainSettler.sol`](./modules/14-intents-solvers-erc7683/contracts/ERC7683CrossChainSettler.sol): ERC-7683 Origin Escrow ve Destination Settler sözleşmesi.
    *   [`intent_solver_auction_sim.py`](./modules/14-intents-solvers-erc7683/intent_solver_auction_sim.py): Hollanda açık artırması fiyat azalımı ve rekabetçi çözücü simülasyonu.

---

## 🛡️ Modül 15: Kuantum Sonrası Kriptografi & Hibrit Durum Makineleri
📁 **Detaylı Rehber ve Kodlar:** [`modules/15-post-quantum-cryptography/`](./modules/15-post-quantum-cryptography/)

*   **Kuantum Tehditleri:**
    *   Shor Algoritması ile $O(\log^3 N)$ sürede `secp256k1` eliptik eğri özel anahtarının kırılması.
    *   Grover Algoritması ile hash fonksiyonu arama uzayının karekök indirgemesi ($2^{256} \rightarrow 2^{128}$).
*   **Kafes Tabanlı Kriptografi (Lattice-Based NIST FIPS):**
    *   Module-LWE, Inhomogeneous Short Integer Solution (ISIS) ve $R_q = \mathbb{Z}_q[X]/(X^n + 1)$ halka cebiri.
    *   NIST FIPS 204 ML-DSA (Dilithium) dijital imza standardı ve red örneklemesi (rejection sampling).
    *   ERC-4337 Hesap Soyutlama üzerinden ECDSA + ML-DSA Hibrit (Dual) imza doğrulama geçiş mimarisi.
*   💻 **Çalıştırılabilir Kodlar:**
    *   [`post_quantum_lattice_signatures.py`](./modules/15-post-quantum-cryptography/post_quantum_lattice_signatures.py): Halka polinom aritmetiği, LWE anahtar üretimi, ML-DSA imzalama/doğrulama ve kuantum dayanımlı hibrit hesap motoru.

---

## 📦 Kurulum, Doğrulama ve Benchmark

Tüm modüllerdeki simülasyonları tek bir komutla doğrulamak ve performans metriklerini görmek için yerleşik Benchmark CLI motorunu çalıştırabilirsiniz:

```bash
# Depoyu klonlayın
git clone https://github.com/bahattinyunus/Ultimate-Blockchain-Protocol-Engineering-Compendium.git
cd Ultimate-Blockchain-Protocol-Engineering-Compendium

# Tüm 20 protokol simülasyonunu tek seferde test edin ve benchmark tablosunu görün:
python compendium_benchmark_cli.py

# Belirli bir modülü filtreleyerek çalıştırın (Örn: quantum, mev, restaking, zkp):
python compendium_benchmark_cli.py --filter quantum
python compendium_benchmark_cli.py --filter restaking
python compendium_benchmark_cli.py --filter mev
```

---

## 📄 Lisans
Bu proje [MIT Lisansı](./LICENSE) altında açık kaynak olarak sunulmaktadır.
