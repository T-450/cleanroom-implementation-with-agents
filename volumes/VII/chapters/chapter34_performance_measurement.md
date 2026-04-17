Chapter 34: Performance Measurement

34.1 Introduction to Performance Engineering

Performance measurement distinguishes between systems that nominally function and systems that function efficiently under real-world load. The clean room methodology extends beyond correctness to encompass performance specifications that define acceptable latency, throughput, and resource consumption. This chapter examines the tools, techniques, and statistical methods required for rigorous performance measurement.

Performance engineering addresses distinct but related concerns. Latency describes the time required to complete individual operations, throughput measures the number of operations per unit time, and resource utilization tracks consumption of CPU, memory, network, and storage. Each metric requires appropriate instrumentation and analysis.

Microbenchmarks measure small code segments in controlled conditions, suitable for algorithm comparison and optimization validation. Macrobenchmarks measure complete systems under realistic workloads, revealing emergent behavior that microbenchmarks cannot predict. Production telemetry provides ground truth about actual user experience but introduces measurement complexity from uncontrolled variables.

34.2 Benchmarking Fundamentals

Effective benchmarking follows established principles: measure the right thing, measure it correctly, and measure it repeatedly. Measuring the right thing requires understanding what users actually experience versus what is technically convenient to measure. Measuring correctly requires eliminating sources of error including warmup, compilation effects, and interference. Measuring repeatedly enables statistical analysis of variance.

Benchmark harnesses must address common pitfalls. Cold start effects dominate initial measurements as JIT compilers optimize and caches populate. Garbage collection introduces unpredictable pauses in managed languages. System load, thermal throttling, and power management cause variation across runs. OS scheduler decisions affect timing resolution.

The benchmarking environment must be controlled. Background processes should be minimized. CPU isolation prevents scheduler interference. Fixed CPU frequency eliminates thermal throttling effects. Sufficient runs enable statistical confidence in results.

34.3 Python Performance Measurement

Python provides multiple timing mechanisms with different characteristics:

The time module provides wall-clock time:

    import time

    start = time.perf_counter()
    result = compute()
    elapsed = time.perf_counter() - start
    print(f"Elapsed: {elapsed:.4f} seconds")

For repeated measurements:

    import statistics
    import time

    def benchmark(func, args=(), iterations=100):
        times = []
        
        # Warmup
        for _ in range(10):
            func(*args)
        
        # Measurement
        for _ in range(iterations):
            start = time.perf_counter()
            func(*args)
            elapsed = time.perf_counter() - start
            times.append(elapsed)
        
        return {
            'mean': statistics.mean(times),
            'median': statistics.median(times),
            'stdev': statistics.stdev(times),
            'min': min(times),
            'max': max(times),
            'p99': sorted(times)[int(len(times) * 0.99)]
        }

timeit module provides convenient microbenchmarking:

    import timeit

    # Command line
    python -m timeit -n 1000 -r 5 -s "import mymodule" "mymodule.compute()"

    # Programmatic
    setup = """
import mymodule
data = list(range(1000))
"""
    
    result = timeit.timeit(
        stmt="mymodule.process(data)",
        setup=setup,
        number=10000,
        repeat=7
    )

34.4 pytest-bench and Benchmark Integration

pytest-benchmark provides integrated benchmarking:

    pip install pytest-benchmark

Basic benchmark test:

    def benchmark_compute(benchmark):
        result = benchmark(compute_expensive_operation)
        assert result > 0

Parameterized benchmarks:

    import pytest

    @pytest.mark.parametrize("size", [100, 1000, 10000])
    def benchmark_process_data(benchmark, size):
        data = list(range(size))
        result = benchmark(process, data)
        assert result is not None

Benchmark configuration:

    # conftest.py
    def pytest_benchmark_update_json(config, benchmarks, output_json):
        for benchmark in output_json['benchmarks']:
            benchmark['custom_field'] = 'custom_value'

    def pytest_benchmark_generate_stats(config, benchmarks):
        # Custom statistics calculation
        pass

