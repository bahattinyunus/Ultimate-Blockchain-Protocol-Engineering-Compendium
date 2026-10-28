# Modül 3: Sanal Makineler (Virtual Machines - EVM, SVM, Move VM)

Bu modül, akıllı sözleşmelerin çalıştırıldığı yürütme motorlarının (Virtual Machines) mimari farklılıklarını, bellek modellerini ve hesaplama modellerini inceler.

---

## 📌 İçindekiler
1. [Ethereum Virtual Machine (EVM) Mimarisi](#1-ethereum-virtual-machine-evm-mimarisi)
2. [EVM Bellek Bölgeleri ve Gaz Modeli](#2-evm-bellek-bölgeleri-ve-gaz-modeli)
3. [Solana Sealevel (SVM): Hesap Modeli ve Paralel Yürütme](#3-solana-sealevel-svm-hesap-modeli-ve-paralel-yürütme)
4. [Move VM: Doğrusal Mantık ve Kaynak Odaklı Programlama](#4-move-vm-doğrusal-mantık-ve-kaynak-odaklı-programlama)
5. [EVM vs SVM vs Move VM Karşılaştırma Matrisi](#5-evm-vs-svm-vs-move-vm-karşılaştırma-matrisi)
6. [Referans Akıllı Sözleşmeler](#6-referans-akıllı-sözleşmeler)

---

## 1. Ethereum Virtual Machine (EVM) Mimarisi

EVM, **256-bit kelime uzunluğuna (word size)** sahip, **yığın tabanlı (stack-based)** bir Turing-tam sanal makinedir:
- **Stack (Yığın):** Maksimum 1024 eleman derinliği. İşlemler yığının en üstündeki elemanlar üzerinde gerçekleşir (`DUP`, `SWAP`, `ADD`, `MUL`). 16 elemandan daha derine erişmeye çalışmak *"Stack too deep"* hatasına neden olur.
- **Memory (Geçici Bellek):** Byte adreslenebilir, çağrı (call) süresince yaşayan lineer bellek. Genişledikçe gaz maliyeti karesel (quadratic) artar:
  $$\text{Cost}(a) = 3 \cdot a + \left\lfloor \frac{a^2}{512} \right\rfloor \quad (a = \text{32-byte kelime sayısı})$$
- **Storage (Kalıcı Depolama):** $2^{256}$ adet 32-byte yuvadan (slot) oluşan anahtar-değer deposu. En pahalı EVM bölgesidir (soğuk SLOAD 2100 gas, ilk SSTORE 20000 gas).
- **Calldata:** İşlem girdilerinin bulunduğu salt-okunur (read-only) bayt dizisi.
- **Transient Storage (EIP-1153 - Cancun):** `TSTORE` ve `TLOAD` opkodları ile çalışan, yalnızca işlem (transaction) süresince geçerli ve işlem bitince silinen geçici depolama. Maliyeti sadece **100 gas**'tır.

---

## 2. EVM Bellek Bölgeleri ve Gaz Modeli

```mermaid
flowchart LR
    subgraph Execution Context
        ST[Stack: max 1024 words]
        MEM[Memory: Linear Byte Array]
        TS[Transient Storage: TSTORE / TLOAD 100 gas]
    end

    subgraph Persistent State
        STORAGE[Persistent Storage: 2^256 Slots]
        CODE[Contract Bytecode]
    end

    CALL[External Calldata] --> Execution Context
    Execution Context <--> STORAGE
```

---

## 3. Solana Sealevel (SVM): Hesap Modeli ve Paralel Yürütme

EVM'in sıralı (single-threaded) yürütme kısıtına karşılık SVM:
1. **State ve Kodun Ayrılması:** Akıllı sözleşmeler (Programs) durum (state) tutmaz; tamamen *stateless* executable bayt dizileridir. Durum, bağımsız "Account" yapılarında saklanır.
2. **Önceden Bildirilen Erişim Listeleri:** Her işlem hangi hesapları salt-okunur (`read-only`) ve hangilerini yazılabilir (`writable`) olarak kullanacağını peşinen bildirir.
3. **Sealevel Engine:** Çakışmayan hesaplara sahip binlerce işlem donanımın tüm çekirdeklerinde paralel olarak yürütülür.

---

## 4. Move VM: Doğrusal Mantık ve Kaynak Odaklı Programlama

Move (Aptos / Sui), dijital varlıkların "kopyalanamaz ve yok edilemez" fiziksel nesneler gibi davranması gerektiği ilkesiyle tasarlanmıştır:
- **Resource Types (Kaynak Tipleri):** Bir varlık asla sıradan bir tamsayı değildir; kopyalanamaz (`copy` yeteneği verilemez) ve düşürülemez (`drop` yeteneği verilemez).
- **Doğrusal Tip Sistemi (Linear Logic):** Bir token oluşturulduğunda mutlaka bir hesaba transfer edilmeli veya açıkça yok edilmelidir; kod içinde sessizce silinemez veya çift harcanamaz.

---

## 5. EVM vs SVM vs Move VM Karşılaştırma Matrisi

| Özellik | Ethereum EVM | Solana SVM | Move VM (Aptos / Sui) |
| :--- | :--- | :--- | :--- |
| **Yürütme Modeli** | Yığın Tabanlı (Stack-based) | Kayıtçı Tabanlı (eBPF Register) | Yığın Tabanlı / Kaynak Odaklı |
| **İşlem Yürütme** | Tek Kanallı (Single-threaded) | Çok Kanallı Paralel (Sealevel) | Paralel (Block-STM / Sui Object DAG) |
| **Durum (State) Modeli** | MPT & Sözleşme İçi Storage | Ayrı Hesaplar (Accounts) | Modüler Kaynaklar & Nesneler (Objects) |
| **Reentrancy Riski** | Yüksek (Harici çağrılarda açık) | Düşük (Kayıt kilit mekanizması) | İmkansız (Kaynak modeli ve çağrı kısıtları) |
| **Yükseltilebilirlik** | Proxy Desenleri (DELEGATECALL) | Yerel Program Yükseltme | Paket Yükseltme Uyumluluk Kontrolleri |

---

## 6. Referans Akıllı Sözleşmeler

Bu dizindeki Cancun & EVM referans sözleşmeleri:
- [`contracts/TransientStorageReentrancyGuard.sol`](./contracts/TransientStorageReentrancyGuard.sol): EIP-1153 `tstore` / `tload` ile 100 gas maliyetli ultra-optimize reentrancy kilidi.
- [`contracts/YulMinimalERC20.sol`](./contracts/YulMinimalERC20.sol): Saf Yul Assembly ile yazılmış, minimum bayt kodu ve maksimum gas tasarruflu ERC-20 implementasyonu.
- [`contracts/StoragePackingDemo.sol`](./contracts/StoragePackingDemo.sol): Storage slot paketleme, bitmap manipülasyonu ve slot ofset hesaplama.
