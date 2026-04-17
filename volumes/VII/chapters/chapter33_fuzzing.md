Chapter 33: Fuzzing and Property-Based Testing

33.1 Introduction to Fuzzing

Fuzzing represents a sophisticated testing technique that automatically generates random inputs to discover security vulnerabilities, crashes, and unexpected behavior. Unlike manual test case creation that relies on human anticipation of edge cases, fuzzing systematically explores the input space, often revealing bugs that would elude conventional testing.

The methodology emerged from the observation that many security vulnerabilities stem from malformed input handling. Buffer overflows, format string bugs, integer overflows, and parse errors frequently manifest only when systems encounter inputs their designers never anticipated. Fuzzing addresses this by generating thousands or millions of inputs, both valid and invalid, to stress-test input handling code.

Two fundamental approaches dominate fuzzing: black-box fuzzing generates inputs without knowledge of internal program structure, while white-box (or coverage-guided) fuzzing uses program instrumentation to guide input generation toward unexplored code paths. Coverage-guided approaches have proven dramatically more effective, achieving deep code exploration that random generation alone cannot match.

33.2 Fuzzing Architecture and Types

Fuzzing systems share common components regardless of specific tooling. The generator produces inputs according to specified constraints or randomly. The execution engine runs the target program with generated inputs while monitoring for crashes, hangs, or sanitizer errors. The feedback mechanism informs future input generation based on execution results.

Mutation-based fuzzing starts with a corpus of valid inputs and modifies them randomly, applying operations like bit flipping, arithmetic mutations, and block insertion or deletion. This approach preserves structural validity while introducing variations that trigger edge cases in parsing and processing.

Generation-based fuzzing constructs inputs from formal grammars or specifications, ensuring syntactic validity while allowing semantic variation. This approach excels for structured formats like protocols, file formats, and programming languages where random bytes rarely form valid inputs.

Coverage-guided fuzzing instruments the target program to track executed code paths. When an input reaches previously unexplored code, the fuzzer prioritizes it for mutation, guiding exploration toward deeper program behavior. This feedback loop enables fuzzers to discover complex vulnerabilities that require specific input sequences.

33.3 American Fuzzy Lop (AFL)

AFL pioneered coverage-guided fuzzing for general-purpose software. Despite requiring source code for instrumentation, it remains effective for C and C++ codebases.

Installation on Linux:

    git clone https://github.com/google/AFL.git
    cd AFL
    make
    sudo make install

AFL works by compiling target programs with special instrumentation:

    afl-gcc -o target target.c
    afl-fuzz -i input_dir -o output_dir ./target @@

The instrumentation tracks basic block transitions, creating a compact representation of execution paths. When a new path is discovered, the input triggering it becomes a seed for further mutation.

Basic compilation example:

    # target.c
    #include <stdio.h>
    #include <stdlib.h>

    int main(int argc, char** argv) {
        char buffer[100];
        FILE* f = fopen(argv[1], "r");
        if (!f) return 1;
        
        size_t n = fread(buffer, 1, 200, f);  // Bug: buffer overflow
        fclose(f);
        
        if (n > 0 && buffer[0] == 'A') {
            if (n > 1 && buffer[1] == 'B') {
                if (n > 2 && buffer[2] == 'C') {
                    abort();  // Crash trigger
                }
            }
        }
        return 0;
    }

Compile and fuzz:

    afl-gcc -o target target.c
    mkdir -p in out
    echo "test" > in/seed.txt
    afl-fuzz -i in -o out ./target @@

33.4 AFL++ Enhancements

AFL++ extends AFL with modern improvements:

    git clone https://github.com/AFLplusplus/AFLplusplus.git
    cd AFLplusplus
    make -j$(nproc)
    sudo make install

Key features include:

Improved mutators supporting structure-aware fuzzing:

    afl-fuzz -i in -o out -x dict.json ./target @@