Advanced benchmark hooks:

    @pytest.fixture(scope="function")
    def benchmark(request, benchmarksession):
        benchmark.extra_info['data_size'] = request.node.callspec.params.get('size', 0)
        return benchmark

Generate comparison reports:

    pytest-benchmark compare 0012 0013 --group-by=name --sort=name

34.5 Statistical Analysis for Performance

Performance measurements require statistical rigor. Single measurements rarely suffice due to inherent variability. Statistical analysis quantifies uncertainty and enables meaningful comparisons.

Basic statistical measures:

    import statistics
    import math

    def analyze_measurements(times):
        n = len(times)
        mean = statistics.mean(times)
        variance = statistics.variance(times)
        stdev = math.sqrt(variance)
        
        # Standard error of mean
        sem = stdev / math.sqrt(n)
        
        # 95% confidence interval (normal approximation)
        ci_95 = 1.96 * sem
        
        # Percentiles
        sorted_times = sorted(times)
        p50 = statistics.median(sorted_times)
        p95 = sorted_times[int(n * 0.95)]
        p99 = sorted_times[int(n * 0.99)]
        
        return {
            'n': n,
            'mean': mean,
            'stdev': stdev,
            'sem': sem,
            'ci_lower': mean - ci_95,
            'ci_upper': mean + ci_95,
            'p50': p50,
            'p95': p95,
            'p99': p99,
        }

Distribution testing identifies outliers:

    import numpy as np
    from scipy import stats

    def detect_outliers(times, threshold=3):
        """Remove values beyond median ± threshold * MAD"""
        median = np.median(times)
        mad = np.median(np.abs(times - median))
        modified_z_scores = 0.6745 * (times - median) / mad
        
        mask = np.abs(modified_z_scores) < threshold
        return times[mask]

34.6 Statistical Significance Testing

Comparing two implementations requires significance testing:

    from scipy import stats

    def compare_benchmarks(times_a, times_b, alpha=0.05):
        """Welch's t-test for unequal variances"""
        t_stat, p_value = stats.ttest_ind(
            times_a, times_b, 
            equal_var=False
        )
        
        # Effect size (Cohen's d)
        pooled_std = np.sqrt(
            ((len(times_a)-1)*np.var(times_a) + 
             (len(times_b)-1)*np.var(times_b)) / 
            (len(times_a) + len(times_b) - 2)
        )
        cohens_d = (np.mean(times_a) - np.mean(times_b)) / pooled_std
        
        return {
            't_statistic': t_stat,
            'p_value': p_value,
            'significant': p_value < alpha,
            'cohens_d': cohens_d,
            'effect_size': interpret_effect_size(abs(cohens_d))
        }

    def interpret_effect_size(d):
        if d < 0.2:
            return "negligible"
        elif d < 0.5:
            return "small"
        elif d < 0.8:
            return "medium"
        else:
            return "large"

Non-parametric alternative (Wilcoxon rank-sum):

    def compare_nonparametric(times_a, times_b):
        """Mann-Whitney U test for non-normal distributions"""
        statistic, p_value = stats.mannwhitneyu(
            times_a, times_b, 
            alternative='two-sided'
        )
        return {
            'statistic': statistic,
            'p_value': p_value,
            'significant': p_value < 0.05
        }

34.7 Profiling with cProfile

cProfile provides deterministic profiling:

    import cProfile
    import pstats
    import io

    def profile_function(func, *args, **kwargs):
        profiler = cProfile.Profile()
        profiler.enable()
        
        result = func(*args, **kwargs)
        
        profiler.disable()
        
        # Print stats
        s = io.StringIO()
        stats_obj = pstats.Stats(profiler, stream=s)
        stats_obj.sort_stats('cumulative')
        stats_obj.print_stats(20)  # Top 20 functions
        print(s.getvalue())
        
        return result

    # Command line
    python -m cProfile -s cumulative script.py

    # Profile output analysis
    python -c "
