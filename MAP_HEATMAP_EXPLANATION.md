# 📊 Penjelasan Map View vs Heatmap View

## Perbezaan Kedua-Dua Views

### 🗺️ MAP VIEW (Leaflet.js) - Sudah Berfungsi ✅

**Kegunaan**: Peta interaktif dengan marker lokasi
- Menunjukkan **circle markers berwarna** untuk setiap negeri Malaysia
- Boleh **click marker** untuk lihat detail nama, jumlah breach, dan akun terancam
- Boleh **zoom in/out** dan **drag** peta
- **Warna marker** menunjukkan severity:
  - 🔴 Merah terang = Critical/High severity
  - 🟠 Jingga = Medium severity
  - 🟡 Kuning = Low severity

**Contoh Data**:
```
Kuala Lumpur: 345 breaches, 2.15 juta akun
Selangor: 234 breaches, 1.89 juta akun
Pulau Pinang: 89 breaches, 580k akun
```

---

### 🔥 HEATMAP VIEW (ECharts) - DIPERBAIKI ✅

**Kegunaan**: Visualisasi intensiti "heat density" 
- Menunjukkan **titik dengan efek glow** yang berdenyut-denyut (ripple effect)
- **Besar glow** = lebih banyak breach (intensiti tinggi)
- **Warna bertingkat** dari biru → jingga → merah (cool → hot)
- Fokus pada **pola spatial** bukan marker yang jelas
- Berguna untuk melihat **konsentrasi area berisiko tinggi**

**Contoh Interpretasi**:
```
- Glow Besar + Merah Terang = Area dengan breach teranyak (KL, Selangor)
- Glow Sederhana + Jingga = Area berisiko sederhana (Johor)
- Glow Kecil + Biru = Area dengan breach rendah (Sabah, Sarawak)
```

---

## Perbezaan Teknis

| Aspek | Map View | Heatmap View |
|-------|----------|--------------|
| **Library** | Leaflet.js | ECharts |
| **Tipe Viz** | Geographic markers | effectScatter dengan ripple |
| **Interaksi** | Click marker untuk detail | Hover untuk intensity info |
| **Data Jelas** | Ya (labels di marker) | Visual (glow size = intensity) |
| **Best For** | Lihat lokasi spesifik | Lihat pola & konsentrasi |
| **Performa** | Cepat | Sederhana dengan animation |

---

## Perubahan yang Dibuat

### ✅ 1. Ganti Data Global → Malaysia States Only

**Sebelum**: 5 lokasi global (USA, UK, Russia, Singapore, Malaysia)

**Sekarang**: 7 negeri Malaysia dengan data realistik:
```javascript
const breachHotspots = [
    { name: 'Kuala Lumpur (FT)', lat: 3.1390, lng: 101.6869, breaches: 345, accounts: 2150000 },
    { name: 'Selangor', lat: 2.7258, lng: 101.5244, breaches: 234, accounts: 1890000 },
    { name: 'Pulau Pinang', lat: 5.3521, lng: 100.3329, breaches: 89, accounts: 580000 },
    { name: 'Johor Bahru', lat: 1.4854, lng: 103.7618, breaches: 156, accounts: 920000 },
    { name: 'Pahang', lat: 3.8126, lng: 103.3256, breaches: 67, accounts: 340000 },
    { name: 'Sabah', lat: 5.9788, lng: 117.8753, breaches: 45, accounts: 210000 },
    { name: 'Sarawak', lat: 1.5533, lng: 110.3592, breaches: 34, accounts: 156000 }
];
```

### ✅ 2. Ubah Map Center & Zoom Ke Malaysia

**Sebelum**: `setView([20, 0], 3)` - Fokus Eropah, zoom level 3 (world view)

**Sekarang**: `setView([4.2, 102.2], 6)` - Fokus Malaysia, zoom level 6 (perfect untuk lihat semua negeri)

### ✅ 3. Perbaiki ECharts Heatmap Config

**Masalah Sebelumnya**:
- Gunakan `type: 'heatmap'` yang hanya untuk grid/matrix 2D, bukan geo coordinates
- Hasilnya: Blank/hitam ketika toggle ke Heatmap View

**Solusi**:
- Guna `type: 'effectScatter'` yang proper untuk geographic data
- Tambah ripple effect (glow berdenyut) untuk visual intensiti
- Dynamic size: glow lebih besar = breach lebih banyak
- Color gradient: biru (rendah) → jingga → merah (tinggi)