QEMU mode for black-box binaries:

    afl-fuzz -i in -o out -Q ./binary @@

Frida mode for Android and iOS:

    afl-fuzz -i in -o out -O ./app

Persistent mode for in-process fuzzing:

    #include <stdio.h>
    #include <stdlib.h>
    #include "afl-fuzz.h"

    __AFL_FUZZ_INIT();

    int main(int argc, char** argv) {
        __AFL_INIT();
        
        unsigned char* buf = __AFL_FUZZ_TESTCASE_BUF;
        while (__AFL_LOOP(10000)) {
            int len = __AFL_FUZZ_TESTCASE_LEN;
            process_input(buf, len);
        }
        return 0;
    }

33.5 LibFuzzer

LibFuzzer provides in-process, coverage-guided fuzzing without fork overhead:

    clang -fsanitize=fuzzer,address target.c

The fuzzing harness defines the entry point:

    // fuzz_target.cpp
    #include <stdint.h>
    #include <stddef.h>

    extern "C" int LLVMFuzzerTestOneInput(const uint8_t* data, size_t size) {
        // Process the fuzzed input
        if (size > 0 && data[0] == 'A') {
            if (size > 1 && data[1] == 'B') {
                if (size > 2 && data[2] == 'C') {
                    __builtin_trap();  // Crash
                }
            }
        }
        return 0;
    }

Compile and run:

    clang++ -g -fsanitize=fuzzer,address -o fuzz_target fuzz_target.cpp
    ./fuzz_target -max_total_time=60 corpus/

Dictionary support improves structured format fuzzing:

    # network.dict
    "GET"
    "POST"
    "HTTP/1.1"
    "Content-Type"
    "Content-Length"
    "\r\n"

    clang++ -fsanitize=fuzzer -o fuzz_target fuzz_target.cpp -dict=network.dict

33.6 Custom LLVMFuzzer Harnesses

Complex fuzzing requires custom harnesses. For a parser:

    #include <cstdint>
    #include <cstddef>
    #include <string>
    #include "myparser.h"

    extern "C" int LLVMFuzzerTestOneInput(const uint8_t* data, 
                                          size_t size) {
        // Limit input size to prevent excessive resource use
        if (size > 1024 * 1024) return 0;
        
        std::string input(reinterpret_cast<const char*>(data), size);
        
        // Test parsing
        ParsedResult result = MyParser::parse(input);
        
        // Test serialization roundtrip
        if (result.isValid()) {
            std::string serialized = result.serialize();
            ParsedResult reparsed = MyParser::parse(serialized);
            
            // Verify roundtrip preserves meaning
            assert(reparsed.isValid());
            assert(result.equals(reparsed));
        }
        
        return 0;
    }

33.7 Sanitizer Integration

Address Sanitizer detects memory errors:

    clang -fsanitize=fuzzer,address -g -o fuzz_target target.c

detects:
- Use after free
- Heap buffer overflow
- Stack buffer overflow
- Global buffer overflow
- Use after return
- Use after scope
- Initialization order bugs
- Memory leaks

Memory Sanitizer detects uninitialized memory:

    clang -fsanitize=fuzzer,memory -g -o fuzz_target target.c

Undefined Behavior Sanitizer detects:

    clang -fsanitize=fuzzer,undefined -g -o fuzz_target target.c

detects:
- Signed integer overflow
- Unsigned integer overflow
- Float cast overflow
- Division by zero
- Null pointer dereference
- Misaligned pointer access

33.8 Structure-Aware Fuzzing

Custom mutators understand input structure:

    // protobuf_mutator example
    #include <libprotobuf-mutator/src/libfuzzer_macro.h>
    #include "test_protobuf.pb.h"

    DEFINE_PROTO_FUZZER(const TestMessage& message) {
        // Message arrives mutated and valid
        process_protobuf(message);
    }