import pstats
p = pstats.Stats('output.prof')
p.sort_stats('cumulative')
p.print_stats()
"

Visualization with snakeviz:

    pip install snakeviz
    python -m cProfile -o output.prof script.py
    snakeviz output.prof

34.8 Line Profiling

Line-by-line profiling identifies hot lines:

    pip install line_profiler

Usage:

    from line_profiler import LineProfiler

    profiler = LineProfiler()

    @profiler
    def process_data(data):
        results = []
        for item in data:      # Line 1
            processed = heavy(item)  # Line 2
            results.append(processed)  # Line 3
        return results         # Line 4

    process_data(large_dataset)
    profiler.print_stats()

Command line:

    kernprof -l -v script.py

34.9 Memory Profiling

Memory profiling tracks allocation patterns:

    pip install memory_profiler

Line-by-line memory profiling:

    from memory_profiler import profile

    @profile
    def process_large_dataset():
        data = load_data()  # Memory spike here
        results = []
        for chunk in chunks(data):
            processed = process(chunk)
            results.extend(processed)
        return results

Command line:

    python -m memory_profiler myscript.py

Memory tracking over time:

    from memory_profiler import memory_usage

    def track_memory(func, interval=0.1):
        mem_usage = memory_usage(
            (func, ()),
            interval=interval,
            max_usage=True,
            retval=True
        )
        return mem_usage

Object allocation tracing:

    import tracemalloc

    def trace_allocations():
        tracemalloc.start()
        
        # Code to analyze
        process_data()
        
        snapshot = tracemalloc.take_snapshot()
        top_stats = snapshot.statistics('lineno')
        
        for stat in top_stats[:10]:
            print(stat)

34.10 py-spy: Sampling Profiler

py-spy provides low-overhead sampling:

    pip install py-spy

Record flames graph:

    py-spy record -o profile.svg -- python myscript.py

Top-like live view:

    py-spy top -- python myscript.py

Dump current stack:

    py-spy dump --pid <pid>

34.11 Go Benchmarking

Go's testing package includes benchmarks:

    // mylib_test.go
    package mylib

    import "testing"

    func BenchmarkProcess(b *testing.B) {
        data := generateTestData()
        
        b.ResetTimer()
        for i := 0; i < b.N; i++ {
            Process(data)
        }
    }

    func BenchmarkProcessParallel(b *testing.B) {
        data := generateTestData()
        
        b.RunParallel(func(pb *testing.PB) {
            for pb.Next() {
                Process(data)
            }
        })
    }

Run benchmarks:

    go test -bench=. -benchmem -count=10
    go test -bench=. -cpuprofile=cpu.prof -memprofile=mem.prof

Profile analysis:

    go tool pprof cpu.prof
    (pprof) top
    (pprof) list myFunction
    (pprof) web  # Generate graph

34.12 Rust Benchmarking with Criterion

Criterion provides statistics-driven benchmarking:

    [dev-dependencies]
    criterion = { version = "0.5", features = ["html_reports"] }

    [[bench]]
    name = "my_benchmark"
    harness = false

Benchmark:

    use criterion::{black_box, criterion_group, criterion_main, Criterion};

    fn process(data: &[u8]) -> Vec<u8> {
        // Implementation
        data.to_vec()
    }

    fn criterion_benchmark(c: &mut Criterion) {
        let data = vec![0u8; 1024];
        
        c.bench_function("process 1k", |b| {
            b.iter(|| process(black_box(&data)))
        });
    }

    criterion_group!(benches, criterion_benchmark);
    criterion_main!(benches);

34.13 Load Testing with Locust

Locust provides Python-based load testing:

    pip install locust

Test definition:

    from locust import HttpUser, task, between

    class WebsiteUser(HttpUser):
        wait_time = between(1, 5)

        @task(10)
        def index_page(self):
            self.client.get("/")

        @task(5)
        def view_item(self):
            item_id = random.randint(1, 10000)
            self.client.get(f"/item/{item_id}", name="/item/[id]")

        @task(1)
        def add_to_cart(self):
            self.client.post("/cart", json={
                "item_id": random.randint(1, 10000),
                "quantity": 1
            })

