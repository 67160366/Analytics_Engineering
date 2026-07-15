# -*- coding: utf-8 -*-
"""
Lab 2: ทำความสะอาดข้อมูลดิบจากเซนเซอร์ IoT
- ลบข้อมูลซ้ำ
- แปลงค่าผิดปกติ (Outlier/Error) เป็น NULL
- จัดการ Missing Value
- เพิ่มคอลัมน์ data_quality_status
- สรุปจำนวน Error, Duplicate, Missing, Outlier
"""

import pandas as pd
import numpy as np

RAW_FILE = "iot_sensor_raw_data_extended.csv"
CLEAN_FILE = "iot_sensor_cleaned_data.csv"

# ค่าที่ถือว่าเป็น "ว่าง" ในไฟล์ดิบ
NA_TOKENS = ["NULL", "null", "", "NaN", "nan", "None"]

# ---------------------------------------------------------------
# 1) โหลด Raw Data (เก็บต้นฉบับไว้ ไม่แก้ไข)
# ---------------------------------------------------------------
raw = pd.read_csv(RAW_FILE, dtype=str, keep_default_na=False)
n_before = len(raw)

# ทำสำเนามาทำความสะอาด
df = raw.copy()

# นับปัญหาแยกหมวด
report = {"missing": 0, "duplicate": 0, "outlier": 0, "error": 0}

# ---------------------------------------------------------------
# 2) Data Quality Rules
#    - temp_c ต้องอยู่ 0–50 °C
#    - battery ต้องอยู่ 0–100
#    - device_id ห้ามว่าง
#    - motion ต้องเป็น true/false เท่านั้น
#    - ห้ามซ้ำที่ device_id + timestamp เดียวกัน
# ---------------------------------------------------------------

# --- 2.1 แปลง token ที่หมายถึงค่าว่าง ให้เป็น NaN จริง ---
df = df.replace(NA_TOKENS, np.nan)

# --- 2.2 normalize คอลัมน์ motion (true/false) ---
def norm_motion(v):
    if pd.isna(v):
        return np.nan
    s = str(v).strip().lower()
    if s in ("true", "t", "1", "yes"):
        return "true"
    if s in ("false", "f", "0", "no"):
        return "false"
    return "__ERROR__"  # เช่น FALSEE, TRUEE, unknown

df["motion"] = df["motion"].apply(norm_motion)
motion_error_mask = df["motion"] == "__ERROR__"
report["error"] += int(motion_error_mask.sum())
df.loc[motion_error_mask, "motion"] = np.nan  # ค่าผิด -> NULL

# --- 2.3 แปลงตัวเลข ---
df["temp_c"] = pd.to_numeric(df["temp_c"], errors="coerce")
df["battery"] = pd.to_numeric(df["battery"], errors="coerce")

# --- 2.4 ตรวจ Outlier / Error ในตัวเลข แล้วแปลงเป็น NULL ---
# temp_c: ค่า -999 = sensor error, นอกช่วง 0-50 = outlier
temp_error_mask = df["temp_c"] <= -900                       # ค่า sensor error (-999)
temp_outlier_mask = (~temp_error_mask) & (
    (df["temp_c"] < 0) | (df["temp_c"] > 50)
) & df["temp_c"].notna()

report["error"] += int(temp_error_mask.sum())
report["outlier"] += int(temp_outlier_mask.sum())
df.loc[temp_error_mask | temp_outlier_mask, "temp_c"] = np.nan

# battery: นอกช่วง 0-100 = outlier
batt_outlier_mask = (
    (df["battery"] < 0) | (df["battery"] > 100)
) & df["battery"].notna()
report["outlier"] += int(batt_outlier_mask.sum())
df.loc[batt_outlier_mask, "battery"] = np.nan

# ---------------------------------------------------------------
# 3) ลบข้อมูลซ้ำ (device_id + timestamp เดียวกัน)
# ---------------------------------------------------------------
dup_mask = df.duplicated(subset=["device_id", "timestamp"], keep="first")
report["duplicate"] = int(dup_mask.sum())
df = df[~dup_mask].copy()

# ---------------------------------------------------------------
# 4) นับ Missing Value (หลังแปลง error/outlier เป็น NULL แล้ว)
#    รวมทั้ง device_id ที่ห้ามว่าง
# ---------------------------------------------------------------
report["missing"] = int(df[["device_id", "temp_c", "motion", "battery"]].isna().sum().sum())

# ---------------------------------------------------------------
# 5) เพิ่มคอลัมน์ data_quality_status
#    OK              = ครบทุกค่า
#    INVALID         = device_id ว่าง (ระบุแหล่งที่มาไม่ได้)
#    MISSING_VALUE   = มีค่าว่างในคอลัมน์อื่น
# ---------------------------------------------------------------
def quality_status(row):
    if pd.isna(row["device_id"]):
        return "INVALID_NO_DEVICE_ID"
    if row[["temp_c", "motion", "battery"]].isna().any():
        return "MISSING_VALUE"
    return "OK"

df["data_quality_status"] = df.apply(quality_status, axis=1)

# ---------------------------------------------------------------
# 6) บันทึกผล
# ---------------------------------------------------------------
n_after = len(df)
df.to_csv(CLEAN_FILE, index=False)

# ---------------------------------------------------------------
# 7) รายงานสรุป
# ---------------------------------------------------------------
print("=" * 55)
print(" สรุปผลการทำความสะอาดข้อมูล IoT Sensor")
print("=" * 55)
print(f"จำนวนแถวก่อนทำความสะอาด : {n_before}")
print(f"จำนวนแถวหลังทำความสะอาด : {n_after}")
print(f"แถวที่ถูกลบ (ซ้ำ)       : {n_before - n_after}")
print("-" * 55)
print(f"{'ประเภทปัญหา':<20}{'จำนวน':>10}")
print("-" * 55)
print(f"{'Error (ค่าผิด/เซนเซอร์เสีย)':<28}{report['error']:>8}")
print(f"{'Duplicate (ข้อมูลซ้ำ)':<28}{report['duplicate']:>8}")
print(f"{'Missing Value (ค่าว่าง)':<28}{report['missing']:>8}")
print(f"{'Outlier (นอกช่วงที่กำหนด)':<28}{report['outlier']:>8}")
print("-" * 55)
print("การกระจายค่า data_quality_status:")
print(df["data_quality_status"].value_counts().to_string())
print("=" * 55)
print(f"บันทึกไฟล์สะอาดแล้ว -> {CLEAN_FILE}")
