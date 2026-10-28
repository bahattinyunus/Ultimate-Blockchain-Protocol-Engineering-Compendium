# Modül 5: L2, Rollup Mimarileri & Modüler Blockchain (Layer 2 & Modular Rollups)

Bu modül, blokzincirlerin ölçeklenebilirlik trilemmasını (Ölçeklenebilirlik, Güvenlik, Merkeziyetsizlik) aşmak için uyguladığı Rollup mekanizmalarını, dolandırıcılık/geçerlilik ispatlarını ve modüler veri erişilebilirlik (DA) katmanlarını detaylandırır.

---

## 📌 İçindekiler
1. [Modüler Blockchain Ayrımı](#1-modüler-blockchain-ayrımı)
2. [Optimistic Rollup Mimarisi ve Sahtekarlık İspatları (Fraud Proofs)](#2-optimistic-rollup-mimarisi-ve-sahtekarlık-ispatları-fraud-proofs)
3. [Zero-Knowledge Rollup (zkEVM) Taksonomisi](#3-zero-knowledge-rollup-zkevm-taksonomisi)
4. [EIP-4844 Proto-Danksharding & Blob Space](#4-eip-4844-proto-danksharding--blob-space)
5. [Veri Erişilebilirliği Örneklemesi (Data Availability Sampling - DAS)](#5-veri-erişilebilirliği-örneklemesi-data-availability-sampling---das)
6. [Simülatörler ve Hesaplama Araçları](#6-simülatörler-ve-hesaplama-araçları)

---

## 1. Modüler Blockchain Ayrımı

Monolitik blokzincirler (ör. Solana, ilk Ethereum) dört temel görevi tek katmanda icra eder:
1. **Execution (Yürütme):** Durum değişikliklerinin ve işlemlerin çalıştırılması.
2. **Settlement (Uzlaşma / Çözümleme):** Anlaşmazlıkların çözülmesi, L2 ispatlarının doğrulanması.
3. **Consensus (Konsensüs):** İşlem sırasının (ordering) belirlenmesi.
4. **Data Availability (DA - Veri Erişilebilirliği):** İşlem verilerinin herkes tarafından indirilebilir olduğunun garanti edilmesi.

Modüler blokzincirlerde bu görevler uzmanlaşmış katmanlara paylaştırılır:
- Rollup = Yalnızca Yürütme (Execution).
- Ethereum = Settlement + Consensus.
- Celestia / EigenDA / Ethereum Blobs = Data Availability.

---

## 2. Optimistic Rollup Mimarisi ve Sahtekarlık İspatları (Fraud Proofs)

Optimistic rolluplarda işlemlerin doğru olduğu varsayılır (iyimser yaklaşım). $7$ günlük meydan okuma süresi (challenge window) vardır.

### Tek Turlu (Single-Round) vs Çok Turlu İnteraktif (Multi-Round Bisection)
- **Tek Turlu (Eski Arbitrum):** L1 sözleşmesi tüm L2 işlemini yeniden yürütür. L1 gas limiti nedeniyle blok boyutları kısıtlanır.
- **İnteraktif İki Taraflı Bölme (Interactive Bisection - Arbitrum Nitro / OP Cannon):**
  - İddia Sahibi (Asserter) ve İtiraz Eden (Challenger) $N$ adımlık yürütme izini (execution trace) ortadan ikiye bölerek tartışır.
  - $\log_2(N)$ turda anlaşmazlık tek bir CPU talimatına (instruction opcode) indirgenir.
  - L1 üzerindeki `OneStepProver` sözleşmesi sadece o tek adımı çalıştırarak haksız olan tarafın teminatını (bond) yakar.

---

## 3. Zero-Knowledge Rollup (zkEVM) Taksonomisi

Vitalik Buterin'in 4 seviyeli zkEVM sınıflandırması:

| Seviye | Tanım | Örnekler | Artılar | Eksiler |
| :--- | :--- | :--- | :--- | :--- |
| **Type 1** | Tam Ethereum Eşdeğeri | Taiko, PSE zkEVM | L1 ile %100 mutlak konsensüs uyumu. | İspat üretimi saatler sürer (aşırı yavaş). |
| **Type 2** | EVM Eşdeğeri | Scroll, Polygon zkEVM | Solidity araçları ve bytecode ile tam uyumlu. | Veri yapıları ve hash fonksiyonları ispatı yavaşlatır. |
| **Type 3** | Neredeyse EVM | Eski zkEVM sürümleri | Daha hızlı ispat üretimi. | Bazı EVM opkodları kaldırılmış veya değiştirilmiştir. |
| **Type 4** | Yüksek Seviye Dil Eşdeğeri | zkSync Era, Starknet (Cairo) | Çok hızlı ZK ispat üretimi, modern mimari. | Solidity bayt kodu doğrudan çalışmaz; transpile gerekir. |

---

## 4. EIP-4844 Proto-Danksharding & Blob Space

Cancun güncellemesi ile Ethereum'a **Blob-carrying Transactions** (Type 3 transactions) eklenmiştir:
- Her blok maksimum 6 blob (hedef: 3 blob) taşıyabilir.
- Her blob tam olarak **128 KB** veri barındırır.
- Bloblar EVM yürütme katmanı tarafından doğrudan okunamaz (geçici veri - 18 gün sonra düğümler tarafından silinir).
- EVM sadece blob'un KZG taahhüdünü doğrulamak için `0x0a` precompile'ını (`point_evaluation_precompile`) kullanır.
- Bağımsız Blob Gas pazarı EIP-1559 benzeri dinamik fiyat ayarlar.

---

## 5. Veri Erişilebilirliği Örneklemesi (Data Availability Sampling - DAS)

Hafif düğümlerin (light nodes) tüm 100 MB'lık blokları indirmeden verinin erişilebilir olduğunu kanıtlaması:
1. Blok verisi **Reed-Solomon Silinti Kodlaması (Erasure Coding)** ile 2 katına genişletilir.
2. Verinin herhangi bir $\%50$'si mevcutsa tüm veri yeniden inşa edilebilir.
3. Düğüm rastgele $k$ adet parça (chunk) sorgular. Kötü niyetli bir blok üreticisinin verinin $\%50$'sini gizlemesi durumunda tespit edilememe olasılığı:
   $$P(\text{fail}) = \left(\frac{1}{2}\right)^k$$
   $k = 30$ sorgu yapıldığında tespit edilememe olasılığı $2^{-30} \approx 10^{-9}$ (milyarda bir) olur.

---

## 6. Simülatörler ve Hesaplama Araçları

- [`interactive_fraud_proof_bisection.py`](./interactive_fraud_proof_bisection.py): $N$-adımlık yürütme izinde $O(\log N)$ adımlı iki taraflı bölme (bisection) protokolü simülasyonu.
- [`blob_gas_calculator.py`](./blob_gas_calculator.py): EIP-4844 blob gas fiyatlandırma formülü ve Calldata vs Blob maliyet karşılaştırma motoru.
