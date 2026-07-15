# -*- coding: utf-8 -*-
"""สร้างและรัน clean_iot_data.ipynb"""
import nbformat as nbf
from nbconvert.preprocessors import ExecutePreprocessor

nb = nbf.v4.new_notebook()
cells = []

cells.append(nbf.v4.new_markdown_cell(
    "# Lab 2: ทำความสะอาดข้อมูลดิบจากเซนเซอร์ IoT\n"
    "\n"
    "ขั้นตอน: ลบข้อมูลซ้ำ · แปลงค่าผิดปกติเป็น NULL · จัดการ Missing Value · "
    "เพิ่มคอลัมน์ `data_quality_status` · สรุปจำนวน Error / Duplicate / Missing / Outlier"
))

cells.append(nbf.v4.new_markdown_cell("## 1) โหลด Raw Data (เก็บต้นฉบับไว้ ไม่แก้ไข)"))
cells.append(nbf.v4.new_code_cell(
    'import pandas as pd\n'
    'import numpy as np\n'
    '\n'
    'RAW_FILE = "iot_sensor_raw_data_extended.csv"\n'
    'CLEAN_FILE = "iot_sensor_cleaned_data.csv"\n'
    'NA_TOKENS = ["NULL", "null", "", "NaN", "nan", "None"]\n'
    '\n'
    '# โหลดเป็น string ทั้งหมดก่อน เพื่อคุมการแปลงค่าเอง\n'
    'raw = pd.read_csv(RAW_FILE, dtype=str, keep_default_na=False)\n'
    'n_before = len(raw)\n'
    'df = raw.copy()\n'
    'report = {"missing": 0, "duplicate": 0, "outlier": 0, "error": 0}\n'
    'print("จำนวนแถว Raw:", n_before)\n'
    'raw.head()'
))

cells.append(nbf.v4.new_markdown_cell(
    "## 2) Data Quality Rules\n"
    "- `temp_c` ต้องอยู่ 0–50 °C (`-999` = sensor error, นอกช่วง = outlier)\n"
    "- `device_id` ห้ามว่าง\n"
    "- `battery` ต้องอยู่ 0–100\n"
    "- `motion` ต้องเป็น true/false\n"
    "- ห้ามซ้ำที่ `device_id` + `timestamp` เดียวกัน"
))

cells.append(nbf.v4.new_markdown_cell("### 2.1 แปลง token ค่าว่าง → NaN"))
cells.append(nbf.v4.new_code_cell('df = df.replace(NA_TOKENS, np.nan)'))

cells.append(nbf.v4.new_markdown_cell("### 2.2 Normalize คอลัมน์ motion (ค่าผิดรูป → NULL)"))
cells.append(nbf.v4.new_code_cell(
    'def norm_motion(v):\n'
    '    if pd.isna(v):\n'
    '        return np.nan\n'
    '    s = str(v).strip().lower()\n'
    '    if s in ("true", "t", "1", "yes"):\n'
    '        return "true"\n'
    '    if s in ("false", "f", "0", "no"):\n'
    '        return "false"\n'
    '    return "__ERROR__"   # FALSEE, TRUEE, unknown\n'
    '\n'
    'df["motion"] = df["motion"].apply(norm_motion)\n'
    'motion_error_mask = df["motion"] == "__ERROR__"\n'
    'report["error"] += int(motion_error_mask.sum())\n'
    'df.loc[motion_error_mask, "motion"] = np.nan\n'
    'print("motion ผิดรูป (error):", int(motion_error_mask.sum()))'
))

cells.append(nbf.v4.new_markdown_cell("### 2.3 แปลง temp_c / battery เป็นตัวเลข แล้วจัดการ Error/Outlier → NULL"))
cells.append(nbf.v4.new_code_cell(
    'df["temp_c"] = pd.to_numeric(df["temp_c"], errors="coerce")\n'
    'df["battery"] = pd.to_numeric(df["battery"], errors="coerce")\n'
    '\n'
    '# temp_c: -999 = sensor error, นอกช่วง 0-50 = outlier\n'
    'temp_error_mask = df["temp_c"] <= -900\n'
    'temp_outlier_mask = (~temp_error_mask) & ((df["temp_c"] < 0) | (df["temp_c"] > 50)) & df["temp_c"].notna()\n'
    'report["error"] += int(temp_error_mask.sum())\n'
    'report["outlier"] += int(temp_outlier_mask.sum())\n'
    'df.loc[temp_error_mask | temp_outlier_mask, "temp_c"] = np.nan\n'
    '\n'
    '# battery: นอกช่วง 0-100 = outlier\n'
    'batt_outlier_mask = ((df["battery"] < 0) | (df["battery"] > 100)) & df["battery"].notna()\n'
    'report["outlier"] += int(batt_outlier_mask.sum())\n'
    'df.loc[batt_outlier_mask, "battery"] = np.nan\n'
    '\n'
    'print("temp error(-999):", int(temp_error_mask.sum()),\n'
    '      "| temp outlier:", int(temp_outlier_mask.sum()),\n'
    '      "| battery outlier:", int(batt_outlier_mask.sum()))'
))