```javascript
{
    type: 'effectScatter',
    coordinateSystem: 'geo',
    rippleEffect: {
        scale: 3,
        period: 4
    },
    symbolSize: function(val) {
        // Size proportional to breach count
        return Math.min(40, 5 + (val[2]/maxBreaches) * 35);
    }
}
```

---

## Cara Guna

### 📍 Map View
1. Login ke dashboard
2. Scroll ke section "Global Breach Hotspots"
3. Klik button "🗺️ Map View" (auto-select di mula)
4. **Click marker** untuk lihat detail:
   - Nama negeri
   - Jumlah breach
   - Jumlah akun terancam
   - Info severity
5. Drag/zoom peta untuk explore

### 🔥 Heatmap View
1. Klik button "🔥 Heatmap View"
2. Lihat **glow effect berdenyut** untuk setiap negeri
3. Glow lebih besar/merah = lebih banyak breach
4. Hover di atas titik untuk lihat exact details
5. Gunakan legend di bawah untuk interpret warna

---

## Data Interpretation Guide

### Severity Levels (warna marker)
- 🔴 **Critical** (merah): KL (345 breaches)
- 🔴 **High** (merah) : Selangor, Pulau Pinang, Johor
- 🟠 **Medium** (jingga): Pahang, Sabah
- 🟡 **Low** (kuning): Sarawak

### Risk Score Translation
- **345 breaches di KL** = 2.15 JUTA akun Malaysia dalam database breach
- **234 breaches di Selangor** = 1.89 JUTA akun dalam database breach
- Total secara keseluruhan = **6.25 JUTA akun Malaysia** dalam breach database

---

## Testing Checklist

✅ **Done**:
- [x] Replace global data dengan Malaysia states
- [x] Center peta ke Malaysia (lat: 4.2, lng: 102.2)
- [x] Adjust zoom ke level 6 (perfect view semua negeri)
- [x] Fix ECharts heatmap (change heatmap → effectScatter)
- [x] Add ripple effect untuk visual intensity
- [x] Update color gradient (biru-jingga-merah)
- [x] Template syntax validasi ✓

⏳ **Perlu Test**:
- [ ] Login & akses dashboard
- [ ] Click "Map View" - lihat 7 marker Malaysia
- [ ] Click "Heatmap View" - lihat glow effect berdenyut
- [ ] Hover marker - lihat tooltip dengan data
- [ ] Zoom in/out - scroll smooth
- [ ] Click marker (Map View) - popup detail

---

## FAQ

**Q: Kenapa Map View dan Heatmap View berbeza?**
A: Keduanya guna library berbeza (Leaflet vs ECharts) dengan visualization style berbeza. Map View untuk precise locations, Heatmap untuk pattern visualization.

**Q: Kenapa Heatmap View sebelumnya blank/hitam?**
A: Config gunakan `type: 'heatmap'` yang salah. Heatmap ECharts hanya untuk grid 2D, bukan geographic. Sekarang guna `effectScatter` yang proper.

**Q: Boleh adjust data breach untuk each state?**
A: Ya! Edit array `breachHotspots` dengan data sebenar. Struktur:
```javascript
{
    name: 'Negeri Name',
    lat: latitude,
    lng: longitude,
    breaches: jumlah_breach,
    accounts: jumlah_akun_terancam,
    color: '#rrggbb',
    severity: 'Critical|High|Medium|Low'
}
```

**Q: Glow effect di Heatmap besar/kecil macam mana?**
A: Algorithm: `size = 5 + (breach_count / max_breach_count) * 35`
- Min: 5px (untuk Sarawak 34 breaches)
- Max: 40px (untuk KL 345 breaches)

---

## Technical Notes untuk Development

**File Modified**: `templates/index.html`

**Functions Updated**:
1. `breachHotspots` array - Data structure (lines 977-1027)
2. `initBreachMap()` - Map center & zoom (lines 1030-1031)
3. `initEChartsHeatmap()` - ECharts config (lines 1113-1200)

**Dependencies**:
- Leaflet.js 1.9.4 (Map View)
- ECharts 5.4.3 (Heatmap View)
- Both libraries sudah included via CDN

**Dark Theme Colors**:
- Background: #0d1117 (GitHub dark)
- Map tiles: Dark CartoDB
- ECharts theme: 'dark'
- Text: #8b949e (muted gray)

**Next Improvements** (Optional):
- [ ] Integrate real breach data dari database
- [ ] Add time-series filter (min/max date)
- [ ] Add export peta as image
- [ ] Add state-specific breach details modal
- [ ] Integrate dengan darkweb_findings untuk show darkweb mentions

