#!/usr/bin/env python3

import re
import sys

from typing import Dict
from typing import List
from typing import Optional
from typing import Set
from typing import Union

FLAG_NAMES: Dict[str, Union[str, List[str]]] = {
    'AVX2': 'avx2',
    'AVX512BW': 'avx512bw',
    'AVX512CD': 'avx512cd',
    'AVX512DQ': 'avx512dq',
    'AVX512F': 'avx512f',
    'AVX512VL': 'avx512vl',
    'AVX': 'avx',
    'BMI1': 'bmi1',
    'BMI2': 'bmi2',
    'CMOV': 'cmov',
    'CMPXCHG16B': 'cx16',
    'CMPXCHG8B': 'cx8',
    'F16C': 'f16c',
    'FMA': 'fma',
    'FPU': 'fpu',
    'FXSR': ['fxsr', 'fxsr_opt'],
    'LAHF': 'lahf_lm',
    'LZCNT': 'abm',
    'MMX': ['mmx', 'mmxext'],
    'MOVBE': 'movbe',
    'OSXSAVE': 'xsave',
    'POPCNT': ['popcnt', 'abm'],
    'SCE': 'syscall',
    'SSE2': 'sse2',
    'SSE3': ['sse3', 'ssse3', 'pni'],
    'SSE4-1': 'sse4_1',
    'SSE4-2': 'sse4_2',
    'SSE': 'sse',
    'SSSE3': 'ssse3',
}

X86_64_REQUIRED_FEATURES: List[str] = [
    'CMOV',
    'CMPXCHG8B',
    'FPU',
    'FXSR',
    'MMX',
    'SCE',
    'SSE',
    'SSE2',
]

X86_64_V2_REQUIRED_FEATURES: List[str] = [
    'CMPXCHG16B',
    'LAHF',
    'POPCNT',
    'SSE3',
    'SSE4-1',
    'SSE4-2',
    'SSSE3',
]

X86_64_V3_REQUIRED_FEATURES: List[str] = [
    'AVX',
    'AVX2',
    'BMI1',
    'BMI2',
    'F16C',
    'FMA',
    'LZCNT',
    'MOVBE',
    'OSXSAVE',
]

X86_64_V4_REQUIRED_FEATURES: List[str] = [
    'AVX512BW',
    'AVX512CD',
    'AVX512DQ',
    'AVX512F',
    'AVX512VL',
]

def main():
    flags = get_current_cpu_flags()
    print('{}'.format(get_max_feature_set(flags)))

def get_current_cpu_flags() -> Set[str]:
    flags = set()

    # Read /proc/cpuinfo
    lines = []
    with open('/proc/cpuinfo', 'r') as f:
        lines = [line.strip() for line in f.readlines()]

    # Get lines defining flags
    flag_lines = []
    flag_line_expression = re.compile(r'^(flags)(\s*:\s*)(.*)$', re.MULTILINE)
    for match in re.findall(flag_line_expression, '\n'.join(lines)):
        flag_lines += [' '.join(match[2].split())]

    # There could be different flags in different flag lines.
    # We add all flags from all flag lines to set in order to
    # get maximum number of flags supported.
    for line in flag_lines:
        for flag in line.split(' '):
            flags.add(flag)

    return flags

def has_feature(flags: Set[str], feature: str) -> bool:
    if not isinstance(feature, str):
        raise Exception('Given feature is not of type str')
    if feature not in FLAG_NAMES:
        raise Exception('Unknown feature flag "{}"'.format(feature))

    # Check if there are multiple flags that signal this feature
    flag = FLAG_NAMES[feature]
    if isinstance(flag, str):
        required_flags = [flag]
    elif isinstance(flag, list):
        required_flags = flag

    return True in (flag in flags for flag in required_flags)

def supports_feature_set(flags: Set[str], featureset: List[str]) -> bool:
    return not False in (has_feature(flags, feat) for feat in featureset)

def supports_x86v1(flags: Set[str]) -> bool:
    return supports_feature_set(flags, X86_64_REQUIRED_FEATURES)

def supports_x86v2(flags: Set[str]) -> bool:
    return supports_feature_set(flags, X86_64_V2_REQUIRED_FEATURES)

def supports_x86v3(flags: Set[str]) -> bool:
    return supports_feature_set(flags, X86_64_V3_REQUIRED_FEATURES)

def supports_x86v4(flags: Set[str]) -> bool:
    return supports_feature_set(flags, X86_64_V4_REQUIRED_FEATURES)

def get_max_feature_set(flags) -> Optional[str]:
    if supports_x86v1(flags):
        if supports_x86v2(flags):
            if supports_x86v3(flags):
                if supports_x86v4(flags):
                    return 'x86-64-v4'
                return 'x86-64-v3'
            return 'x86-64-v2'
        return 'x86-64'

    return None

if __name__ == '__main__':
    sys.exit(main())
