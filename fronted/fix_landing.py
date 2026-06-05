import re
with open('fronted/src/routes/+page.svelte', 'r') as f:
    text = f.read()

replacements = {
    r'bg-\[\#0B0F17\](?!\/)': 'bg-white dark:bg-[#0B0F17]',
    r'bg-\[\#0B0F17\]\/20': 'bg-white/20 dark:bg-[#0B0F17]/20',
    r'bg-\[\#0B0F17\]\/75': 'bg-white/95 dark:bg-[#0B0F17]/75',
    r'bg-\[\#121826\](?!\/)': 'bg-zinc-50 dark:bg-[#121826]',
    r'bg-\[\#121826\]\/80': 'bg-zinc-50/80 dark:bg-[#121826]/80',
    r'bg-\[\#121826\]\/90': 'bg-zinc-50/90 dark:bg-[#121826]/90',
    r'text-\[\#E8ECF4\]': 'text-zinc-900 dark:text-[#E8ECF4]',
    r'text-\[\#A3ADBF\]': 'text-zinc-600 dark:text-[#A3ADBF]',
    r'text-\[\#7B8497\]': 'text-zinc-500 dark:text-[#7B8497]',
    r'border-\[\#242E43\]': 'border-zinc-200 dark:border-[#242E43]',
    r'border-\[\#33415C\]': 'border-zinc-300 dark:border-[#33415C]',
    r'border-\[\#0B0F17\]': 'border-white dark:border-[#0B0F17]',
    r'hover\:bg-\[\#1A2233\]': 'hover:bg-zinc-100 dark:hover:bg-[#1A2233]',
    r'hover\:bg-\[\#33415C\]': 'hover:bg-zinc-200 dark:hover:bg-[#33415C]',
    r'hover\:border-\[\#242E43\]': 'hover:border-zinc-300 dark:hover:border-[#242E43]',
    r'bg-\[\#0F1522\]': 'bg-zinc-100 dark:bg-[#0F1522]',
    r'bg-white text-black': 'bg-black dark:bg-white text-white dark:text-black',
    r'bg-gray-200': 'bg-zinc-800 dark:bg-gray-200',
    r'selection\:bg-\[\#5B8CFF\]\/40 selection\:text-white': 'selection:bg-zinc-900 selection:text-white dark:selection:bg-[#5B8CFF]/40 dark:selection:text-white'
}

for pattern, replacement in replacements.items():
    text = re.sub(pattern, replacement, text)

with open('fronted/src/routes/+page.svelte', 'w') as f:
    f.write(text)

