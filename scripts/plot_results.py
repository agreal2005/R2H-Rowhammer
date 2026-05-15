import matplotlib.pyplot as plt
import numpy as np

# Final data from ChampSim experiments
configs = ['Trad-RH\nConventional', 'Trad-RH\nRandomized', 'R2H\nConventional', 'R2H\nRandomized']
accesses = [967663, 321, 251095, 280621]
misses = [1165, 321, 4488, 7434]
miss_rates = [1165/967663*100, 100, 4488/251095*100, 7434/280621*100]

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.5))
colors = ['#2196F3', '#FF9800', '#4CAF50', '#F44336']

# LLC Accesses
bars1 = ax1.bar(configs, accesses, color=colors, edgecolor='black')
ax1.set_ylabel('LLC Accesses', fontsize=12)
ax1.set_title('LLC Access Count', fontsize=13, fontweight='bold')
ax1.set_yscale('log')
ax1.set_ylim(100, 2000000)
for bar, val in zip(bars1, accesses):
    ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height()*1.15, f'{val:,}', ha='center', fontsize=9, fontweight='bold')
ax1.axhline(y=321, color='red', linestyle='--', alpha=0.3, label='Trad-RH Rand baseline')
ax1.legend(fontsize=8)

# Annotate the key finding
ax1.annotate('875x increase', xy=(2, 280621), xytext=(2.5, 500000),
            arrowprops=dict(arrowstyle='->', color='red'), fontsize=10, color='red', fontweight='bold')

# Miss Rate
bars2 = ax2.bar(configs, miss_rates, color=colors, edgecolor='black')
ax2.set_ylabel('LLC Miss Rate (%)', fontsize=12)
ax2.set_title('LLC Miss Rate', fontsize=13, fontweight='bold')
for bar, val in zip(bars2, miss_rates):
    ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height()+0.8, f'{val:.1f}%', ha='center', fontsize=9, fontweight='bold')

plt.suptitle('R2H Rowhammer Attack: Conventional vs Randomized LLC', fontsize=14, fontweight='bold')
plt.tight_layout()
plt.savefig('results/r2h_results.png', dpi=150, bbox_inches='tight')
print("Plot saved to results/r2h_results.png")