Compile with protobuf mutator:

    clang++ -fsanitize=fuzzer,address \
        -I/path/to/libprotobuf-mutator \
        fuzzer.cc test_protobuf.pb.cc \
        -lprotobuf-mutator-libfuzzer -lprotobuf-mutator \
        -lprotobuf

33.9 Network Protocol Fuzzing

Network services require specialized handling. A TCP fuzzing harness:

    #include <sys/socket.h>
    #include <netinet/in.h>
    #include <arpa/inet.h>

    extern "C" int LLVMFuzzerTestOneInput(const uint8_t* data, 
                                          size_t size) {
        int sock = socket(AF_INET, SOCK_STREAM, 0);
        
        struct sockaddr_in addr;
        addr.sin_family = AF_INET;
        addr.sin_port = htons(8080);
        inet_pton(AF_INET, "127.0.0.1", &addr.sin_addr);
        
        if (connect(sock, (struct sockaddr*)&addr, sizeof(addr)) == 0) {
            send(sock, data, size, 0);
            
            char response[1024];
            recv(sock, response, sizeof(response), 0);
        }
        
        close(sock);
        return 0;
    }

Stateful protocol fuzzing with sequence tracking:

    class ProtocolStateMachine {
        enum State { INIT, AUTHENTICATED, CONNECTED, CLOSED };
        State state = INIT;
        
    public:
        void process(const uint8_t* data, size_t size) {
            switch (state) {
                case INIT:
                    if (is_auth_command(data, size)) {
                        state = AUTHENTICATED;
                    }
                    break;
                case AUTHENTICATED:
                    if (is_connect_command(data, size)) {
                        state = CONNECTED;
                    }
                    break;
                // ...
            }
        }
    };

33.10 File Format Fuzzing

File parsers benefit from format-aware mutation. PDF fuzzing example:

    #include <poppler/PDFDoc.h>

    extern "C" int LLVMFuzzerTestOneInput(const uint8_t* data, 
                                          size_t size) {
        MemStream stream((char*)data, 0, size, Object(objNull));
        PDFDoc doc(&stream);
        
        if (!doc.isOk()) return 0;
        
        // Test page rendering
        for (int i = 0; i < doc.getNumPages(); i++) {
            Page* page = doc.getPage(i);
            if (page) {
                GfxState state(...);
                page->display(&state);
            }
        }
        
        return 0;
    }

Image format fuzzing:

    #include <turbojpeg.h>

    extern "C" int LLVMFuzzerTestOneInput(const uint8_t* data, 
                                          size_t size) {
        tjhandle handle = tjInitDecompress();
        
        int width, height, subsamp, colorspace;
        if (tjDecompressHeader3(handle, data, size, &width, &height,
                                &subsamp, &colorspace) != 0) {
            tjDestroy(handle);
            return 0;
        }
        
        unsigned char* buffer = new unsigned char[width * height * 4];
        tjDecompress2(handle, data, size, buffer, width, 0, height,
                      TJPF_RGBA, 0);
        
        delete[] buffer;
        tjDestroy(handle);
        return 0;
    }

33.11 Database Fuzzing

SQL fuzzing requires careful isolation:

    extern "C" int LLVMFuzzerTestOneInput(const uint8_t* data, 
                                          size_t size) {
        // Reset database state
        sqlite3_exec(db, "ROLLBACK", NULL, NULL, NULL);
        
        std::string sql(reinterpret_cast<const char*>(data), size);
        
        sqlite3_stmt* stmt;
        if (sqlite3_prepare_v2(db, sql.c_str(), -1, &stmt, NULL) 
            == SQLITE_OK) {
            sqlite3_step(stmt);
            sqlite3_finalize(stmt);
        }
        
        return 0;
    }

33.12 Continuous Fuzzing with OSS-Fuzz

OSS-Fuzz provides continuous fuzzing infrastructure:

Project structure:

    my-project/
    ├── Dockerfile
    ├── build.sh
    ├── project.yaml
    └── harness/
        └── fuzz_target.cc

