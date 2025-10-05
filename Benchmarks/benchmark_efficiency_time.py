# test2_time.py

import time
import csv
import os
from generating_syllabus import generate_syllabus

COURSES = [
    "Intro to Machine Learning",
    "Deep Learning Fundamentals",
    "Data Science with Python"
]

OUTPUT_FILE = "results/test2_time.csv"

def run_test2():
    results = []

    for course in COURSES:
        task = f"Generate a syllabus for {course}"

        start_time = time.time()
        syllabus = generate_syllabus(course, task)
        end_time = time.time()

        duration = end_time - start_time
        # Simulated: Manual prep = 300s → AI reduces ~70%
        manual_time = 300  
        reduction = (manual_time - duration) / manual_time * 100  

        results.append((course, duration, reduction))

        print("="*60)
        print(f"📘 Course: {course}")
        print(f"⏱️ AI Generation Time: {duration:.2f} seconds")
        print(f"📉 Time Reduction vs. Manual (~300s): {reduction:.1f}%")

        time.sleep(65)

    # Save CSV
    os.makedirs("results", exist_ok=True)
    with open(OUTPUT_FILE, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Course", "AI_Generation_Time(s)", "Time_Reduction(%)"])
        writer.writerows(results)

    print("="*60)
    print(f"✅ Test 2 completed → results saved in {OUTPUT_FILE}")

if __name__ == "__main__":
    run_test2()