Run:

    locust -f locustfile.py --host=http://localhost:8000

Headless mode:

    locust -f locustfile.py \
        --headless \
        -u 1000 \
        -r 100 \
        --run-time 30m \
        --csv=results

34.14 k6 for Modern Load Testing

k6 provides JavaScript-based load testing:

    import http from 'k6/http';
    import { check, sleep } from 'k6';

    export const options = {
        stages: [
            { duration: '2m', target: 100 },
            { duration: '5m', target: 100 },
            { duration: '2m', target: 200 },
            { duration: '5m', target: 200 },
            { duration: '2m', target: 0 },
        ],
        thresholds: {
            http_req_duration: ['p(95)<500'],
            http_req_failed: ['rate<0.1'],
        },
    };

    export default function () {
        const res = http.get('https://api.example.com/users');
        check(res, {
            'status is 200': (r) => r.status === 200,
            'response time < 500ms': (r) => r.timings.duration < 500,
        });
        sleep(1);
    }

Run:

    k6 run script.js

Cloud execution:

    k6 cloud script.js

34.15 Distributed Load Testing

Distributed Locust:

    # Master node
    locust -f locustfile.py --master --web-host=0.0.0.0

    # Worker nodes (multiple)
    locust -f locustfile.py --worker --master-host=<master-ip>

Docker Compose setup:

    version: '3'
    services:
      master:
        image: locustio/locust
        ports:
          - "8089:8089"
        volumes:
          - ./locustfile.py:/mnt/locust/locustfile.py
        command: -f /mnt/locust/locustfile.py --master -H http://target:8000
    
      worker:
        image: locustio/locust
        volumes:
          - ./locustfile.py:/mnt/locust/locustfile.py
        command: -f /mnt/locust/locustfile.py --worker --master-host master
        deploy:
          replicas: 10

34.16 Performance Regression Detection

Automated regression detection in CI:

    # compare_performance.py
    import json
    import statistics
    import sys

    def load_benchmarks(path):
        with open(path) as f:
            return json.load(f)

    def detect_regression(baseline, current, threshold=0.05):
        regressions = []
        
        for bench_name, current_data in current.items():
            if bench_name not in baseline:
                continue
            
            baseline_mean = baseline[bench_name]['mean']
            current_mean = current_data['mean']
            
            regression_ratio = (current_mean - baseline_mean) / baseline_mean
            
            if regression_ratio > threshold:
                regressions.append({
                    'benchmark': bench_name,
                    'baseline': baseline_mean,
                    'current': current_mean,
                    'regression': regression_ratio * 100
                })
        
        return regressions

    if __name__ == '__main__':
        baseline = load_benchmarks('baseline.json')
        current = load_benchmarks('current.json')
        
        regressions = detect_regression(baseline, current)
        
        if regressions:
            print("PERFORMANCE REGRESSIONS DETECTED:")
            for r in regressions:
                print(f"  {r['benchmark']}: +{r['regression']:.1f}%")
            sys.exit(1)
        else:
            print("No regressions detected")
            sys.exit(0)

GitHub Actions integration:

    # .github/workflows/perf.yml
    name: Performance Regression

    on: [pull_request]

    jobs:
      benchmark:
        runs-on: ubuntu-latest
        steps:
        - uses: actions/checkout@v3
          with:
            fetch-depth: 0
    
        - name: Run baseline benchmarks
          run: |
            git checkout main
            pytest bench/ --benchmark-json=baseline.json
    
        - name: Run current benchmarks
          run: |
            git checkout ${{ github.sha }}
            pytest bench/ --benchmark-json=current.json
    
        - name: Compare
          run: python compare_performance.py

34.17 Latency Percentile Analysis

