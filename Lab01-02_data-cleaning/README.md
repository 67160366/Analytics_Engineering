# Analytics Engineering — Lab 1 & Lab 2

งานส่งวิชา Analytics Engineering
**นิสิต:** 67160366

---

## 📌 สรุปงาน

| Lab | หัวข้อ | ผลลัพธ์ |
|-----|--------|---------|
| **Lab 1** | จำแนกประเภทและออกแบบการจัดเก็บข้อมูล | ตารางวิเคราะห์ข้อมูล 8 ประเภท → [ดูรายงาน](reports/รายงาน_Lab1_Lab2.md) |
| **Lab 2** | ทำความสะอาดข้อมูลดิบจากเซนเซอร์ IoT | โค้ด + Cleaned Data + รายงานสรุป |

---

## 📂 โครงสร้างไฟล์

```
Lab01-02_data-cleaning/
├── README.md                          ← หน้านี้ (สรุปงานทั้งหมด)
├── clean_iot_data.ipynb               ← ⭐ Notebook ทำความสะอาดข้อมูล (รันแล้ว มี output ในตัว)
├── clean_iot_data.py                  ← สคริปต์เวอร์ชัน .py (ผลเหมือน notebook)
├── iot_sensor_raw_data_extended.csv   ← ข้อมูลดิบต้นฉบับ (Raw Data — ไม่แก้ไข)
├── iot_sensor_cleaned_data.csv        ← ข้อมูลที่ทำความสะอาดแล้ว (Cleaned Data)
├── reports/
│   ├── รายงาน_Lab1_Lab2.docx          ← รายงานฉบับ Word (Lab 1 + Lab 2)
│   └── รายงาน_Lab1_Lab2.md            ← รายงานฉบับ Markdown
├── assignment/
│   └── Lab1.docx.md                   ← โจทย์ต้นฉบับ
└── tools/                             ← สคริปต์ช่วยสร้างไฟล์ docx / notebook
```

> 💡 **แนะนำสำหรับตรวจงาน:** เปิด [`clean_iot_data.ipynb`](clean_iot_data.ipynb) ได้เลย — GitHub เรนเดอร์ notebook พร้อมผลลัพธ์ทุกขั้นตอนให้เห็นทันที **โดยไม่ต้องรันเอง**

---

## 🧪 Lab 2 — ผลการทำความสะอาดข้อมูล

**ข้อมูล:** `iot_sensor_raw_data_extended.csv` (480 แถว)

### Data Quality Rules
- `temp_c` ต้องอยู่ระหว่าง 0–50 °C (`-999` = sensor error, นอกช่วง = outlier)
- `device_id` ห้ามเป็นค่าว่าง
- `battery` ต้องอยู่ระหว่าง 0–100
- `motion` ต้องเป็น `true` / `false`
- ห้ามข้อมูลซ้ำที่ `device_id` + `timestamp` เดียวกัน

### ตารางสรุปจำนวนปัญหา

| ประเภทปัญหา | จำนวน |
|-------------|------:|
| Error (temp=-999 จำนวน 6 + motion ผิดรูป 3) | 9 |
| Duplicate (ข้อมูลซ้ำ) | 25 |
| Missing Value (ค่าว่าง) | 32 |
| Outlier (temp 4 + battery 5) | 9 |

### เปรียบเทียบก่อน–หลัง
- ก่อน: **480 แถว** → หลัง: **455 แถว** (ลบข้อมูลซ้ำ 25 แถว)
- เพิ่มคอลัมน์ `data_quality_status`:

| สถานะ | จำนวน |
|-------|------:|
| OK | 423 |
| MISSING_VALUE | 30 |
| INVALID_NO_DEVICE_ID | 2 |

> **หมายเหตุ:** แถวที่มี Missing/Invalid เลือก *ทำเครื่องหมายสถานะ (flag)* แทนการลบ
> เพราะคอลัมน์อื่นยังใช้งานได้ และเพื่อให้ตรวจสอบย้อนกลับได้ (ดูเหตุผลเต็มในรายงาน)

---

## ▶️ วิธีรันโค้ด

ต้องมี Python 3 + ไลบรารี `pandas`

```bash
pip install pandas
python clean_iot_data.py
```

หรือเปิด `clean_iot_data.ipynb` ด้วย Jupyter / VS Code แล้ว Run All

โปรแกรมจะอ่าน `iot_sensor_raw_data_extended.csv` แล้วสร้าง `iot_sensor_cleaned_data.csv` ใหม่
