# R2H: Rowhammer Attack in Presence of Randomized LLC

Course project reproducing the R2H attack from HiPCW 2025 using ChampSim and Ramulator2.

---

## Quick Start (5 minutes)

### Prerequisites
- Ubuntu/Debian or WSL
- `g++-12` or newer, `cmake`, `python3`, `pip`

### 1. Clone and Setup
```bash
git clone https://github.com/agreal2005/R2H-Rowhammer.git
cd R2H-Rowhammer

# Install system dependencies
sudo apt-get update && sudo apt-get install -y curl zip unzip tar cmake python3-pip

# Install Python dependencies
pip3 install matplotlib numpy

```

### 2. Build ChampSim (with Randomized LLC Patch)

```bash
cd champsim/src

# Initialize vcpkg and install dependencies
git submodule update --init
./vcpkg/bootstrap-vcpkg.sh
./vcpkg/vcpkg install

# The randomized LLC patch is already applied to src/cache.cc
# If needed, re-apply:
# cp src/cache.cc.bak src/cache.cc
# patch -p1 < ../patch/llc_random.patch

# Build
./config.sh champsim_config.json
make -j$(nproc)
cd ../..

```

### 3. Generate Attack Traces

```bash
python3 scripts/generate_traces.py
```

This creates binary ChampSim traces for both Trad-RH and R2H attack patterns.

### 4. Run Experiments

```bash
cd champsim/src

# Experiment 1: Traditional Rowhammer + Conventional LLC
echo "=== Exp 1: Trad-RH + Conventional ==="
./bin/champsim --warmup-instructions 0 --simulation-instructions 1280000 \
  ../../traces/trad_rh/trad_128.champsim 2>&1 | grep -E "LLC TOTAL|L2C TOTAL|DRAM|IPC"

# Experiment 2: Traditional Rowhammer + Randomized LLC
echo "=== Exp 2: Trad-RH + Randomized ==="
CHAMPSIM_RANDOMIZE_LLC=1 ./bin/champsim --warmup-instructions 0 --simulation-instructions 1280000 \
  ../../traces/trad_rh/trad_128.champsim 2>&1 | grep -E "LLC TOTAL|L2C TOTAL|DRAM|IPC"

# Experiment 3: R2H Attack + Conventional LLC
echo "=== Exp 3: R2H + Conventional ==="
./bin/champsim --warmup-instructions 0 --simulation-instructions 1740800 \
  ../../traces/r2h/r2h_final.champsim 2>&1 | grep -E "LLC TOTAL|L2C TOTAL|DRAM|IPC"

# Experiment 4: R2H Attack + Randomized LLC
echo "=== Exp 4: R2H + Randomized ==="
CHAMPSIM_RANDOMIZE_LLC=1 ./bin/champsim --warmup-instructions 0 --simulation-instructions 1740800 \
  ../../traces/r2h/r2h_final.champsim 2>&1 | grep -E "LLC TOTAL|L2C TOTAL|DRAM|IPC"

cd ../..
```

### 5. Generate Plot

```bash
python3 scripts/plot_results.py
```

Output: `results/r2h_results.png`

### How Randomization Works

The randomized LLC is implemented in `champsim/src/src/cache.cc`:

```cpp
long CACHE::get_set_index(champsim::address address) const {
  static bool randomize = []() {
    const char* env = std::getenv("CHAMPSIM_RANDOMIZE_LLC");
    return env != nullptr && std::string(env) == "1";
  }();
  if (!randomize) {
    // Conventional: deterministic bit-slice
    return address.slice(...).to<long>();
  }
  // Randomized: SplitMix64 hash
  uint64_t a = address.to<uint64_t>();
  a = (a ^ (a >> 30)) * 0xbf58476d1ce4e5b9ULL;
  a = (a ^ (a >> 27)) * 0x94d049bb133111ebULL;
  a = a ^ (a >> 31);
  return static_cast<long>((a >> OFFSET_BITS) % NUM_SET);
}
```

Toggle via: `CHAMPSIM_RANDOMIZE_LLC=1` (randomized) or unset (conventional).

### Repository Structure

```text
R2H-Rowhammer/
├── champsim/
│   ├── src/                  # ChampSim source (with randomization patch)
│   ├── config/               # JSON config files
│   └── patch/                # LLC randomization patch file
├── ramulator2/
│   ├── src/                  # Ramulator2 source
│   └── configs/              # AQUA and trace YAML configs
├── traces/
│   ├── trad_rh/              # Traditional Rowhammer traces
│   └── r2h/                  # R2H attack traces
├── scripts/
│   ├── generate_traces.py    # Trace generation
│   └── plot_results.py       # Results visualization
├── results/
│   ├── champsim_outputs/     # Raw experiment outputs
│   └── r2h_results.png       # Final comparison plot
└── README.md
```

(showing key files only)