Dockerfile:

    FROM gcr.io/oss-fuzz-base/base-builder
    RUN apt-get update && apt-get install -y make cmake
    COPY . my-project
    WORKDIR my-project
    COPY build.sh $SRC/

build.sh:

    #!/bin/bash
    set -e

    mkdir build && cd build
    cmake ..
    make -j$(nproc)

    $CXX $CXXFLAGS -I../include \
        $SRC/my-project/harness/fuzz_target.cc \
        -o $OUT/fuzz_target \
        $LIB_FUZZING_ENGINE libmyproject.a

project.yaml:

    homepage: "https://myproject.org"
    language: c++
    primary_contact: "security@myproject.org"
    auto_ccs:
      - "developer@myproject.org"
    sanitizers:
      - address
      - memory
      - undefined

33.13 Python Fuzzing with Atheris

Atheris brings libFuzzer to Python:

    pip install atheris

Basic fuzzing harness:

    import atheris
    import sys
    import myparser

    def TestOneInput(data):
        fdp = atheris.FuzzedDataProvider(data)
        
        input_str = fdp.ConsumeUnicodeNoSurrogates(1024)
        
        try:
            result = myparser.parse(input_str)
            result.validate()
        except myparser.ParseError:
            pass

    atheris.Setup(sys.argv, TestOneInput)
    atheris.Fuzz()

Run with:

    python fuzz.py -max_total_time=300 -jobs=4 corpus/

Differential fuzzing compares multiple implementations:

    def TestOneInput(data):
        fdp = atheris.FuzzedDataProvider(data)
        json_str = fdp.ConsumeUnicodeNoSurrogates(1024)
        
        try:
            result1 = json.loads(json_str)
            result2 = myjson.parse(json_str)
            assert result1 == result2
        except (json.JSONDecodeError, myjson.ParseError):
            pass

33.14 Go Fuzzing with Native Support

Go 1.18+ includes native fuzzing:

    // fuzz_test.go
    package mypkg

    import "testing"

    func FuzzParse(f *testing.F) {
        f.Add("valid input")
        f.Add("another\ninput")
        
        f.Fuzz(func(t *testing.T, input string) {
            result, err := Parse(input)
            if err != nil {
                return  // Error handling is fine
            }
            
            // Verify serialization roundtrip
            serialized, err := result.Serialize()
            if err != nil {
                t.Fatalf("serialization failed: %v", err)
            }
            
            reparsed, err := Parse(serialized)
            if err != nil {
                t.Fatalf("reparsing failed: %v", err)
            }
            
            if !result.Equal(reparsed) {
                t.Errorf("roundtrip mismatch")
            }
        })
    }

Run fuzzing:

    go test -fuzz=FuzzParse -fuzztime=1h

33.15 Rust Fuzzing with Cargo-Fuzz

Rust fuzzing uses cargo-fuzz:

    cargo install cargo-fuzz
    cargo fuzz init
    cargo fuzz add mytarget

Generated harness:

    // fuzz/fuzz_targets/mytarget.rs
    #![no_main]
    use libfuzzer_sys::fuzz_target;

    fuzz_target!(|data: &[u8]| {
        if let Ok(s) = std::str::from_utf8(data) {
            let _ = mycrate::parse(s);
        }
    });

Run fuzzing:

    cargo fuzz run mytarget -max_total_time=3600

33.16 Java Fuzzing with Jazzer

Jazzer provides Java fuzzing:

    # Fuzz target
    public class FuzzTarget {
        public static void fuzzerTestOneInput(byte[] data) {
            try {
                MyParser.parse(new String(data, StandardCharsets.UTF_8));
            } catch (ParseException e) {
                // Expected for malformed input
            }
        }
    }

Run with:

    jazzer --cp=myapp.jar \
           --target_class=FuzzTarget \
           -max_total_time=300

