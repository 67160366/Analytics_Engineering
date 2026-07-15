# Analytics Engineering

รวมงานส่งวิชา **Analytics Engineering**
**นิสิต:** 67160366

---

## 📚 สารบัญงาน

| งาน | หัวข้อ | ลิงก์ |
|-----|--------|-------|
| **Lab 1–2** | จำแนกประเภทข้อมูล + ทำความสะอาดข้อมูล IoT Sensor | [เปิดโฟลเดอร์](Lab01-02_data-cleaning/) |

> งานครั้งต่อไปจะเพิ่มเป็นโฟลเดอร์ใหม่ (เช่น `Lab03_.../`) และอัปเดตตารางนี้

---

## 📂 ไฟล์ในงาน Lab 1–2 (เฉพาะที่ต้องส่ง)

| ไฟล์ | Deliverable |
|------|-------------|
| `clean_iot_data.ipynb` | Source code (รันแล้ว มี output แสดงการตรวจปัญหา + ตารางสรุป) |
| `iot_sensor_cleaned_data.csv` | Cleaned Data |
| `รายงาน_Lab1_Lab2.docx` | รายงานปัญหาที่พบ + ตารางสรุป Error/Duplicate/Missing/Outlier + Lab 1 |
| `iot_sensor_raw_data_extended.csv` | Raw Data ต้นฉบับ (อินพุตของ source code — ไม่แก้ไข) |

---

## 🔁 วิธีเพิ่มงานครั้งต่อไป

1. สร้างโฟลเดอร์ใหม่ เช่น `Lab03_ชื่องาน/`
2. `git add -A && git commit -m "Add Lab 03"` แล้ว `git push`
3. tag สแนปชอตการส่ง: `git tag lab03-submit && git push origin lab03-submit`
4. อัปเดตตารางสารบัญด้านบน แล้ววาง**ลิงก์โฟลเดอร์งาน**ใน Google Classroom

> ส่ง Classroom แนะนำให้ใช้ลิงก์ที่ชี้ tag (สแนปชอตถาวร ไม่เปลี่ยนหลังส่ง) เช่น
> `.../tree/lab03-submit/Lab03_ชื่องาน`
