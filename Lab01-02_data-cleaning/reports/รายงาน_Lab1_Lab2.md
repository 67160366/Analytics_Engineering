# รายงาน Lab 1 & Lab 2 — Analytics Engineering

---

## Lab 1: จำแนกประเภทและออกแบบการจัดเก็บข้อมูล

ตารางวิเคราะห์ข้อมูล 8 ประเภทของมหาวิทยาลัย

| # | ข้อมูล | ประเภทข้อมูล | รูปแบบไฟล์ / Schema (อธิบาย) | แหล่งจัดเก็บที่เหมาะสม |
|---|--------|--------------|------------------------------|------------------------|
| 1 | ตารางข้อมูลนิสิต (CSV) | **Structured** | ไฟล์ CSV มี schema ชัดเจน คอลัมน์คงที่ เช่น `student_id, name, faculty, gpa` แต่ละแถวคือ 1 record | **Relational Database** (เช่น MySQL/PostgreSQL) หรือ **Data Warehouse** เมื่อใช้เพื่อวิเคราะห์ |
| 2 | ข้อมูลเซนเซอร์อุณหภูมิ (JSON) | **Semi-structured** | JSON มีโครงสร้างแบบ key–value / nested เช่น `{"device_id":..., "temp_c":..., "ts":...}` schema ยืดหยุ่น เปลี่ยน field ได้ | **Data Lake** หรือ **NoSQL** (เช่น MongoDB) รองรับข้อมูลไหลเข้าต่อเนื่องจำนวนมาก |
| 3 | ภาพจากกล้องวงจรปิด | **Unstructured** | ไฟล์ภาพ/วิดีโอ (JPG, MP4) ไม่มี schema เป็นข้อมูล binary ขนาดใหญ่ | **Object Storage** (เช่น Amazon S3, MinIO, Azure Blob) |
| 4 | ไฟล์ PDF ใบสมัครทุน | **Unstructured** | เอกสาร PDF ข้อความ+ภาพ ไม่มีโครงสร้างตาราง (ต้องใช้ OCR/NLP ดึงข้อมูล) | **Object Storage** หรือ **Data Lake** |
| 5 | Log การเข้าใช้งาน LMS | **Semi-structured** | ไฟล์ log ข้อความกึ่งมีรูปแบบ เช่น `timestamp user_id action ip` หรือ JSON log line | **Data Lake** (สำหรับเก็บดิบ) → **Data Warehouse** เมื่อทำ analytics |
| 6 | ผลการลงทะเบียนเรียน (MySQL) | **Structured** | ตารางในฐานข้อมูลเชิงสัมพันธ์ schema กำหนดชัด มี PK/FK เช่น `enrollment(student_id, course_id, grade)` | **Relational Database** (MySQL) / **Data Warehouse** สำหรับรายงาน |
| 7 | ไฟล์เสียงศูนย์รับแจ้งปัญหา | **Unstructured** | ไฟล์เสียง (WAV, MP3) เป็น binary ไม่มี schema (ต้องแปลงเป็นข้อความด้วย Speech-to-Text) | **Object Storage** |
| 8 | ข้อมูลดิบเครื่องอ่านบัตร (ยังไม่ตรวจสอบ) | **Raw Data** (มักเป็น Semi-structured) | ข้อมูลดิบยังไม่ถูก clean/validate อาจมี error, ค่าว่าง, รูปแบบไม่สม่ำเสมอ | **Data Lake** (Raw / Landing Zone) เก็บต้นฉบับก่อนนำไปทำความสะอาด |

**สรุปหลักการเลือกแหล่งจัดเก็บ**
- **Structured** → Relational Database / Data Warehouse
- **Semi-structured** → Data Lake / NoSQL
- **Unstructured** → Object Storage
- **Raw Data** → Data Lake (Raw Zone) ก่อนแปลงเป็น Cleaned/Curated Zone

---

## Lab 2: ทำความสะอาดข้อมูลดิบจากเซนเซอร์ IoT

ไฟล์ต้นฉบับ: `iot_sensor_raw_data_extended.csv` (480 แถวข้อมูล + 1 header)

### 1) ปัญหาคุณภาพข้อมูลที่พบ (รายงานปัญหา)

| ประเภทปัญหา | ตัวอย่างที่พบในไฟล์ | รายละเอียด |
|-------------|--------------------|------------|
| **Error – เซนเซอร์เสีย** | `temp_c = -999.0` | ค่า sentinel ที่เซนเซอร์ส่งเมื่ออ่านค่าไม่ได้ |
| **Error – motion ผิดรูปแบบ** | `FALSEE`, `TRUEE`, `unknown` | สะกดผิด/ค่าที่ไม่ใช่ true-false |
| **Outlier – temp_c นอกช่วง** | `85.0`, `67.8` | เกินช่วง 0–50 °C ที่กำหนด |
| **Outlier – battery นอกช่วง** | `-5`, `-1`, `108`, `115`, `999` | เกินช่วง 0–100 |
| **Duplicate** | เช่น `2026-07-12 14:53:00, SN-9982` ปรากฏ 2 ครั้ง | แถวซ้ำที่มี `device_id` + `timestamp` เดียวกัน (25 คู่) |
| **Missing Value** | `NULL` ใน `device_id`, `temp_c`, `motion`, `battery` | ค่าว่างในหลายคอลัมน์ |