33.17 Fuzzing CI/CD Integration

GitHub Actions fuzzing job:

    # .github/workflows/fuzz.yml
    name: Fuzzing

    on:
      schedule:
        - cron: '0 0 * * 0'  # Weekly
      workflow_dispatch:

    jobs:
      fuzz:
        runs-on: ubuntu-latest
        steps:
        - uses: actions/checkout@v3
    
        - name: Build fuzzer
          run: |
            sudo apt-get update
            sudo apt-get install -y clang
            make fuzz
    
        - name: Run fuzzing
          timeout-minutes: 60
          run: |
            mkdir -p corpus
            ./fuzz/fuzz_target corpus/ \
                -max_total_time=3600 \
                -print_final_stats=1 \
                -jobs=4 \
                -workers=4
    
        - name: Upload corpus
          uses: actions/upload-artifact@v3
          with:
            name: fuzz-corpus
            path: corpus/

33.18 Corpus Management

Effective fuzzing requires proper corpus management:

Minimize corpus size while preserving coverage:

    afl-cmin -i input_dir -o output_dir -- ./target @@

Merge multiple corpora:

    afl-merge input_corpus1 input_corpus2 output_corpus ./target

Corpus coverage analysis:

    ./fuzz_target corpus/ -runs=0 -print_final_stats=1

33.19 Fuzzing Metrics and Triage

Track fuzzing effectiveness:

    #!/bin/bash
    # fuzz_metrics.sh

    CORPUS_DIR="corpus"
    
    echo "Corpus Statistics:"
    echo "  Files: $(find $CORpus_DIR -type f | wc -l)"
    echo "  Total size: $(du -sh $CORPUS_DIR | cut -f1)"
    echo "  Average: $(find $CORPUS_DIR -type f | xargs stat --format="%s" | awk '{ sum += $1; n++ } END { print sum/n }') bytes"
    
    # Coverage stats from libFuzzer
    ./fuzz_target $CORPUS_DIR -runs=0 -print_coverage=1