Service level objective tracking:

    import numpy as np
    from dataclasses import dataclass

    @dataclass
    class SLO:
        target_p50: float  # ms
        target_p95: float  # ms
        target_p99: float  # ms
        target_error_rate: float

    class LatencyAnalyzer:
        def __init__(self, slo: SLO):
            self.slo = slo
            self.latencies = []
            self.errors = 0
            self.total = 0

        def record(self, latency_ms: float, error: bool = False):
            self.latencies.append(latency_ms)
            self.total += 1
            if error:
                self.errors += 1

        def analyze(self):
            if not self.latencies:
                return {}
            
            sorted_lat = sorted(self.latencies)
            n = len(sorted_lat)
            
            return {
                'p50': sorted_lat[int(n * 0.50)],
                'p95': sorted_lat[int(n * 0.95)],
                'p99': sorted_lat[int(n * 0.99)],
                'p99.9': sorted_lat[int(n * 0.999)],
                'min': sorted_lat[0],
                'max': sorted_lat[-1],
                'mean': statistics.mean(sorted_lat),
                'error_rate': self.errors / self.total,
                'slo_compliance': {
                    'p50': sorted_lat[int(n * 0.50)] <= self.slo.target_p50,
                    'p95': sorted_lat[int(n * 0.95)] <= self.slo.target_p95,
                    'p99': sorted_lat[int(n * 0.99)] <= self.slo.target_p99,
                }
            }

34.18 Throughput Testing

Throughput measurement methodology:

    import concurrent.futures
    import time
    import queue
    import threading

    class ThroughputTest:
        def __init__(self, target_tps: int, duration_seconds: int):
            self.target_tps = target_tps
            self.duration = duration_seconds
            self.results = queue.Queue()
            self.stop_event = threading.Event()

        def worker(self, worker_id: int):
            interval = 1.0 / self.target_tps
            next_time = time.perf_counter()
            
            while not self.stop_event.is_set():
                current_time = time.perf_counter()
                if current_time < next_time:
                    time.sleep(next_time - current_time)
                
                start = time.perf_counter()
                try:
                    result = perform_operation()
                    success = True
                except Exception:
                    success = False
                latency = time.perf_counter() - start
                
                self.results.put({
                    'worker': worker_id,
                    'latency': latency,
                    'success': success,
                    'timestamp': start
                })
                
                next_time += interval

        def run(self, workers: int = 10):
            threads = []
            for i in range(workers):
                t = threading.Thread(target=self.worker, args=(i,))
                t.start()
                threads.append(t)
            
            time.sleep(self.duration)
            self.stop_event.set()
            
            for t in threads:
                t.join()
            
            return self.analyze_results()

        def analyze_results(self):
            results = []
            while not self.results.empty():
                results.append(self.results.get())
            
            successful = [r for r in results if r['success']]
            latencies = [r['latency'] for r in successful]
            
            return {
                'total_requests': len(results),
                'successful': len(successful),
                'failed': len(results) - len(successful),
                'actual_tps': len(results) / self.duration,
                'p99_latency': np.percentile(latencies, 99) if latencies else None,
            }

34.19 Resource Utilization Monitoring

Monitor system resources during tests:

    import psutil
    import threading
    import time

    class ResourceMonitor:
        def __init__(self, interval=1.0):
            self.interval = interval
            self.measurements = []
            self._stop = threading.Event()
            self._thread = None

        def _monitor(self):
            process = psutil.Process()
            
            while not self._stop.is_set():
                measurement = {
                    'timestamp': time.time(),
                    'cpu_percent': process.cpu_percent(),
                    'memory_mb': process.memory_info().rss / 1024 / 1024,
                    'memory_percent': process.memory_percent(),
                    'num_threads': process.num_threads(),
                    'open_files': len(process.open_files()),
                    'connections': len(process.connections()),
                }
                
                # System-wide metrics
                measurement['system_cpu'] = psutil.cpu_percent(interval=None)
                measurement['system_memory'] = psutil.virtual_memory().percent
                
                self.measurements.append(measurement)
                time.sleep(self.interval)

        def start(self):
            self._thread = threading.Thread(target=self._monitor)
            self._thread.start()

        def stop(self):
            self._stop.set()
            if self._thread:
                self._thread.join()

        def summary(self):
            if not self.measurements:
                return {}
            
            cpu_values = [m['cpu_percent'] for m in self.measurements]
            memory_values = [m['memory_mb'] for m in self.measurements]
            
            return {
                'cpu_avg': statistics.mean(cpu_values),
                'cpu_max': max(cpu_values),
                'memory_avg_mb': statistics.mean(memory_values),
                'memory_max_mb': max(memory_values),
                'duration': len(self.measurements) * self.interval
            }