> หมายเหตุ: ค่า `motion` ที่แปลงได้ เช่น `yes → true`, `0 → false`, `1 → true` ถือเป็นการ normalize ไม่ใช่ error

### 2) Data Quality Rules ที่กำหนด

1. `temp_c` ต้องอยู่ระหว่าง **0–50 °C** (ค่า `-999` = sensor error, นอกช่วง = outlier → NULL)
2. `device_id` **ห้ามเป็นค่าว่าง** (ถ้าว่าง = แถว INVALID ระบุแหล่งที่มาไม่ได้)
3. **ห้ามมีข้อมูลซ้ำ** ที่ `device_id` + `timestamp` เดียวกัน
4. `battery` ต้องอยู่ระหว่าง **0–100** (นอกช่วง → NULL)
5. `motion` ต้องเป็น **true / false** เท่านั้น (ค่าผิดรูป → NULL)

### 3) โปรแกรมทำความสะอาด (Python / Pandas)

Source code: **`clean_iot_data.py`** ทำงาน 5 ขั้นตอน
- แปลง token ค่าว่าง (`NULL`, `""`, `NaN`) → `NaN` จริง
- Normalize `motion` เป็น true/false, ค่าผิดรูป → NULL
- แปลง `temp_c`/`battery` เป็นตัวเลข, ค่า error/outlier → NULL
- ลบข้อมูลซ้ำ (`device_id` + `timestamp`)
- เพิ่มคอลัมน์ `data_quality_status` (`OK` / `MISSING_VALUE` / `INVALID_NO_DEVICE_ID`)

> **การจัดการ Missing Value:** ในงานนี้เลือก**ทำเครื่องหมายสถานะ (flag)** ผ่านคอลัมน์ `data_quality_status`
> แทนการเติมค่ามั่ว เพื่อไม่บิดเบือนข้อมูลเซนเซอร์ ผู้ใช้ปลายทางเลือกได้เองว่าจะกรอง
> แถว `MISSING_VALUE` ออก หรือเติมค่า (เช่น interpolate ตามเวลา) ตามความเหมาะสม

### 4) เปรียบเทียบจำนวนแถวก่อน–หลังทำความสะอาด

| รายการ | จำนวนแถว |
|--------|---------:|
| ก่อนทำความสะอาด | **480** |
| ลบข้อมูลซ้ำออก | −25 |
| หลังทำความสะอาด | **455** |

### 5) ตารางสรุปจำนวนปัญหา

| ประเภทปัญหา | จำนวน |
|-------------|------:|
| **Error** (ค่าผิด/เซนเซอร์เสีย: -999 + motion ผิดรูป) | 9 |
| **Duplicate** (ข้อมูลซ้ำ) | 25 |
| **Missing Value** (ค่าว่าง หลังแปลง error/outlier) | 32 |
| **Outlier** (temp/battery นอกช่วง) | 9 |

การกระจายค่า `data_quality_status` หลังทำความสะอาด:

| สถานะ | จำนวนแถว |
|-------|---------:|
| OK | 423 |
| MISSING_VALUE | 30 |
| INVALID_NO_DEVICE_ID | 2 |

### 6) เหตุผลที่ไม่ควรลบ Raw Data ต้นฉบับ

1. **ตรวจสอบย้อนกลับได้ (Traceability/Audit):** เก็บต้นฉบับไว้เพื่อพิสูจน์ที่มาของข้อมูลและตรวจสอบภายหลัง
2. **แก้ไข Logic การ clean ใหม่ได้:** ถ้ากฎคุณภาพเปลี่ยน (เช่นขยายช่วงอุณหภูมิ) ต้องกลับไปประมวลผลจาก Raw ใหม่
3. **ข้อมูลที่ดูเหมือน "ผิด" อาจมีความหมาย:** เช่น `-999` บอกช่วงเวลาที่เซนเซอร์เสีย ซึ่งเป็นข้อมูลสำคัญเชิงบำรุงรักษา
4. **ป้องกันข้อมูลสูญหายถาวร:** การ clean คือการ "ตีความ" ถ้าลบต้นฉบับแล้วตีความผิดจะกู้คืนไม่ได้
5. **หลักการ Data Lake:** แยกชั้น Raw (ต้นฉบับ) → Cleaned → Curated ต้นฉบับต้องคงอยู่เสมอ

---

## ไฟล์ผลลัพธ์ที่ส่ง

| ไฟล์ | คำอธิบาย |
|------|----------|
| `clean_iot_data.py` | Source code (Python/Pandas) |
| `iot_sensor_cleaned_data.csv` | ไฟล์ Cleaned Data (455 แถว + คอลัมน์ `data_quality_status`) |
| `รายงาน_Lab1_Lab2.md` | รายงานปัญหา + ตารางสรุป + ตอบ Lab 1 |