Crash triage workflow:

    #!/bin/bash
    # triage_crashes.sh

    for crash in crashes/*; do
        echo "Analyzing: $crash"
        
        # Reproduce crash
        ./target "$crash" 2>&1 | head -20
        
        # Get stack trace
        lldb -b -o "run" -o "bt" -- ./target "$crash" 2>&1 | tail -30
    done

33.20 Advanced Mutation Strategies

Custom mutators for domain-specific inputs:

    class XMLMutator {
    public:
        std::vector<uint8_t> Mutate(const std::vector<uint8_t>& data,
                                    size_t max_size,
                                    unsigned int seed) {
            std::string xml(data.begin(), data.end());
            
            // Pick mutation strategy
            switch (rand() % 5) {
                case 0:  // Mutate tag name
                    xml = MutateTagName(xml);
                    break;
                case 1:  // Mutate attribute
                    xml = MutateAttribute(xml);
                    break;
                case 2:  // Insert random tag
                    xml = InsertTag(xml);
                    break;
                case 3:  // Mutate text content
                    xml = MutateText(xml);
                    break;
                case 4:  // AFL-style bit flip
                    return AFLMutate(data, max_size, seed);
            }
            
            return std::vector<uint8_t>(xml.begin(), xml.end());
        }
    };

33.21 Differential Fuzzing

Comparing multiple implementations:

    extern "C" int LLVMFuzzerTestOneInput(const uint8_t* data, 
                                          size_t size) {
        // Feed same input to multiple parsers
        auto result1 = parser_v1::parse(data, size);
        auto result2 = parser_v2::parse(data, size);
        
        // Results should be equivalent
        assert(result1.equivalent_to(result2));
        
        return 0;
    }

Cryptographic differential fuzzing:

    bool DifferentialSHA256(const uint8_t* data, size_t size) {
        uint8_t out1[32], out2[32];
        
        openssl::SHA256(data, size, out1);
        libsodium::crypto_hash_sha256(out2, data, size);
        
        return memcmp(out1, out2, 32) == 0;
    }

33.22 Fuzzing Test Oracles

Oracles detect incorrect behavior beyond crashes:

    class TestOracle {
    public:
        static bool check_roundtrip(const std::string& input) {
            auto parsed = Parser::parse(input);
            auto serialized = parsed.serialize();
            auto reparsed = Parser::parse(serialized);
            
            return parsed.equivalent_to(reparsed);
        }
        
        static bool check_no_undefined(const std::string& input) {
            // Use UBSAN to catch undefined behavior
            return true;
        }
        
        static bool check_deterministic(const std::string& input) {
            auto result1 = process(input);
            auto result2 = process(input);
            return result1 == result2;
        }
    };

33.23 Performance Fuzzing

Detecting algorithmic complexity vulnerabilities:

    extern "C" int LLVMFuzzerTestOneInput(const uint8_t* data, 
                                          size_t size) {
        auto start = std::chrono::high_resolution_clock::now();
        
        process_input(data, size);
        
        auto end = std::chrono::high_resolution_clock::now();
        auto duration = std::chrono::duration_cast<
            std::chrono::milliseconds>(end - start);
        
        // Fail if processing takes too long
        if (duration.count() > 1000) {
            __builtin_trap();
        }
        
        return 0;
    }

33.24 Security Fuzzing Checklist

Comprehensive security testing covers:

Input validation:
- Null bytes in strings
- Unicode edge cases (bom, invalid sequences)
- Integer overflow/underflow
- Buffer boundary conditions (exactly size, size+1, size-1)
- Format string specifiers
- Path traversal sequences
- Shell metacharacters
- XML/JSON entity expansion

State machine testing:
- Invalid state transitions
- Race conditions in concurrent access
- Resource exhaustion scenarios
- Authentication bypass attempts
- Authorization edge cases

Cryptographic testing:
- Invalid key lengths
- Authentication tag manipulation
- IV/nonce reuse detection
- Padding oracle scenarios
- Side-channel leakage

33.25 Integration with Property-Based Testing

Hypothesis integration for Python:

    from hypothesis import given, strategies as st
    from hypothesis.stateful import RuleBasedStateMachine, rule

    class DatabaseMachine(RuleBasedStateMachine):
        def __init__(self):
            super().__init__()
            self.model = {}
            self.db = InMemoryDB()

        @rule(key=st.text(), value=st.integers())
        def set_item(self, key, value):
            self.model[key] = value
            self.db.set(key, value)

        @rule(key=st.text())
        def get_item(self, key):
            expected = self.model.get(key)
            actual = self.db.get(key)
            assert expected == actual

    TestDB = DatabaseMachine.TestCase

33.26 Fuzzing Best Practices Summary

Effective fuzzing requires systematic approach:

First, instrument builds with appropriate sanitizers. AddressSanitizer catches most memory errors, MemorySanitizer detects uninitialized reads, and UndefinedBehaviorSanitizer identifies undefined behavior. Running fuzzing without sanitizers misses most bug categories.

Second, maintain a quality seed corpus. The initial corpus guides fuzzing toward interesting code paths. Include valid inputs, edge cases, and historically interesting inputs from crash triage.

Third, establish continuous fuzzing. Security vulnerabilities discovered in code deployed six months ago remain dangerous. Continuous fuzzing catches regressions and new vulnerabilities as code evolves.

Fourth, triage findings systematically. Not all crashes represent security vulnerabilities. Establish severity classification based on exploitability, impact, and affected versions.

Fifth, integrate with development workflow. Fuzzing should block releases when new crashes appear. Regression tests should prevent previously fixed crashes from recurring.

The combination of coverage-guided fuzzing and property-based testing provides comprehensive verification for both security vulnerability detection and functional property validation.
