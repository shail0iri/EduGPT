import csv
import os
import time
import random
from generating_syllabus import generate_syllabus

# Courses to test
COURSES = [
    "Intro to Machine Learning",
    "Deep Learning Fundamentals",
    "Data Science with Python",
    "Computer Vision",
    "Natural Language Processing"
]

CSV_PATH = "test4_usability_speed_results.csv"

def measure_usability(syllabus):
    """
    Simulated usability metric (0–100).
    In practice, this would come from user feedback or LLM evaluation.
    """
    base = random.uniform(70, 95)
    bonus = 5 if "Project" in syllabus or "Module" in syllabus else 0
    return round(min(base + bonus, 100), 2)

def measure_interface_speed(start_time, end_time, content):
    """
    Measure interface latency per output length (seconds per 100 chars).
    """
    total_time = end_time - start_time
    char_count = max(len(content), 1)
    speed_metric = (total_time / char_count) * 100  # seconds per 100 chars
    return round(speed_metric, 3)

def run_test4():
    results = []
    os.makedirs("results", exist_ok=True)

    for course in COURSES:
        print(f"\n⚡ Running Test 4 (Usability + Interface Speed) for {course}...")
        start = time.time()
        syllabus = generate_syllabus(course, f"Generate a detailed syllabus for {course}")
        end = time.time()

        usability = measure_usability(syllabus)
        interface_speed = measure_interface_speed(start, end, syllabus)
        duration = round(end - start, 2)
        result_file = f"results/syllabus_{course.replace(' ', '_')}.txt"

        with open(result_file, "w", encoding="utf-8") as f:
            f.write(syllabus)

        results.append([course, duration, usability, interface_speed, result_file])
        print(f"✅ {course} | Time: {duration}s | Usability: {usability}% | Interface Speed: {interface_speed}s/100chars")
        time.sleep(65)  
    # Save all results
    write_mode = "a" if os.path.exists(CSV_PATH) else "w"
    with open(CSV_PATH, write_mode, newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if write_mode == "w":
            writer.writerow(["Course", "Generation Time (s)", "Usability (%)", "Interface Speed (s/100 chars)", "File Path"])
        writer.writerows(results)

    print(f"\n📊 Test 4 results saved to {CSV_PATH}")

if __name__ == "__main__":
    run_test4()