Usage:

    monitor = ResourceMonitor(interval=0.5)
    monitor.start()
    
    run_benchmark()
    
    monitor.stop()
    print(monitor.summary())

34.20 Distributed Tracing for Performance

OpenTelemetry integration tracks request flows:

    from opentelemetry import trace
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor
    from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter

    provider = TracerProvider()
    processor = BatchSpanProcessor(OTLPSpanExporter(endpoint="localhost:4317"))
    provider.add_span_processor(processor)
    trace.set_tracer_provider(provider)

    tracer = trace.get_tracer(__name__)

    def process_request(request):
        with tracer.start_as_current_span("process_request") as span:
            span.set_attribute("request.size", len(request.body))
            
            with tracer.start_as_current_span("validate"):
                validated = validate(request)
            
            with tracer.start_as_current_span("process"):
                result = do_processing(validated)
            
            with tracer.start_as_current_span("store"):
                store_result(result)
            
            return result

Jaeger visualization shows request latency breakdown across services.

34.21 Database Query Performance

SQL query analysis:

    import time
    import functools
    import logging

    class QueryProfiler:
        def __init__(self, threshold_ms=100):
            self.threshold_ms = threshold_ms
            self.queries = []

        def profile(self, func):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                start = time.perf_counter()
                result = func(*args, **kwargs)
                elapsed_ms = (time.perf_counter() - start) * 1000
                
                query_info = {
                    'function': func.__name__,
                    'duration_ms': elapsed_ms,
                    'slow': elapsed_ms > self.threshold_ms
                }
                self.queries.append(query_info)
                
                if query_info['slow']:
                    logging.warning(f"Slow query: {func.__name__} took {elapsed_ms:.2f}ms")
                
                return result
            return wrapper

    # SQLAlchemy integration
    from sqlalchemy import event

    @event.listens_for(engine, "before_cursor_execute")
    def before_cursor_execute(conn, cursor, statement, parameters, 
                              context, executemany):
        context._query_start_time = time.time()

    @event.listens_for(engine, "after_cursor_execute")
    def after_cursor_execute(conn, cursor, statement, parameters, 
                             context, executemany):
        total = time.time() - context._query_start_time
        if total > 0.1:  # 100ms threshold
            logging.warning(f"Slow query ({total:.2f}s): {statement[:200]}")

34.22 Caching Performance Analysis

Cache hit rate measurement:

    import functools
    from collections import OrderedDict

    class InstrumentedCache:
        def __init__(self, maxsize=128):
            self.cache = OrderedDict()
            self.maxsize = maxsize
            self.hits = 0
            self.misses = 0

        def get(self, key):
            if key in self.cache:
                self.hits += 1
                self.cache.move_to_end(key)
                return self.cache[key]
            self.misses += 1
            return None

        def put(self, key, value):
            if key in self.cache:
                self.cache.move_to_end(key)
            self.cache[key] = value
            if len(self.cache) > self.maxsize:
                self.cache.popitem(last=False)

        def stats(self):
            total = self.hits + self.misses
            return {
                'hits': self.hits,
                'misses': self.misses,
                'hit_rate': self.hits / total if total > 0 else 0,
                'size': len(self.cache),
                'maxsize': self.maxsize
            }