cells.append(nbf.v4.new_markdown_cell("## 3) ลบข้อมูลซ้ำ (device_id + timestamp)"))
cells.append(nbf.v4.new_code_cell(
    'dup_mask = df.duplicated(subset=["device_id", "timestamp"], keep="first")\n'
    'report["duplicate"] = int(dup_mask.sum())\n'
    'df = df[~dup_mask].copy()\n'
    'print("แถวซ้ำที่ลบ:", report["duplicate"])'
))

cells.append(nbf.v4.new_markdown_cell("## 4) นับ Missing Value (หลังแปลง error/outlier เป็น NULL)"))
cells.append(nbf.v4.new_code_cell(
    'report["missing"] = int(df[["device_id", "temp_c", "motion", "battery"]].isna().sum().sum())\n'
    'df[["device_id", "temp_c", "motion", "battery"]].isna().sum()'
))

cells.append(nbf.v4.new_markdown_cell(
    "## 5) เพิ่มคอลัมน์ data_quality_status\n"
    "- `OK` = ครบทุกค่า\n"
    "- `INVALID_NO_DEVICE_ID` = device_id ว่าง\n"
    "- `MISSING_VALUE` = มีค่าว่างในคอลัมน์อื่น"
))
cells.append(nbf.v4.new_code_cell(
    'def quality_status(row):\n'
    '    if pd.isna(row["device_id"]):\n'
    '        return "INVALID_NO_DEVICE_ID"\n'
    '    if row[["temp_c", "motion", "battery"]].isna().any():\n'
    '        return "MISSING_VALUE"\n'
    '    return "OK"\n'
    '\n'
    'df["data_quality_status"] = df.apply(quality_status, axis=1)\n'
    'df["data_quality_status"].value_counts()'
))

cells.append(nbf.v4.new_markdown_cell("## 6) บันทึกไฟล์ Cleaned Data"))
cells.append(nbf.v4.new_code_cell(
    'n_after = len(df)\n'
    'df.to_csv(CLEAN_FILE, index=False)\n'
    'print("บันทึก:", CLEAN_FILE, "| แถวหลัง clean:", n_after)\n'
    'df.head()'
))

cells.append(nbf.v4.new_markdown_cell("## 7) รายงานสรุป"))
cells.append(nbf.v4.new_code_cell(
    'print("=" * 55)\n'
    'print(" สรุปผลการทำความสะอาดข้อมูล IoT Sensor")\n'
    'print("=" * 55)\n'
    'print(f"จำนวนแถวก่อนทำความสะอาด : {n_before}")\n'
    'print(f"จำนวนแถวหลังทำความสะอาด : {n_after}")\n'
    'print(f"แถวที่ถูกลบ (ซ้ำ)       : {n_before - n_after}")\n'
    'print("-" * 55)\n'
    'print(f"Error (ค่าผิด/เซนเซอร์เสีย) : {report[\'error\']}")\n'
    'print(f"Duplicate (ข้อมูลซ้ำ)      : {report[\'duplicate\']}")\n'
    'print(f"Missing Value (ค่าว่าง)    : {report[\'missing\']}")\n'
    'print(f"Outlier (นอกช่วงที่กำหนด)  : {report[\'outlier\']}")\n'
    'print("-" * 55)\n'
    'summary = pd.DataFrame({\n'
    '    "ประเภทปัญหา": ["Error", "Duplicate", "Missing Value", "Outlier"],\n'
    '    "จำนวน": [report["error"], report["duplicate"], report["missing"], report["outlier"]],\n'
    '})\n'
    'summary'
))

nb["cells"] = cells

# ---- execute ----
ep = ExecutePreprocessor(timeout=120, kernel_name="python3")
ep.preprocess(nb, {"metadata": {"path": "."}})

OUT = "clean_iot_data.ipynb"
with open(OUT, "w", encoding="utf-8") as f:
    nbf.write(nb, f)
print("สร้างและรัน notebook เสร็จ ->", OUT)
