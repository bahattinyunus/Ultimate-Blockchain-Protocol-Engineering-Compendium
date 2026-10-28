# Modül 1: Kriptografik Temeller & Matematik (Cryptography & Mathematics)

Bu modül, modern blokzincir sistemlerinin üzerinde yükseldiği matematiksel temelleri, eliptik eğri teorisini, imza protokollerini ve sıfır bilgi ispatı (ZKP) yapılarını derinlemesine inceler.

---

## 📌 İçindekiler
1. [Sonlu Alanlar ve Grup Teorisi](#1-sonlu-alanlar-ve-grup-teorisi)
2. [Eliptik Eğri Kriptografisi (ECC)](#2-eliptik-eğri-kriptografisi-ecc)
3. [Dijital İmza Şemaları (ECDSA, Schnorr, BLS)](#3-dijital-imza-şemaları-ecdsa-schnorr-bls)
4. [Merkle Ağaçları ve Merkle Patricia Trie](#4-merkle-ağaçları-ve-merkle-patricia-trie)
5. [KZG Polinom Taahhütleri ve Verkle Ağaçları](#5-kzg-polinom-taahhütleri-ve-verkle-ağaçları)
6. [Sıfır Bilgi İspatları (ZKP: SNARKs vs STARKs)](#6-sıfır-bilgi-ispatları-zkp-snarks-vs-starks)
7. [Referans Kodlar ve Simülatörler](#7-referans-kodlar-ve-simülatörler)

---

## 1. Sonlu Alanlar ve Grup Teorisi

Kriptografide kullanılan tüm işlemler belirli bir asal sayı $p$ modülünde tanımlı **Galois Alanları** $\mathbb{F}_p$ üzerinde gerçekleşir.

* **Toplamsal Grup:** $(a + b) \pmod p$
* **Çarpımsal Ters:** Genişletilmiş Öklid Algoritması veya Fermat'nın Küçük Teoremi ($a^{p-2} \equiv a^{-1} \pmod p$) ile bulunur.
* **Ayrık Logaritma Problemi (DLP):** $g^x = h \pmod p$ verildiğinde, $g$ ve $h$'den $x$'i bulmak hesaplama açısından zor (intractable) olmalıdır.

---

## 2. Eliptik Eğri Kriptografisi (ECC)

Modern zincirlerde yaygın kullanılan standart Weierstrass formundaki eğriler:

$$y^2 \equiv x^3 + ax + b \pmod p$$

| Zincir / Protokol | Eğri Adı | Denklem | Temel Avantaj |
| :--- | :--- | :--- | :--- |
| **Bitcoin / Ethereum** | `secp256k1` | $y^2 = x^3 + 7 \pmod p$ | Koblitz eğrisi; özel $a=0$ yapısı ile verimli skaler çarpım. |
| **Solana / Polkadot** | `Ed25519` (Twisted Edwards) | $-x^2 + y^2 = 1 - \frac{121665}{121666}x^2y^2$ | Yan kanal saldırılarına (side-channel) karşı tam bağışıklık, hızlı doğrulama. |
| **Ethereum PoS / ZK** | `BLS12-381` | Pairing-friendly | İmzaların birleştirilebilirliği (aggregation) ve KZG taahhütleri. |

### Nokta Toplama ve İkiye Katlama (Point Addition & Doubling)
İki nokta $P(x_1, y_1)$ ve $Q(x_2, y_2)$ için:

$$\lambda = \begin{cases} \frac{y_2 - y_1}{x_2 - x_1} \pmod p, & P \neq Q \\ \frac{3x_1^2 + a}{2y_1} \pmod p, & P = Q \end{cases}$$

$$x_3 = \lambda^2 - x_1 - x_2 \pmod p, \quad y_3 = \lambda(x_1 - x_3) - y_1 \pmod p$$

---

## 3. Dijital İmza Şemaları (ECDSA, Schnorr, BLS)

1. **ECDSA (Elliptic Curve Digital Signature Algorithm):**
   - Ethereum ve Bitcoin standardı.
   - Rastgele nonce $k$'nın zayıflığı (Sony PS3 açığı gibi) özel anahtarın ($d_A$) anında ifşa olmasına yol açar:
     $$s = k^{-1}(z + r \cdot d_A) \pmod n$$
2. **Schnorr İmzaları (BIP-340 / Taproot):**
   - Doğrusal yapı: $s = k + e \cdot x$.
   - **MuSig / İmza Birleştirme:** Birden fazla imza tek bir $64$-byte imzaya indirgenebilir.
3. **BLS İmzaları (Boneh-Lynn-Shacham):**
   - Eşleşme (Pairing) tabanlı: $e(P, Q) = e(G, \text{PK})$.
   - Ethereum konsensüs katmanında binlerce validatörün onayını tek bir $96$-byte agregasyon imzasına sıkıştırmayı sağlar.

---

## 4. Merkle Ağaçları ve Merkle Patricia Trie

- **Binary Merkle Tree:** $O(\log N)$ boyutunda üyelik ispatı (proof).
- **Modified Merkle Patricia Trie (MPT):** Ethereum World State yapısı. Üç tip düğüm:
  1. *Leaf Node:* Key-end ve Value taşır.
  2. *Extension Node:* Ortak önekleri (prefix) sıkıştırır.
  3. *Branch Node:* 16 heksadesimal karakter (`0x0` - `0xf`) ve değer yuvası.

---

## 5. KZG Polinom Taahhütleri ve Verkle Ağaçları

- **KZG (Kate-Zaverucha-Goldberg):** Bir polinom $P(X)$ taahhüdü tek bir grup elemanıdır: $C = [P(\tau)]_1$.
- **Polinom Açıklaması:** $P(z) = y$ olduğunu ispatlamak için bölüm polinomu $Q(X) = \frac{P(X) - y}{X - z}$ hesaplanır ve ispat $\pi = [Q(\tau)]_1$ verilir.
- **Doğrulama Eşleşmesi:**
  $$e(\pi, [\tau - z]_2) = e(C - [y]_1, [1]_2)$$
- Verkle Ağaçları, Merkle ispatlarındaki $O(\log N)$ boyutunu $O(1)$ sabit boyuta indirerek stateless istemcileri mümkün kılar.

---

## 6. Sıfır Bilgi İspatları (ZKP: SNARKs vs STARKs)

| Kriter | zk-SNARKs (Groth16, PLONK) | zk-STARKs |
| :--- | :--- | :--- |
| **Aritmetizasyon** | R1CS, Plonkish Gate sistemi | AIR (Algebraic Intermediate Representation) |
| **Güvenilir Kurulum (Trusted Setup)** | Gerekli (Powers of Tau) | Gerekmez (Transparent - sadece Hash fonksiyonları) |
| **Kuantum Direnci** | Yok (Ayrık logaritma ve eşleşme tabanlı) | Var (Sadece çakışmaya dirençli hash fonksiyonları) |
| **İspat Boyutu** | Çok küçük (~200 - 400 bytes) | Nispeten büyük (~40 - 100 KB) |
| **On-Chain Doğrulama Maliyeti** | Çok düşük (~200,000 gas) | Yüksek gas maliyeti |

---

## 7. Referans Kodlar ve Simülatörler

Bu dizindeki çalıştırılabilir scriptler:
- [`secp256k1_ecdsa_demo.py`](./secp256k1_ecdsa_demo.py): Sonlu alan aritmetiğinden imza doğrulamaya sıfırdan saf Python ECDSA motoru.
- [`merkle_tree.py`](./merkle_tree.py): SHA-256 tabanlı Merkle Tree inşası, Merkle Proof üretimi ve doğrulaması.
- [`kzg_polynomial_commitment.py`](./kzg_polynomial_commitment.py): KZG taahhüt şemasının çalışma prensibini gösteren sonlu alan simülatörü.