34.23 Network Performance Testing

Network latency and throughput measurement:

    import socket
    import struct
    import time
    import statistics

    class NetworkBenchmark:
        def __init__(self, host: str, port: int):
            self.host = host
            self.port = port

        def measure_latency(self, samples: int = 100) -> dict:
            latencies = []
            
            for _ in range(samples):
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                start = time.perf_counter()
                sock.connect((self.host, self.port))
                elapsed = time.perf_counter() - start
                latencies.append(elapsed * 1000)  # Convert to ms
                sock.close()
            
            return {
                'p50': statistics.median(latencies),
                'p95': sorted(latencies)[int(samples * 0.95)],
                'p99': sorted(latencies)[int(samples * 0.99)],
                'mean': statistics.mean(latencies),
                'stdev': statistics.stdev(latencies) if samples > 1 else 0
            }

        def measure_throughput(self, duration: int = 10) -> dict:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((self.host, self.port))
            
            bytes_transferred = 0
            chunk = b'X' * 4096
            start = time.time()
            
            while time.time() - start < duration:
                sock.sendall(chunk)
                bytes_transferred += len(chunk)
                
            sock.close()
            
            elapsed = time.time() - start
            return {
                'bytes_per_second': bytes_transferred / elapsed,
                'bits_per_second': bytes_transferred * 8 / elapsed,
                'duration': elapsed
            }

34.24 JVM Performance Analysis

JVM-specific profiling tools:

    import subprocess
    import json

    class JVMProfiler:
        def __init__(self, pid: int):
            self.pid = pid

        def gc_stats(self) -> dict:
            result = subprocess.run(
                ['jstat', '-gc', str(self.pid)],
                capture_output=True, text=True
            )
            # Parse jstat output
            return self._parse_gc_output(result.stdout)

        def heap_dump(self, path: str):
            subprocess.run([
                'jmap', '-dump:format=b,file=' + path, 
                str(self.pid)
            ])

        def thread_dump(self) -> str:
            result = subprocess.run(
                ['jstack', str(self.pid)],
                capture_output=True, text=True
            )
            return result.stdout

        def flight_recording(self, duration_sec: int, filename: str):
            subprocess.run([
                'jcmd', str(self.pid), 
                'JFR.start',
                f'duration={duration_sec}s',
                f'filename={filename}'
            ])

34.25 Performance Testing Best Practices

Effective performance testing requires systematic approach:

Isolate test environment: Run benchmarks on dedicated hardware or isolated cloud instances to prevent interference from other workloads. Disable CPU frequency scaling and lock to constant frequency. Ensure sufficient thermal headroom to prevent throttling.

Warmup properly: JIT compilers and caches require warmup before measurements stabilize. Run multiple warmup iterations before recording measurements. Monitor for convergence in results before accepting measurements.

Measure statistically significant samples: Single measurements are insufficient due to inherent variability. Collect sufficient samples for statistical analysis (typically 30+ for rough estimates, 100+ for confidence). Report confidence intervals rather than point estimates.

Test realistic scenarios: Synthetic microbenchmarks rarely predict production performance. Test with production-like data volumes and access patterns. Include realistic concurrency levels matching production usage.

Monitor resource utilization: Performance regressions often manifest as increased resource consumption rather than direct latency increases. Monitor CPU, memory, network, and disk utilization alongside latency metrics. Include resource efficiency in regression detection.

Establish SLOs early: Service level objectives provide objective criteria for acceptable performance. Define latency percentiles (p50, p95, p99) with specific targets. Report compliance against SLOs rather than raw numbers.

Automate regression detection: Manual performance comparison is error-prone and rarely sustained. Automate performance testing in CI/CD pipelines. Fail builds on significant regressions with clear attribution.

Profile before optimizing: Measurement identifies whether optimization is needed; profiling identifies where optimization will help. Comprehensive profiling prevents wasted effort optimizing non-critical paths. Focus optimization on hot paths identified through profiling.
