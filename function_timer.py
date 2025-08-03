import sys
import time
import csv

class FunctionTimer:
    def __init__(self):
        self.call_stack = []
        self.timings = []

    def trace_calls(self, frame, event, arg):
        if event == 'call':
            code = frame.f_code
            func_name = code.co_name
            filename = code.co_filename
            lineno = frame.f_lineno

            # Skip files from site-packages, standard library, or venvs
            if any(part in filename.lower() for part in ['gui_agents', 'yudi']):
               self.call_stack.append((time.time(), func_name, filename, lineno))

            

        elif event == 'return':
            if self.call_stack:
                start_time, func_name, filename, lineno = self.call_stack.pop()
                elapsed = time.time() - start_time
                self.timings.append({
                    "name": func_name,
                    "file": filename,
                    "line": lineno,
                    "time": elapsed
                })

        return self.trace_calls


    def start(self):
        sys.settrace(self.trace_calls)

    def stop(self):
        sys.settrace(None)

    def export_csv(self, path="function_timings.csv"):
        if not self.timings:
            print("No functions were timed.")
            return

        min_time = min(t["time"] for t in self.timings)

        with open(path, mode="w", newline="") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["Function", "File", "Line", "Time (s)", "Relative Scale (×min)"])
            for t in self.timings:
                scaled = t["time"] / min_time
                writer.writerow([t["name"], t["file"], t["line"], f"{t['time']:.6f}", f"{scaled:.2f}"])

        print(f"⏱️ Function timing summary exported to: {path}")
