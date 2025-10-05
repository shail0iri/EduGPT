# bench_syllabus.py

from generating_syllabus import generate_syllabus
import time, random, os, argparse, csv

# Default list of courses
COURSES = [
    "Intro to Machine Learning",
    "Deep Learning Fundamentals",
    "Data Science with Python",
    "Computer Vision",
    "Natural Language Processing"
]

# Retry wrapper with exponential backoff
def safe_generate(course, task, retries=5):
    for attempt in range(retries):
        try:
            return generate_syllabus(course, task)
        except Exception as e:
            wait = (2 ** attempt) + random.uniform(0, 3)
            print(f"⚠️ Error generating '{course}': {e} → retrying in {wait:.1f}s...")
            time.sleep(wait)
    raise RuntimeError(f"❌ All retries failed for {course}")

# Save syllabus to file
def save_syllabus(course, syllabus):
    os.makedirs("results", exist_ok=True)
    filename = f"results/syllabus_{course.replace(' ', '_')}.txt"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(syllabus)
    return filename

def run_benchmark(courses):
    os.makedirs("results", exist_ok=True)
    summary_file = "results/benchmark_summary.csv"

    # Create CSV header if file doesn’t exist
    if not os.path.exists(summary_file):
        with open(summary_file, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Course", "Generation Time (s)", "File Path"])

    for course in courses:
        task = f"Generate a detailed syllabus for the course: {course}"
        
        start = time.time()
        syllabus = safe_generate(course, task)
        end = time.time()
        
        duration = round(end - start, 2)
        file_path = save_syllabus(course, syllabus)

        # Append results to CSV
        with open(summary_file, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([course, duration, file_path])
        
        print("="*60)
        print(f"📘 Course: {course}")
        print(f"⏱️ Generation time: {duration:.2f} seconds")
        print(f"💾 Saved syllabus → {file_path}")
        print(f"📄 Preview:\n{syllabus[:500]}...\n")  # print only first 500 chars

        time.sleep(65)  # cooldown between requests
    
    print("="*60)
    print(f"✅ Benchmark completed successfully!\n📊 Summary saved in {summary_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--course", type=str, help="Run benchmark for a single course")
    args = parser.parse_args()

    if args.course:
        run_benchmark([args.course])
    else:
        run_benchmark(COURSES)
